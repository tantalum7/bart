
# Library imports
import numpy as np


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

    def __init__(self, instrument_list):
        self._instruments = set(instrument_list)

    def subscribe_instrument(self, instrument):
        self._instruments.add(instrument)

    def unsubscribe_instrument(self, instrument):
        self._instruments.remove(instrument)

    def update_pricing(self):
        pass
    def stuf(self):
        return self._streaming_api.pricing.stream(self.active_account, instruments=instrument).parts()







if __name__ == "__main__":

    fifo = NumpyFixedFifo(10)

    print("done")