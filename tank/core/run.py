#
#   module tank.core.run
#
import os
import sys
import tempfile
from shutil import rmtree
from time import time
from typing import Dict
from uuid import uuid4
import json
from datetime import datetime
from subprocess import DEVNULL

import sh
from cement import fs
from filelock import FileLock
import namesgenerator

from tank.core import resource_path
from tank.core.binding import AnsibleBinding
from tank.core.testcase import TestCase
from tank.core.tf import PlanGenerator
from tank.core.utils import yaml_load, yaml_dump, grep_dir


class Run:
    """
    Single run of a tank testcase.

    TODO detect and handle CloudUserSettings change.
    """

    @classmethod
    def new_run(cls, app, testcase: TestCase):
        run_id = namesgenerator.get_random_name()

        fs.ensure_dir_exists(cls._runs_dir(app))

        temp_dir = tempfile.mkdtemp(prefix='_{}'.format(run_id), dir=cls._runs_dir(app))
        cls._save_meta(temp_dir, testcase)

        # make a copy to make sure any alterations of the source won't affect us
        testcase.save(fs.join(temp_dir, 'testcase.yml'))

        # TODO prevent collisions
        os.rename(temp_dir, fs.join(cls._runs_dir(app), run_id))

        return cls(app, run_id)

    @classmethod
    def list_runs(cls, app):
        return [cls(app, run_id) for run_id in grep_dir(cls._runs_dir(app), '^[a-zA-Z0-9][a-zA-Z_0-9]*$', isdir=True)]


    def __init__(self, app, run_id: str):
        self._app = app
        self.run_id = run_id

        self._testcase = TestCase(fs.join(self._dir, 'testcase.yml'))
        self._meta = yaml_load(fs.join(self._dir, 'meta.yml'))

    def init(self):
        """
        Download plugins and modules for Terraform.
        """
        with self._lock:
            self._generate_tf_plan()

            sh.Command(self._app.terraform_run_command)(
                "init", "-backend-config", "path={}".format(self._tf_state_file), self._tf_plan_dir,
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr)

    def plan(self):
        """
        Generate and show an execution plan by Terraform.
        """
        with self._lock:
            sh.Command(self._app.terraform_run_command)(
                "plan", "-input=false", self._tf_plan_dir,
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr)

    def create(self):
        """
        Create instances for the cluster.
        """
        with self._lock:
            sh.Command(self._app.terraform_run_command)(
                "apply", "-auto-approve", "-parallelism=100", self._tf_plan_dir,
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr)

    def dependency(self):
        """
        Install Ansible roles from Galaxy or SCM.
        """
        with self._lock:
            ansible_deps = yaml_load(resource_path('ansible', 'ansible-requirements.yml'))

            ansible_deps.extend(AnsibleBinding(self._app, self._testcase.binding).get_dependencies())

            requirements_file = fs.join(self._dir, 'ansible-requirements.yml')
            yaml_dump(requirements_file, ansible_deps)

            sh.Command("ansible-galaxy")(
                "install", "-f", "-r", requirements_file,
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr)

    def provision(self):
        # including blockchain-specific part of the playbook
        extra_vars = {
            'blockchain_ansible_playbook':
                fs.join(self._roles_path, AnsibleBinding.BLOCKCHAIN_ROLE_NAME, 'tank', 'playbook.yml')
        }

        with self._lock:
            sh.Command("ansible-playbook")(
                "-f", "10", "-u", "root",
                "-i", self._app.terraform_inventory_run_command,
                "--extra-vars", self._ansible_extra_vars(extra_vars),
                "--private-key={}".format(self._app.cloud_settings.provider_vars['pvt_key']),
                resource_path('ansible', 'core.yml'),
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr, _cwd=self._tf_plan_dir)

    def bench(self, load_profile: str, tps: int, total_tx: int):
        bench_command = 'bench --common-config=/tool/bench.config.json ' \
                        '--module-config=/tool/polkadot.bench.config.json'
        if tps is not None:
            # It's assumed, that every node is capable of running the bench.
            per_node_tps = max(int(tps / self._testcase.total_instances), 1)
            bench_command += ' --common.tps {}'.format(per_node_tps)

        if total_tx is not None:
            # It's assumed, that every node is capable of running the bench.
            per_node_tx = max(int(total_tx / self._testcase.total_instances), 1)
            bench_command += ' --common.stopOn.processedTransactions {}'.format(per_node_tx)

        # FIXME extract hostnames from inventory, but ignore monitoring
        host_patterns = ','.join('*{}*'.format(name) for name in self._testcase.instances)

        with self._lock:
            # send the load_profile to the cluster
            extra_vars = {'load_profile_local_file': fs.abspath(load_profile)}

            sh.Command("ansible-playbook")(
                "-f", "10", "-u", "root",
                "-i", self._app.terraform_inventory_run_command,
                "--extra-vars", self._ansible_extra_vars(extra_vars),
                "--private-key={}".format(self._app.cloud_settings.provider_vars['pvt_key']),
                "-t", "send_load_profile",
                fs.join(self._roles_path, AnsibleBinding.BLOCKCHAIN_ROLE_NAME, 'tank', 'send_load_profile.yml'),
                _env=self._make_env(), _out=DEVNULL, _err=sys.stderr, _cwd=self._tf_plan_dir)

            # run the bench
            sh.Command("ansible")(
                '-f', '100', '-B', '3600', '-P', '10', '-u', 'root',
                '-i', self._app.terraform_inventory_run_command,
                '--private-key={}'.format(self._app.cloud_settings.provider_vars['pvt_key']),
                host_patterns,
                '-a', bench_command,
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr, _cwd=self._tf_plan_dir)

    def destroy(self):
        with self._lock:
            sh.Command(self._app.terraform_run_command)(
                "destroy", "-auto-approve", "-parallelism=100",
                self._tf_plan_dir,
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr)

            # atomic move before cleanup
            temp_dir = fs.join(self.__class__._runs_dir(self._app), '_{}'.format(self.run_id))
            os.rename(self._dir, temp_dir)

        # cleanup with the lock released
        rmtree(temp_dir)


    @property
    def meta(self) -> Dict:
        return dict(self._meta)

    @property
    def created_at(self) -> datetime:
        return datetime.fromtimestamp(self.meta['created'])

    @property
    def testcase_copy(self) -> TestCase:
        """
        Copy of the original testcase.
        """
        return self._testcase


    @classmethod
    def _runs_dir(cls, app) -> str:
        return fs.join(app.user_dir, 'run')

    @classmethod
    def _save_meta(cls, run_dir: str, testcase: TestCase):
        yaml_dump(fs.join(run_dir, 'meta.yml'), {
            'testcase_filename': fs.abspath(testcase.filename),
            'created': int(time()),
            'setup_id': uuid4().hex,
        })

    def _ansible_extra_vars(self, extra: Dict = None) -> str:
        a_vars = dict(('bc_{}'.format(k), v) for k, v in self._app.cloud_settings.ansible_vars.items())

        if extra is not None:
            a_vars.update(extra)

        return json.dumps(a_vars, sort_keys=True)


    def _make_env(self) -> Dict:
        fs.ensure_dir_exists(self._tf_data_dir)
        fs.ensure_dir_exists(self._log_dir)

        env = self._app.app_env

        env["TF_LOG_PATH"] = fs.join(self._log_dir, 'terraform.log')
        env["TF_DATA_DIR"] = self._tf_data_dir
        env["TF_VAR_state_path"] = self._tf_state_file
        env["TF_VAR_blockchain_name"] = self._testcase.binding.replace('_', '-')
        env["TF_VAR_setup_id"] = self._meta['setup_id']

        for k, v in self._app.cloud_settings.provider_vars.items():
            env["TF_VAR_{}".format(k)] = v

        env["ANSIBLE_ROLES_PATH"] = self._roles_path
        env["ANSIBLE_CONFIG"] = resource_path('ansible', 'ansible.cfg')

        return env

    def _generate_tf_plan(self):
        """
        Generation of Terraform manifests specific for this run and user preferences.
        """
        PlanGenerator(self._app, self._testcase).generate(self._tf_plan_dir)


    @property
    def _dir(self) -> str:
        return fs.join(self.__class__._runs_dir(self._app), self.run_id)

    @property
    def _lock(self) -> FileLock:
        return FileLock(fs.join(self._dir, '.lock'))

    @property
    def _tf_data_dir(self) -> str:
        return fs.join(self._dir, 'tf_data')

    @property
    def _tf_plan_dir(self) -> str:
        return fs.join(self._dir, 'tf_plan')

    @property
    def _tf_state_file(self) -> str:
        return fs.join(self._dir, "blockchain.tfstate")

    @property
    def _log_dir(self) -> str:
        return fs.join(self._dir, 'log')

    @property
    def _roles_path(self) -> str:
        return fs.join(self._dir, "ansible_roles")

