#
#   module tank.core.binding
#
# Binding of the Tank core to a particular blockchain.
#

import os.path
import copy
from shutil import copy2

from cement.utils import fs

from tank.core import resource_path
from tank.core.exc import TankConfigError
from tank.core.utils import yaml_load


class AnsibleBinding:
    """
    Ansible part of the binding.
    """
    BLOCKCHAIN_ROLE_NAME = 'tank.blockchain'

    def __init__(self, app, binding_name: str):
        """
        Ctor.
        :param binding_name: codename of the binding to use
        :param app: Tank app
        """
        self.binding_name = binding_name
        self._app = app

    def get_dependencies(self):
        """
        Provides ansible dependencies in the form of requirements.yml records.
        :returns: dependency record list
        """
        bindings_conf = _BindingsConfig(self._app)
        conf = bindings_conf.config.get(self.binding_name)
        if conf is None:
            raise TankConfigError('Configuration for binding named {} is not found under {}'.format(
                self.binding_name, bindings_conf.config_file
            ))

        result = {
            'src': conf['ansible']['src'],
            'name': self.__class__.BLOCKCHAIN_ROLE_NAME,
        }
        if 'version' in conf['ansible']:
            result['version'] = conf['ansible']['version']

        return [result]


class _BindingsConfig:

    def __init__(self, app):
        self._app = app

        self.config_file = fs.join(app.user_dir, 'bindings.yml')
        # TODO atomically
        if not os.path.exists(self.config_file):
            # setting up the default config
            copy2(resource_path('bindings.yml'), self.config_file)

        # TODO validate
        self._config = yaml_load(self.config_file)

    @property
    def config(self):
        return copy.deepcopy(self._config)
