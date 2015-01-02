#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A simple sample reader for a source...
'''

import collections
from urllib import parse
from mgdpck import model
from mgdpck import data_access
import logging

logger = logging.getLogger(__name__)

ChapterInfo = collections.namedtuple('ChapterInfo', ('name', 'url'))
class ImageInfo(collections.namedtuple('ImageInfo', ('chapter_info', 'url', 'img_url', 'next_page'))):
    def __new__(cls, chapter_info, url, img_url=None, next_page=None):
      return super(ImageInfo, cls).__new__(cls, chapter_info, url, img_url, next_page)

class BookInfo(collections.namedtuple('BookInfo', ('short_name', 'url', 'full_name'))):
  def __new__(cls, short_name, url, full_name=None):
    return super(BookInfo, cls).__new__(cls, short_name, url, full_name)


REG_READER = {}
REG_READER_ID = {}


def register_reader(site_name, reader):
  REG_READER[site_name] = reader


def create_all_site():
  for site_name, reader in REG_READER.items():
    create_site_from_reader(site_name, reader)


def create_site_from_reader(site_name, reader):
  hostname = parse.urlparse(site_name).hostname
  with model.session_scope() as s:
    sites = data_access.find_site_with_host_name(hostname, s)
    if len(sites) == 0:
      logger.debug('Creating a new site object for: "%s"', hostname)
      # no site founded we create one
      site = model.Site()
      site.name = reader.name
      site.hostname = hostname
      s.add(site)
    else:
      # len == 1 because unique constrain in DB
      site = sites[0]
      logger.debug('Using an existing site object for: "%s"', hostname)
      # we update name if not the same
      site.name = reader.name
      s.add(site)

    s.commit()
    logger.debug('Register reader for site: "%s" (from: "%s")', hostname, site_name)
    REG_READER_ID[site.id] = reader


def update_books_all_site(session=None):
  with model.session_scope(session) as s:
    for si in data_access.find_all_site(s):
      update_books_for_site(si, s)


def update_books_for_site(site, session=None):
  with model.session_scope(session) as s:
    reader = REG_READER_ID[site.id]
    for b in reader.get_book_info_list():
      if b is None:
        continue
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


def get_reader_from_site(site):
  logger.debug('Searching reader for site: "%s"', site)
  reader = REG_READER.get(site.id)
  logger.debug('Found reader: %s hostname: "%s" ', reader is not None, url)
  return reader
