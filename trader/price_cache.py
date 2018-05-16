
# Library imports
import numpy as np
import multiprocessing as mp
import ctypes
import time
import v20
from v20.pricing import Price


class NumpyFixedFifo(object):

    def __init__(self, fixed_size):
        self._array = mp.Array(ctypes.c_float, fixed_size)
        self._num_pushes = 0
        self._size = fixed_size

    @property
    def num_pushes(self):
        return self._num_pushes

    @property
    def size(self):
        return self._size

    def push(self, value):
        self._array = np.roll(self._array, 1)
        self._array[0] = value
        self._num_pushes += 1

    def array(self):
        return self._array[0:self.num_pushes if self.num_pushes < self.size else self.size]



class LivePriceCache(object):

    # Start a thread to get prices

    def __init__(self, cfg_dict, instrument_dict, cache_size=100):
        self._dpoint_count = 0
        self._cfg = cfg_dict

        self._init_shared_arrays(instrument_dict, cache_size)

        self._kill_process_event = mp.Event()

        self._process = _LivePriceCacheProcess(cfg_dict, self._instrument_arrays, self._kill_process_event)

        self._process.start()

    @property
    def dataset_memory(self):
        return self._dpoint_count * 32 * 4

    def _init_shared_arrays(self, instrument_dict, cache_size):
        self._instrument_arrays = {}
        for instrument, fields in instrument_dict.items():
            field_arrays = {}
            for field in fields:
                field_arrays[field] = (NumpyFixedFifo(cache_size), NumpyFixedFifo(cache_size))
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
                          token=self.cfg["token"])

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
                    self.instrument_arrays[data.instrument][field].push(getattr(data, field))

            # Sleep so we don't overload the api (broker api has rate limiting)
            time.sleep(0.25)
