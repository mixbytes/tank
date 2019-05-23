
import os
from tinydb import TinyDB
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from .core.exc import MixbytesTankError
from .controllers.base import Base
from .controllers.cluster import Cluster
from cement.utils import fs
import pkg_resources

# configuration defaults
CONFIG = init_defaults('tank',
                       'digitalocean',
                       'log.logging')
CONFIG['tank']['state_file'] = '~/.tank/tank.json'
CONFIG['tank']['provider'] = 'digitalocean'
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
        config_dirs = '~/.tank'

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [
            Base,
            Cluster,
        ]

        # register hooks
        hooks = [
            ('post_setup', extend_tinydb),
        ]

    def setup(self):
        super(MixbytesTank, self).setup()
        self.work_dir = fs.abspath('.')
        self.state_dir = self.work_dir + '/.tank/state/'
        self.log_dir = self.work_dir + '/.tank/log/'
        self.provider = self.config.get(self.Meta.label, "provider")
        self.root_dir = pkg_resources.resource_filename(
             self.Meta.label, '/')
        self.terraform_plan_dir = pkg_resources.resource_filename(
             self.Meta.label, 'providers' + "/" + self.provider)
        self.terraform_log_path = self.log_dir + 'terraform.log'

        fs.ensure_dir_exists(self.state_dir)
        fs.ensure_dir_exists(self.log_dir)
        self.terraform_state_file = self.state_dir+"/dev-do-00001.tfstate"
        self.app_env = os.environ.copy()
        self.app_env["TF_LOG"] = "TRACE"
        self.app_env["TF_LOG_PATH"] = self.terraform_log_path
        self.app_env["TF_DATA_DIR"] = self.state_dir
        self.app_env["TF_IN_AUTOMATION"] = "true"
        self.app_env["TF_VAR_state_path"] = self.terraform_state_file
        for common_key in self.config.keys(self.Meta.label):
            self.app_env["TF_VAR_"+common_key] = self.config.get(self.Meta.label, common_key)
        for provider_key in self.config.keys(self.provider):
            self.app_env["TF_VAR_"+provider_key] = self.config.get(self.provider, provider_key)

        # print(self.app_env)
        # print(self.app_env["TF_VAR_setup_id"])
        # print(self.app_env["TF_VAR_state_path"])

class MixbytesTankTest(TestApp, MixbytesTank):
    """A sub-class of MixbytesTank that is better suited for testing."""

    class Meta:
        label = 'tank'


def main():
    with MixbytesTank() as app:
        try:
            # print(app.hook.list())
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

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


if __name__ == '__main__':
    main()
