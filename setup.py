
from setuptools import setup, find_packages
from tank.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='tank',
    version=VERSION,
    description='Bench toolkit for blockchain',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Andrey Levkin',
    author_email='alevkin@gmail.com',
    url='https://github.com/mixbytes/tank/',
    license='Apache-2.0',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'tank': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        tank = tank.main:main
    """,
)
