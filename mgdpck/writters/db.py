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
logger.addHandler(logging.NullHandler())
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


  def __copy_img(self, img_src):
    if img_src is not None:
      img = model.Image()
      copy_attrs(img_src, img, ('url', 'base_url', 'content', 'mimetype', 'downloaded'))
      self.s.add(img)
      return img
    else:
      return None


  def export_book(self, lsb, chapter_min, chapter_max):
    site = data_access.find_site_with_host_name(lsb.site.hostname, self.s)
    if site is None:
      # no site founded we create one
      site = model.Site()
      self.s.add(site)
      copy_attrs(lsb.site, site, ('name', 'hostname'))

    book = data_access.find_books_with_short_name(lsb.book.short_name, self.s)
    if book is None:
      # we did not found any book with the name
      book = model.Book()
      self.s.add(book)
      copy_attrs(lsb.book, book, ('short_name', 'full_name'))

    self.lsb = data_access.make_site_book_link(site, book, lsb.url, self.s)

    copy_attrs(lsb, self.lsb,
      ('url', 'followed', 'min_chapter', 'max_chapter'))
    self.lsb.image = self.__copy_img(lsb.image)
    self.s.commit()


  def export_cover(self, lsb):
    # already done ;)
    pass

  def export_chapter(self, ch):
    self.ch = data_access.find_chapter_with_num(self.lsb, ch.num, self.s)
    if self.ch is None:
      self.ch = model.Chapter()
      self.s.add(self.ch)
      self.ch.lsb = self.lsb
      copy_attrs(ch, self.ch, ('num', 'name', 'url', 'completed'))


  def export_page(self, pa):
    pa_out = data_access.find_page_with_num(self.ch, pa.num, self.s)
    if pa_out is None:
      pa_out = model.Page()
      self.s.add(pa_out)
      pa_out.chapter = self.ch
      copy_attrs(pa, pa_out, ('url', 'num'))
      pa_out.image = self.__copy_img(pa.image)


actions.register_writter(DbWritter)
