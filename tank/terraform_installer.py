import zipfile
from pathlib import Path


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
    moving_folder_name: str  # name of directory to move to storage_path
    storage_path: str = '/usr/local/bin'  # TODO pathlib

    def _download_archive(self):
        """Download archive from provided url."""

    def _unpack_archive(self):
        """Unpack archive with provided name."""

    def _remove_archive(self):
        """Remove archive after unpacking."""

    def _move_directory(self):
        """Move unpacked files to storage path."""

    def install(self):
        """Installation logic is here."""

        # TODO check if already installed
        self._download_archive()
        self._unpack_archive()
        self._remove_archive()
        self._move_directory()


class TerraformInstaller(BaseInstaller):
    """Terraform installer."""

    version = '0.11.13'
    url = 'https://releases.hashicorp.com/terraform/{v}/terraform_{v}_linux_amd64.zip'.format(v=version)
    archive_name = 'terraform_{v}_linux_amd64.zip'.format(v=version)
    moving_folder_name = 'terraform'


class TerraformInventoryInstaller(BaseInstaller):
    """Terraform inventory installer."""

    version = 'v0.8'
    url = (
        'https://github.com/adammck/terraform-inventory/releases/download/{v}/terraform-inventory_{v}_linux_amd64.zip'
    ).format(v=version)

    archive_name = 'terraform-inventory_{v}_linux_amd64.zip'.format(v=version)
    moving_folder_name = 'terraform-inventory'


def unzip(path: Path):
    with zipfile.ZipFile('test.zip', 'r') as zip_ref:
        zip_ref.extractall('.')


if __name__ == '__main__':
    TerraformInstaller().install()
    TerraformInventoryInstaller().install()
