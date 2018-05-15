
# Library imports
from trader import schema
import json
import v20


class Trader(object):

    def __init__(self, cfg_filepath="v20.json"):

        # Load json config file
        self._load_cfg(cfg_filepath)

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
        return self._cfg["active_account"]

    def get_pricing(self, instrument_list, since=None):
        resp = self._api.pricing.get(self.active_account, instruments=",".join(instrument_list))
        return {price.instrument: price for price in resp.get("prices", 200)}

    def get_pricing_stream(self, instrument):
        return self._streaming_api.pricing.stream(self.active_account, instruments=instrument).parts()

    def test_stream(self, instrument):
        return self._streaming_api.pricing.stream(self.active_account, instruments=instrument).parts()


    def _populate_instrument_list(self):
        self._instruments = self._api.account.instruments(self.active_account).get("instruments", 200)

    def _load_cfg(self, cfg_filepath):
        with open(cfg_filepath) as fp:
            data = json.load(fp)
            schema.validate_json(data, schema.V20_CFG)
            self._cfg = data

    def _get_api_context(self, streaming=False):
        return v20.Context(hostname=self._cfg["streaming_hostname"] if streaming else self._cfg["hostname"],
                           port=self._cfg["port"],
                           token=self._cfg["token"])


