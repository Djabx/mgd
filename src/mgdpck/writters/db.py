#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A db writter
'''

from mgdpck import model
from mgdpck import actions
from mgdpck import data_access
import os
import mimetypes
import logging

import sqlalchemy.orm

logger = logging.getLogger(__name__)
DEFAULT_OUT_DB_NAME = model.DEFAULT_FILE_DB_NAME[:-3] + '_out.db'



def copy_attrs(obj_src, obj_dest, attrs):
  for attr in attrs:
    setattr(obj_dest, attr, getattr(obj_src, attr))


class DbWritter(actions.AbsWritter):
  @classmethod
  def get_name(cls):
    return 'db'

  def __init__(self, outdir):
    self.sm = model.StoreManager(os.path.join(outdir, DEFAULT_OUT_DB_NAME))
    self.s = None
    self.lsb = None
    self.ch = None


  def do(self):
    self.sm.create_db(force_init=True)
    self.s = self.sm.get_session()


  def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type:
      self.s.rollback()
    else:
      self.s.commit()
    self.s.close()
    return False  # we're not suppressing exceptions


  def export_book(self, lsb, chapter_min, chapter_max):
    sites = data_access.find_site_with_host_name(lsb.site.hostname, self.s)
    site = None
    if len(sites) == 0:
      # no site founded we create one
      site = model.Site()
      self.s.add(site)
      copy_attrs(lsb.site, site, ('name', 'hostname'))
    else:
      site = sites[0]

    books = data_access.find_books_with_short_name(lsb.book.short_name, self.s)
    book = None
    if len(books) == 0:
      # we did not found any book with the name
      book = model.Book()
      self.s.add(book)
      copy_attrs(lsb.book, book, ('short_name', 'full_name'))
    else:
      # we found some and we found one
      book = books[0]

    data_access.make_site_book_link(site, book, lsb.url, self.s)

    self.lsb = data_access.find_site_book_link(site, book, self.s)[0]
    copy_attrs(lsb, self.lsb,
      ('url', 'followed', 'url_cover', 'cover', 'type_cover', 'min_chapter', 'max_chapter'))
    self.s.commit()


  def export_cover(self, lsb):
    # already done ;)
    pass

  def export_chapter(self, ch):
    try:
      self.ch = data_access.find_chapter_with_num(self.lsb, ch.num, self.s)
    except sqlalchemy.orm.exc.NoResultFound:
      self.ch = model.Chapter()
      self.s.add(self.ch)
      self.ch.lsb = self.lsb
      copy_attrs(ch, self.ch, ('num', 'name', 'url'))


  def export_content(self, co):
    try:
      co_out = data_access.find_content_with_num(self.ch, co.num, self.s)
    except sqlalchemy.orm.exc.NoResultFound:
      co_out = model.Content()
      self.s.add(co_out)
      co_out.chapter = self.ch
      copy_attrs(co, co_out, ('url', 'url_content', 'base_url_content', 'num', 'content', 'type_content'))

actions.register_writter(DbWritter)
