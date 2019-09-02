
import sys
import json

from cement import Controller, ex
from tabulate import tabulate

from tank.core.exc import TankError
from tank.core.run import Run
from tank.core.testcase import TestCase
from tank.core.lambdas import first, second


class BaseClusterController(Controller):
    """Base controller for overriding."""

    def _deploy(self):
        testcase = TestCase(first(self.app.pargs.testcase), self.app)
        run = Run.new_run(self.app, testcase)
        print('Created tank run: {}'.format(run.run_id))

        run.init()
        run.create()
        run.dependency()
        run.provision()

        self._show_hosts(run.inspect())
        print('\nTank run id: {}'.format(run.run_id))

    def _show_hosts(self, run_inspect_data):
        if 'cluster' not in run_inspect_data:
            raise TankError('There are no information about hosts. Have you performed provision/deploy?')

        rows = sorted([[ip, i['hostname']] for ip, i in run_inspect_data['cluster'].items()], key=second)
        print(tabulate(list(rows), headers=['IP', 'HOSTNAME']))

        for ip, info in run_inspect_data['cluster'].items():
            if info['hostname'].endswith('-monitoring'):
                print('\nMonitoring: http://{}/'.format(ip))
                break


class EmbeddedCluster(BaseClusterController):
    """Embedded cluster controller for providing short commands."""

    class Meta:
        label = 'embedded cluster'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(
        help='Create and setup a cluster (init, create, dependency, provision)',
        arguments=[(['testcase'], {'type': str, 'nargs': 1})]
    )
    def run(self):
        """Equal with cluster deploy."""
        self._deploy()


class NestedCluster(BaseClusterController):

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
        testcase = TestCase(first(self.app.pargs.testcase), self.app)
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
            (['run_id'],
             {'type': str, 'nargs': 1}),
            (['load_profile'],
             {'type': str, 'nargs': 1}),
            (['--tps'],
             {'help': 'set global transactions per second generation rate',
              'type': int}),
            (['--total-tx'],
             {'help': 'how many transactions to send',
              'type': int}),
        ])
    def bench(self):
        Run(self.app, first(self.app.pargs.run_id)).bench(
            first(self.app.pargs.load_profile), self.app.pargs.tps, self.app.pargs.total_tx)

    @ex(help='Destroy all instances of the cluster',
        arguments=[(['run_id'], {'type': str, 'nargs': 1})])
    def destroy(self):
        Run(self.app, first(self.app.pargs.run_id)).destroy()

    @ex(help='Low-level info about a run',
        arguments=[(['run_id'], {'type': str, 'nargs': 1})])
    def inspect(self):
        data = Run(self.app, first(self.app.pargs.run_id)).inspect()
        json.dump(data, sys.stdout, indent=4, sort_keys=True)

    @ex(help='Info about a run',
        arguments=[(['info_type'], {'choices': ['hosts'], 'nargs': 1}),
                   (['run_id'], {'type': str, 'nargs': 1})])
    def info(self):
        info_type = first(self.app.pargs.info_type)
        data = Run(self.app, first(self.app.pargs.run_id)).inspect()

        if info_type == 'hosts':
            self._show_hosts(data)

    @ex(
        help='Create and setup a cluster (init, create, dependency, provision)',
        arguments=[(['testcase'], {'type': str, 'nargs': 1})]
    )
    def deploy(self):
        self._deploy()
