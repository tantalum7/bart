
# Library imports
import numpy as np
import multiprocessing as mp
import ctypes
import time
import v20
from v20.pricing import Price

# Project imports
from data_objects.sync_fifo import NumpySynchronisedFifo


class LivePriceCache(object):

    def __init__(self, cfg_dict, instrument_dict, cache_size=100):
        """
        This class presents a FIFO based array of the latest market data.

        :param cfg_dict:
        :param instrument_dict:
        :param cache_size:
        """
        # Init class vars
        self._dpoint_count = 0
        self._cfg = cfg_dict
        self._kill_process_event = mp.Event()

        # Init sync data fifos
        self._init_sync_fifos(instrument_dict, cache_size)

        # Spawn live price process, and start it
        self._process = _LivePriceCacheProcess(cfg_dict, self._instrument_arrays, self._kill_process_event)
        self._process.start()

    def __getitem__(self, key):
        return self._instrument_arrays[key]

    @property
    def dataset_memory(self):
        return self._dpoint_count * 32 * 4

    def _init_sync_fifos(self, instrument_dict, cache_size):
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
        while not self.kill_event.is_set()

            # Keep looping until the kill event is set

            # C            # Pump the stream generator
            #             data = next(stream)[1]heck if the data is a Price object
            if isinstance(data, Price):

                for field in self.instrument_arrays[data.instrument].keys():
                    self.instrument_arrays[data.instrument][field].push(getattr(data, field), float(data.time))

            # Sleep so we don't overload the api (broker api has rate limiting)
            time.sleep(0.25)
