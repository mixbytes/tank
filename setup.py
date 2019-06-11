
from setuptools import setup, find_packages
from tank.core.version import get_version

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

requires = [
    'cement==3.0.4',
    'ansible==2.8.0',
    'jinja2',
    'pyyaml',
    'colorlog',
    'tinydb',
    'sh==1.12.13'
 ]

setup_options = dict(
    name='mixbytes-tank',
    version=get_version(),
    description='Benchmark engine for blockchains',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='MixBytes LLC',
    author_email='hello@mixbytes.io',
    url='https://github.com/mixbytes/tank/',
    license='Apache-2.0',
    classifiers=[
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Benchmark",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Clustering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    keywords='bench benchmark blockchain',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={
        'tank':
            ['templates/*',
             'providers/*/*',
             'tools/*/*',
             '*.sh']
    },
    include_package_data=True,
    install_requires=requires,
    python_requires='>=3',
    entry_points="""
        [console_scripts]
        tank = tank.main:main
    """,
)

setup(**setup_options)
