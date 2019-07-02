#
#   module tank.core.utils
#
# Misc. utils.
#

import os
import re

import yaml


def yaml_load(filename: str):
    with open(filename) as fh:
        return yaml.safe_load(fh)


def yaml_dump(filename: str, data):
    with open(filename, 'w') as fh:
        return yaml.dump(data, fh, default_flow_style=False)


def grep_dir(dirname: str, filter_regex: str = None, isdir: bool = False):
    """
    Enumerate and filter contents of a directory.
    """
    contents = os.listdir(dirname)

    if filter_regex is not None:
        filter_re = re.compile(filter_regex)
        contents = filter(lambda name: filter_re.match(name) is not None, contents)

    if isdir is not None:
        contents = filter(lambda name: os.path.isdir(os.path.join(dirname, name)), contents)

    return contents
