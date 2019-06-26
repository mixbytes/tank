#
#   module tank.core.tf
#
# Terraform-related code.
#

from os.path import dirname, isdir

from cement.utils import fs

from tank.core.exc import TankError, TankTestCaseError
from tank.core.testcase import TestCase


class PlanGenerator:
    """
    Generates a Terraform plan for the run based on the testcase and the user settings.
    """

    def __init__(self, app, testcase: TestCase):
        self._app = app
        self.testcase = testcase

        if not isdir(self._provider_templates):
            raise TankError('Failed to find Terraform templates for cloud provider {} at {}'.format(
                self._app.cloud_settings.provider.value, self._provider_templates
            ))

    def generate(self, plan_dir: str):
        instances = self.testcase.instances
        for name, cfg in instances.items():
            if name.lower() == 'monitoring':
                raise TankTestCaseError('\'monitoring\' instance name is reserved')
            if isinstance(cfg, int):
                instances[name] = {'count': cfg, 'type': 'small'}

        total_machines = sum(cfg['count'] for cfg in instances.values())
        if total_machines <= 10:
            monitoring_machine_type = 'small'
        elif total_machines < 50:
            monitoring_machine_type = 'standard'
        else:
            monitoring_machine_type = 'large'

        self._app.template.copy(self._provider_templates, plan_dir, {
            'instances': instances,
            'monitoring_machine_type': monitoring_machine_type,
        })


    @property
    def _provider_templates(self) -> str:
        return fs.abspath(fs.join(dirname(__file__), '..', 'providers', self._app.cloud_settings.provider.value))
