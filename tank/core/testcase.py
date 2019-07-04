#
#   module tank.core.testcase
#

from typing import Dict

import yaml
import jsonschema

from tank.core.exc import TankTestCaseError
from tank.core.utils import yaml_load, yaml_dump


class TestCase:
    """
    Entity describing single test performed by Tank.
    """
    def __init__(self, filename):
        self.filename = filename

        self._content = yaml_load(filename)
        try:
            jsonschema.validate(self._content, self.__class__._TESTCASE_SCHEMA)
        except jsonschema.ValidationError as e:
            raise TankTestCaseError('Failed to validate testcase {}'.format(filename), e)

        for name, cfg in self._content['instances'].items():
            if name.lower() == 'monitoring':
                raise TankTestCaseError('\'monitoring\' instance name is reserved')
            if isinstance(cfg, int):
                self._content['instances'][name] = {'count': cfg, 'type': 'small'}

    def save(self, filename):
        yaml_dump(filename, self._content)

    @property
    def binding(self) -> str:
        return self._content['binding']

    @property
    def instances(self) -> Dict:
        return dict(self._content['instances'])

    @property
    def total_instances(self) -> int:
        return sum(cfg['count'] for cfg in self.instances.values())


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
