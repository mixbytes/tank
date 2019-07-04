#
#   module tank.core.cloud_settings
#

from enum import Enum

import yaml
import jsonschema

from tank.core.exc import TankConfigError


class CloudProvider(Enum):
    DIGITAL_OCEAN = 'digitalocean'
    GOOGLE_CLOUD_ENGINE = 'gce'

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        """
        Serializes a member into string.
        """
        return self.value

    @classmethod
    def from_string(cls, str_value):
        """
        Deserializes a member from string.
        :param str_value: serialized form
        :return: enum member or None if not found
        """
        for m in cls:
            if m.value == str_value:
                return m
        else:
            return None


class CloudUserSettings:
    """
    Management and validation of cloud provider user-specific settings.
    """

    def __init__(self, app_config):
        self.provider = CloudProvider.from_string(app_config.get('tank', 'provider'))
        if self.provider is None:
            raise TankConfigError('Cloud provider is not specified or not known')

        self.provider_vars = app_config.get_dict().get(self.provider.value)
        if self.provider_vars is None or not isinstance(self.provider_vars, dict):
            raise TankConfigError('Cloud provider is not configured')

        self.ansible_vars = self.provider_vars.pop('ansible', dict())

        try:
            jsonschema.validate(self.provider_vars, self.__class__._SCHEMAS[self.provider])
        except jsonschema.ValidationError as e:
            raise TankConfigError('Failed to validate config for cloud provider {}'.format(self.provider), e)

        assert 'pvt_key' in self.provider_vars, 'pvt_key is required for ansible'

        try:
            jsonschema.validate(self.ansible_vars, self.__class__._ANSIBLE_SCHEMA)
        except jsonschema.ValidationError as e:
            raise TankConfigError('Failed to validate ansible config for cloud provider {}'.format(self.provider), e)

        if 'private_interface' not in self.ansible_vars:
            self.ansible_vars['private_interface'] = {
                CloudProvider.DIGITAL_OCEAN: 'eth0',
                CloudProvider.GOOGLE_CLOUD_ENGINE: 'enp0s8',
            }[self.provider]


    _SCHEMAS = {
        CloudProvider.DIGITAL_OCEAN: yaml.safe_load(r'''
type: object
additionalProperties: False
required:
    - token
    - pvt_key
    - ssh_fingerprint
properties:
    token:
        type: string
    pvt_key:
        type: string
    ssh_fingerprint:
        type: string
'''),

        CloudProvider.GOOGLE_CLOUD_ENGINE: yaml.safe_load(r'''
type: object
additionalProperties: False
required:
    - pub_key
    - pvt_key
    - cred_path
properties:
    pub_key:
        type: string
    pvt_key:
        type: string
    cred_path:
        type: string
    project:
        type: string
'''),
    }

    _ANSIBLE_SCHEMA = yaml.safe_load(r'''
type: object
additionalProperties: False
properties:
    private_interface:
        type: string
''')

