#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A simple sample reader for a source...
'''

import collections

ChapterInfo = collections.namedtuple('ChapterInfo', ('name', 'url'))
class ImageInfo(collections.namedtuple('innerImageInfo', ('chapter_info', 'url', 'img_url', 'next_page'))):
    def __new__(cls, chapter_info, url, img_url=None, next_page=None):
      super(cls, ImageInfo).__new__(chapter_info, url, img_url, next_page)


class History(object):
  def __init__(self):
    self.dt={}
    self.dt['info'] = {}
    self.dt['info']['chapters'] = {} # chapter name -> (chapter_url, )
    self.dt['info']['images'] = {} # url -> (chapter name, img url)
    self.dt['info']['url_map'] = {} # page/image url -> next page url
    self.dt['done']['chapters'] = {} # chapter name -> local path
    self.dt['done']['images'] = {} # img url -> local file

  def save(self, dest):
    json.dump(self.dt, dest)

  def load(self, dest):
    self.dt = json.load(dh)

  def add_chapter_info(self, ci):
    self.dt['info']['chapters'][ci.name] = (ci.url, )

  def add_image_info(self, ii):
    self.dt['info']['images'][ii.url] = (ii.chapter_info.name, ii.img_url)
    self.dt['info']['url_map'][ii.url] = ii.next_page


class Reader(object):
    def __init__(self, data):
      self._data = data
      pass

    def parse_serie(self, serie_page):
      '''
      Read the serie page and return a list of ImageInfo

      The page is a BeautifulSoup document

      Best practice is to yield ImageInfo
      '''
      return []
