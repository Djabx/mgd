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
  print('Creating sqlengine')
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
class Site(Base):
  __tablename__ = 'site'
  id = Column(Integer, primary_key=True)
  name = Column(String(250))
  hostname = Column(String(250))

  books = relationship(
        'Book',
        secondary='link_site_book'
  )


  def __repr__(self):
    return 'Site <{}"{}">'.format(self.id, self.name)


################################################################################
class Book(Base):
  __tablename__ = 'book'
  id = Column(Integer, primary_key=True)
  full_name = Column(String(250))
  short_name = Column(String(50))

  sites = relationship(
    'Site',
    secondary='link_site_book'
  )
  chapters = relationship(
    'Chapter',
    order_by='Chapter.num'
  )


  def __repr__(self):
    return 'Book <{}"{}">'.format(self.id, self.short_name)


################################################################################
# because the same book can be on different sites
class LinkSiteBook(Base):
  __tablename__ = 'link_site_book'
  site_id = Column(Integer, ForeignKey('site.id'), primary_key=True)
  book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)


################################################################################
class Chapter(Base):
  __tablename__ = 'chapter'
  id = Column(Integer, primary_key=True)
  site_id = Column(Integer, ForeignKey('site.id'))
  book_id = Column(Integer, ForeignKey('book.id'))

  url = Column(String(2048), nullable=False)
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

  url = Column(String(2048), nullable=False)
  num = Column(Integer, nullable=False) # page number in the chapter
  content = Column(LargeBinary())
  type_content = Column(String(50), nullable=False) # type of content

  chapter = relationship(Chapter)

  def __repr__(self):
    return 'Content <{} \#{} of {}>'.format(self.id, self.num,
    self.chapter if self.chapter is not None else '"No chapter found"')
