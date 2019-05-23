
from cement import Controller, ex
# from cement.utils import fs
import sh
from io import StringIO
# import os
# import pkg_resources


class Cluster(Controller):

    class Meta:
        label = 'cluster'
        stacked_type = 'nested'
        stacked_on = 'base'

        # text displayed at the top of --help output
        description = 'Manipulating of cluster'

        # text displayed at the bottom of --help output
        title = 'Low level cluster management commands'
        help = 'Low level cluster management commands'

    def process_output(line, stdin, process):
        print(line)

    def approve_destroy(self, line, stdin):
        line = line.strip()
        print(line)
        if line.endswith("Enter a value:"):
            stdin.put("correcthorsebatterystaple")

    @ex(help='Download plugins, modules for Terraform', hide=True)
    def init(self):
        sh.terraform(
            "init",
            self.app.terraform_plan_dir,
            _cwd=self.app.terraform_plan_dir,
            _env=self.app.app_env,
            _out=self.app.terraform_log_path
        )
        print("OK")

    @ex(help='Generate and show an execution plan by Terraform', hide=True)
    def plan(self):
        sh.terraform(
            "plan", "-input=false", self.app.terraform_plan_dir,
            _cwd=self.app.terraform_plan_dir,
            _env=self.app.app_env,
            _out=self.app.terraform_log_path
        )

    @ex(help='Create instances for cluster')
    def create(self):
        sh.terraform(
            "apply", "-auto-approve",
            "-parallelism=100",
            self.app.terraform_plan_dir,
            _cwd=self.app.terraform_plan_dir,
            _env=self.app.app_env,
            _out=self.app.terraform_log_path
        )

    @ex(help='Install Ansible roles from Galaxy or SCM')
    def dependency(self):
        pass

    @ex(help='Setup instances: configs, packages, services, etc')
    def provision(self):
        pass

    @ex(help='Destroy all instances')
    def destroy(self):
        sh.terraform(
            "destroy", "-auto-approve",
            "-parallelism=100",
            self.app.terraform_plan_dir,
            _cwd=self.app.terraform_plan_dir,
            _env=self.app.app_env,
            _out=self.app.terraform_log_path
        )
