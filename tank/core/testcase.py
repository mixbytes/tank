#
#   module tank.core.testcase
#
import copy
from typing import List

from jsonschema import Draft4Validator, ValidationError

from tank.core import resource_path
from tank.core.exc import TankTestCaseError
from tank.core.regions import RegionsConfig
from tank.core.utils import yaml_load, yaml_dump, ratio_from_percent, split_evenly


class InstancesCanonizer(object):
    """Canonize config for instances.

    Accept only valid instances content.
    Transforms dict to following format:

    Role:
      Region1:
        count: ...
        type: ...
        packetloss: ...
      Region2:
        count: ...
        type: ...
        packetloss: ...
    """

    _GENERAL_OPTIONS = {
        'type': 'small',
        'packetloss': 0,
    }

    def __init__(self, instances_content: dict):
        """Load content and defaults."""
        self._content = instances_content
        self._global_defaults = self._load_defaults()

    def _load_defaults(self) -> dict:
        """Provide defaults for config.

        Now they are default region and type.
        """
        defaults = dict()

        for option, default in self._GENERAL_OPTIONS.items():
            defaults[option] = self._content.get(option, default)
            if option in self._content.keys():
                self._content.pop(option)

        defaults['region'] = 'default'
        return defaults

    def _build_configuration(self, count: int, type: str = None, packetloss: int = None) -> dict:
        """Build minimal configuration from parameters."""
        configuration = {
            'count': count,
            'type': self._global_defaults['type'] if type is None else type,
            'packetloss': ratio_from_percent(self._global_defaults['packetloss'] if packetloss is None else packetloss),
        }

        return configuration

    def canonize(self) -> dict:
        """Convert to canonized config."""
        canonized_dict = dict()

        for role, config in self._content.items():
            if isinstance(config, int):  # shortest number configuration
                canonized_dict[role] = {
                    self._global_defaults['region']: self._build_configuration(count=config),
                }
            elif 'regions' in config:  # dict configuration with regions
                canonized_dict[role] = dict()

                for region, region_config in config['regions'].items():
                    if isinstance(region_config, int):
                        canonized_dict[role][region] = self._build_configuration(
                            count=region_config,
                            type=config.get('type'),
                            packetloss=config.get('packetloss'),
                        )
                    else:
                        canonized_dict[role][region] = self._build_configuration(
                            count=region_config['count'],
                            type=region_config.get('type', config.get('type')),
                            packetloss=region_config.get('packetloss', config.get('packetloss')),
                        )
            else:  # dict configuration without regions (config must contain count param in this case)
                canonized_dict[role] = {
                    self._global_defaults['region']: self._build_configuration(
                        count=config['count'],
                        type=config.get('type'),
                        packetloss=config.get('packetloss'),
                    )
                }

        return canonized_dict


class RegionsConverter(object):
    """Convert and merge regions in canonized instances configuration.

    Convert regions to machine-readable format.
    random = equal amount for all regions.

    Example below:
        Role:
            default:
                count: 1
                type: small
                packetloss: 0
        ...

    Convert to:
        Role:
            - {
                region: FRA1
                count: 1
                type: small
                packetloss: 0
            }
            - ...
            - ...
        ...
    """

    _GROUP_PARAMETERS = ('region', 'type', 'packetloss',)

    def __init__(self, app):
        """Save provider, load RegionsConfig."""
        self._provider = app.provider
        self._regions_config = RegionsConfig(app).config
        self._available_regions = RegionsConfig.REGIONS

    def _merge_configurations(self, machine_configurations: List[dict]) -> List[dict]:
        """Merge machine configurations with equal parameters."""
        configurations_dict = dict()

        for configuration in machine_configurations:
            key = tuple(configuration[param] for param in self._GROUP_PARAMETERS)

            if key in configurations_dict:
                configurations_dict[key]['count'] += configuration['count']
            else:
                configurations_dict[key] = configuration

        return list(configurations_dict.values())

    def _convert_region(self, human_readable: str) -> str:
        """Convert region from human readable type to machine readable via regions config."""
        return self._regions_config[self._provider][human_readable]

    def convert(self, instances_config: dict) -> dict:
        """Convert configuration to machine readable."""
        converted_config = dict()

        for role, config in instances_config.items():
            machines_configurations = []

            for region, region_config in config.items():
                if region == 'random':
                    for i, count in enumerate(split_evenly(region_config['count'], len(self._available_regions))):
                        if count:
                            machines_configurations.append(
                                {
                                    'region': self._convert_region(self._available_regions[i]),
                                    'count': count,
                                    'packetloss': region_config['packetloss'],
                                    'type': region_config['type'],
                                }
                            )
                else:
                    machines_configurations.append(
                        {
                            'region': self._convert_region(region),
                            **region_config
                        },
                    )

            converted_config[role] = self._merge_configurations(machines_configurations)

        return converted_config


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
        self._filename = filename
        self._original_content = yaml_load(filename)

        self._content = copy.deepcopy(self._original_content)
        TestCaseValidator(self._content, filename).validate()
        self._content = self._prepare_content()

    @property
    def filename(self) -> str:
        return self._filename

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
        """Calculate amount of all instances.

        It works only after instances config canonization and converting.
        """
        instances_amount = 0
        for config in self._content['instances'].values():
            for item in config:
                instances_amount += item['count']

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
        """Save original content to file."""
        yaml_dump(filename, self._original_content)

    def _prepare_content(self):
        """Convert to canonized config."""
        result = dict()
        canonized_instances = InstancesCanonizer(self._content['instances']).canonize()
        result['instances'] = RegionsConverter(self._app).convert(canonized_instances)
        result['binding'] = self._content['binding']
        result['ansible'] = self._content.get('ansible', dict())
        return result
