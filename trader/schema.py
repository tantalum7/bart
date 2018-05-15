
# Library imports
import jsonschema
from jsonschema import ValidationError

V20_CFG =   {'type': 'object',
             'required': ['hostname', 'streaming_hostname', 'port', 'ssl', 'token', 'username', 'accounts', 'active_account'],
             'properties': {'hostname': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                            'streaming_hostname': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                            'port': {'type': 'number', 'multipleOf': 1.0, "min": 1, "max": 65535},
                            'ssl': {'enum': [True, False]},
                            'token': {'type': 'string', 'minLength': 1, 'maxLength': 100},
                            'accounts': {'type': 'array', 'items': {'type': 'string', 'minLength': 1, 'maxLength': 255}},
                            'active_account': {'type': 'string', 'minLength': 1, 'maxLength': 100}}}


def validate_json(json_dict: dict, json_schema: dict):
    jsonschema.validate(json_dict, json_schema)
    return json_dict


"""
hostname: api-fxpractice.oanda.com
streaming_hostname: stream-fxpractice.oanda.com
port: 443
ssl: true
token: 73b28af25ac5df74dcd533efb1d5b879-97cb320d0c6077e3daf2dd8cefe8ea3b
username: tantalum7
accounts:
- 101-004-8415962-002
active_account: 101-004-8415962-002
"""