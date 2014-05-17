#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangareader.net/ reader
'''

import common


class MangaReaderReader(common.Reader):

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
