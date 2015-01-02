#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangareader.net/ reader
'''

from mgdpck import info
from mgdpck import model
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import logging
HOST = r'http://www.mangareader.net'

logger = logging.getLogger(__name__)


class MangaReaderReader:

  def __init__(self):
    self.name = 'Manga reader'
    self.url_book_list = r'http://www.mangareader.net/alphabetical'


  def get_book_info_list(self):
    '''
    Search and return a list (can yield) of books (added to the session)

    @return: a list (or yeild) of Manga object (added to the session)
    '''
    sp = BeautifulSoup(requests.get(self.url_book_list).text)
    for s in sp.find_all('ul', class_='series_alpha'):
      for a in s.find_all('a'):
        yield info.BookInfo(short_name=a.text.strip(), url=HOST + a.attrs['href'])


  def get_book_chapter_info(self, book_link):
    url = book_link.url
    sp = BeautifulSoup(requests.get(url).text)
    table_manga = sp.find('table', attrs={'id' : 'listing'})
    url_set = set()
    chapters_url = []
    chapters = []
    for tr in table_manga.find_all('tr'):
      tds = tr.find_all('td')
      if len(tds) == 0:
        continue
      td = tds[0]
      for a in td.find_all('a'):
        chapter_num = int(a.text.split()[-1])
        chapter_url = HOST + a.get('href')
      chapter_name = ':'.join(td.text.split(':')[1:])
      yield info.ChapterInfo(chapter_name, chapter_url, chapter_num)


  def get_chapter_content_info(self, chapter):
    pass


  def parse_chapters(self, serie_page):
    table_manga = self.main_soup.find('table', attrs={'id' : 'listing'})
    url_set = set()
    chapters_url = []
    chapters = []
    for a in table_manga.find_all('a'):
      chapter_name = a.string
      chapter_url = self.main_site + a.get('href')

      ci = common.ChapterInfo(chapter_name, chapter_url)
      yield ci


  def parser_page(self):
    current_url = ci.page_url
    while True:
      next_url = self.history.get_next_page(current_url)
      if next_url is None:
        pass
    pass


info.register_reader(HOST, MangaReaderReader())
