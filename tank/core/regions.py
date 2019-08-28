import copy
import os
from shutil import copy2

from cement.utils import fs

from tank.core import resource_path
from tank.core.utils import yaml_load


class RegionsConfig(object):
    """Config object for regions."""

    FILE_NAME = 'regions.yml'
    REGIONS = ('Europe', 'Asia', 'NorthAmerica',)

    def __init__(self, app):
        """Load or copy config file."""
        self._config_file = fs.join(app.user_dir, self.FILE_NAME)

        if not os.path.exists(self._config_file):
            copy2(resource_path('regions.yml'), self._config_file)

        self._config = yaml_load(self._config_file)

    @property
    def config(self):
        """Return loaded config."""
        return copy.deepcopy(self._config)
