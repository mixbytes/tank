#
#   module tank.core.utils
#
# Misc. utils.
#

import yaml


def yaml_load(filename: str):
    with open(filename) as fh:
        return yaml.safe_load(fh)


def yaml_dump(filename: str, data):
    with open(filename, 'w') as fh:
        return yaml.dump(data, fh, default_flow_style=False)
