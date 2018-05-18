
# Library imports
import json
import jsonschema


class V20Config(object):

    # Json validation schema
    _V20_CFG = {'type': 'object',
                'required': ['hostname', 'streaming_hostname', 'port', 'ssl', 'token', 'username', 'accounts',
                             'active_account'],
                'properties': {'hostname': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                               'streaming_hostname': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                               'port': {'type': 'number', 'multipleOf': 1.0, "min": 1, "max": 65535},
                               'ssl': {'enum': [True, False]},
                               'token': {'type': 'string', 'minLength': 1, 'maxLength': 100},
                               'accounts': {'type': 'array',
                                            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255}},
                               'active_account': {'type': 'string', 'minLength': 1, 'maxLength': 100}}}

    def __init__(self, filepath):
        """ Simple config value container """
        # Open the config file
        with open(filepath, "r") as fp:

            # Parse the file as json, into a dict
            self._data = json.load(fp)

            # Validate the json dict against the schema
            jsonschema.validate(self._data, self._V20_CFG)

    @property
    def hostname(self):
        return self._data["hostname"]

    @property
    def streaming_hostname(self):
        return self._data["streaming_hostname"]

    @property
    def port(self):
        return self._data["port"]

    @property
    def ssl(self):
        return self._data["ssl"]

    @property
    def token(self):
        return self._data["token"]

    @property
    def accounts(self):
        return self._data["accounts"]

    @property
    def active_account(self):
        return self._data["active_account"]

    @property
    def datetime_format(self):
        return "UNIX"