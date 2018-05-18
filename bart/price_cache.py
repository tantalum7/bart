
# Library imports
import numpy as np
import multiprocessing as mp
import ctypes
import time
import v20
from v20.pricing import Price

# Project imports
from data_objects.sync_fifo import NumpySynchronisedFifo
from bart.v20config import V20Config


class LivePriceCache(object):

    def __init__(self, v20config, instrument_dict, cache_size=100):
        # type: (V20Config, dict, int) -> None
        """
        This class presents a FIFO based array of the latest market data.
        """
        # Init class vars
        self._dpoint_count = 0
        self._v20config = v20config
        self._kill_process_event = mp.Event()

        # Init sync data fifos
        self._init_sync_fifos(instrument_dict, cache_size)

        # Spawn live price process, and start it
        self._process = _LivePriceCacheProcess(v20config, self._instrument_arrays, self._kill_process_event)
        self._process.start()

    def __getitem__(self, key):
        return self._instrument_arrays[key]

    @property
    def instruments(self):
        return self._instrument_arrays.copy()
    
    @property
    def dataset_memory(self):
        return self._dpoint_count * 32 * 4

    def _init_sync_fifos(self, instrument_dict, cache_size):
        self._instrument_arrays = {}
        for instrument, fields in instrument_dict.items():
            field_arrays = {}
            for field in fields:
                field_arrays[field] = NumpySynchronisedFifo(cache_size)
                self._dpoint_count += 2 * cache_size
            self._instrument_arrays[instrument] = field_arrays


class _LivePriceCacheProcess(mp.Process):

    def __init__(self, v20config, instrument_arrays, kill_event):
        # type: (V20Config, dict, mp.Event) -> None
        super(_LivePriceCacheProcess, self).__init__()

        self.v20config = v20config
        self.instrument_arrays = instrument_arrays
        self.kill_event = kill_event

    def run(self):

        # Create streaming api context
        api = v20.Context(hostname=self.v20config.streaming_hostname,
                          port=self.v20config.port,
                          token=self.v20config.token,
                          datetime_format=self.v20config.datetime_format)

        # Squash instrument list into a csv string
        instrument_str_list = ",".join(self.instrument_arrays.keys())

        # Prepare stream
        stream = api.pricing.stream(self.v20config.active_account, instruments=instrument_str_list).parts()

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
