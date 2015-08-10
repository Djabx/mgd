#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A simple sample reader for a source...
'''

import os
import collections
import logging
import urllib.parse
# use of dummy package because we do not careabout process or thread
# we care about muli connexion
import multiprocessing.dummy as multiprc

import requests
from clint.textui import progress

from mgdpck import model
from mgdpck import data_access

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


MSG_NOT_IMPLEMENTED = 'The methode "{0.__self__.__class__.__name__}.{0.__name__}" MUST be implemented'

class DummyWritter:
  @classmethod
  def get_name(cls):
    return "DummyWritter"

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.done()
    return False  # we're not suppressing exceptions

  def __init__(self, outdir, book_name, chapter_min, chapter_max):
    pass

  def done(self):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.done))

  def export_cover(self, lsb):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.export_cover))

  def export_chapter(self, ch):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.export_chapter))

  def export_content(self, co):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.export_content))


REG_READER = {}
REG_READER_ID = {}
REG_WRITTER = {}


def register_reader(site_name, reader):
  REG_READER[site_name] = reader


def register_writter(writter):
  REG_WRITTER[writter.get_name()] = writter


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
    for i, si in enumerate(data_access.find_all_site(s)):
      update_books_for_site(si, s)
      if i % 10 == 0:
        # we commit every 10 books
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
    with multiprc.Pool(POOL_SIZE) as pool:
      pool.map(update_one_book_chapters, (lsb.id for lsb in data_access.find_books_followed(s)))
    s.commit()


def update_one_book_chapters(lsb_id):
  with model.session_scope() as s:
    lsb = data_access.find_link_with_id(lsb_id, s)
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
  pass


def update_all_contents(session=None):
  logger.debug('update all chapter content')
  with model.session_scope(session) as s:
    for lsb in data_access.find_books_followed(s):
      with multiprc.Pool(POOL_SIZE) as pool:
        pool.map(update_one_chapter_content, ((lsb.id, ch.id) for ch in data_access.find_chapters_to_update(lsb, s)))


def update_one_chapter_content(lsb_id, ch_id):
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
      c.base_url_content = urllib.parse.urlparse(co.url_content).netloc
      c.num = co.num

    ch.completed = True
    logger.info("Get content structure of chapter: %s", str(ch))


def update_all_images(session=None):
  logger.debug('update all images')
  with model.session_scope(session) as s:
    with multiprc.Pool(POOL_SIZE) as pool:
      # we do not give any session because they will be in another thread
      pool.map(update_one_image_content, (co.id for co in data_access.find_content_to_update(s)))
      pool.map(update_one_image_lsb, (lsb.id for lsb in data_access.find_cover_to_update(s)))


def update_one_image_content(co_id):
  with model.session_scope() as s:
    co = data_access.find_content_with_id(co_id, s)
    logger.debug('get content at: %s', co.url_content)
    r = requests.get(co.url_content)
    co.type_content = r.headers['Content-Type']
    co.content = r.content
    # we commit after every image.. just in case
    s.commit()


def update_one_image_lsb(lsb_id):
  with model.session_scope() as s:
    lsb = data_access.find_link_with_id(lsb_id, s)
    logger.debug('get cover at: %s', lsb.url_cover)
    r = requests.get(lsb.url_cover)
    lsb.type_cover = r.headers['Content-Type']
    lsb.cover = r.content
    # we commit after every image.. just in case
    s.commit()


def export_book(exporter, outdir, lsb, chapters, session):
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  chapter_min = chapters[0]
  chapter_max = chapters[-1]
  with exporter(outdir, lsb, chapter_min, chapter_max) as expo:
    length_bar = data_access.count_book_contents(lsb, chapter_min.num, chapter_max.num, session)
    with progress.Bar(label='exporting "{0}" in {1}: '.format(lsb.book.short_name, expo.get_name()), expected_size=length_bar)  as bar:
      counter = 0
      if lsb.cover is not None:
        expo.export_cover(lsb)

      for ch in chapters:
        expo.export_chapter(ch)

        for co in ch.contents:
          expo.export_content(co)

          counter += 1
          bar.show(counter)
          session.expire(co)
        session.expire(ch)