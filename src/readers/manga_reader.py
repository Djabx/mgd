#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangareader.net/ reader
'''

import common


class MangaReaderReader(common.Reader):
  def __init__(self, history):
    self.history = history

  def parse_serie(self, serie_page):
    table_manga = self.main_soup.find('table', attrs={'id' : 'listing'})
    url_set = set()
    chapters_url = []
    chapters = []
    for a in table_manga.find_all('a'):
      chapter_name = a.string
      chapter_url = self.main_site + a.get('href')

      ci = common.ChapterInfo(chapter_name, chapter_url)

      chapters_url.append(chapter_url)
      chapters.append(ci)

    for ci in chapters:
      next_url = ci.page_url
      while True:
        previous_url = next_url


    pass
