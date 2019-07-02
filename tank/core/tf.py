#
#   module tank.core.tf
#
# Terraform-related code.
#

from os.path import dirname, isdir

from cement.utils import fs

from tank.core import resource_path
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
        if self.testcase.total_instances <= 10:
            monitoring_machine_type = 'small'
        elif self.testcase.total_instances < 50:
            monitoring_machine_type = 'standard'
        else:
            monitoring_machine_type = 'large'

        self._app.template.copy(self._provider_templates, plan_dir, {
            'instances': self.testcase.instances,
            'monitoring_machine_type': monitoring_machine_type,
        })


    @property
    def _provider_templates(self) -> str:
        return resource_path('providers', self._app.cloud_settings.provider.value)
