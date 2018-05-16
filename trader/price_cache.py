
# Library imports
import numpy as np
import multiprocessing as mp
import ctypes
import time
import v20
from v20.pricing import Price


class NumpyFixedFifo(object):

    def __init__(self, fixed_size, default_value=-1):
        self._array = np.full(fixed_size, default_value)

    def push(self, value):
        self._array = np.roll(self._array, 1)
        self._array[0] = value

    def array(self):
        return np.copy(self._array)


class LivePriceCache(object):

    # Start a thread to get prices 

    def __init__(self, cfg_dict, instrument_dict, cache_size=100):
        self._dpoint_count = 0
        self._cfg = cfg_dict

        self._init_shared_arrays(instrument_dict, cache_size)

        self._process = _LivePriceCacheProcess(cfg_dict, self._instrument_arrays)

        self._process.start()

    @property
    def dataset_memory(self):
        return self._dpoint_count * 32 * 4

    def _init_shared_arrays(self, instrument_dict, cache_size):
        self._instrument_arrays = {}
        for instrument, fields in instrument_dict.items():
            field_arrays = {}
            for field in fields:
                field_arrays[field] = (mp.Array(ctypes.c_float, cache_size), mp.Array(ctypes.c_float, cache_size))
                self._dpoint_count += 2 * cache_size
            self._instrument_arrays[instrument] = field_arrays




class _LivePriceCacheProcess(mp.Process):

    def __init__(self, cfg_dict, instrument_arrays):
        super(_LivePriceCacheProcess, self).__init__()

        self.cfg = cfg_dict
        self.instrument_arrays = instrument_arrays

    def run(self):

        print("process up")

        api = v20.Context(hostname=self.cfg["streaming_hostname"],
                          port=self.cfg["port"],
                          token=self.cfg["token"])

        instrument_str_list = ",".join(self.instrument_arrays.keys())

        stream = api.pricing.stream(self.cfg["active_account"], instruments=instrument_str_list).parts()

        while True:

            g = next(stream)
            if isinstance(g[1], Price):
                print("{}: {}".format(g[1].instrument, g[1].closeoutBid))
            time.sleep(0.25)
