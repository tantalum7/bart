
# Library imports
import numpy as np
import multiprocessing as mp
import ctypes
import time
import v20
from v20.pricing import Price
from decimal import Decimal


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


class NumpyFixedFifo(object):

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
        d = np.array(self._data_array[:stop])
        dd = self._data_array.copy()
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

class LivePriceCache(object):

    # Start a thread to get prices

    def __init__(self, cfg_dict, instrument_dict, cache_size=100):
        self._dpoint_count = 0
        self._cfg = cfg_dict

        self._init_shared_arrays(instrument_dict, cache_size)

        self._kill_process_event = mp.Event()

        self._process = _LivePriceCacheProcess(cfg_dict, self._instrument_arrays, self._kill_process_event)

        self._process.start()

    def __getitem__(self, key):
        return self._instrument_arrays[key]

    @property
    def dataset_memory(self):
        return self._dpoint_count * 32 * 4

    def _init_shared_arrays(self, instrument_dict, cache_size):
        self._instrument_arrays = {}
        for instrument, fields in instrument_dict.items():
            field_arrays = {}
            for field in fields:
                field_arrays[field] = NumpyFixedFifo(cache_size)
                self._dpoint_count += 2 * cache_size
            self._instrument_arrays[instrument] = field_arrays




class _LivePriceCacheProcess(mp.Process):

    def __init__(self, cfg_dict, instrument_arrays, kill_event):
        super(_LivePriceCacheProcess, self).__init__()

        self.cfg = cfg_dict
        self.instrument_arrays = instrument_arrays
        self.kill_event = kill_event

    def run(self):

        # Create streaming api context
        api = v20.Context(hostname=self.cfg["streaming_hostname"],
                          port=self.cfg["port"],
                          token=self.cfg["token"],
                          datetime_format=self.cfg["datetime_format"])

        # Squash instrument list into a csv string
        instrument_str_list = ",".join(self.instrument_arrays.keys())

        # Prepare stream
        stream = api.pricing.stream(self.cfg["active_account"], instruments=instrument_str_list).parts()

        # Keep looping until the kill event is set
        while not self.kill_event.is_set():

            # Pump the stream generator
            data = next(stream)[1]

            # Check if the data is a Price object
            if isinstance(data, Price):

                for field in self.instrument_arrays[data.instrument].keys():
                    self.instrument_arrays[data.instrument][field].push(getattr(data, field), float(data.time))

            # Sleep so we don't overload the api (broker api has rate limiting)
            time.sleep(0.25)
