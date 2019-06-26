#
#   module tank.core.testcase
#

from typing import Dict

import yaml
import jsonschema

from tank.core.exc import TankTestCaseError


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
            raise TankTestCaseError('Failed to validate testcase {}'.format(filename), e)

    def save(self, filename):
        with open(filename, 'w') as fh:
            yaml.dump(self._content, fh, default_flow_style=False)

    @property
    def binding(self) -> str:
        return self._content['binding']

    @property
    def instances(self) -> Dict:
        return dict(self._content['instances'])


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
        propertyNames:
            pattern: "^[A-Za-z_]+$"

        additionalProperties:
        
            oneOf:
                - {type: integer, minimum: 0}
                  
                - type: object
                  additionalProperties: False
                  required:
                      - count
                  properties:
                      count: {type: integer, minimum: 0}
                      type: {enum: ["micro", "small", "standard", "large", "xlarge", "xxlarge", "huge"]}
    ''')
