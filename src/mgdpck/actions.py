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

class AbsInfoGetter:
  def __enter__(self):
    return self

  def __exit__(self, *exc):
    return False

  def get_count(self):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.get_count))

  def get_info(self):
    '''
    Search and return a list (can yield) of books (added to the session)

    @return: a list (or yeild) of Manga object (added to the session)
    '''
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.get_info))


class AbsReader:
  def get_book_info_getter(self):
    '''
    Return a AbsInfoGetter for retriving book info.
    '''
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.get_book_info_list))

  def get_chapter_info_getter(self, lsb):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.get_book_chapter_info))

  def get_chapter_content_info_getter(self, chapter, next_chapter):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.get_chapter_content_info))


class AbsWritter:
  @classmethod
  def get_name(cls):
    return "DummyWritter"

  def __enter__(self):
    self.do()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.done()
    return False  # we're not suppressing exceptions

  def __init__(self, outdir):
    pass

  def do(self):
    pass

  def done(self):
    pass

  def export_book(self, lsb, chapter_min, chapter_max):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.export_book))

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


def create_all_site(sm, session=None):
  logger.info('updating all site')
  with sm.session_scope(session) as s:
    with multiprc.Pool(POOL_SIZE) as pool:
      # we do not give any session because they will be in another thread
      pool.map(create_site_from_reader,
          ((site_name, reader, sm) for site_name, reader in REG_READER.items()))


def create_site_from_reader(args):
  site_name, reader, sm = args
  hostname = site_name
  with sm.session_scope() as s:
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


def update_books_all_site(sm, session=None):
  logger.info('updating all book list')
  with sm.session_scope(session) as s:
    # we do not use map() because in python3
    # it's an iterator so we have to iterate over it
    for si in data_access.find_all_site(s):
      update_books_for_site(si, sm)


def update_books_for_site(site, sm):
  reader = REG_READER_ID[site.id]
  with multiprc.Pool(POOL_SIZE) as pool:
    with reader.get_book_info_getter() as book_getter:
      label = 'Importing books from "{}"'.format(reader.name)
      counter = 0
      with progress.Bar(label=label, expected_size=book_getter.get_count())  as bar:
        for bi in book_getter.get_info():
          if bi is not None:
            counter += 1
            pool.apply_async(update_book_for_site, (bi, site.id, sm))
            bar.show(counter)


def update_book_for_site(args):
  b, site_id, sm = args
  with sm.session_scope() as s:
    site = data_access.find_site_with_id(site_id, s)
    books = data_access.find_books_with_short_name(b.short_name, s)
    book = None
    if len(books) == 0:
      # we did not found any book with the name
      book = model.Book()
      book.short_name = b.short_name
      book.full_name = b.full_name
    else:
      # we found some and we found one
      book = books[0]

    data_access.make_site_book_link(site, book, b.url, s)


def update_all_chapters(sm, session=None):
  logger.info('updating all chapters')
  with sm.session_scope(session) as s:
    with multiprc.Pool(POOL_SIZE) as pool:
      pool.map(update_one_book_chapters, ((lsb.id, sm) for lsb in data_access.find_books_followed(s)))


def update_one_book_chapters(args):
  lsb_id, sm = args
  with sm.session_scope() as s:
    lsb = data_access.find_link_with_id(lsb_id, s)
    reader = REG_READER_ID[lsb.site.id]
    with reader.get_chapter_info_getter(lsb) as chapter_getter:
      counter = 0
      label = 'Importing chapters from "{!r}"'.format(lsb.book.short_name)
      with progress.Bar(label=label, expected_size=chapter_getter.get_count())  as bar:
        for ch in chapter_getter.get_info():
          if ch is None:
            continue
          counter += 1
          bar.show(counter)
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
            c = model.Chapter()
            c.lsb = lsb
            c.num = ch.num
            c.name = ch.name
            c.url = ch.url
            s.add(c)


def update_all_contents(sm, session=None):
  logger.debug('update all chapter content')
  with sm.session_scope(session) as s:
    for lsb in data_access.find_books_followed(s):
      with multiprc.Pool(POOL_SIZE) as pool:
        pool.map(update_one_chapter_content, ((lsb.id, ch.id, sm) for ch in data_access.find_chapters_to_update(lsb, s)))


def update_one_chapter_content(args):
  lsb_id, ch_id, sm = args
  with sm.session_scope() as s:
    lsb = data_access.find_link_with_id(lsb_id, s)
    ch = data_access.find_chapter_with_id(ch_id, s)
    next_chapter = data_access.find_chapter_with_num(lsb, ch.num+1, s)
    reader = REG_READER_ID[lsb.site.id]
    contents = {c.num:c for c in data_access.find_content_for_chapter(ch, s)}
    with reader.get_chapter_content_info_getter(ch, next_chapter) as content_getter:
      counter = 0
      label = 'Importing pages of chapter {0!r}#{1}'.format(lsb.book.short_name, ch.num)
      with progress.Bar(label=label, expected_size=content_getter.get_count())  as bar:
        for co in content_getter.get_info():
          if co is None:
            continue
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
          contents[c.num] = c

          counter += 1
          bar.show(counter)

    ch.completed = True


def update_all_images(sm, session=None):
  logger.debug('update all images')
  with sm.session_scope(session) as s:
    nb_cover = data_access.count_cover_to_update(s)
    if nb_cover > 0:
      label = 'Downloading covers'
      counter = 0
      with progress.Bar(label=label, expected_size=nb_cover) as bar:
        for lsb in data_access.find_cover_to_update(s):
          r = requests.get(lsb.url_cover)
          lsb.type_cover = r.headers['Content-Type']
          lsb.cover = r.content

          counter += 1
          bar.show(counter)

    nb_content = data_access.count_content_to_update(s)
    if nb_content > 0:
      with multiprc.Pool(POOL_SIZE) as pool:
        label = 'Downloading images'
        counter = 0
        with progress.Bar(label=label, expected_size=nb_content) as bar:
          d_t = {}
          for base_url, co_id in data_access.find_base_url_content_to_update(s):
            d_t.setdefault(base_url, []).append(co_id)

          chunk_size = 10
          co_ids_batch = []
          for _, co_ids in d_t.items():
            # we split the list in sublist of length chunk_size
            co_ids_batch.extend(co_ids[chunk_size*i:chunk_size*(i+1)]
              for i in range(int(len(co_ids)/chunk_size + 1)))

          results = []
          for co_ids in co_ids_batch:
            results.append(pool.apply_async(update_images, (sm, co_ids)))

          for r in results:
            bar.show(counter)
            counter += r.get() # blocking call


def update_images(sm, co_ids):
  #sm, co_ids = args
  counter = 0
  with sm.session_scope() as s:
    rs = requests.Session()
    for co_id in co_ids:
      co = data_access.find_content_with_id(co_id, s)
      r = rs.get(co.url_content)
      co.type_content = r.headers['Content-Type']
      co.content = r.content
      counter += 1
  return counter


def export_book(exporter, outdir, lsbs, chapter_start, chapter_end, session):
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with exporter(outdir) as expo:
    for lsb in lsbs:
      length_bar = data_access.count_book_contents(lsb, chapter_start, chapter_end, session)
      label_bar = 'exporting "{0}" in {1}: '.format(lsb.book.short_name, expo.get_name())
      with progress.Bar(label=label_bar, expected_size=length_bar)  as bar:
        counter = 0

        chapters = data_access.find_chapters_for_book(lsb, session, chapter_start, chapter_end)
        expo.export_book(lsb, chapters[0], chapters[-1])
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
