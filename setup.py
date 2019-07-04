
from setuptools import setup, find_packages
from tank.core.version import get_version

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

with open('requirements.txt', 'r') as f:
    requires = list(filter(None, map(str.strip, f.read().split('\n'))))

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
    include_package_data=True,
    install_requires=requires,
    python_requires='>=3',
    entry_points="""
        [console_scripts]
        tank = tank.main:main
    """,
)

setup(**setup_options)
