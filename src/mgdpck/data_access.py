#! /usr/bin/python
# -*- coding: utf-8 -*-

from mgdpck import model



def find_obj_with_id(clazz, id_, session):
  with model.session_scope(session) as s:
    return s.query(clazz).filter(clazz.id==id_).all()


def find_site_with_host_name(hn, session):
  with model.session_scope(session) as s:
    return s.query(model.Site).filter(model.Site.hostname==hn).all()


def find_all_site(session):
  with model.session_scope(session) as s:
    return s.query(model.Site).all()


def find_books_with_short_name(sn, session):
  with model.session_scope(session) as s:
    return s.query(model.Book).filter(model.Book.short_name==sn).all()


def find_site_book_link(si, bk, session):
  with model.session_scope(session) as s:
    return s.query(model.LinkSiteBook).filter(model.LinkSiteBook.site==si).filter(model.LinkSiteBook.book==bk).all()


def make_site_book_link(si, bk, url, session):
  with model.session_scope(session) as s:
    links = find_site_book_link(si, bk, session)
    if len(links) == 0:
      lsb = model.LinkSiteBook(site=si, book=bk, url=url)
      s.add(lsb)
    else:
      lsb = links[0]
      lsb.url = url
    s.commit()
