#! /usr/bin/python
# -*- coding: utf-8 -*-

from mgdpck import model
from sqlalchemy import func
import logging
logger = logging.getLogger(__name__)


def find_obj_with_id(clazz, id_, session):
  with model.session_scope(session) as s:
    return s.query(clazz).filter(clazz.id==id_).one()


def find_site_with_id(id_, session):
  return find_obj_with_id(model.Site, id_, session)


def find_book_with_id(id_, session):
  return find_obj_with_id(model.Book, id_, session)


def find_link_with_id(id_, session):
  return find_obj_with_id(model.LinkSiteBook, id_, session)


def find_chapter_with_id(id_, session):
  return find_obj_with_id(model.Chapter, id_, session)


def find_content_with_id(id_, session):
  return find_obj_with_id(model.Content, id_, session)


def find_site_with_host_name(hn, session):
  with model.session_scope(session) as s:
    return s.query(model.Site).filter(model.Site.hostname==hn).all()


def find_all_site(session):
  with model.session_scope(session) as s:
    return s.query(model.Site) \
      .order_by(model.Site.name) \
      .all()


def find_books_with_short_name(sn, session):
  with model.session_scope(session) as s:
    return s.query(model.Book).filter(model.Book.short_name==sn).all()


def find_site_book_link(si, bk, session):
  with model.session_scope(session) as s:
    return s.query(model.LinkSiteBook).filter(model.LinkSiteBook.site==si).filter(model.LinkSiteBook.book==bk).all()


def find_books_followed(session):
  with model.session_scope(session) as s:
    return s.query(model.LinkSiteBook) \
      .join(model.Book).join(model.Site) \
      .filter(model.LinkSiteBook.followed==True) \
      .order_by(model.Book.short_name) \
      .order_by(model.Site.name) \
      .all()


def find_books(session):
  with model.session_scope(session) as s:
    return s.query(model.LinkSiteBook) \
      .join(model.Book).join(model.Site) \
      .order_by(model.Book.short_name) \
      .order_by(model.Site.name) \
      .all()


def find_chapters_to_update(lsb, session):
  with model.session_scope(session) as s:
    q = s.query(model.Chapter) \
      .join(model.LinkSiteBook) \
      .filter(model.Chapter.lsb==lsb) \
      .filter(model.Chapter.completed==False)

    if lsb.min_chapter is not None:
      q = q.filter(model.Chapter.num >= lsb.min_chapter)

    if lsb.max_chapter is not None:
      q = q.filter(model.Chapter.num <= lsb.max_chapter)

    return q.all()


def find_chapters_for_book(lsb, session):
  with model.session_scope(session) as s:
    return s.query(model.Chapter).filter(model.Chapter.lsb==lsb).all()


def find_content_for_chapter(ch, session):
  with model.session_scope(session) as s:
    return s.query(model.Content).filter(model.Content.chapter==ch).all()


def find_content_to_update(session):
  with model.session_scope(session) as s:
    return s.query(model.Content).join(model.Chapter).join(model.LinkSiteBook) \
      .filter(model.Chapter.completed==True) \
      .filter(model.Content.content==None) \
      .order_by(model.LinkSiteBook.book_id) \
      .order_by(model.Chapter.num) \
      .order_by(model.Content.num) \
      .all()


def find_cover_to_update(session):
  with model.session_scope(session) as s:
    return s.query(model.LinkSiteBook) \
      .filter(model.LinkSiteBook.cover==None) \
      .filter(model.LinkSiteBook.url_cover!=None) \
      .filter(model.LinkSiteBook.followed==True) \
      .all()


def make_site_book_link(si, bk, url, session):
  with model.session_scope(session) as s:
    links = find_site_book_link(si, bk, session)
    if len(links) == 0:
      lsb = model.LinkSiteBook(site=si, book=bk, url=url)
      s.add(lsb)
    else:
      lsb = links[0]
      lsb.url = url


def search_book(name, site_name, session):
  name = name if name is not None else '%'
  site_name = site_name if site_name is not None else '%'

  with model.session_scope(session) as s:
    return s.query(model.LinkSiteBook) \
      .join(model.Book).join(model.Site) \
      .filter(func.lower(model.Book.short_name).like(name.lower())) \
      .filter(func.lower(model.Site.name).like(site_name.lower())) \
      .order_by(model.Site.name) \
      .order_by(model.Book.short_name) \
      .all()


def count_book_chapters(lsb, session):
  with model.session_scope(session) as s:
    return s.query(func.count(model.Chapter.id))\
      .filter(model.Chapter.lsb_id==lsb.id)\
      .one()[0]


def count_chapter_contents(ch, session):
  with model.session_scope(session) as s:
    return s.query(func.count(model.Content.id))\
      .filter(model.Content.chapter_id==ch.id)\
      .one()[0]


def count_book_contents(lsb, session):
  with model.session_scope(session) as s:
    return s.query(func.count(model.Content.id))\
      .filter(model.Chapter.lsb_id==lsb.id)\
      .filter(model.Content.chapter_id==model.Chapter.id)\
      .one()[0]
