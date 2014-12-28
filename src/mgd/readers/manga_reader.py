#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A http://www.mangareader.net/ reader
'''

from mgd import readers


class MangaReaderReader:
  HOTNAME=r'http://www.mangareader.net/'
  SITE_URL='http://www.mangareader.net/alphabetical'

  def get_manga_list(self, site, session, request):
    '''
    Search and return a list (can yield) of Manga (added to the session)

    @param site: the Site object associated with the current reader.
    @param session: the session to use to store object in db.
    @param request: the request object to use for connection.

    @return: a list (or yeild) of Manga object (added to the session)
    '''
    self.main_html = urlopen(url)
    self.main_soup = BeautifulSoup(self.main_html.read())
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

readers.register_reader(r'http://www.mangareader.net', MangaReaderReader())
