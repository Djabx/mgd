#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A simple sample reader for a source...
'''

import collections

DownloadElement = collections.namedtuple('DownloadElement', ('chapter_name', 'page_url', 'img_url'))


class Reader(object):
    def __init__(self):
      pass

    def parse_serie(self, serie_page):
      '''
      Read the serie page and return a list of DownloadElement

      The page is a BeautifulSoup document

      Best practice is to yield DownloadElement
      '''
      return []
