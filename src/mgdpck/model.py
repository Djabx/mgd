#! /usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
import datetime
from contextlib import contextmanager
from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary, UniqueConstraint, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mgdpck import logging_util
from mgdpck import _version
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

__DB = None
__SESSION_MAKER = None
URL_LENGTH = 2048


def get_db_version(file_name):
  import sqlite3
  conn = sqlite3.connect(file_name)
  c = conn.cursor()
  c.execute("select version, version_full from version where id = 1")
  result = c.fetchone()
  if result is None:
    # TODO: create some real exceptions
    raise Exception('Unable to find version informations')
  # we ignore the full version
  version, _ = result
  return version


def is_db_version_compatible(file_name):
  logger.debug('checkin version of db file: "%s"', file_name)

  db_version = get_db_version(file_name)
  logger.debug('get db version: "%s"', db_version)

  current_version = _version.get_versions()['version']
  logger.debug('get current version: "%s"', current_version)

  if len(db_version) == 0 or len(current_version) == 0:
    # it's the case in dev... so we do not care
    return True

  from distutils.version import LooseVersion
  dbv = tuple(LooseVersion(db_version).version[:2])
  crv = tuple(LooseVersion(current_version).version[:2])
  return dbv == crv



def store_version():
  with session_scope() as s:
    v = Version()
    v.id = 1
    v.version = _version.get_versions()['version']
    v.version_full = _version.get_versions()['full']
    vcreation_date = datetime.datetime.now()
    s.add(v)
    s.commit()


def create_db(file_name='mdg.store', force=False):
  global __DB
  if __DB is not None and force is False:
    logger.info('db file already configured')
    # TODO: create some real exceptions
    raise Exception('Engine already exist !')

  init_db = True
  if os.path.exists(file_name):
    init_db = False
    if not is_db_version_compatible(file_name):
      logger.error('The db file is in version: "%(old_version)s" maybe incompatible with the expected version: "%(new_version)s"',
        old_version=get_db_version(),
        new_version=get_versions()['version'])
      # TODO: create some real exceptions
      raise Exception('Incompatible versions')
  else:
    parent_dir = os.path.dirname(file_name)
    if not os.path.exists(parent_dir):
      os.makedirs(parent_dir)

  db = __DB = create_engine('sqlite:///' + file_name)
  logger.info('Creating sqlengine')
  # Create all tables in the engine. This is equivalent to "Create Table"
  # statements in raw SQL.
  if init_db:
    Base.metadata.create_all(db)
    store_version()
  return db


def get_db():
  return __DB


def get_session():
  global __SESSION_MAKER
  db = get_db()
  if __SESSION_MAKER is None:
    sm =__SESSION_MAKER = sessionmaker()
    sm.configure(bind=db)

  return __SESSION_MAKER()


def remove_db():
  global __DB, __SESSION_MAKER
  __DB = None
  __SESSION_MAKER = None


@contextmanager
def session_scope(session=None):
  """Provide a transactional scope around a series of operations."""
  s = session
  if session is None:
    s = get_session()
  try:
    yield s
    if session is None:
      s.commit()
  except:
    s.rollback()
    raise
  finally:
    if session is None:
      s.close()


################################################################################
# Model
################################################################################

################################################################################
class Version(Base):
  __tablename__ = 'version'
  id = Column(Integer, primary_key=True)
  version = Column(String(250)) # long string version
  version_full = Column(String(250)) # full tag version
  creation_date = Column(DateTime)


################################################################################
class Site(Base):
  __tablename__ = 'site'
  id = Column(Integer, primary_key=True)
  name = Column(String(250))
  hostname = Column(String(250))

  books = relationship("LinkSiteBook", backref="site")

  __table_args__ = (
      UniqueConstraint('hostname'),
  )

  def __repr__(self):
    return 'Site <{} "{}">'.format(self.id, self.name)


################################################################################
class Book(Base):
  __tablename__ = 'book'
  id = Column(Integer, primary_key=True)
  full_name = Column(String(250))
  short_name = Column(String(50), nullable=False)

  __table_args__ = (
      UniqueConstraint('short_name'),
  )

  chapters = relationship(
    'Chapter',
    order_by='Chapter.num'
  )

  def __str__(self):
    return 'Book <{} "{}">'.format(self.id, self.short_name)


################################################################################
# because the same book can be on different sites
class LinkSiteBook(Base):
  __tablename__ = 'link_site_book'
  site_id = Column(Integer, ForeignKey('site.id'), primary_key=True)
  book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
  url = Column(String(URL_LENGTH), nullable=False)

  book = relationship("Book", backref="site_links")

  def __str__(self):
    return 'LinkSiteBook <{} {} "{}">'.format(self.site, self.book, self.url)


################################################################################
class Chapter(Base):
  __tablename__ = 'chapter'
  id = Column(Integer, primary_key=True)
  site_id = Column(Integer, ForeignKey('site.id'))
  book_id = Column(Integer, ForeignKey('book.id'))

  url = Column(String(URL_LENGTH), nullable=False)
  completed = Column(Boolean(), default=False) # if we download all the chapter or not
  num = Column(Integer, nullable=False) # chapter number in the serie
  name = Column(String(250), nullable=False) # the chapter name

  __table_args__ = (
      UniqueConstraint('site_id', 'book_id', 'num'),
  )

  book = relationship(Book)
  site = relationship(Site)
  contents = relationship(
    'Content',
    order_by='Content.num')

  def __repr__(self):
    return 'Chapter <{} \#{} of {}>'.format(self.id, self.num,
    self.book if self.book is not None else '"No book"')



################################################################################
class Content(Base):
  __tablename__ = 'content'
  id = Column(Integer, primary_key=True)
  chapter_id = Column(Integer, ForeignKey('chapter.id'))

  url = Column(String(URL_LENGTH), nullable=False) # the page url
  url_content = Column(String(URL_LENGTH), nullable=False) # the content url
  num = Column(Integer, nullable=False) # page number in the chapter
  content = Column(LargeBinary())
  type_content = Column(String(50), nullable=False) # type of content

  chapter = relationship(Chapter)

  def __repr__(self):
    return 'Content <{} \#{} of {}>'.format(self.id, self.num,
    self.chapter if self.chapter is not None else '"No chapter found"')
