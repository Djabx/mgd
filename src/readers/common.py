#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A simple sample reader for a source...
'''

import collections

ChapterInfo = collections.namedtuple('ChapterInfo', ('chapter_name', 'page_url'))
ImageInfo = collections.namedtuple('ImageInfo', ('chapter_info', 'page_url', 'img_url'))


class Reader(object):
    def __init__(self):
      pass

    def parse_serie(self, serie_page):
      '''
      Read the serie page and return a list of ImageInfo

      The page is a BeautifulSoup document

      Best practice is to yield ImageInfo
      '''
      return []
