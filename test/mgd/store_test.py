#! /usr/bin/python
# -*- coding: utf-8 -*-

import mgd.store as store
import os
import unittest
import collections

SiteInfo = collections.namedtuple('SiteInfo', ('name', 'hostname'))
BookInfo = collections.namedtuple('BookInfo', ('short_name', 'full_name'))
ChapterInfo = collections.namedtuple('ChapterInfo', ('num', 'name', 'url', 'completed'))
ContentInfo = collections.namedtuple('ContentInfo', ('num', 'type_content', 'url'))

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
  BookInfo('book 3', 'book 3 - full name')
)

CHAPTERS = (
  ChapterInfo(1, 'Chapter 1', 'http://test1.test.net/1/1', True),
  ChapterInfo(2, 'Chapter 2', 'http://test1.test.net/1/2', False),
  ChapterInfo(3, 'Chapter 3', 'http://test1.test.net/1/3', False),
  ChapterInfo(4, 'Chapter 4', 'http://test1.test.net/1/3', False),
  ChapterInfo(5, 'Chapter 5', 'http://test1.test.net/1/3', False)
)

CONTENTS = (
  ContentInfo(1, 'pngs', 'http://test1.test.net/1/1/1'),
  ContentInfo(2, 'png', 'http://test1.test.net/1/1/2'),
  ContentInfo(3, 'png', 'http://test1.test.net/1/1/3'),
  ContentInfo(4, 'png', 'http://test1.test.net/1/1/4'),
  ContentInfo(5, 'png', 'http://test1.test.net/1/1/5')
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


def create_chapter(num_chapter, session=None):
  return __create_meta(num_chapter, store.Chapter, CHAPTERS, session)


def create_content(num_book, session=None):
  return __create_meta(num_book, store.Content, CONTENTS, session)


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


################################################################################
# TestSite
################################################################################
class TestSite(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)
    store.create_db(TEST_DB)


  @classmethod
  def tearDownClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)


  def test_creation(self):
    s = store.get_session()
    s0 = create_site(0, s)

    self.assertIsNotNone(s0.id)
    self.assertEqual(s.query(store.Site).count(), 1)

    sts = s.query(store.Site).all()
    self.assertEqual(len(sts), 1)
    st = sts[0]
    self.assertIs(st, s0)



################################################################################
# TestBook
################################################################################
class TestBook(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)
    store.create_db(TEST_DB)


  @classmethod
  def tearDownClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)


  def test_creation(self):
    s = store.get_session()
    b0 = create_book(0, s)

    self.assertIsNotNone(b0.id)
    bks = s.query(store.Book).filter(store.Book.id==b0.id).all()
    self.assertEqual(len(bks), 1)
    bk = bks[0]
    self.assertIs(bk, b0)


  def test_book_links(self):
    s = store.get_session()
    s1 = create_site(1, s)
    s2 = create_site(2, s)

    def test_link_of_book(book_id):
      bx = s.query(store.Book).filter(store.Book.short_name==BOOKS[book_id].short_name).all()
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



################################################################################
# TestChapter
################################################################################
class TestChapter(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)
    store.create_db(TEST_DB)


  @classmethod
  def tearDownClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)


  def test_creation(self):
    s = store.get_session()
    c0 = create_chapter(0, s)

    self.assertIsNotNone(c0.id)
    chs = s.query(store.Chapter).filter(store.Chapter.id==c0.id).all()
    self.assertEqual(len(chs), 1)
    ch = chs[0]
    self.assertIs(ch, c0)


  def test_chapter_links(self):
    s = store.get_session()
    s0 = create_site(0, s)
    s1 = create_site(1, s)

    b0 = create_book(0, s)
    b1 = create_book(1, s)

    s0.books.append(b0)
    s0.books.append(b1)
    s1.books.append(b0)

    c0 = create_chapter(0, s)
    c0.site = s0
    c1 = create_chapter(1, s)
    c1.site = s0
    c2 = create_chapter(2, s)
    c2.site = s0

    # we add chapters to the book in an incorrect order
    b1.chapters.append(c1)
    c2.book = b1
    c0.book = b1

    s.commit()

    self.assertEqual(len(b1.chapters), 3)
    self.assertIs(b1.chapters[0], c0)
    self.assertIs(b1.chapters[1], c1)
    self.assertIs(b1.chapters[2], c2)


################################################################################
# TestContent
################################################################################
class TestContent(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)
    store.create_db(TEST_DB)


  @classmethod
  def tearDownClass(cls):
    store.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)


  def test_creation(self):
    s = store.get_session()
    c0 = create_content(0, s)

    self.assertIsNotNone(c0.id)
    cts = s.query(store.Content).filter(store.Content.id==c0.id).all()
    self.assertEqual(len(cts), 1)
    ct = cts[0]
    self.assertIs(ct, c0)


  def test_content_links(self):
    s = store.get_session()
    ch0 = create_chapter(0, s)

    c0 = create_content(0, s)
    c1 = create_content(1, s)
    c2 = create_content(2, s)
    c3 = create_content(3, s)
    c4 = create_content(4, s)


    # we add content to the chapter in an incorrect order
    ch0.contents.append(c3)
    c2.chapter = ch0
    c0.chapter = ch0
    c1.chapter = ch0
    c4.chapter = ch0

    s.commit()

    self.assertEqual(len(ch0.contents), 5)
    self.assertIs(ch0.contents[0], c0)
    self.assertIs(ch0.contents[1], c1)
    self.assertIs(ch0.contents[2], c2)
    self.assertIs(ch0.contents[3], c3)
    self.assertIs(ch0.contents[4], c4)



if __name__ == '__main__':
  unittest.main()
