#! /usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
from contextlib import contextmanager
from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

__DB = None
__SESSION_MAKER = None

def create_db(file_name='mdg.store', force=False):
  global __DB
  if __DB is not None and force is False:
    # TODO: create some real exceptions
    raise Exception('Engine already exist !')
  db = __DB = create_engine('sqlite:///' + file_name)
  # Create all tables in the engine. This is equivalent to "Create Table"
  # statements in raw SQL.
  Base.metadata.create_all(db)
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
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def run_my_program():
    with session_scope() as session:
        ThingOne().go(session)
        ThingTwo().go(session)



################################################################################
# Model
################################################################################
class Site(Base):
  __tablename__ = 'site'
  id = Column(Integer, primary_key=True)
  name = Column(String(250))
  hostname = Column(String(250))

  mangas = relationship(
        'Manga',
        secondary='site_manga_link'
  )

  @classmethod
  def find_with_hostname(cls, hn):
    with session_scope() as s:
      result = s.query(Site).filter(Site.hostname==hn).all()
      result_l = len(result)
      if result_l > 1:
        # too much result
        return None
      elif result_l == 1:
        # ok return
        return result[0]
      else:
        # no result
        return None


class Manga(Base):
  __tablename__ = 'manga'
  id = Column(Integer, primary_key=True)
  name = Column(String(250))
  sites = relationship(
        Site,
        secondary='site_manga_link'
  )

# because the same manga can be on different sites
class SiteMangaLink(Base):
    __tablename__ = 'site_manga_link'
    site_id = Column(Integer, ForeignKey('site.id'), primary_key=True)
    manga_id = Column(Integer, ForeignKey('manga.id'), primary_key=True)


class Chapter(Base):
  __tablename__ = 'chapter'
  __table_args__ = (
      UniqueConstraint('site_id', 'manga_id', 'num'),
  )
  id = Column(Integer, primary_key=True)
  num = Column(Integer) # chapter number in the serie
  site_id = Column(Integer, ForeignKey('site.id'))
  manga_id = Column(Integer, ForeignKey('manga.id'))
  url = Column(String(2048), nullable=False)
  name = Column(String(250), nullable=False)
  done = Column(Boolean()) # if we download the chapter or not

  manga = relationship(Manga)
  site = relationship(Site)
  images = relationship('Image')


class Image(Base):
  __tablename__ = 'image'
  id = Column(Integer, primary_key=True)
  url = Column(String(2048), nullable=False)
  img = Column(LargeBinary())
  num = Column(Integer, nullable=False) # page number in the chapter
  chapter_id = Column(Integer, ForeignKey('chapter.id'))
  type_mime = Column(String(50), nullable=False)

  chapter = relationship(Chapter)
