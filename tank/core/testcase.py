#
#   module tank.core.testcase
#
import copy

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
        # 'packetloss': 0,
    }

    def __init__(self, content: dict):
        """Load content and defaults."""
        super().__init__(content)
        self._global_defaults = self._load_defaults()

    def _load_defaults(self) -> dict:
        """Provide defaults for config.

        Now they are default region and type.
        """
        defaults = dict()

        for option, default in self._GENERAL_OPTIONS.items():
            defaults[option] = self.get(option, default)
            if option in self.keys():
                self.pop(option)

        defaults['region'] = 'default'
        return defaults

    def canonize(self) -> dict:
        """Convert to canonized config."""
        canonized_dict = dict()

        for role, config in self.items():
            if isinstance(config, int):  # shortest number configuration
                canonized_dict[role] = {
                    self._global_defaults['region']: {
                        'count': config,
                        'type': self._global_defaults['type'],
                    },
                }
            elif 'regions' in config:  # dict configuration with regions
                default_type = config.get('type', self._global_defaults['type'])

                canonized_dict[role] = dict()
                for region, region_config in config['regions'].items():
                    if isinstance(region_config, int):
                        region_count = region_config
                        region_type = default_type
                    else:
                        region_count = region_config['count']
                        region_type = region_config.get('type', default_type)

                    canonized_dict[role][region] = {
                        'count': region_count,
                        'type': region_type,
                    }
            else:  # dict configuration without regions (config must contain count param in this case)
                canonized_dict[role] = {
                    self._global_defaults['region']: {
                        'count': config['count'],
                        'type': config.get('type', self._global_defaults['type']),
                    },
                }

        return canonized_dict


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

    def __init__(self, filename, app):
        """Load content."""
        self._app = app

        self.filename = filename
        self._content = yaml_load(filename)
        TestCaseValidator(self._content, filename).validate()
        self._content = self._prepare_content()

    @property
    def binding(self) -> str:
        """Return provided binding."""
        return self._content['binding']

    @property
    def instances(self) -> dict:
        """Return copy of instances."""
        return copy.deepcopy(self._content['instances'])

    @property
    def total_instances(self) -> int:
        """Calculate amount of all instances. It works only after instances config canonization."""
        instances_amount = 0
        for config in self._content['instances'].values():
            for region, region_config in config.items():
                instances_amount += region_config['count']

        return instances_amount

    @property
    def ansible(self) -> dict:
        """Return copy of ansible config."""
        return copy.deepcopy(self._content['ansible'])

    @property
    def content(self) -> dict:
        """Return copy of all content."""
        return copy.deepcopy(self._content)

    def save(self, filename):
        """Save content to file."""
        yaml_dump(filename, self._content)

    def _prepare_content(self):
        """Convert to canonized config."""
        result = dict()
        result['binding'] = self._content['binding']
        result['ansible'] = self._content.get('ansible', dict())
        result['instances'] = InstancesDict(self._content['instances']).canonize()
        return result
