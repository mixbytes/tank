#
#   module tank.core.utils
#
# Misc. utils.
#
import os
import re
import stat
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


def check_file_rights(file):
    """
    Checks whether file has only owner permissions
    """
    # oct -'0o77', bin - '0b000111111', which is the same as ----rwxrwx
    NOT_OWNER_PERMISSION = stat.S_IRWXG + stat.S_IRWXO

    # oct - '0o400', bin - '0b100000000', which is the same as -r--------
    ONLY_OWNER_PERMISSION = stat.S_IRUSR

    file_stat: os.stat_result = os.stat(file)    
    file_mode = stat.S_IMODE(file_stat.st_mode)

    if (file_mode & NOT_OWNER_PERMISSION != 0) or (file_mode & ONLY_OWNER_PERMISSION == 0):
        raise TankConfigError(f'File {file} has wrong permission mask - {oct(file_mode)[2:]}.')
