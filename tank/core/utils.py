#
#   module tank.core.utils
#
# Misc. utils.
#
import os
import re
import json
import hashlib
from typing import List

import yaml


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


def ratio_from_percent(percent: int) -> float:
    """Convert percent to ratio."""
    return percent / 100


def split_evenly(number: int, count: int) -> List[int]:
    """Return mostly equal parts.

    Example: number = 11, count = 3, result = [4, 4, 3]
    """
    parts = []

    for _ in range(count):
        if number % count:
            parts.append(number // count + 1)
            number -= parts[-1]
        else:
            parts.append(number // count)
            number -= parts[-1]

        count -= 1

    return parts
