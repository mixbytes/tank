#
#   module tank.core.testcase
#

import yaml
import jsonschema

from tank.core.exc import TankError


class TestCase:
    """
    Entity describing single test performed by Tank.
    """
    def __init__(self, filename):
        self.filename = filename

        with open(filename, 'r') as fh:
            self._content = yaml.safe_load(fh)

        try:
            jsonschema.validate(self._content, self.__class__._TESTCASE_SCHEMA)
        except jsonschema.ValidationError as e:
            raise TankError('Failed to validate testcase {}'.format(filename), e)

    def save(self, filename):
        with open(filename, 'w') as fh:
            yaml.dump(self._content, fh, default_flow_style=False)


    _TESTCASE_SCHEMA = yaml.safe_load(r'''
type: object

additionalProperties: False
required:
    - binding
    - instances

properties:

    binding:
        type: string
    
    instances:
        type: object
        additionalProperties:
            type: integer
            minimum: 0
    ''')
