#! /usr/bin/python
# -*- coding: utf-8 -*-
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

import sys
from setuptools.command.test import test as TestCommand


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
    'requests==2.3.0',
    'BeautifulSoup==3.2.1',
    'sqlalchemy==0.9.4',
    ]


setup(name='mgd',
      version='0.1.0',
      description='Module for downloading manga.',
      long_description=long_description,
      author='Alexandre Badez',
      author_email='alexandre.badez@gmail.com',
      install_requires=install_requires,
      license='Apache',
      url='https://github.com/Djabx/mangareader-downloader',
      package_dir={'' : 'src'},
      packages=[
        'mgd',
        'mgd.readers',
        'mgd.writters'
        ],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      classifiers=['Development Status :: 1 - Alpha',
                   'Programming Language :: Python :: 2.7'])
