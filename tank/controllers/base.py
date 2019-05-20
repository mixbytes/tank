
from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version
import os

VERSION_BANNER = """
Bench toolkit for blockchain %s
%s
""" % (get_version(), get_version_banner())



class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Bench toolkit for blockchain'

        # text displayed at the bottom of --help output
        epilog = 'Usage: tank command --foo bar'

        # controller level arguments. ex: 'tank --version'
        arguments = [
            # add a version banner
            (['-v', '--version'],
             {'action': 'version',
                'version': VERSION_BANNER}),
        ]

    def _default(self):
        """Default action if no sub-command is passed."""
        self.app.args.print_help()
