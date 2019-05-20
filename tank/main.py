
import os, sh
from tinydb import TinyDB
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from .core.exc import MixbytesTankError
from .controllers.base import Base
from .controllers.cluster import Cluster
from cement.utils import fs
import pkg_resources

# configuration defaults
CONFIG = init_defaults('tank', 'log.logging')
CONFIG['tank']['state_file'] = '~/.tank/tank.json'
CONFIG['tank']['provider'] = 'gce'
CONFIG['log.logging']['level'] = 'info'
CONFIG['provider'] = 'gce'


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

        app_work_dir = fs.abspath('.')
        provider = "digitalocean"

        terraform_plan_dir = pkg_resources.resource_filename(
            label, 'providers' + "/"
                       + provider)
        app_state_dir = app_work_dir + "/"+label+"./state/"
        app_log_dir = app_work_dir + "/."+label+"/log/"
        terraform_log_path = app_log_dir + 'terraform.log'

        fs.ensure_dir_exists(app_state_dir)
        fs.ensure_dir_exists(app_log_dir)
        terraform_state_file = app_state_dir+"/dev-do-00001.tfstate"
        app_env = os.environ.copy()
        app_env["TF_LOG"] = "TRACE"
        app_env["TF_LOG_PATH"] = terraform_log_path
        app_env["TF_VAR_state_path"] = terraform_state_file

class MixbytesTankTest(TestApp, MixbytesTank):
    """A sub-class of MixbytesTank that is better suited for testing."""

    class Meta:
        label = 'tank'


def main():
    with MixbytesTank() as app:
        try:
            # tank_root_dir = pkg_resources.resource_filename(
            #     self.app.label, '/')
            # terr_plan_dir = pkg_resources.resource_filename(
            #    app.label, 'providers' + "/"
            #    + app.config(app.label, 'provider'))
            # tank_work_dir = fs.abspath('.')

            print(app.plugins.list)
            #app.run()

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
