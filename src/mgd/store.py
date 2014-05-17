#! /usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Site(Base):
  __tablename__ = 'site'
  id = Column(Integer, primary_key=True)
  name = Column(String(250))
  hostname = Column(String(250))
  mangas = relationship(
        'Manga',
        secondary='site_manga_link'
  )


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
  site = relationship(site)



class Image(Base):
  __tablename__ = 'image'
  id = Column(Integer, primary_key=True)
  url = Column(String(2048), nullable=False)
  img = Column(LargeBinary())
  num = Column(Integer, nullable=False) # page number in the chapter
  chapter_id = Column(Integer, ForeignKey('chapter.id'))

  chapter = relationship(Chapter)




# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///store.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
