import cv2
import matplotlib.pyplot as plt
import openface
import os
from IPython import display
import pickle
import index
import numpy as np
from ...models import *

nnet = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')
align = openface.AlignDlib('/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat')

NNET_INP_SHAPE = 96
NNET_OUT_SHAPE = 128

PATH = 'django/mapdrive/utils/putin_face_recognition/'
IMAGE_PATH = ''
IMAGE_URL = '/media/'

class Video:
    def __init__(self, path):
        self.vidcap = cv2.VideoCapture(path)
        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.total_frames = self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        self.length = self.total_frames / self.fps
    
    def read(self):
        success, image = self.vidcap.read()
        if success:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return success, image
    
    def delayed_read(self, skip_seconds):
        skip_frames = int(self.fps * skip_seconds)
        success = True
        while success and skip_frames > 0:
            success, image = self.read()
            skip_frames -= 1
        return self.read()


def imread(fname):
    image = cv2.imread(fname)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def read_imgs(path):
    fnames = [os.path.join(path, x) for x in os.listdir(path)]
    images = []
    for fname in fnames:
        images.append(imread(fname))
    return images

def build_index_from(path_to_faces):
    fnames = os.listdir(path_to_faces)
    vector_index = index.RecommenderVectorIndex(NNET_OUT_SHAPE, n_trees=32)
    data = np.zeros((len(fnames), NNET_OUT_SHAPE))
    images = read_imgs(path_to_faces)
    for i, fname in enumerate(fnames):
        image = images[i]
        alignedFace = align.align(NNET_INP_SHAPE, image,\
                                  landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        try:
            vector = nnet.forward(alignedFace)
        except:
            print(i)
            print(fname)
            plt.imshow(image)
            plt.show()
        
        data[i] = vector
        images.append(image)
    vector_index.fill_build(data)
    return vector_index, images


### COPY-PASTE FROM "extract_frames_from_video.ipynb"
def mark_image_with_rectangles(image, rectangles):
    image = image.copy()
    for rect in rectangles:
        pt1 = (rect.left(), rect.top())
        pt2 = (rect.right(), rect.bottom())
        cv2.rectangle(image, pt1, pt2, (0, 255, 0), 2)
    return image

def process_frame(file, image, seconds):
    bbs = align.getAllFaceBoundingBoxes(image)
    if len(bbs) == 0:
        print "NOT FOUND ANY FACES ON THE FRAME IMAGE! FUCK"
        plt.imshow(image)
        plt.show()
        return
    for bb in bbs:
        print "PROCESS THIS FACE:"
        marked_image = mark_image_with_rectangles(image, [bb])
        plt.imshow(marked_image)
        plt.show()
        alignedFace = align.align(NNET_INP_SHAPE, image, bb, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        vector = nnet.forward(alignedFace)
        neighb_ids, dists = vector_index.get_nns_by_vector(vector, 3, search_k=10)
        
        if dists[0] < 0.7:
            image_name = file.file.name + str(seconds) + ".png"
            plt.imsave(image_name, image)
            artifact = ProcessResultArtifact.objects.create(url=IMAGE_URL + image_name, seconds=seconds, file=file)

        print "NEAREST NEIGHBORS IN ANNOY INDEX:"
        for n_id, dist in zip(neighb_ids, dists):
            print "ID:\t{0};\tFNAME:\t{1};\tDIST:\t{2:.3f}".format(n_id, putin_faces_fnames[n_id], dist)
        print "-----"*10


def find_nns(image):
    bbs = align.getAllFaceBoundingBoxes(image)
    if len(bbs) == 0:
        return None
    dists = []
    for bb in bbs:
        alignedFace = align.align(NNET_INP_SHAPE, image, bb, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        vector = nnet.forward(alignedFace)
        _, bb_dists = vector_index.get_nns_by_vector(vector, 1, search_k=10)
        dists.append(bb_dists[0])
    return dists

def extract_frames(path, seconds, verbose=100):
    basename = os.path.splitext(os.path.basename(path))[0]
    video = Video(path)
    success, image = video.delayed_read(seconds)
    while success:
        yield image

        success, image = video.delayed_read(seconds)

def find_putin(file):
    seconds = 1
    for (i, image) in enumerate(extract_frames(file.file.name, seconds)):
        process_frame(file, image, i * seconds)

vector_index = index.RecommenderVectorIndex(NNET_OUT_SHAPE)
vector_index.load(PATH + 'index_putin_faces.dump')
putin_faces_fnames = os.listdir(PATH + 'putin_faces/')
