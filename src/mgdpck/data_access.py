#! /usr/bin/python
# -*- coding: utf-8 -*-

from mgdpck import model



def find_obj_with_id(clazz, id_, session=None):
  with model.session_scope(session) as s:
    return s.query(clazz).filter(clazz.id==id_).all()

def find_site_with_host_name(hn, session=None):
  with model.session_scope(session) as s:
    return s.query(model.Site).filter(model.Site.hostname==hn).all()


def find_books_with_short_name(sn, session=None):
  with model.session_scope(session) as s:
    return s.query(model.Book).filter(model.Book.short_name==sn).all()
