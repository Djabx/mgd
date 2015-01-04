#! /usr/bin/python
# -*- coding: utf-8 -*-

from mgdpck import model
from mgdpck import data_access
import os
import unittest
import collections

SiteInfo = collections.namedtuple('SiteInfo', ('name', 'hostname'))
BookInfo = collections.namedtuple('BookInfo', ('short_name', 'full_name'))
ChapterInfo = collections.namedtuple('ChapterInfo', ('num', 'name', 'url', 'completed'))
ContentInfo = collections.namedtuple('ContentInfo', ('num', 'type_content', 'url', 'url_content'))

TEST_DB = './test.db'

# list of sites
SITES = []
# list of books
BOOKS = []
# site_id -> book_id -> chapter info
CHAPTERS = {}
# site_id -> book_id -> chapter_id -> content info
CONTENTS = {}

def __gen_data():
  for b in range(3):
    BOOKS.append(BookInfo('book {}'.format(b), 'book {} - full name'.format(b)))

  for s in range(3):
    SITES.append(SiteInfo('test {}'.format(s) , 'http://test{}.test.net'.format(s)))
    for b in range(len(BOOKS)):
      for c in range(5):
        CHAPTERS.setdefault(s, {}).setdefault(b, []).append(ChapterInfo(c, 'Chapter {}'.format(c), 'http://test{}.test.net/{}/{}'.format(s, b, c), bool(c%2)))
        for cn in range(5):
          CONTENTS.setdefault(s, {}).setdefault(b, {}).setdefault(c, []).append(ContentInfo(cn, 'pngs',
            'http://test{}.test.net/{}/{}/{}.html'.format(s, b, c, cn),
            'http://test{}.test.net/{}/{}/{}.png'.format(s, b, c, cn)))
__gen_data()

def __create_meta(path, clazz, infos, session):
  info_c = infos
  for p in path:
    info_c = info_c[p]
  info = info_c

  # first we try to find it
  with model.session_scope(session) as s:
    result = s.query(clazz).filter(getattr(clazz, info._fields[0])==info[0]).all()

    if len(result) == 1:
      # we found one and the only one we search for
      return result[0]

    elif len(result) == 0:
      instance = clazz()
      for f in info._fields:
        setattr(instance, f, getattr(info, f))
      return instance

    else:
      # fucking problem.. we found more thant 1
      raise Exception('You should not pass !')


def create_site(num_site, session):
  with model.session_scope(session) as s:
    r = __create_meta((num_site,), model.Site, SITES, s)
    s.add(r)
    s.commit()
    return r


def create_book(num_book, session):
  with model.session_scope(session) as s:
    r = __create_meta((num_book,), model.Book, BOOKS, session)
    s.add(r)
    s.commit()
    return r


def create_site_book(site, book, session):
  with model.session_scope(session) as s:
    links = data_access.find_site_book_link(site, book, s)
    new_url = '{}/{}/'.format(site.hostname, book.short_name.split()[1])
    if len(links) == 0:
      lsb = model.LinkSiteBook(site=site, book=book, url=new_url)
      s.add(lsb)
    else:
      lsb = links[0]
      lsb.url = new_url
    s.commit()
    return lsb


def create_chapter(num_site, num_book, num_chapter, lsb, session):
  with model.session_scope(session) as s:
    r = __create_meta((num_site, num_book, num_chapter), model.Chapter, CHAPTERS, session)
    r.lsb = lsb
    s.add(r)
    s.commit()
    return r


def create_content(num_site, num_book, num_chapter, num_content, session):
  with model.session_scope(session) as s:
    r = __create_meta((num_site, num_book, num_chapter, num_content), model.Content, CONTENTS, session)
    s.add(r)
    s.commit()
    return r


################################################################################
# TestModel
################################################################################
class TestModel(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    model.remove_db()
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)

  def test_create_db(self):
    self.assertFalse(os.path.exists(TEST_DB))
    e = model.create_db(TEST_DB)
    self.assertTrue(os.path.exists(TEST_DB))
    e2 = model.get_db()
    self.assertIs(e, e2)

    with self.assertRaises(Exception):
      model.create_db()


  def test_remove_db(self):
    self.assertTrue(os.path.exists(TEST_DB))
    with self.assertRaises(Exception):
      model.create_db(TEST_DB)
    model.remove_db()
    self.assertTrue(os.path.exists(TEST_DB))
    e = model.create_db(TEST_DB)
    e2 = model.get_db()
    self.assertIs(e, e2)


################################################################################
# TestSite
################################################################################
class TestSite(unittest.TestCase):

  def test_creation(self):
    with model.session_scope() as s:
      s0 = create_site(0, s)

      self.assertIsNotNone(s0.id)
      self.assertEqual(s.query(model.Site).count(), 1)

      sts = s.query(model.Site).all()
      self.assertEqual(len(sts), 1)
      st = sts[0]
      self.assertIs(st, s0)


################################################################################
# TestBook
################################################################################
class TestBook(unittest.TestCase):

  def test_creation(self):
    with model.session_scope() as s:
      b0 = create_book(0, s)

      self.assertIsNotNone(b0.id)
      bks = s.query(model.Book).filter(model.Book.id==b0.id).all()
      self.assertEqual(len(bks), 1)
      bk = bks[0]
      self.assertIs(bk, b0)


  def link_of_book_test(self, sites, book_id, session=None):
    with model.session_scope(session) as s:
      bx = s.query(model.Book).filter(model.Book.short_name==BOOKS[book_id].short_name).all()
      self.assertEqual(len(bx), 1, 'No result found...')
      b0 = bx[0]
      self.assertEqual(b0.short_name, BOOKS[book_id].short_name, 'Not the proper book founded')
      self.assertEqual(len(b0.site_links), len(sites), 'No sites founded...')

      possible_sites = set(sites)
      founded_sites = set(sl.site for sl in b0.site_links)

      intersection = possible_sites - founded_sites
      self.assertEqual(len(intersection), 0, 'Did not found all sites')
      intersection2 = founded_sites - possible_sites
      self.assertEqual(len(intersection), 0, 'Found more thant possible')


  def test_book_links(self):
    with model.session_scope() as s:
      s1 = create_site(1, s)
      s2 = create_site(2, s)

      b1 = create_book(1, s)

      create_site_book(s1, b1, s)
      create_site_book(s1, b1, s)
      create_site_book(s2, b1, s)
      s.commit()
      self.link_of_book_test((s1, s2), 1, s)

      b2 = create_book(2, s)
      create_site_book(s1, b2, s)
      create_site_book(s2, b2, s)
      s.commit()
      self.link_of_book_test((s1, s2), 2, s)


  def test_multi_links(self):
    sites_created = set()
    # we create all boks and all site and link them to each others
    with model.session_scope() as s:
      for sid in range(len(SITES)):
        sn = create_site(sid, s)
        for bid in range(len(BOOKS)):
          bm = create_book(bid, s)
          create_site_book(sn, bm, s)
          s.commit()

    with model.session_scope() as s:
      # do the same in an other session and a inner session
      for sid in range(len(SITES)):
        sn = create_site(sid, s)
        with model.session_scope(s) as s2:
          for bid in range(len(BOOKS)):
            bm = create_book(bid, s2)
            create_site_book(sn, bm, s2)
            s2.commit()


################################################################################
# TestChapter
################################################################################
class TestChapter(unittest.TestCase):

  def test_creation(self):
    with model.session_scope() as s:
      s0 = create_site(0, s)
      b0 = create_book(0, s)
      lsb0 = create_site_book(s0, b0, s)
      c0 = create_chapter(0, 0, 0, lsb0, s)

      self.assertIsNotNone(c0.id)
      chs = s.query(model.Chapter).filter(model.Chapter.id==c0.id).all()
      self.assertEqual(len(chs), 1)
      ch = chs[0]
      self.assertIs(ch, c0)


  def test_chapter_links(self):
    with model.session_scope() as s:
      s0 = create_site(0, s)
      s1 = create_site(1, s)

      b0 = create_book(0, s)
      b1 = create_book(1, s)

      lsb00 = create_site_book(s0, b0, s)
      lsb01 = create_site_book(s0, b1, s)
      lsb10 = create_site_book(s1, b0, s)
      lsb11 = create_site_book(s1, b1, s)

      c0 = create_chapter(0, 0, 0, lsb00, s)
      c1 = create_chapter(0, 0, 1, lsb00, s)
      c2 = create_chapter(0, 0, 2, lsb00, s)

      c2 = create_chapter(1, 1, 2, lsb11, s)
      c0 = create_chapter(1, 1, 0, lsb11, s)
      c1 = create_chapter(1, 1, 1, lsb11, s)
      # we add chapters to the book in an incorrect order

      s.commit()

      self.assertEqual(len(lsb11.chapters), 3)
      self.assertIs(lsb11.chapters[0], c0)
      self.assertIs(lsb11.chapters[1], c1)
      self.assertIs(lsb11.chapters[2], c2)


################################################################################
# TestContent
################################################################################
class TestContent(unittest.TestCase):

  def test_creation(self):
    with model.session_scope() as s:
      c0 = create_content(0, 0, 0, 0, s)

      self.assertIsNotNone(c0.id)
      cts = s.query(model.Content).filter(model.Content.id==c0.id).all()
      self.assertEqual(len(cts), 1)
      ct = cts[0]
      self.assertIs(ct, c0)


  def test_content_links(self):
    with model.session_scope() as s:
      s0 = create_site(0, s)
      b0 = create_book(0, s)
      lsb0 = create_site_book(s0, b0, s)
      ch0 = create_chapter(0, 0, 0, lsb0, s)

      c0 = create_content(0, 0, 0, 0, s)
      c1 = create_content(0, 0, 0, 1, s)
      c2 = create_content(0, 0, 0, 2, s)
      c3 = create_content(0, 0, 0, 3, s)
      c4 = create_content(0, 0, 0, 4, s)


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
