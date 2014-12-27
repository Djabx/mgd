#! /usr/bin/python
# -*- coding: utf-8 -*-

import mgd.store as store
import os
import unittest


TEST_DB = './test.db'

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


class TestSite(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    store.create_db(TEST_DB, force=True)

  def test_creation(self):
    si = store.Site()
    si.name = 'test'
    si.hostname = 'test.test.net'

    self.assertIsNone(si.id)

    s = store.get_session()
    s.add(si)
    s.commit()

    self.assertIsNotNone(si.id)
    self.assertEqual(s.query(store.Site).count(), 1)

    sts = s.query(store.Site).all()
    self.assertEqual(len(sts), 1)
    st = sts[0]
    self.assertEqual(st.id, si.id)
    self.assertEqual(st.name, si.name)
    self.assertEqual(st.hostname, si.hostname)

  def test_find_with_hostname(self):
    s1 = store.Site()
    s1.name = 'test1'
    s1.hostname = 'test1.net'

    s2 = store.Site()
    s2.name = 'test2'
    s2.hostname = 'test2.net'

    s = store.get_session()
    s.add(s1)
    s.add(s2)
    s.commit()

    store.Site.find_with_hostname('test1')


if __name__ == '__main__':
  unittest.main()
