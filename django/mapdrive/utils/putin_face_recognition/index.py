import annoy
import numpy as np
import logging
import glob
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommenderVectorIndex(object):
    """Database index for finding nearest neighbors. The rows are float
    vectors, such as Word2Vec vectors or some other embeddings.

    """

    def __init__(self, vector_size, n_indices=1, n_trees=16):
        """Creates an instance of recommender index which contains one or many
        AnnoyIndex instances.

        Args:
            vector_size (int): Size of vector annoy index keeps.
            n_indices (int, optional): Number of annoy indices to create.
            n_trees (int, optional): Number of trees in each annoy
                index. A larger value will give more accurate results,
                but larger indexes.
        """
        self.indices = [annoy.AnnoyIndex(vector_size) for _ in
                        range(n_indices)]
        self.vector_size = vector_size
        self.n_trees = n_trees

    @property
    def n_indices(self):
        return len(self.indices)

    def _fill_build_index(self, index, data):
        """Fills one annoy index with data and build.

        Args:
            index (annoy.AnnoyIndex): Index to fill and build.
            data (numpy.array): Array with vectors.
        """
        logger.info("INSERTing {0} vectors.".format(data.shape[0]))
        for i in xrange(data.shape[0]):
            index.add_item(i, data[i])
        logger.info("Building index.")
        index.build(self.n_trees)

    def fill_build(self, data):
        """Fills annoy indices with vectors in data and builds all indices.

        Args:
            data (numpy.array, list of numpy.array): If `self.n_indices` ==
                1, then `data` is a numpy.array with number of columns ==
                `self.vector_size`. Otherwise, `data` is a list of length
                equal to `self.n_indices` of `numpy.array`'s with the shape
                above.
        """
        assert (self.n_indices == 1 and isinstance(data, np.ndarray)) or (
            self.n_indices > 1 and isinstance(data, list) and all(map(
                lambda x: isinstance(x, np.ndarray), data)))

        logger.info("Fill {0} indices.".format(self.n_indices))
        if self.n_indices == 1:
            self._fill_build_index(self.indices[0], data)
        else:
            _parallel_fill_build(self, data)

    def get_n_items(self):
        """Gets a list of sizes of each index.

        Returns:
            res (list of ints): List of sizes of each index.

        """
        return [index.get_n_items() for index in self.indices]

    def get_nns_by_vector(self, vector, n_neighbors, n_index=0, search_k=-1,
                          include_distances=True):
        """Returns `n_neighbors` closest items of `vector`
        in index with number `n_index`.

        Args:
            vector (numpy.array): Vector which neighbors you want to find.
            n_neighbors (int): How many neighbors to find.
            n_index (int): In which index to search.
            search_k: The number of nodes to inspect during searching. A larger
                value will give more accurate results,
                but will take longer time to return.
            include_distances (bool): Whether to include distances or not.
                If True, it will return a 2 element tuple with two lists in it:
                the second one containing all corresponding distances.

        Returns:
            res (list or tuple of two lists): List of neigbors ids. If
                `include_distances` is True, then tuple of two lists.
        """
        res = self.indices[n_index].get_nns_by_vector(vector, n_neighbors,
                                                      search_k=search_k,
                                                      include_distances=include_distances)
        return res

    def get_item_vector(self, i, n_index=0):
        """Returns vector with number `i` from index `n_index`.

        Args:
            i (int): Id of vector.
            n_index: Number of index for searching.
        """
        return self.indices[n_index].get_item_vector(i)

    def save(self, fname):
        for i in range(self.n_indices):
            index = self.indices[i]
            fname_out = fname + str(i)
            logger.info("Save index #{0} to {1}".format(i, fname_out))
            index.save(fname_out)

    @staticmethod
    def __resolve_index_number(fname):
        match = re.fullmatch(r".*?(\d+)", fname)
        return int(match.group(1))

    def load(self, fname):
        index_fnames = glob.glob(fname + '*')
        index_fnames = [fname + '0'] 
        assert len(index_fnames) == self.n_indices
        for index_fname in index_fnames:
            self.indices[0] = annoy.AnnoyIndex(self.vector_size)
            self.indices[0].load(index_fname)
