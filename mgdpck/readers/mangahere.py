#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangahere.co/ reader
'''

from mgdpck import model
from mgdpck import actions
from bs4 import BeautifulSoup
from contextlib import contextmanager
import requests
import logging
import re

HOST = r'http://www.mangahere.co'
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

REX_NAME_NUM = re.compile(r'''
  ^\s*                             # the begining if the string
  (?P<name>.*?)                    # the name of the manga
  (?P<num>\d+?)                    # the num of the manga
  (\.(?P<revision>\d+?))?          # the revesion of the manga
  \s*$                             # the end of the string
''', re.VERBOSE)


ses = requests.Session()


class BookInfoGetter(actions.AbsInfoGetter):
  def __init__(self):
    self.url_book_list = r'http://www.mangahere.co/mangalist/'
    self.sp = BeautifulSoup(ses.get(self.url_book_list).text, "html.parser")
    self.info = {}


  def get_count(self):
    for s in self.sp.find_all('div', class_='list_manga'):
      for a in s.find_all('a', class_="manga_info"):
        names = a.attrs['rel']
        if type(names) == type([]):
          name = ' '.join(names)
        else:
          names = name
        self.info[name] = a.attrs['href']
    return len(self.info)


  def get_info(self):
    for name, url in self.info.items():
      yield actions.BookInfo(short_name=name, url=url)



class ChapterInfoGetter(actions.AbsInfoGetter):
  def __init__(self, lsb):
    sp = BeautifulSoup(ses.get(lsb.url).text, "html.parser")
    self.spans = sp.find('div', class_="detail_list").find_all('span', class_='left')

    top = sp.find('div', class_='manga_detail_top')
    if top is not None:
      imgholder = top.find('img')
      url_cover = imgholder.attrs['src']
      lsb.url_cover = url_cover

  def get_count(self):
    return len(self.spans)

  def get_info(self):
    for sp in self.spans:
      a = sp.find('a')
      sp_name = sp.find('span')
      match = REX_NAME_NUM.match(a.text)
      if match is not None:
        chapter_name = match.group('name')
        chapter_num = match.group('num')
      chapter_url = a.get('href')
      yield actions.ChapterInfo(chapter_name, chapter_url, chapter_num)



class PageInfoGetter(actions.AbsInfoGetter):
  def __init__(self, chapter, next_chapter):
    self.url = chapter.url
    self.urls = None


  def get_count(self):
    url = self.url
    sp = BeautifulSoup(ses.get(url).text, "html.parser")

    self.urls = [v['value'] for v in
          sp.find("select", class_="wid60").find_all('option')]
    return len(self.urls)


  def get_info(self):
    for num, url in enumerate(self.urls):
      sp = BeautifulSoup(ses.get(url).text, "html.parser")
      url_image = sp.find('img', attrs={'id' : 'image'}).attrs['src']

      yield actions.PageInfo(url, url_image, num)



class MangaHereReader(actions.AbsReader):
  def __init__(self):
    self.name = 'Manga Here'


  def get_book_info_getter(self):
    return BookInfoGetter()


  def get_chapter_info_getter(self, lsb):
    return ChapterInfoGetter(lsb)


  def get_page_info_getter(self, chapter, next_chapter):
    return PageInfoGetter(chapter, next_chapter)



actions.register_reader(HOST, MangaHereReader())
