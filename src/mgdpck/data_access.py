#! /usr/bin/python
# -*- coding: utf-8 -*-

from mgdpck import model
from sqlalchemy import func
import sqlalchemy.orm
import logging
logger = logging.getLogger(__name__)


def find_obj_with_id(clazz, id_, session):
  try:
    return session.query(clazz) \
        .filter(clazz.id==id_) \
        .one()
  except sqlalchemy.orm.exc.NoResultFound:
    return None


def find_site_with_id(id_, session):
  return find_obj_with_id(model.Site, id_, session)


def find_book_with_id(id_, session):
  return find_obj_with_id(model.Book, id_, session)


def find_link_with_id(id_, session):
  return find_obj_with_id(model.LinkSiteBook, id_, session)


def find_chapter_with_id(id_, session):
  return find_obj_with_id(model.Chapter, id_, session)


def find_page_with_id(id_, session):
  return find_obj_with_id(model.Page, id_, session)


def find_image_with_id(id_, session):
  return find_obj_with_id(model.Image, id_, session)


def find_site_with_host_name(hn, session):
  try:
    return session.query(model.Site) \
      .filter(model.Site.hostname==hn) \
      .one()
  except sqlalchemy.orm.exc.NoResultFound:
    return None


def find_all_site(session):
  return session.query(model.Site) \
    .order_by(model.Site.name) \
    .all()


def find_all_book(session):
  return session.query(model.Book) \
    .all()


def find_books_with_short_name(sn, session):
  try:
    return session.query(model.Book) \
      .filter(model.Book.short_name==sn) \
      .one()
  except sqlalchemy.orm.exc.NoResultFound:
    return None


def find_site_book_link(si, bk, session):
  try:
    return session.query(model.LinkSiteBook) \
      .filter(model.LinkSiteBook.site==si) \
      .filter(model.LinkSiteBook.book==bk) \
      .one()
  except sqlalchemy.orm.exc.NoResultFound:
    return None


def find_books_followed(session):
  return session.query(model.LinkSiteBook) \
    .join(model.Book).join(model.Site) \
    .filter(model.LinkSiteBook.followed==True) \
    .order_by(model.Book.short_name) \
    .order_by(model.Site.name) \
    .all()


def find_books(session):
  return session.query(model.LinkSiteBook) \
    .join(model.Book).join(model.Site) \
    .order_by(model.Book.short_name) \
    .order_by(model.Site.name) \
    .all()


def count_chapters_to_update(session):
  return session.query(func.count(model.Chapter.id)) \
    .join(model.LinkSiteBook) \
    .filter(model.LinkSiteBook.followed==True) \
    .filter(model.Chapter.completed==False) \
    .filter((model.LinkSiteBook.min_chapter == None) |
        (model.Chapter.num >= model.LinkSiteBook.min_chapter)) \
    .filter((model.LinkSiteBook.max_chapter == None) |
        (model.Chapter.num <= model.LinkSiteBook.max_chapter)) \
    .one()[0]


def find_chapters_to_update(session):
  q = session.query(model.Chapter) \
    .join(model.LinkSiteBook) \
    .filter(model.LinkSiteBook.followed==True) \
    .filter(model.Chapter.completed==False) \
    .filter((model.LinkSiteBook.min_chapter == None) |
        (model.Chapter.num >= model.LinkSiteBook.min_chapter)) \
    .filter((model.LinkSiteBook.max_chapter == None) |
        (model.Chapter.num <= model.LinkSiteBook.max_chapter))

  return q.all()


def find_chapters_for_book(lsb, session, chapter_min=None, chapter_max=None):
  q = session.query(model.Chapter) \
      .filter(model.Chapter.lsb==lsb)
  if chapter_min is not None:
    q = q.filter(model.Chapter.num >= chapter_min)
  if chapter_max is not None:
    q = q.filter(model.Chapter.num <= chapter_max)
  return q.all()


def find_chapter_with_num(lsb, chapter_num, session):
  try:
    return session.query(model.Chapter) \
      .filter(model.Chapter.lsb==lsb) \
      .filter(model.Chapter.num == chapter_num) \
      .one()
  except sqlalchemy.orm.exc.NoResultFound:
    return None


def find_page_with_num(ch, page_num, session):
  try:
    return session.query(model.Page) \
      .filter(model.Page.chapter==ch) \
      .filter(model.Page.num == page_num) \
      .one()
  except sqlalchemy.orm.exc.NoResultFound:
    return None


def find_page_for_chapter(ch, session):
  return session.query(model.Page) \
      .filter(model.Page.chapter == ch) \
      .all()


def count_image_to_update(session):
  return session.query(func.count(model.Image.id)) \
    .filter(model.Image.downloaded == False) \
    .one()[0]


def find_base_url_image_to_update(session):
  return session.query(model.Image.base_url, model.Image.id) \
    .filter(model.Image.downloaded == False) \
    .all()


def make_site_book_link(si, bk, url, session):
  lsb = find_site_book_link(si, bk, session)
  if lsb is None:
    lsb = model.LinkSiteBook()
    lsb.site = si
    lsb.book = bk
    lsb.url = url
    session.add(lsb)
  return lsb


def search_book(name, site_name, session):
  name = name if name is not None else '%'
  site_name = site_name if site_name is not None else '%'

  return session.query(model.LinkSiteBook) \
    .join(model.Book).join(model.Site) \
    .filter(func.lower(model.Book.short_name).like(name.lower())) \
    .filter(func.lower(model.Site.name).like(site_name.lower())) \
    .order_by(model.Site.name) \
    .order_by(model.Book.short_name) \
    .all()


def count_book_chapters(lsb, session):
  return session.query(func.count(model.Chapter.id)) \
    .filter(model.Chapter.lsb_id==lsb.id) \
    .one()[0]


def count_chapter_pages(ch, session):
  return session.query(func.count(model.Page.id)) \
    .filter(model.Page.chapter_id==ch.id) \
    .one()[0]


def count_book_pages(lsb, chapter_min, chapter_max, session):
  q = session.query(func.count(model.Page.id)) \
    .filter(model.Chapter.lsb_id==lsb.id) \
    .filter(model.Page.chapter_id==model.Chapter.id)
  if chapter_min is not None:
    q = q.filter(model.Chapter.num >= chapter_min)
  if chapter_max is not None:
    q = q.filter(model.Chapter.num <= chapter_max)

  return q.one()[0]


def delete_lsb(lsb, session):
  session.query(model.Chapter) \
    .filter(model.Chapter.lsb_id == lsb.id) \
    .delete()
