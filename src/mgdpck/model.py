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
from sqlalchemy.orm import sessionmaker, scoped_session
from mgdpck import logging_util
from mgdpck import _version
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

URL_LENGTH = 1024

DEFAULT_FILE_DB_NAME='mgd_store.db'
DEFAULT_STORE_MANAGER=None

def clean_path(p, default=None):
  op = os.path
  p = p if p is not None else DEFAULT_FILE_DB_NAME
  return op.abspath(op.realpath(op.normpath(p)))


class StoreManager:
  def __init__(self, file_db_name=None, default=False):
    self.file_db_name = clean_path(file_db_name)
    self.db = None
    self.session_maker = None
    self.session_scoped = None

    if default:
      global DEFAULT_STORE_MANAGER
      DEFAULT_STORE_MANAGER = self


  def get_db_version(self):
    import sqlite3
    conn = sqlite3.connect(self.file_db_name)
    c = conn.cursor()
    c.execute("select version, version_full from version where id = 1")
    result = c.fetchone()
    if result is None:
      # TODO: create some real exceptions
      raise Exception('Unable to find version informations')
    # we ignore the full version
    version, _ = result
    return version


  def is_db_version_compatible(self):
    logger.debug('checkin version of db file: "%s"', self.file_db_name)

    db_version = get_db_version(self.file_db_name)
    logger.debug('get db version: "%s"', db_version)

    current_version = _version.get_versions()['version']
    logger.debug('get current version: "%s"', current_version)

    if len(db_version) == 0 or len(current_version) == 0:
      # it's the case in dev... so we do not care
      return True

    if current_version == 'unknown':
      # it's an other case in dev so we do not care
      return True

    from distutils.version import LooseVersion
    dbv = tuple(LooseVersion(db_version).version[:2])
    crv = tuple(LooseVersion(current_version).version[:2])
    return dbv == crv


  def store_version(self):
    with self.session_scope() as s:
      v = Version()
      v.id = 1
      v.version = _version.get_versions()['version']
      v.version_full = _version.get_versions()['full']
      vcreation_date = datetime.datetime.now()
      s.add(v)
      s.commit()


  def create_db(self, force=False, force_init=False):
    if self.db is not None and force is False:
      logger.info('db file already configured')
      # TODO: create some real exceptions
      raise Exception('Engine already exist !')

    init_db = True
    if os.path.exists(self.file_db_name):
      init_db = force_init
      if not self.is_db_version_compatible():
        logger.error('The db file is in version: "%(old_version)s" maybe incompatible with the expected version: "%(new_version)s"',
          {'old_version':self.get_db_version(),
          'new_version':_version.get_versions()['version']})
        # TODO: create some real exceptions
        raise Exception('Incompatible versions')
    else:
      parent_dir = os.path.dirname(self.file_db_name)
      if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    self.db = create_engine('sqlite:///' + self.file_db_name)
    logger.info('Creating sqlengine')
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    if init_db:
      Base.metadata.create_all(self.db)
      self.store_version()
    return db


  def get_db(self):
    return self.db


  def get_session(self):
    if self.session_maker is None:
      sm = self.session_maker = sessionmaker()
      sm.configure(bind=self.db)
      self.session_scoped = scoped_session(sm)

    return self.session_scoped()


  @contextmanager
  def session_scope(self, session=None):
    """Provide a transactional scope around a series of operations."""
    s = session
    if session is None:
      s = self.get_session()
    try:
      with s.no_autoflush:
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
    return '<Site {} "{}">'.format(self.id, self.name)


################################################################################
class Book(Base):
  __tablename__ = 'book'
  id = Column(Integer, primary_key=True)
  full_name = Column(String(250))
  short_name = Column(String(50), nullable=False, index=True)

  __table_args__ = (
      UniqueConstraint('short_name'),
  )

  def __str__(self):
    return '<Book {} "{}">'.format(self.id, self.short_name)


################################################################################
# because the same book can be on different sites
class LinkSiteBook(Base):
  __tablename__ = 'link_site_book'
  id = Column(Integer, primary_key=True)
  site_id = Column(Integer, ForeignKey('site.id'), index=True)
  book_id = Column(Integer, ForeignKey('book.id'), index=True)
  url = Column(String(URL_LENGTH), nullable=False)
  followed = Column(Boolean, default=False)
  url_cover = Column(String(URL_LENGTH), nullable=True) # the cover url
  cover = Column(LargeBinary(), nullable=True)
  type_cover = Column(String(50), nullable=True) # type of cover
  min_chapter = Column(Integer)
  max_chapter = Column(Integer)

  __table_args__ = (
      UniqueConstraint('site_id', 'book_id'),
  )

  book = relationship("Book", backref="site_links")

  chapters = relationship(
    'Chapter',
    lazy="dynamic",
    order_by='Chapter.num'
  )

  def __str__(self):
    return '<LinkSiteBook {} {} {} {} >'.format(self.id, self.site, self.book, self.followed)


################################################################################
class Chapter(Base):
  __tablename__ = 'chapter'
  id = Column(Integer, primary_key=True)
  lsb_id = Column(Integer, ForeignKey('link_site_book.id'), index=True)
  num = Column(Integer, nullable=False, index=True) # chapter number in the serie

  url = Column(String(URL_LENGTH), nullable=False)
  completed = Column(Boolean(), default=False) # if we download all the chapter or not
  name = Column(String(250)) # the chapter name

  __table_args__ = (
      UniqueConstraint('lsb_id', 'num'),
  )

  lsb = relationship(LinkSiteBook)
  contents = relationship(
    'Content',
    order_by='Content.num')

  def __repr__(self):
    return '<Chapter {} \#{} of {}>'.format(self.id, self.num,
      self.lsb if self.lsb is not None else '"No book"')



################################################################################
class Content(Base):
  __tablename__ = 'content'
  id = Column(Integer, primary_key=True)
  chapter_id = Column(Integer, ForeignKey('chapter.id'), index=True)

  url = Column(String(URL_LENGTH), nullable=False) # the page url
  url_content = Column(String(URL_LENGTH), nullable=False) # the content url
  base_url_content = Column(String(URL_LENGTH), nullable=False, index=True) # the base url content url
  num = Column(Integer, nullable=False, index=True) # page number in the chapter
  content = Column(LargeBinary())
  type_content = Column(String(50)) # type of content

  __table_args__ = (
      UniqueConstraint('chapter_id', 'num'),
  )

  chapter = relationship(Chapter)

  def __repr__(self):
    return '<Content {} \#{} of {}>'.format(self.id, self.num,
    self.chapter if self.chapter is not None else '"No chapter found"')
