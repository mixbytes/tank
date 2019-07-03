
from cement import Controller, ex
from tabulate import tabulate

from tank.core.run import Run
from tank.core.testcase import TestCase
from tank.core.lambdas import first


class Cluster(Controller):

    class Meta:
        label = 'cluster'
        stacked_type = 'nested'
        stacked_on = 'base'

        # text displayed at the top of --help output
        description = 'Manipulating a cluster'

        # text displayed at the bottom of --help output
        title = 'Low level cluster management commands'
        help = 'Low level cluster management commands'

    @ex(help='Show clusters')
    def list(self):
        runs = Run.list_runs(self.app)

        def make_row(run):
            return [
                run.run_id,
                run.created_at.strftime('%c'),
                run.testcase_copy.total_instances + 1,
                run.meta['testcase_filename']
            ]

        print(tabulate(list(map(make_row, runs)), headers=['RUN ID', 'CREATED', 'INSTANCES', 'TESTCASE']))

    @ex(help='Init a Tank run, download plugins and modules for Terraform', hide=True,
        arguments=[(['testcase'], {'type': str, 'nargs': 1})])
    def init(self):
        testcase = TestCase(first(self.app.pargs.testcase))
        run = Run.new_run(self.app, testcase)
        print('Created tank run: {}'.format(run.run_id))

        run.init()

    @ex(help='Generate and show an execution plan by Terraform', hide=True,
        arguments=[(['run_id'], {'type': str, 'nargs': 1})])
    def plan(self):
        Run(self.app, first(self.app.pargs.run_id)).plan()

    @ex(help='Create instances for cluster', hide=True,
        arguments=[(['run_id'], {'type': str, 'nargs': 1})])
    def create(self):
        Run(self.app, first(self.app.pargs.run_id)).create()

    @ex(help='Install Ansible roles from Galaxy or SCM', hide=True,
        arguments=[(['run_id'], {'type': str, 'nargs': 1})])
    def dependency(self):
        Run(self.app, first(self.app.pargs.run_id)).dependency()

    @ex(help='Setup instances: configs, packages, services, etc', hide=True,
        arguments=[(['run_id'], {'type': str, 'nargs': 1})])
    def provision(self):
        Run(self.app, first(self.app.pargs.run_id)).provision()

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
        raise NotImplementedError()
        # bench_command = 'bench --common-config=/tool/bench.config.json ' \
        #                 '--module-config=/tool/polkadot.bench.config.json'
        # if self.app.pargs.tps:
        #     # FIXME extract blockchain_instances from inventory
        #     per_node_tps = max(int(self.app.pargs.tps / self.app.blockchain_instances), 1)
        #     bench_command += ' --common.tps {}'.format(per_node_tps)
        #
        # if self.app.pargs.total_tx:
        #     # FIXME extract blockchain_instances from inventory
        #     per_node_tx = max(int(self.app.pargs.total_tx / self.app.blockchain_instances), 1)
        #     bench_command += ' --common.stopOn.processedTransactions {}'.format(per_node_tx)
        #
        # check_call(['ansible', '-f', '100', '-B', '3600', '-P', '10', '-u', 'root',
        #             '-i', self.app.terraform_inventory_run_command,
        #             '--private-key', self.app.config.get(self.app.label, 'pvt_key'),
        #             '*producer*',
        #             '-a', bench_command],
        #            cwd=self.app.terraform_plan_dir,
        #            env=self.app.app_env)

    @ex(help='Destroy all instances of the cluster',
        arguments=[(['run_id'], {'type': str, 'nargs': 1})])
    def destroy(self):
        Run(self.app, first(self.app.pargs.run_id)).destroy()

    @ex(help='Create and setup a cluster (init, create, dependency, provision)',
        arguments=[(['testcase'], {'type': str, 'nargs': 1})])
    def deploy(self):
        testcase = TestCase(first(self.app.pargs.testcase))
        run = Run.new_run(self.app, testcase)
        print('Created tank run: {}'.format(run.run_id))

        run.init()
        run.create()
        run.dependency()
        run.provision()
