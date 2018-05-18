
# Library imports
import numpy as np
import ctypes
import multiprocessing as mp

# Project imports
from data_objects.sync_array import NumpySynchronisedArray


class NumpySynchronisedFifo(object):

    # Data/time keys
    DATA_KEY = 0
    TIME_KEY = 1

    def __init__(self, fixed_size):
        self._data_array = NumpySynchronisedArray(ctypes.c_float, fixed_size)
        self._time_array = NumpySynchronisedArray(ctypes.c_float, fixed_size)
        self._num_pushes = mp.Value(ctypes.c_long)
        self._size = fixed_size

    @property
    def num_pushes(self):
        return self._num_pushes.value

    @property
    def size(self):
        return self._size

    def __getitem__(self, key):
        if key is self.DATA_KEY:
            return self.array()[self.DATA_KEY]
        return self.array()[:key]

    def push(self, data, timestamp):
        with self._data_array as data_array:
            np.copyto(data_array, np.roll(data_array, 1))
        with self._time_array as time_array:
            np.copyto(time_array, np.roll(time_array, 1))
        self._data_array[self.DATA_KEY] = data
        self._time_array[self.TIME_KEY] = timestamp
        self._incr_pushes()

    def array(self):
        stop = self.num_pushes if self.num_pushes < self.size else self.size
        return np.array([self._data_array[:stop], self._time_array[:stop]])

    def latest(self):
        return np.array([self._data_array[0], self._time_array[0]])

    def latest_data(self):
        return self.latest()[self.DATA_KEY]

    def latest_time(self):
        return self.latest()[self.TIME_KEY]

    def data_array(self):
        return self.array()[self.DATA_KEY]

    def time_array(self):
        return self.array()[self.TIME_KEY]

    def _incr_pushes(self):
        with self._num_pushes.get_lock():
            self._num_pushes.value += 1