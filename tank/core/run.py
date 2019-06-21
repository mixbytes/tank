#
#   module tank.core.run
#

import os
import tempfile

import sh
from cement import fs
from time import time

from tank.core.testcase import TestCase


class Run:
    """
    Single run of a tank testcase.
    """

    @classmethod
    def _runs_dir(cls, app) -> str:
        return fs.join(app.user_dir, 'run')

    @classmethod
    def new_run(cls, app, testcase: TestCase):
        # TODO fancy names
        run_id = str(int(time()))

        fs.ensure_dir_exists(cls._runs_dir(app))
        temp_dir = tempfile.mkdtemp(prefix=run_id, dir=cls._runs_dir(app))

        # make a copy to make sure any alterations of the source won't affect us
        testcase.save(fs.join(temp_dir, 'testcase.yml'))

        os.rename(temp_dir, fs.join(cls._runs_dir(app), run_id))

        return cls(app, run_id)


    def __init__(self, app, run_id: str):
        self._app = app
        self.run_id = run_id

        self._testcase = TestCase(fs.join(self._dir, 'testcase.yml'))

    def deploy(self):
        self._init()
        self._create()
        self._dependency()
        self._provision()


    def _make_env(self):
        fs.ensure_dir_exists(self._tf_data_dir)
        fs.ensure_dir_exists(self._log_dir)

        env = self._app.app_env

        env["TF_LOG_PATH"] = fs.join(self._log_dir, 'terraform.log')
        env["TF_DATA_DIR"] = self._tf_data_dir

        env["TF_VAR_state_path"] = fs.join(self._dir, "blockchain.tfstate")
        env["TF_VAR_bc_count_prod_instances"] = str(self.blockchain_instances - 1)

        for common_key in self.config.keys(self.Meta.label):
            env["TF_VAR_" + common_key] = \
                self.config.get(self.Meta.label, common_key)
        for provider_key in self.config.keys(self.provider):
            env["TF_VAR_" + provider_key] = \
                self.config.get(self.provider, provider_key)

        env["ANSIBLE_ROLES_PATH"] = \
            self.state_dir + "/roles"
        env["ANSIBLE_CONFIG"] = \
            self.root_dir + "/tools/ansible/ansible.cfg"

        return env

    def _init(self):
        """
        Download plugins, modules for Terraform.
        """
        sh.Command(self.app.terraform_run_command)(
            "init", "-backend-config", "path="+self.app.terraform_state_file,
            self.app.terraform_plan_dir,
            _env=self.app.app_env,
            _out=self.process_output)

    def _create(self):
        pass

    def _dependency(self):
        pass

    def _provision(self):
        pass


    @property
    def _dir(self) -> str:
        return fs.join(self.__class__._runs_dir(self._app), self.run_id)

    @property
    def _tf_data_dir(self) -> str:
        return fs.join(self._dir, 'tf_data')

    @property
    def _log_dir(self) -> str:
        return fs.join(self._dir, 'log')

