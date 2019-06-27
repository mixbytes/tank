#
#   module tank.core
#

import os.path

from cement.utils import fs


def resource_path(*path_parts: str) -> str:
    """
    Resolves path to a resource.
    """
    if '..' in path_parts:
        raise ValueError('parent directory references are forbidden')

    tank_src = os.path.dirname(os.path.dirname(fs.abspath(__file__)))
    return fs.join(tank_src, 'resources', *path_parts)
