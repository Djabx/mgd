#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangareader.net/ reader
'''

from mgd import readers
from mgd import model
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

HOST = r'http://www.mangareader.net/'


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
        yield readers.BookInfo(short_name=a.text.strip(), url=a.attrs['href'])


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


readers.register_reader(HOST, MangaReaderReader())
