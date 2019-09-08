import logging
import os
import stat
import sys
import zipfile
from urllib.request import urlopen

import sh


_logger = logging.getLogger(__name__)


class BaseInstaller(object):
    """Base installer.

    1. Download ZIP archive.
    2. Unzip it.
    3. Remove ZIP file.
    4. Move file to storage_path directory.
    5. Make file executable
    6. Add variable to $PATH
    """

    version: str
    url: str
    archive_name: str
    file_name: str  # name of file in archive

    def __init__(self, storage_path: str):
        """Build archive full path."""
        self._storage_path = storage_path
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        self._archive_full_path = os.path.join(storage_path, self.archive_name)
        self._file_full_path = os.path.join(storage_path, self.file_name)

    def _is_installed(self) -> bool:
        """Returns True if tool is installed else False."""
        try:
            sh.Command(self._file_full_path)
            return True
        except sh.CommandNotFound:
            return False

    def _download_archive(self):
        """Download archive from provided url."""
        _logger.debug('Downloading archive...')
        response = urlopen(self.url)

        with open(self._archive_full_path, 'wb') as archive_file:
            chunk_size = 1024 * 1024  # 1 MB
            chunk = response.read(chunk_size)

            while chunk:
                archive_file.write(chunk)
                chunk = response.read(chunk_size)

        _logger.debug('Archive {name} has been successfully downloaded.'.format(name=self.archive_name))

    def _unpack_archive(self):
        """Unpack archive with provided name."""
        with zipfile.ZipFile(self._archive_full_path, 'r') as zip_ref:
            zip_ref.extractall(self._storage_path)

        _logger.debug('Archive has been unpacked.')

    def _remove_archive(self):
        """Remove archive after unpacking."""
        os.remove(self._archive_full_path)
        _logger.debug('Archive has been removed.')

    def _make_executable(self):
        """Makes file executable."""
        file_stat = os.stat(self._file_full_path)
        os.chmod(self._file_full_path, file_stat.st_mode | stat.S_IEXEC)

    def _add_variables(self):
        """Add variables to $PATH."""
        path_variable = os.environ.get('PATH', '')
        paths = path_variable.split(os.pathsep)

        if self._storage_path not in paths:
            if path_variable:
                os.environ['PATH'] = os.pathsep.join([self._storage_path, path_variable])
            else:
                os.environ['PATH'] = self._storage_path

        _logger.debug('Variable has been added to $PATH.')

    def install(self):
        """Installation logic is here."""
        if not self._is_installed():
            _logger.debug('Installing {name}...'.format(name=self.file_name))
            self._download_archive()
            self._unpack_archive()
            self._remove_archive()
            self._make_executable()
        else:
            _logger.debug('{name} is already installed.'.format(name=self.file_name))

        self._add_variables()


class TerraformInstaller(BaseInstaller):
    """Terraform installer."""

    version = '0.11.13'
    file_name = 'terraform'
    archive_name = 'terraform_{v}_{platform}_amd64.zip'.format(v=version, platform=sys.platform.lower())
    url = 'https://releases.hashicorp.com/terraform/{v}/{filename}'.format(v=version, filename=archive_name)


class TerraformInventoryInstaller(BaseInstaller):
    """Terraform inventory installer."""

    version = 'v0.8'
    file_name = 'terraform-inventory'
    archive_name = 'terraform-inventory_{v}_{platform}_amd64.zip'.format(v=version, platform=sys.platform.lower())
    url = (
        'https://github.com/adammck/terraform-inventory/releases/download/{v}/{filename}'
    ).format(v=version, filename=archive_name)


if __name__ == '__main__':
    default_directory = os.path.join(os.path.expanduser('~'), '.tank', 'bin')
    TerraformInstaller(default_directory).install()
    TerraformInventoryInstaller(default_directory).install()
