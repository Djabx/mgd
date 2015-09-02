#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangareader.net/ reader
'''

from mgdpck import model
from mgdpck import actions
from bs4 import BeautifulSoup
from contextlib import contextmanager
import requests
import logging
HOST = r'http://www.mangareader.net'

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BookInfoGetter(actions.AbsInfoGetter):
  def __init__(self):
    self.url_book_list = r'http://www.mangareader.net/alphabetical'
    self.sp = BeautifulSoup(requests.get(self.url_book_list).text, "html.parser")
    self.info = {}


  def get_count(self):
    for s in self.sp.find_all('ul', class_='series_alpha'):
      for a in s.find_all('a'):
        self.info[a.text.strip()] = HOST + a.attrs['href']
    return len(self.info)


  def get_info(self):
    for name, url in self.info.items():
      yield actions.BookInfo(short_name=name, url=url)



class ChapterInfoGetter(actions.AbsInfoGetter):
  def __init__(self, lsb):
    sp = BeautifulSoup(requests.get(lsb.url).text, "html.parser")
    self.table_manga = sp.find('table', attrs={'id' : 'listing'})

    imgholder = sp.find('div', attrs={'id' : 'mangaimg'})
    if imgholder is not None:
      url_cover = imgholder.find('img').attrs['src']
      lsb.url_cover = url_cover


  def get_count(self):
    count = 0
    for tr in self.table_manga.find_all('tr'):
      tds = tr.find_all('td')
      if len(tds) == 0:
        continue
      td = tds[0]
      for a in td.find_all('a'):
        count += 1
    return count


  def get_info(self):
    for tr in self.table_manga.find_all('tr'):
      tds = tr.find_all('td')
      if len(tds) == 0:
        continue
      td = tds[0]
      for a in td.find_all('a'):
        chapter_num = int(a.text.split()[-1])
        chapter_url = HOST + a.get('href')
      chapter_name = ':'.join(td.text.split(':')[1:])
      yield actions.ChapterInfo(chapter_name, chapter_url, chapter_num)



class PageInfoGetter(actions.AbsInfoGetter):
  def __init__(self, chapter, next_chapter):
    self.url = chapter.url
    self.urls = None
    self.rs = None


  def get_count(self):
    self.rs = requests.Session()
    url = self.url
    sp = BeautifulSoup(self.rs.get(url).text, "html.parser")

    self.urls = [HOST + v['value'] for v in sp.find_all(id="pageMenu")[0].find_all('option')]
    return len(self.urls)


  def get_info(self):
    for num, url in enumerate(self.urls):
      sp = BeautifulSoup(self.rs.get(url).text, "html.parser")
      imgholder = sp.find('div', attrs={'id' : 'imgholder'})
      url_image = imgholder.find('img', attrs={'id' : 'img'}).attrs['src']

      yield actions.PageInfo(url, url_image, num)



class MangaReaderReader(actions.AbsReader):
  def __init__(self):
    self.name = 'Manga reader'


  def get_book_info_getter(self):
    return BookInfoGetter()


  def get_chapter_info_getter(self, lsb):
    return ChapterInfoGetter(lsb)


  def get_page_info_getter(self, chapter, next_chapter):
    return PageInfoGetter(chapter, next_chapter)



actions.register_reader(HOST, MangaReaderReader())
