#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A simple sample reader for a source...
'''

import collections
from urllib.parse import urlparse
import logging

logger = logging.getlogger(__name__)

ChapterInfo = collections.namedtuple('ChapterInfo', ('name', 'url'))
class ImageInfo(collections.namedtuple('innerImageInfo', ('chapter_info', 'url', 'img_url', 'next_page'))):
    def __new__(cls, chapter_info, url, img_url=None, next_page=None):
      super(cls, ImageInfo).__new__(chapter_info, url, img_url, next_page)


REG_READER = {}

def register_reader(site_name, reader):
  logger.debug('Register reader for site: "%s"', site_name)
  REG_READER[site_name] = reader


def get_reader_from_url(url):
  logger.debug('Searching reader for url: "%s"', url)
  urlparse(url).hostname
  reader = REG_READER.get(url)
  logger.debug('Found reader: %s hostname: "%s" ', reader is not None, url)
  return reader
