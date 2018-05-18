
# Library imports
import v20

# Project imports
from bart.v20config import V20Config


class Bart(object):

    def __init__(self, cfg_filepath="v20.json"):

        # Load json config file
        self.v20config = V20Config(cfg_filepath)

        # Grab api contexts
        self._api = self._get_api_context()
        self._streaming_api = self._get_api_context(True)

        # Init
        self._populate_instrument_list()

    @property
    def instruments(self):
        return self._instruments

    @property
    def active_account(self):
        return self.v20config.active_account

    def get_pricing(self, instrument_list, since=None):
        resp = self._api.pricing.get(self.active_account, instruments=",".join(instrument_list))
        return {price.instrument: price for price in resp.get("prices", 200)}

    def get_pricing_stream(self, instrument):
        return self._streaming_api.pricing.stream(self.active_account, instruments=instrument).parts()

    def test_stream(self, instrument):
        return self._streaming_api.pricing.stream(self.active_account, instruments=instrument).parts()

    def _populate_instrument_list(self):
        self._instruments = self._api.account.instruments(self.active_account).get("instruments", 200)

    def _get_api_context(self, streaming=False):
        return v20.Context(hostname=self.v20config.streaming_hostname if streaming else self.v20config.hostname,
                           port=self.v20config.port,
                           token=self.v20config.token)


