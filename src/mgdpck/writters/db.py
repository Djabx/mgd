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


class DbWritter(actions.DummyWritter):
  @classmethod
  def get_name(cls):
    return 'db'

  def __init__(self, outdir, lsb, chapter_min, chapter_max):
    self.sm = model.StoreManager(os.path.join(outdir, DEFAULT_OUT_DB_NAME))
    self.sm.create_db(force_init=True)

    with self.sm.session_scope() as s:
      sites = data_access.find_site_with_host_name(lsb.site.hostname ,s)
      site = None
      if len(sites) == 0:
        # no site founded we create one
        site = model.Site()
        s.add(site)
        copy_attrs(lsb.site, site, ('name', 'hostname'))
        s.commit()
      else:
        site = sites[0]

      books = data_access.find_books_with_short_name(lsb.book.short_name, s)
      book = None
      if len(books) == 0:
        # we did not found any book with the name
        book = model.Book()
        s.add(book)
        copy_attrs(lsb.book, book, ('short_name', 'full_name'))
        s.commit()
      else:
        # we found some and we found one
        book = books[0]

      data_access.make_site_book_link(site, book, lsb.url, s)
      s.commit()

      lsb_out = data_access.find_site_book_link(site, book, s)[0]
      copy_attrs(lsb, lsb_out,
        ('url', 'followed', 'url_cover', 'cover', 'type_cover', 'min_chapter', 'max_chapter'))
      s.commit()
      self.lsb_out_id = lsb_out.id


  def done(self):
    pass


  def export_cover(self, lsb):
    # already done ;)
    pass

  def export_chapter(self, ch):
    with self.sm.session_scope() as s:
      lsb_out = data_access.find_link_with_id(self.lsb_out_id, s)
      try:
        c_out = data_access.find_chapter_with_num(lsb_out, ch.num, s)
      except sqlalchemy.orm.exc.NoResultFound:
        c_out = model.Chapter()
        s.add(c_out)
        c_out.lsb = lsb_out
        copy_attrs(ch, c_out, ('num', 'name', 'url'))
        s.commit()
      self.ch_out_id = c_out.id


  def export_content(self, co):
    with self.sm.session_scope() as s:
      ch_out = data_access.find_chapter_with_id(self.ch_out_id, s)
      try:
        co_out = data_access.find_content_with_num(ch_out, co.num, s)
      except sqlalchemy.orm.exc.NoResultFound:
        co_out = model.Content()
        s.add(co_out)
        co_out.chapter = ch_out
        copy_attrs(co, co_out, ('url', 'url_content', 'base_url_content', 'num', 'content', 'type_content'))

actions.register_writter(DbWritter)
