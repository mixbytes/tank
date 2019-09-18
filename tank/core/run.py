#
#   module tank.core.run
#
import os
import sys
import stat
import tempfile
from shutil import rmtree
from shutil import copytree
from time import time
from typing import Dict
from uuid import uuid4
import json
from datetime import datetime

import sh
from cement import fs
from filelock import FileLock
import namesgenerator

from tank.core import resource_path
from tank.core.binding import AnsibleBinding
from tank.core.exc import TankError, TankConfigError
from tank.core.testcase import TestCase
from tank.core.tf import PlanGenerator
from tank.core.utils import yaml_load, yaml_dump, grep_dir, json_load, sha256
from tank.terraform_installer import TerraformInstaller, TerraformInventoryInstaller


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

        copytree(resource_path('scripts'), temp_dir+'/scripts')

        # TODO prevent collisions
        os.rename(temp_dir, fs.join(cls._runs_dir(app), run_id))

        return cls(app, run_id)

    @classmethod
    def list_runs(cls, app):
        fs.ensure_dir_exists(cls._runs_dir(app))
        return [cls(app, run_id) for run_id in grep_dir(cls._runs_dir(app), '^[a-zA-Z0-9][a-zA-Z_0-9]*$', isdir=True)]


    def __init__(self, app, run_id: str):
        self._app = app
        self.run_id = run_id

        # install terraform and terraform-inventory
        TerraformInstaller(storage_path=app.installation_dir).install()
        TerraformInventoryInstaller(storage_path=app.installation_dir).install()

        self._testcase = TestCase(fs.join(self._dir, 'testcase.yml'), app)
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
        self._check_private_key_permissions()

        with self._lock:
            sh.Command(self._app.terraform_run_command)(
                "apply", "-auto-approve", "-parallelism=51", self._tf_plan_dir,
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
        self._check_private_key_permissions()

        extra_vars = {
            # including blockchain-specific part of the playbook
            'blockchain_ansible_playbook':
                fs.join(self._roles_path, AnsibleBinding.BLOCKCHAIN_ROLE_NAME, 'tank', 'playbook.yml'),
            # saving a report of the important cluster facts
            '_cluster_ansible_report': self._cluster_report_file,
            # grafana monitoring login/password
            'monitoring_user_login': self._app.cloud_settings.monitoring_vars['admin_user'],
            'monitoring_user_password': self._app.cloud_settings.monitoring_vars['admin_password'],
        }

        with self._lock:
            sh.Command("ansible-playbook")(
                "-f", self._app.ansible_config['forks'],
                "-u", "root",
                "-i", self._app.terraform_inventory_run_command,
                "--extra-vars", self._ansible_extra_vars(extra_vars),
                "--private-key={}".format(self._app.cloud_settings.provider_vars['pvt_key']),
                resource_path('ansible', 'core.yml'),
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr, _cwd=self._tf_plan_dir)

    def inspect(self):
        with self._lock:
            result = {
                'meta': self.meta,
                'testcase': self._testcase.content,
            }

            if os.path.exists(self._cluster_report_file):
                result['cluster'] = self._cluster_report()

        return result

    def bench(self, load_profile: str, tps: int, total_tx: int):
        self._check_private_key_permissions()

        bench_command = 'bench --common-config=/tool/bench.config.json ' \
                        '--module-config=/tool/blockchain.bench.config.json'
        if tps is not None:
            # It's assumed, that every node is capable of running the bench.
            per_node_tps = max(int(tps / self._testcase.total_instances), 1)
            bench_command += ' --common.tps {}'.format(per_node_tps)

        if total_tx is not None:
            # It's assumed, that every node is capable of running the bench.
            per_node_tx = max(int(total_tx / self._testcase.total_instances), 1)
            bench_command += ' --common.stopOn.processedTransactions {}'.format(per_node_tx)

        # FIXME extract hostnames from inventory, but ignore monitoring
        ips = [ip for ip, i in self._cluster_report().items() if i['bench_present']]
        if not ips:
            raise TankError('There are no nodes capable of running the bench util')
        host_patterns = ','.join(ips)

        with self._lock:
            # send the load_profile to the cluster
            extra_vars = {'load_profile_local_file': fs.abspath(load_profile)}

            sh.Command("ansible-playbook")(
                "-f", self._app.ansible_config['forks'],
                "-u", "root",
                "-i", self._app.terraform_inventory_run_command,
                "--extra-vars", self._ansible_extra_vars(extra_vars),
                "--private-key={}".format(self._app.cloud_settings.provider_vars['pvt_key']),
                "-t", "send_load_profile",
                fs.join(self._roles_path, AnsibleBinding.BLOCKCHAIN_ROLE_NAME, 'tank', 'send_load_profile.yml'),
                _env=self._make_env(), _out=sys.stdout, _err=sys.stderr, _cwd=self._tf_plan_dir)

            # run the bench
            sh.Command("ansible")(
                '-f', '150', '-B', '3600', '-P', '10', '-u', 'root',
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
            'setup_id': sha256(uuid4().bytes)[:12],
        })

    def _ansible_extra_vars(self, extra: Dict = None) -> str:
        a_vars = dict(('bc_{}'.format(k), str(v)) for k, v in self._app.cloud_settings.ansible_vars.items())
        a_vars.update(dict(('bc_{}'.format(k), str(v)) for k, v in self._testcase.ansible.items()))

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
        env["TF_VAR_blockchain_name"] = self._testcase.binding.replace('_', '-')[:10]
        env["TF_VAR_setup_id"] = self._meta['setup_id']
        env["TF_VAR_scripts_path"] = fs.join(self._dir, 'scripts')

        for k, v in self._app.cloud_settings.provider_vars.items():
            env["TF_VAR_{}".format(k)] = v

        env["ANSIBLE_ROLES_PATH"] = self._roles_path
        env["ANSIBLE_CONFIG"] = resource_path('ansible', 'ansible.cfg')
        env["ANSIBLE_LOG_PATH"] = fs.join(self._log_dir, 'ansible.log')

        return env

    def _generate_tf_plan(self):
        """
        Generation of Terraform manifests specific for this run and user preferences.
        """
        PlanGenerator(self._app, self._testcase).generate(self._tf_plan_dir)

    def _cluster_report(self):
        return json_load(self._cluster_report_file)

    def _check_private_key_permissions(self):
        """
        Checks whether groups and others have 0 access to private key
        """
        # oct -'0o77', bin - '0b000111111', which is the same as ----rwxrwx
        NOT_OWNER_PERMISSION = stat.S_IRWXG + stat.S_IRWXO

        file_stat: os.stat_result = os.stat(self._app.cloud_settings.provider_vars['pvt_key'])
        file_mode = stat.S_IMODE(file_stat.st_mode)

        if file_mode & NOT_OWNER_PERMISSION != 0:
            raise TankConfigError('Private key has wrong permission mask.')

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

    @property
    def _cluster_report_file(self) -> str:
        return fs.join(self._dir, 'cluster_ansible_report.json')
