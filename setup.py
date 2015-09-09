#! /usr/bin/python
# -*- coding: utf-8 -*-
#from ez_setup import use_setuptools
#use_setuptools()

import sys
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand
import versioneer

LONG='''
MGD stand for ManGa Downloader.

It's command line tool for downloading manga from various site.

Actually foes nothing really serious.


More information on: https://github.com/Djabx/mgd

'''


versioneer.VCS = 'git'
versioneer.versionfile_source = 'mgdpck/_version.py'
versioneer.versionfile_build = 'mgdpck/_version.py'
versioneer.tag_prefix = 'v' # tags are like v1.2.0
versioneer.parentdir_prefix = 'mgd' # dirname like 'mgd-v1.2.0'



class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


cmdclass_arg = versioneer.get_cmdclass()
cmdclass_arg.update({'test': PyTest})

setup(name='mgd',
      description='Module for downloading manga.',
      long_description=LONG,
      author='Alexandre Badez',
      author_email='alexandre.badez@gmail.com',
      install_requires=[
          'requests',
          'beautifulsoup4',
          'sqlalchemy',
          'clint',
          ],
      license='Apache',
      url='https://github.com/Djabx/mgd',
      version=versioneer.get_version(),
      scripts = [
        os.path.join('cmd', 'mgd.py')
        ],
      packages=[
        'mgdpck',
        'mgdpck.readers',
        'mgdpck.writters'
        ],
      tests_require=['pytest'],
      cmdclass=cmdclass_arg,
      classifiers=['Development Status :: 1 - Alpha',
                   'Programming Language :: Python :: 3.4'])
