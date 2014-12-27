#! /usr/bin/python
# -*- coding: utf-8 -*-

import mgd.store as store
import os
import unittest
import collections

SiteInfo = collections.namedtuple('SiteInfo', ('name', 'hostname'))
BookInfo = collections.namedtuple('BookInfo', ('short_name', 'full_name'))

TEST_DB = './test.db'

SITES = (
  # name / hostname
  SiteInfo('test1', 'test1.test.net'),
  SiteInfo('test2', 'test2.test.net'),
  SiteInfo('test3', 'test3.test.net')
)

BOOKS = (
  BookInfo('book 1', 'book 1 - full name'),
  BookInfo('book 2', 'book 2 - full name'),
  BookInfo('book 3', 'book 3 - full name'),
)

def __create_meta(num, clazz, infos, session=None):
  info = infos[num]

  # first we try to find it
  with store.session_scope(session) as s:
    result = s.query(clazz).filter(getattr(clazz, info._fields[0])==info[0]).all()

    if len(result) == 1:
      # we found one and the only one we search for
      return result[0]

    elif len(result) == 0:
      instance = clazz()
      for f in info._fields:
        setattr(instance, f, getattr(info, f))
      s.add(instance)
      s.commit()
      return instance

    else:
      # fucking problem.. we found more thant 1
      raise Exception('You should not pass !')

def create_site(num_site, session=None):
  return __create_meta(num_site, store.Site, SITES, session)


def create_book(num_book, session=None):
  return __create_meta(num_book, store.Book, BOOKS, session)


################################################################################
# TestStore
################################################################################
class TestStore(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)

  def test_create_db(self):
    self.assertFalse(os.path.exists(TEST_DB))
    e = store.create_db(TEST_DB)
    self.assertTrue(os.path.exists(TEST_DB))
    e2 = store.get_db()
    self.assertIs(e, e2)

    with self.assertRaises(Exception):
      store.create_db()

  def test_remove_db(self):
    self.assertTrue(os.path.exists(TEST_DB))
    with self.assertRaises(Exception):
      store.create_db(TEST_DB)
    store.remove_db()
    self.assertTrue(os.path.exists(TEST_DB))
    e = store.create_db(TEST_DB)
    e2 = store.get_db()
    self.assertIs(e, e2)

  @classmethod
  def tearDownClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)


################################################################################
# TestSite
################################################################################
class TestSite(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    store.create_db(TEST_DB, force=True)

  def test_creation(self):
    s = store.get_session()
    s0 = create_site(0, s)

    self.assertIsNotNone(s0.id)
    self.assertEqual(s.query(store.Site).count(), 1)

    sts = s.query(store.Site).all()
    self.assertEqual(len(sts), 1)
    st = sts[0]
    self.assertEqual(st.id, s0.id)
    self.assertEqual(st.name, s0.name)
    self.assertEqual(st.hostname, s0.hostname)


  def test_find_with_hostname(self):
    s = store.get_session()
    s1 = create_site(1, s)
    s2 = create_site(2, s)

    sx = store.Site.find_with_hostname(SITES[1].hostname, s)
    self.assertEqual(len(sx), 1, 'No result found...')

    s0 = sx[0]
    self.assertEqual(s0.id, s1.id)
    self.assertEqual(s0.name, s1.name)
    self.assertEqual(s0.hostname, s1.hostname)

  @classmethod
  def tearDownClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)

################################################################################
# TestBook
################################################################################
class TestBook(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    store.create_db(TEST_DB, force=True)

  def test_creation(self):
    s = store.get_session()
    b0 = create_book(0, s)

    self.assertIsNotNone(b0.id)
    self.assertEqual(s.query(store.Book).count(), 1)

    bks = s.query(store.Book).all()
    self.assertEqual(len(bks), 1)
    bk = bks[0]
    self.assertEqual(bk.id, b0.id)
    self.assertEqual(bk.short_name, b0.short_name)
    self.assertEqual(bk.full_name, b0.full_name)


  def test_find_with_short_name(self):
    s = store.get_session()
    bx = store.Book.find_with_short_name(BOOKS[0].short_name, s)
    self.assertEqual(len(bx), 1, 'No result found...')

    b0 = bx[0]
    self.assertEqual(b0.short_name, BOOKS[0].short_name)
    self.assertEqual(b0.full_name, BOOKS[0].full_name)
    self.assertEqual(b0.id, 1)


  def test_site_links(self):
    s = store.get_session()
    s1 = create_site(1, s)
    s2 = create_site(2, s)

    def test_link_of_book(book_id):
      bx = store.Book.find_with_short_name(BOOKS[book_id].short_name, s)
      self.assertEqual(len(bx), 1, 'No result found...')
      b0 = bx[0]
      self.assertEqual(b0.short_name, BOOKS[book_id].short_name, 'Not the proper book founded')
      print("foudned sites: {}", b0.sites)
      self.assertEqual(len(b0.sites), 2, 'No sites founded...')

      possible_sites = set((s1, s2))
      founded_sites = set(b0.sites)

      intersection = possible_sites - founded_sites
      self.assertEqual(len(intersection), 0, 'Did not found all sites')
      intersection2 = founded_sites - possible_sites
      self.assertEqual(len(intersection), 0, 'Found more thant possible')


    b1 = create_book(1, s)
    b1.sites.append(s1)
    b1.sites.append(s2)
    s.commit()
    test_link_of_book(1)

    b2 = create_book(2)
    s1.books.append(b2)
    s2.books.append(b2)
    s.commit()
    test_link_of_book(2)


if __name__ == '__main__':
  unittest.main()
