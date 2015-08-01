#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangareader.net/ reader
'''

from mgdpck import info
from mgdpck import model
from bs4 import BeautifulSoup
import requests
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
    sp = BeautifulSoup(requests.get(self.url_book_list).text, "html.parser")
    for s in sp.find_all('ul', class_='series_alpha'):
      for a in s.find_all('a'):
        yield info.BookInfo(short_name=a.text.strip(), url=HOST + a.attrs['href'])


  def get_book_chapter_info(self, lsb):
    url = lsb.url
    sp = BeautifulSoup(requests.get(url).text, "html.parser")
    table_manga = sp.find('table', attrs={'id' : 'listing'})
    url_set = set()
    chapters_url = []
    chapters = []

    imgholder = sp.find('div', attrs={'id' : 'mangaimg'})
    if imgholder is not None:
      url_cover = imgholder.find('img').attrs['src']
      lsb.url_cover = url_cover

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


  def get_chapter_content_info(self, chapter, next_chapter):
    rs = requests.Session()
    chapter_finished = False
    url = chapter.url
    next_chapter_url = next_chapter.url if next_chapter is not None else None
    while not chapter_finished:
      sp = BeautifulSoup(rs.get(url).text, "html.parser")
      if sp is None:
        return

      div_select_page = sp.find('div', attrs={'id': 'selectpage'})
      if div_select_page is None:
        return
      opt_selected = div_select_page.find('option', attrs={'selected': 'selected'})
      if opt_selected is None:
        return
      num = opt_selected.text.strip()

      imgholder = sp.find('div', attrs={'id' : 'imgholder'})
      next_url = imgholder.find('a').attrs['href']
      url_content = imgholder.find('img', attrs={'id' : 'img'}).attrs['src']

      if next_url:
        next_url = HOST + next_url

      yield info.ContentInfo(url, url_content, num)
      chapter_finished = next_chapter_url == next_url
      url = next_url


info.register_reader(HOST, MangaReaderReader())
