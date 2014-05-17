# -*- coding: utf-8 -*-
from distutils.core import setup


with open("README.md") as f:
    long_description = f.read()

install_requires = [
    'requests',
    'sqlalchemy',
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
        ],
      classifiers=['Development Status :: 1 - Alpha',
                   'Programming Language :: Python :: 2.7'])
