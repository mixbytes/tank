
from cement import Controller, ex
from cement.utils import fs
import sh
import os
import pkg_resources

class Cluster(Controller):
    # tank_provider = self.app.config.get(self.app.label, 'provider')
    # terr_plan_dir = pkg_resources.resource_filename(
    #     self.app.label, 'providers' + "/" + tank_provider)

    # tank_work_dir=os.path.dirname(os.path.realpath(__file__))

    # terr_state_dir = fs.abspath(fs.ensure_dir_exists('./.tank/state'))
    # terr_state_file=terr_state_dir+"/dev-do-00001.tfstate"
    # terr_plan_dir=tank_work_dir+"/lib/providers/digitalocean/"

    class Meta:
        label = 'cluster'
        stacked_type = 'nested'
        stacked_on = 'base'

        # text displayed at the top of --help output
        description = 'Manipulating of cluster'

        # text displayed at the bottom of --help output
        epilog = ''


    @ex(help='init')
    def init(self):
        # tank_provider = self.app.config.get(self.app.label, 'provider')
        ## tank_root_dir = pkg_resources.resource_filename(
        ##     self.app.label, '/')
        # terr_plan_dir = pkg_resources.resource_filename(
        #     self.app.label, 'providers' + "/" + tank_provider)
        # tank_work_dir = fs.abspath('.')
        # tank_state_dir = tank_work_dir + '/.tank/state/'
        # tank_log_dir = tank_work_dir + '/.tank/log/'
        # terr_log_path = tank_log_dir + 'terraform.log'

        # fs.ensure_dir_exists(tank_state_dir)
        # fs.ensure_dir_exists(tank_log_dir)
        # terr_state_file = tank_state_dir+"/dev-do-00001.tfstate"

        # tank_env = os.environ.copy()
        # tank_env["TF_LOG"] = "TRACE"
        # tank_env["TF_LOG_PATH"] = terr_log_path
        # tank_env["TF_VAR_state_path"] = terr_state_file

        print(sh.terraform(
            "init", self.app.Meta.terraform_plan_dir,
            _cwd=self.app.Meta.terraform_plan_dir, _env=self.app.Meta.app_env))

    @ex(help='plan')
    def plan(self):
        pass

    @ex(help='create')
    def create(self):
        pass

    @ex(help='dependency')
    def dependency(self):
        pass

    @ex(help='provision')
    def provision(self):
        pass

    @ex(help='destroy')
    def destroy(self):
        pass
