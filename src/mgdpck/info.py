#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A simple sample reader for a source...
'''

import collections
from mgdpck import model
from mgdpck import data_access
import urllib.parse
import logging
import requests
# use of dummy package because we do not careabout process or thread
# we care about muli connexion
import multiprocessing.dummy as multiprc

# not too many or the given site may close the connection
POOL_SIZE = 2

logger = logging.getLogger(__name__)

ChapterInfo = collections.namedtuple('ChapterInfo', ('name', 'url'))
class ImageInfo(collections.namedtuple('ImageInfo', ('chapter_info', 'url', 'img_url', 'next_page'))):
    def __new__(cls, chapter_info, url, img_url=None, next_page=None):
      return super(ImageInfo, cls).__new__(cls, chapter_info, url, img_url, next_page)

class BookInfo(collections.namedtuple('BookInfo', ('short_name', 'url', 'full_name'))):
  def __new__(cls, short_name, url, full_name=None):
    return super(BookInfo, cls).__new__(cls, short_name, url, full_name)

ChapterInfo = collections.namedtuple('ChapterInfo', ('name', 'url', 'num'))

ContentInfo = collections.namedtuple('ContentInfo', ('url', 'url_content', 'num'))



REG_READER = {}
REG_READER_ID = {}


def register_reader(site_name, reader):
  REG_READER[site_name] = reader


def create_all_site(session=None):
  logger.info('updating all site')
  with model.session_scope(session) as s:
    with multiprc.Pool(POOL_SIZE) as pool:
      # we do not give any session because they will be in another thread
      pool.map(create_site_from_reader, REG_READER.items())


def create_site_from_reader(args, session=None):
  site_name, reader = args
  hostname = site_name
  with model.session_scope(session) as s:
    sites = data_access.find_site_with_host_name(hostname, s)
    if len(sites) == 0:
      logger.debug('Creating a new site object for: "%s"', hostname)
      # no site founded we create one
      site = model.Site()
      site.name = reader.name
      site.hostname = hostname
      s.add(site)
      s.commit()
    else:
      # len == 1 because unique constrain in DB
      site = sites[0]
      logger.debug('Using an existing site object for: "%s"', hostname)
      # we update name if not the same
      site.name = reader.name

    logger.debug('Register reader for site: "%s" (from: "%s")', hostname, site_name)
    REG_READER_ID[site.id] = reader


def update_books_all_site(session=None):
  logger.info('updating all book list')
  with model.session_scope(session) as s:
    for si in data_access.find_all_site(s):
      update_books_for_site(si, s)
      s.commit()


def update_books_for_site(site, session=None):
  with model.session_scope(session) as s:
    reader = REG_READER_ID[site.id]
    with multiprc.Pool(POOL_SIZE) as pool:
      pool.map(update_book_for_site, ((bi, site.id) for bi in reader.get_book_info_list() if bi is not None))


def update_book_for_site(args):
  b, site_id = args
  with model.session_scope() as s:
    site = data_access.find_site_with_id(site_id, s)
    books = data_access.find_books_with_short_name(b.short_name, s)
    book = None
    if len(books) == 0:
      # we did not found any book with the name
      logger.debug('Creating a new book object for: "%s"', b)
      book = model.Book()
      book.short_name = b.short_name
      book.full_name = b.full_name
    else:
      # we found some and we found one
      book = books[0]

    data_access.make_site_book_link(site, book, b.url, s)
    s.commit()


def update_all_chapters(session=None):
  logger.info('updating all chapters')
  with model.session_scope(session) as s:
    for lsb in data_access.find_books_followed(s):
      reader = REG_READER_ID[lsb.site.id]
      for ch in reader.get_book_chapter_info(lsb):
        if ch is None:
          continue
        chapters = {c.num:c for c in data_access.find_chapters_for_book(lsb, s)}
        if ch.num in chapters:
          # maybe we have to update ?
          c = chapters[ch.num]
          if not c.completed:
            # we have to update
            c.name = ch.name
            c.url = ch.url
          # else
          # the chapter is already completed
        else:
          # we did not found any book with the name
          logger.debug('Creating a new chapter object for: "%s"', ch)
          c = model.Chapter()
          c.lsb = lsb
          c.num = ch.num
          c.name = ch.name
          c.url = ch.url
          s.add(c)
    s.commit()


def update_all_contents(session=None):
  with model.session_scope(session) as s:
    for lsb in data_access.find_books_followed(s):
      with multiprc.Pool(POOL_SIZE) as pool:
        pool.map(update_one_chapter_content, ((lsb.id, ch.id) for ch in data_access.find_chapters_to_update(lsb, s)))


def update_one_chapter_content(args):
  lsb_id, ch_id = args
  with model.session_scope() as s:
    lsb = data_access.find_link_with_id(lsb_id, s)
    ch = data_access.find_chapter_with_id(ch_id, s)
    ch_dic = {c.num:c for c in lsb.chapters}
    reader = REG_READER_ID[lsb.site.id]
    next_chapter = ch_dic.get(ch.num+1)
    for co in reader.get_chapter_content_info(ch, next_chapter):
      if co is None:
        continue
      contents = {c.num:c for c in data_access.find_content_for_chapter(ch, s)}
      if co.num in contents:
        c = contents[co.num]
      else:
        c = model.Content()
        c.chapter = ch
        s.add(c)
      c.url = co.url
      c.url_content = co.url_content
      c.num = co.num

    ch.completed = True
    logger.info("Get content structure of chapter: %s", str(ch))


def update_all_images(session=None):
  with model.session_scope(session) as s:
    with multiprc.Pool(POOL_SIZE) as pool:
      # we do not give any session because they will be in another thread
      pool.map(update_one_image, (co.id for co in data_access.find_content_to_update(s)))


def update_one_image(args):
  co_id = args
  with model.session_scope() as s:
    co = data_access.find_content_with_id(co_id, s)
    logger.debug('get content at: %s', co.url_content)
    r = requests.get(co.url_content)
    co.type_content = r.headers['Content-Type']
    co.content = r.content
    # we commit after every image.. just in case
    s.commit()
