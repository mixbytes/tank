
from setuptools import setup, find_packages
# from tank.core.version import get_version
import tank

VERSION = tank.__version__

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

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
    name='tank',
    version=VERSION,
    description='Bench toolkit for blockchain',
    long_description='Long Description',
    long_description_content_type='text/markdown',
    author='Andrey Levkin',
    author_email='alevkin@gmail.com',
    url='https://github.com/mixbytes/tank/',
    license='Apache-2.0',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache-2.0 License",
        "Operating System :: OS Independent",
        #"Topic :: Software Development :: Build Tools",
        #"Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords='bench blockchain',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'tank': ['templates/*']},
    include_package_data=True,
    install_requires=requires,
    python_requires='>=3',
    entry_points="""
        [console_scripts]
        tank = tank.main:main
    """,
)

setup(**setup_options)
