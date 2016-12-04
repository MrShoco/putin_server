from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from jfu.http import upload_receive, UploadResponse, JFUResponse
from django.conf import settings
from time import sleep
import json
import os
from django.http import JsonResponse
from background_task import background

from .utils.putin_face_recognition.putin_face_finder import find_putin


@background(schedule=5)
def process_video(id):
    find_putin(File.objects.get(id=id))

def track_uploaded(request, email, file):
    try:
        user = User.objects.get(username=email)
        profile = user.profile
        user.save()
    except User.DoesNotExist:
        user = User(username=email)
        user.save()
        profile = Profile()
        profile.total_distance = 0
        profile.user = user
    profile.save()
    login(request, user)

    process_video(file)

def process_result(request, id):
  file = File.objects.get(pk=id)
  artifacts = file.process_result_artifact.all()
  context = {'file': file, 'artifacts': artifacts}
  return render(request, 'process_result.html', context=context)


@require_POST
def upload( request ):
    file = upload_receive( request )

    instance = File(file = file)
    instance.save()

    basename = os.path.basename( instance.file.path )

    file_dict = {
        'name' : basename,
        'size' : file.size,
        'url': settings.MEDIA_URL + 'track/' + basename,
        'deleteUrl': reverse('jfu_delete', kwargs = {'pk': instance.pk }),
        'id': instance.pk,
        'deleteType': 'POST',
    }
    sleep(0.1)
    return UploadResponse( request, file_dict )


@require_POST
def upload_delete(request, pk):
    success = True
    try:
        instance = File.objects.get(pk=pk)
        os.unlink(instance.file.path)
        instance.delete()
    except File.DoesNotExist:
        success = False
    return JFUResponse(request, success)


@require_POST
def send(request):
    email = request.POST["email"]
    files = list(map(int, request.POST["file-ids"].split(",")))
    file = files[0]
    track_uploaded(request, email, file)
    return HttpResponseRedirect("/process_result/" +  str(file) + "/")


def index(request):
    context = {}
    return render(request, 'index.html', context=context)
