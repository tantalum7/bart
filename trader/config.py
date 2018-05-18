
# Library imports


# Project imports
from trader import schema

class Config(object):

    def __init__(self):
        pass


    def _load_cfg(self, cfg_filepath):
        with open(cfg_filepath) as fp:
            data = json.load(fp)
            schema.validate_json(data, schema.V20_CFG)
            self._cfg = data