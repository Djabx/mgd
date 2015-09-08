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
CHUNK_SIZE = 10

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ChapterInfo = collections.namedtuple('ChapterInfo', ('name', 'url'))
class ImageInfo(collections.namedtuple('ImageInfo', ('chapter_info', 'url', 'img_url', 'next_page'))):
  def __new__(cls, chapter_info, url, img_url=None, next_page=None):
    return super(ImageInfo, cls).__new__(cls, chapter_info, url, img_url, next_page)

class BookInfo(collections.namedtuple('BookInfo', ('short_name', 'url', 'full_name'))):
  def __new__(cls, short_name, url, full_name=None):
    return super(BookInfo, cls).__new__(cls, short_name, url, full_name)

ChapterInfo = collections.namedtuple('ChapterInfo', ('name', 'url', 'num'))

PageInfo = collections.namedtuple('PageInfo', ('url', 'url_image', 'num'))


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

  def get_page_info_getter(self, chapter, next_chapter):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.get_page_info_getter))


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

  def export_page(self, co):
    raise NotImplementedError(MSG_NOT_IMPLEMENTED.format(self.export_page))


REG_READER = {}
REG_READER_ID = {}
REG_WRITTER = {}


def register_reader(site_name, reader):
  REG_READER[site_name] = reader


def register_writter(writter):
  REG_WRITTER[writter.get_name()] = writter


def create_all_site(s):
  logger.info('updating all site')
  for site_name, reader in REG_READER.items():
    create_site_from_reader(site_name, reader, s)


def create_site_from_reader(hostname, reader, s):
  site = data_access.find_site_with_host_name(hostname, s)
  if site is None:
    logger.debug('Creating a new site object for: "%s"', hostname)
    # no site founded we create one
    site = model.Site()
    site.name = reader.name
    site.hostname = hostname
    s.add(site)
    s.commit()

  logger.debug('Register reader for site: "%s" (from: "%s")', hostname, hostname)
  REG_READER_ID[site.id] = reader


def update_books_all_site(s):
  logger.info('updating all book list')
  #its faster than making many select
  books = {b.short_name:b for b in data_access.find_all_book(s)}
  for si in data_access.find_all_site(s):
    reader = REG_READER_ID[si.id]
    book_getter = reader.get_book_info_getter()
    label = 'Importing books from "{}" '.format(reader.name)
    counter = 0
    with progress.Bar(label=label, expected_size=book_getter.get_count())  as bar:
      for bi in book_getter.get_info():
        if bi.short_name not in books:
          # we did not found any book with the name
          book = model.Book()
          book.short_name = bi.short_name
          s.add(book)
          books[book.short_name] = book
        book = books[bi.short_name]
        if bi.full_name is not None:
          book.full_name = bi.full_name
        data_access.make_site_book_link(si, book, bi.url, s)

        counter += 1
        bar.show(counter)


def update_all_chapters(s):
  logger.info('updating all chapters')
  for lsb in data_access.find_books_followed(s):
    update_one_book_chapters(lsb, s)


def update_one_book_chapters(lsb, s):
  reader = REG_READER_ID[lsb.site.id]
  with reader.get_chapter_info_getter(lsb) as chapter_getter:
    counter = 0
    label = 'Importing chapters from {!r} '.format(lsb.book.short_name)
    with progress.Bar(label=label, expected_size=chapter_getter.get_count())  as bar:
      chapters = {c.num:c for c in data_access.find_chapters_for_book(lsb, s)}
      for ch in chapter_getter.get_info():
        if ch.num not in chapters:
          # we did not found any book with the name
          c = model.Chapter()
          c.lsb = lsb
          c.num = ch.num
          s.add(c)
          chapters[c.num] = c

        c = chapters[ch.num]
        c.name = ch.name
        c.url = ch.url

        counter += 1
        bar.show(counter)


def update_all_pages(s):
  logger.debug("update all chapter's pages")
  counter = 0
  label = 'Importing pages of chapters '
  with progress.Bar(label=label, expected_size=data_access.count_chapters_to_update(s))  as bar:
    for ch in data_access.find_chapters_to_update(s):
      update_one_chapter_page(ch, s)

      counter += 1
      bar.show(counter)



def update_one_chapter_page(ch, s):
  next_chapter = data_access.find_chapter_with_num(ch.lsb, ch.num+1, s)
  reader = REG_READER_ID[ch.lsb.site.id]
  with reader.get_page_info_getter(ch, next_chapter) as page_getter:
    page_getter.get_count()
    for pa in page_getter.get_info():
      p = data_access.find_page_with_num(ch, pa.num, s)
      if p is None:
        p = model.Page()
        p.chapter = ch
        s.add(p)
      p.url = pa.url
      p.num = pa.num
      p.image = __get_image(pa.url_image, s)

    ch.completed = True
    s.commit()


def __get_image(img_url, session):
  img = model.Image()
  img.url = img_url
  img.base_url = urllib.parse.urlparse(img_url).netloc
  session.add(img)
  return img


def update_all_images(sm):
  logger.debug('update all images')
  with sm.session_scope() as s:
    nb_img = data_access.count_image_to_update(s)
    if nb_img > 0:
      with multiprc.Pool(POOL_SIZE) as pool:
        label = 'Downloading images'
        counter = 0
        with progress.Bar(label=label, expected_size=nb_img) as bar:
          d_t = {}
          for base_url, img_id in data_access.find_base_url_image_to_update(s):
            d_t.setdefault(base_url, []).append(img_id)

          img_ids_batch = []
          for _, img_ids in d_t.items():
            # we split the list in sublist of length CHUNK_SIZE
            img_ids_batch.extend(img_ids[CHUNK_SIZE*i:CHUNK_SIZE*(i+1)]
              for i in range(int(len(img_ids)/CHUNK_SIZE + 1)))

          results = []
          for img_ids in img_ids_batch:
            results.append(pool.apply_async(update_images, (sm, img_ids)))

          bar.show(counter)
          for r in results:
            bar.show(counter)
            counter += r.get() # blocking call
            bar.show(counter)


def update_images(sm, img_ids):
  #sm, co_ids = args
  counter = 0
  with sm.session_scope() as s:
    rs = requests.Session()
    for img_id in img_ids:
      img = data_access.find_image_with_id(img_id, s)
      r = rs.get(img.url)
      img.mimetype = r.headers['Content-Type']
      img.content = r.content
      img.downloaded = True
      counter += 1
  return counter


def export_book(exporter, outdir, lsbs, chapter_start, chapter_end, session):
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  with exporter(outdir) as expo:
    for lsb in lsbs:
      length_bar = data_access.count_book_pages(lsb, chapter_start, chapter_end, session)
      label_bar = 'exporting "{0}" in {1}: '.format(lsb.book.short_name, expo.get_name())
      with progress.Bar(label=label_bar, expected_size=length_bar)  as bar:
        counter = 0

        chapters = data_access.find_chapters_for_book(lsb, session, chapter_start, chapter_end)
        expo.export_book(lsb, chapters[0], chapters[-1])
        if lsb.image is not None:
          expo.export_cover(lsb)

        for ch in chapters:
          expo.export_chapter(ch)

          for pa in ch.pages:
            expo.export_page(pa)

            counter += 1
            bar.show(counter)
            session.expire(pa)
          session.expire(ch)


def delete_book(lsb, s):
  data_access.delete_lsb(lsb, s)
