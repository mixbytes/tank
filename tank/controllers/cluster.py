
from subprocess import check_call

from cement import Controller, ex
import sh


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

    def process_output(self, line):
        print(line, end='', flush=True)

    @ex(help='Download plugins, modules for Terraform', hide=True)
    def init(self):
        cmd = sh.Command(self.app.terraform_run_command)
        p = cmd(
            "init", "-backend-config", "path="+self.app.terraform_state_file,
            self.app.terraform_plan_dir,
            _env=self.app.app_env,
            _out=self.process_output,
            _bg=True)
        p.wait()

    @ex(help='Generate and show an execution plan by Terraform', hide=True)
    def plan(self):
        cmd = sh.Command(self.app.terraform_run_command)
        p = cmd(
            "plan", "-input=false", self.app.terraform_plan_dir,
            _env=self.app.app_env,
            _out=self.process_output,
            _bg=True)
        p.wait()

    @ex(help='Create instances for cluster')
    def create(self):
        cmd = sh.Command(self.app.terraform_run_command)
        p = cmd(
                "apply", "-auto-approve",
                "-parallelism=100",
                self.app.terraform_plan_dir,
                _env=self.app.app_env,
                _out=self.process_output,
                _bg=True
                )
        p.wait()

    @ex(help='Install Ansible roles from Galaxy or SCM')
    def dependency(self):
        self.data = {
            'blockchain_ansible_repo': self.app.config.get(
                self.app.label, 'blockchain_ansible_repo'),
            'blockchain_ansible_repo_version': self.app.config.get(
                self.app.label, 'blockchain_ansible_repo_version')
        }
        self.ansible_req_src = self.app.root_dir+"templates"
        self.ansible_req_dst = self.app.state_dir+"/roles"
        self.app.template.copy(
            self.ansible_req_src,
            self.ansible_req_dst,
            self.data, force=True)
        cmd = sh.Command("ansible-galaxy")
        p = cmd(
                "install", "-f", "-r",
                self.app.root_dir+"/tools/ansible/ansible-requirements.yml",
                _env=self.app.app_env,
                _out=self.process_output,
                _bg=True)
        p.wait()
        p = cmd(
                "install", "-f", "-r",
                self.app.state_dir+"/roles/requirements.yml",
                _env=self.app.app_env,
                _out=self.process_output,
                _bg=True)
        p.wait()

    @ex(help='Setup instances: configs, packages, services, etc')
    def provision(self):
        cmd = sh.Command("ansible-playbook")
        p = cmd(
                "-f", "10", "-u", "root", "-i",
                self.app.terraform_inventory_run_command,
                "-e", "bc_private_interface='"+self.app.config.get(self.app.provider, "private_interface")+"'",
                "--private-key={}".format(self.app.config.get(self.app.label, 'pvt_key')),
                self.app.root_dir+"/tools/ansible/play.yml",
                _cwd=self.app.terraform_plan_dir,
                _env=self.app.app_env,
                _out=self.process_output,
                _bg=True)
        p.wait()

    @ex(help='Runs bench on prepared cluster',
        arguments=[
            (['--tps'],
             {'help': 'set global transactions per second generation rate',
              'type': int}),
            (['--total-tx'],
             {'help': 'how many transactions to send',
              'type': int}),
        ])
    def bench(self):
        bench_command = 'bench --common-config=/tool/bench.config.json ' \
                        '--module-config=/tool/polkadot.bench.config.json'
        if self.app.pargs.tps:
            # FIXME extract blockchain_instances from inventory
            per_node_tps = max(int(self.app.pargs.tps / self.app.blockchain_instances), 1)
            bench_command += ' --common.tps {}'.format(per_node_tps)

        if self.app.pargs.total_tx:
            # FIXME extract blockchain_instances from inventory
            per_node_tx = max(int(self.app.pargs.total_tx / self.app.blockchain_instances), 1)
            bench_command += ' --common.stopOn.processedTransactions {}'.format(per_node_tx)

        check_call(['ansible', '-f', '100', '-B', '3600', '-P', '10', '-u', 'root',
                    '-i', self.app.terraform_inventory_run_command,
                    '--private-key', self.app.config.get(self.app.label, 'pvt_key'),
                    '*producer*',
                    '-a', bench_command],
                   cwd=self.app.terraform_provider_dir,
                   env=self.app.app_env)

    @ex(help='Destroy all instances')
    def destroy(self):
        cmd = sh.Command(self.app.terraform_run_command)
        p = cmd(
                "destroy", "-auto-approve",
                "-parallelism=100",
                self.app.terraform_plan_dir,
                _env=self.app.app_env,
                _out=self.process_output,
                _bg=True)
        p.wait()

    @ex(help='Create and setup cluster (init, create, dependency, provision')
    def deploy(self):
        self.init()
        self.create()
        self.dependency()
        self.provision()

