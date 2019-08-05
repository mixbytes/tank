#
#   module tank.core.utils
#
# Misc. utils.
#
import os
import re
import json
import hashlib

import yaml

from tank.core.exc import TankConfigError


def yaml_load(filename: str):
    with open(filename) as fh:
        return yaml.safe_load(fh)


def yaml_dump(filename: str, data):
    with open(filename, 'w') as fh:
        return yaml.dump(data, fh, default_flow_style=False)


def json_load(filename: str):
    with open(filename) as fh:
        return json.load(fh)


def sha256(bin_data) -> str:
    return hashlib.sha256(bin_data).hexdigest()


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


def check_file_rights(file: str, mode: str):
    file_stat: os.stat_result = os.stat(file)

    # oct(file_stat.st_mode) returns '0o100XXX' <- last three numbers under X show file's permission mask
    file_mode = oct(file_stat.st_mode)[-3:]

    if file_mode != mode:
        raise TankConfigError(f'File {file} has wrong permission mask - {file_mode}. Should be {mode}.')
