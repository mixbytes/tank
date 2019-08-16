#
#   module tank.core.testcase
#
from jsonschema import Draft4Validator, ValidationError

from tank.core import resource_path
from tank.core.exc import TankTestCaseError
from tank.core.utils import yaml_load, yaml_dump


class InstancesDict(dict):
    """Canonical config for instances.

    Accept only valid content.
    Transforms dict to following format:

    Role:
      Region1:
        count: ...
        type: ...
      Region2:
        count: ...
        type: ...
    """

    _GENERAL_OPTIONS = {
        'type': 'small',
    }

    def __init__(self, content: dict):
        super().__init__(content)
        self._global_defaults = self._load_defaults()

    def _load_defaults(self) -> dict:
        defaults = dict()

        for option, default in self._GENERAL_OPTIONS:
            defaults[option] = self.get(option, default)
            self.pop(option)

        defaults['region'] = 'default'
        return defaults

    def _canonize(self):
        for role, config in self.items():
            if isinstance(config, int):  # shortest number configuration
                self[role] = {
                    self._global_defaults['region']: {
                        'count': config,
                        'type': self._global_defaults['type'],
                    },
                }
            elif 'regions' in config:  # dict configuration with regions
                ...
            else:  # dict configuration without regions (config must contain count param in this case)
                self[role] = {
                    self._global_defaults['region']: {
                        'count': config['count'],
                        'type': config.get('type', self._global_defaults['type']),
                    },
                }


class TestCaseValidator(object):
    """Class for validation TestCase object."""

    SCHEMA_FILE = resource_path('testcase_schema.yml')

    def __init__(self, content: dict, filename):
        """Save filename with content."""
        self._content = content
        self._filename = filename

    def validate(self):
        """Perform all validations."""
        self._validate_schema()
        self._check_reserved_names()
        self._check_counts_equality()

    def _validate_schema(self):
        """Validate via JSON schema."""
        try:
            Draft4Validator(yaml_load(self.SCHEMA_FILE)).validate(self._content)
        except ValidationError as e:
            raise TankTestCaseError('Failed to validate testcase {}'.format(self._filename), e)

    def _check_reserved_names(self):
        """Check reserved names existence."""
        reserved_names = {'count', 'monitoring'}

        for role in self._content['instances'].keys():
            if role.lower() in reserved_names:
                raise TankTestCaseError('\'{name}\' instance name is reserved'.format(name=role))

    def _check_counts_equality(self):
        """Check if total count is equal with sum of counts in regions."""
        for role, config in self._content['instances'].items():
            if isinstance(config, dict) and all(key in config for key in ['count', 'regions']):
                total_count = config['count']
                regions_count = 0

                for region, region_config in config['regions'].items():
                    if isinstance(region_config, int):
                        regions_count += region_config
                    else:
                        regions_count += region_config['count']

                if total_count != regions_count:
                    raise TankTestCaseError(
                        'The total count does not match sum of count in regions in role {}'.format(role)
                    )


class TestCase(object):
    """Entity describing single test performed by Tank."""

    def __init__(self, filename):
        """Load content."""
        self.filename = filename
        self._content = yaml_load(filename)
        TestCaseValidator(self._content, filename).validate()

    @property
    def binding(self) -> str:
        return self._content['binding']

    @property
    def instances(self) -> dict:
        return dict()

    @property
    def total_instances(self) -> int:
        return 9

    @property
    def ansible(self) -> dict:
        return dict(self._content.get('ansible', dict()))

    @property
    def content(self) -> dict:
        return dict()

    def save(self, filename):
        """Save content to file."""
        yaml_dump(filename, self._content)
