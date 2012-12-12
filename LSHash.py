import os
import json

from collections import defaultdict

try:
    import redis
except ImportError:
    redis = False

try:
    import numpy as np
except ImportError:
    raise ImportError("LSHash requires numpy to be pre-installed.")

try:
    from bitarray import bitarray
except ImportError:
    bitarray = False


class LSHash(object):
    """ LSHash implments locality sensitive hashing on for vectors of
    dimension `input_dim`.

    Attributes:

    :param hash_size:
        The length of the resulting binary hash.
    :param input_dim:
        The dimension of the input vector.
    :param num_hashtables:
        (optional) The number of hash tables used for multiple lookups.
    :param storage:
        (optional) Specify the name of the storage to be used for the index
        storage. Options include "redis".
    :param matrices_filename:
        (optional) Specify the path to the .npz file random matrices are stored
        or to be stored if the file does not exist yet
    :param overwrite:
        (optional) Whether to overwrite the matrices file if it already exist
    """
    def __init__(self, hash_size, input_dim, num_hashtables=1, storage=None,
                 matrices_filename=None, overwrite=False):

        self.hash_size = hash_size
        self.input_dim = input_dim
        self.num_hashtables = num_hashtables
        if storage is None:
            self.storage = None
        else:
            self.storage = storage.lower()

        if matrices_filename and not matrices_filename.endswith('.npz'):
            raise ValueError("The specified file name must end with .npz")
        self.matrices_filename = matrices_filename
        self.overwrite = overwrite
        self._initialize_uniform_planes()
        self._initialize_hashtables()

    def _initialize_uniform_planes(self):
        """
        if filename exist and (overwrite or not a file), save the file by
        np.save.
        if filename exist and is a file and not overwrite, load by np.load.

        if filename does not exist and regardless of overwrite, only set
        self.uniform_planes.
        """

        if self.matrices_filename:
            file_exist = os.path.isfile(self.matrices_filename)
            if file_exist and not self.overwrite:
                try:
                    npzfiles = np.load(self.matrices_filename)
                except IOError:
                    print("Cannot load specified file as a numpy array")
                    raise
                else:
                    npzfiles = sorted(npzfiles.items(), key=lambda x: x[0])
                    self.uniform_planes = [t[1] for t in npzfiles]
            else:
                self.uniform_planes = [self._generate_uniform_planes()
                                       for _ in xrange(self.num_hashtables)]
                try:
                    np.savez_compressed(self.matrices_filename,
                                        *self.uniform_planes)
                except IOError:
                    print("IOError when saving matrices to specificed path")
                    raise
        else:
            self.uniform_planes = [self._generate_uniform_planes()
                                   for _ in xrange(self.num_hashtables)]

    def _initialize_hashtables(self):
        """ Initialize the hash tables such that each record will be in the
        form of (,) """
        if self.storage is None:
            self.hash_tables = [defaultdict(list)
                               for _ in xrange(self.num_hashtables)]
        elif self.storage == "redis":
            # TODO change to custom config details
            try:
                self.hash_tables = [redis.StrictRedis(host='localhost',
                                                      port=6379,
                                                      db=i)
                                    for i in xrange(self.num_hashtables)]
            except Exception:
                print("ConecctionError occur when trying to connect to redis")
                raise
        else:
            raise ValueError("The storage name you specified is not supported")

    def _generate_uniform_planes(self):
        """ generate uniformly distributed hyperplanes and return it as a 2D
        numpy array.
        """
        return np.random.randn(self.hash_size, self.input_dim)

    def _hash(self, planes, input_point):
        """ generates the binary hash of `input_point` using random projection
        and returns it.
        """
        try:
            input_point = np.array(input_point)  # for faster dot product
            projections = np.dot(planes, input_point)
        except TypeError as e:
            print("""The input point needs to be an array-like object with
                  numbers only elements""")
            raise
        except ValueError as e:
            print("""The input point needs to be of the same dimension as
                  `input_dim` when initializing this LSHash instance""", e)
            raise
        else:
            return "".join(['1' if i > 0 else '0' for i in projections])

    def _as_np_array(self, json_or_array_or_dict):
        if isinstance(json_or_array_or_dict, basestring):
            try:
                array_or_dict = json.loads(json_or_array_or_dict)
            # TODO fix it
            except Exception:
                raise
        else:
            array_or_dict = json_or_array_or_dict

        if isinstance(array_or_dict, dict):
            return np.asarray(array_or_dict.keys()[0])
        elif isinstance(array_or_dict, list) or isinstance(array_or_dict, tuple):
            try:
                return np.asarray(array_or_dict)
            except ValueError as e:
                print("The input needs to be an array-like object", e)
                raise
        else:
            raise TypeError("query data is not supported")

    def index(self, input_point, extra_data=False):
        """ index a single input point. If `extra_data` is provided, it will
        become the value of the dictionary {input_point: extra_data}, which in
        turn will become the value of the hash table
        """

        if extra_data:
            value = {input_point: extra_data}
        else:
            value = tuple(input_point)

        for i, table in enumerate(self.hash_tables):
            if self.storage is None:
                table[self._hash(self.uniform_planes[i], input_point)]\
                        .append(value)
            elif self.storage == "redis":
                table.rpush(self._hash(self.uniform_planes[i], input_point),
                            json.dumps(value))
            else:
                raise ValueError("Only redis is allowed for now")

    def query(self, query_point, num_results=None, distance_func="euclidian"):
        """ return num_results of results based on the supplied metric """

        if distance_func == "euclidian":
            d_func = LSHash.euclidian_dist
        elif distance_func == "cosine":
            d_func = LSHash.cosine_dist
        elif distance_func == "l1norm":
            d_func = LSHash.l1norm_dist
        else:
            raise ValueError("The distance function name entered is invalid.")

        candidates = set()

        for i, table in enumerate(self.hash_tables):
            if self.storage is None:
                match_list = table.get(self._hash(self.uniform_planes[i],
                                                  query_point), [])
            elif self.storage == "redis":
                match_list = table.lrange(self._hash(self.uniform_planes[i],
                                                     query_point), 0, -1)
            else:
                raise ValueError
            candidates.update(match_list)

        # rank candidates
        candidates = [(ix, d_func(query_point, self._as_np_array(ix)))
                      for ix in candidates]

        candidates.sort(key=lambda x: x[1])
        if num_results:
            return candidates[:num_results]
        else:
            return candidates

    ### distance functions

    @staticmethod
    def hamming_dist(bitarray1, bitarray2):
        xor_result = bitarray(bitarray1) ^ bitarray(bitarray2)
        return xor_result.count()

    @staticmethod
    def euclidian_dist(x, y):
        return np.linalg.norm(x - y)

    @staticmethod
    def l1norm_dist(x, y):
        return sum(abs(x - y))

    @staticmethod
    def cosine_dist(x, y):
        return 1 - np.dot(x, y) / ((np.dot(x, x) * np.dot(y, y)) ** 0.5)
