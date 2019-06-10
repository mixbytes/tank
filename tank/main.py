import os
from os.path import join
import sh
from tinydb import TinyDB
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from .core.exc import MixbytesTankError, TerraformNotAvailable
from .controllers.base import Base
from .controllers.cluster import Cluster
from cement.utils import fs

# configuration defaults
CONFIG = init_defaults('tank',
                       'digitalocean',
                       'log.logging')
CONFIG['tank']['state_file'] = '~/.tank/tank.json'
CONFIG['tank']['provider'] = 'digitalocean'
CONFIG['tank']['terraform_run_command'] = 'terraform'
CONFIG['tank']['terraform_inventory_run_command'] = '/usr/local/bin/terraform-inventory'
CONFIG['tank']['blockchain_instances'] = 2
CONFIG['digitalocean']['private_interface'] = 'eth0'
CONFIG['log.logging']['level'] = 'info'


def extend_tinydb(app):
    state_file = app.config.get('tank', 'state_file')
    state_file = fs.abspath(state_file)
    state_dir = os.path.dirname(state_file)
    if not os.path.exists(state_dir):
        os.makedirs(state_dir)

    app.extend('state', TinyDB(state_file))


class MixbytesTank(App):
    """MixBytes Tank primary application."""

    class Meta:
        label = 'tank'

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        close_on_exit = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        # List of configuration directory
        config_dirs = ['~/.tank']

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        template_handler = 'jinja2'

        # register handlers
        handlers = [
            Base,
            Cluster
        ]

        # register hooks
        hooks = [
            ('post_setup', extend_tinydb),
        ]

    def _check_terraform_availability(self):
        try:
            sh.Command(self.terraform_run_command, "--version")
        except Exception:
            raise TerraformNotAvailable('Terraform not found. Running command \'{}\''.format(self.terraform_run_command))

        try:
            sh.Command(self.terraform_inventory_run_command, "-version")
        except Exception:
            raise TerraformNotAvailable('Terraform Inventory not found. Running command \'{}\''.format(self.terraform_inventory_run_command))
        return

    def _check_terraform_inventory_availability(self):
        try:
            sh.Command(self.terraform_run_command, "--version")
        except Exception:
            raise TerraformInventoryNotAvailable
        return

    def setup(self):
        super(MixbytesTank, self).setup()
        self.work_dir = fs.abspath('.')
        self.state_dir = self.work_dir + '/.tank/state/'
        self.log_dir = self.work_dir + '/.tank/log/'
        self.root_dir = os.path.realpath(os.path.dirname(__file__))+"/"

        self.provider = self.config.get(self.Meta.label, "provider")
        self.terraform_provider_dir = join(self.root_dir, 'providers', self.provider)
        self.terraform_plan_dir = self.terraform_provider_dir
        self.terraform_log_path = self.log_dir + 'terraform.log'
        self.terraform_run_command = self.config.get(self.Meta.label, 'terraform_run_command')
        self.terraform_inventory_run_command = self.config.get(self.Meta.label, 'terraform_inventory_run_command')

        fs.ensure_dir_exists(self.state_dir)
        fs.ensure_dir_exists(self.log_dir)

        self.terraform_state_file = self.state_dir + "/blockchain.tfstate"
        self.app_env = os.environ.copy()
        self.app_env["TF_LOG"] = "TRACE"
        self.app_env["TF_LOG_PATH"] = self.terraform_log_path
        self.app_env["TF_DATA_DIR"] = self.state_dir
        self.app_env["TF_IN_AUTOMATION"] = "true"
        self.app_env["TF_VAR_state_path"] = self.terraform_state_file
        self.app_env["TF_VAR_bc_count_prod_instances"] = str(self.blockchain_instances - 1)
        for common_key in self.config.keys(self.Meta.label):
            self.app_env["TF_VAR_" + common_key] = \
                self.config.get(self.Meta.label, common_key)
        for provider_key in self.config.keys(self.provider):
            self.app_env["TF_VAR_" + provider_key] = \
                self.config.get(self.provider, provider_key)
        self.app_env["ANSIBLE_ROLES_PATH"] = \
            self.state_dir + "/roles"
        self.app_env["ANSIBLE_CONFIG"] = \
            self.root_dir + "/tools/ansible/ansible.cfg"

    @property
    def blockchain_instances(self):
        return int(self.config.get(self.Meta.label, 'blockchain_instances'))


class MixbytesTankTest(TestApp, MixbytesTank):
    """A sub-class of MixbytesTank that is better suited for testing."""

    class Meta:
        label = 'tank'


def main():
    with MixbytesTank() as app:
        try:
            # app.config.parse_file('~/.tank/config/tank.yml')
            # print(app.config.get_dict())
            app._check_terraform_availability()
            app._check_terraform_inventory_availability()
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except TerraformNotAvailable as e:
            print(e)
            app.exit_code = 1

        except MixbytesTankError as e:
            print('MixbytesTankError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0

        except sh.CommandNotFound as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('You should install terraform')
            app.exit_code = 0


if __name__ == '__main__':
    main()
