import os
import sys
import zipfile
from urllib.request import urlopen


class BaseInstaller(object):  # TODO add logging
    """Base installer.

    1. Download ZIP archive.
    2. Unzip it.
    3. Remove ZIP file.
    4. Move directory to another /usr/local/bin/ as default.
    """

    version: str
    url: str
    archive_name: str
    file_name: str  # name of file in archive

    def __init__(self, storage_path: str):
        """Build archive full path."""
        self._storage_path = storage_path
        self._archive_full_path = os.path.join(storage_path, self.archive_name)
        self._file_full_path = os.path.join(storage_path, self.file_name)

    def _download_archive(self):
        """Download archive from provided url."""
        response = urlopen(self.url)

        with open(self._archive_full_path, 'wb') as archive_file:
            chunk_size = 1024 * 1024  # 1 MB
            chunk = response.read(chunk_size)

            while chunk:
                archive_file.write(chunk)
                chunk = response.read(chunk_size)

        print('Archive {name} has been successfully downloaded.'.format(name=self.archive_name))

    def _unpack_archive(self):
        """Unpack archive with provided name."""
        with zipfile.ZipFile(self._archive_full_path, 'r') as zip_ref:
            zip_ref.extractall(self._storage_path)

        print('Archive has been unpacked.')

    def _remove_archive(self):
        """Remove archive after unpacking."""
        os.remove(self._archive_full_path)
        print('Archive has been removed.')

    def _add_variables(self):
        """Add variables to $PATH and app.app_env."""
        path_variable = os.environ['PATH']
        if path_variable:
            os.environ['PATH'] = os.pathsep.join([path_variable, self._storage_path])
        else:
            os.environ['PATH'] = self._storage_path

        print('Variables have been added to $PATH and app.app_env.')

    def install(self):
        """Installation logic is here."""
        if not os.path.exists(self._file_full_path):
            self._download_archive()
            self._unpack_archive()
            self._remove_archive()
        else:
            print('{name} already exists.'.format(name=self.file_name))

        self._add_variables()  # TODO check exist


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
    TerraformInstaller('/home/alexei/.tank').install()
    # TerraformInventoryInstaller().install()
