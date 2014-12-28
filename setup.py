#! /usr/bin/python
# -*- coding: utf-8 -*-
#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup

import sys
from setuptools.command.test import test as TestCommand
import versioneer


versioneer.VCS = 'git'
versioneer.versionfile_source = 'src/mgd/_version.py'
versioneer.versionfile_build = 'mgd/_version.py'
versioneer.tag_prefix = '' # tags are like 1.2.0
versioneer.parentdir_prefix = 'mgd-' # dirname like 'myproject-1.2.0'



class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


with open("README.md") as f:
    long_description = f.read()

install_requires = [
    'requests',
    'beautifulsoup4',
    'sqlalchemy',
    ]

cmdclass_arg = versioneer.get_cmdclass()
cmdclass_arg.update({'test': PyTest})

setup(name='mgd',
      description='Module for downloading manga.',
      long_description=long_description,
      author='Alexandre Badez',
      author_email='alexandre.badez@gmail.com',
      install_requires=install_requires,
      license='Apache',
      url='https://github.com/Djabx/mangareader-downloader',
      package_dir={'' : 'src'},
      version=versioneer.get_version(),
      packages=[
        'mgd',
        'mgd.readers',
        'mgd.writters'
        ],
      tests_require=['pytest'],
      cmdclass=cmdclass_arg,
      classifiers=['Development Status :: 1 - Alpha',
                   'Programming Language :: Python :: 3.4'])
