
# Library imports
import numpy as np
import multiprocessing as mp


class NumpySynchronisedArray(object):

    def __init__(self, c_type, size):
        # If size is a tuple/list (nD array) multiply all the numbers to get the flat size
        # If size is a number (1D array), flat_size is just the size
        self._flat_size = np.prod(np.array(size)) if type(size) in [list, tuple] else size
        self._raw_array = mp.RawArray(c_type, self._flat_size)
        self._size = size
        self._c_type = c_type
        self._lock = mp.RLock()

    def __enter__(self):
        self._lock.acquire()
        return np.frombuffer(self._raw_array, self._c_type, self._flat_size).reshape(self._size)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def __getitem__(self, key):
        with self as data:
            return np.array(data[key])

    def __setitem__(self, key, value):
        with self as data:
            data[key] = value

    def copy(self):
        with self as data:
            return np.array(data)