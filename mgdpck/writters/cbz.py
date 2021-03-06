#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A cbz writter
'''

from mgdpck import actions
import os
import mimetypes
import zipfile

class CbzWritter(actions.AbsWritter):
  @classmethod
  def get_name(cls):
    return 'cbz'


  def __init__(self, outdir):
    self.outdir = outdir
    self.out = None


  def done(self):
    if self.out:
      self.out.close()


  def export_book(self, lsb, chapter_min, chapter_max):
    self.out_file = os.path.join(self.outdir, "{0.book.short_name}_{1.num:>03}_{2.num:>03}.cbz".format(lsb, chapter_min, chapter_max))
    self.out = zipfile.ZipFile(self.out_file, "w", compression=zipfile.ZIP_DEFLATED)


  def export_cover(self, lsb):
    cv_path = "{0:>03}_{0:>03}_{1}{2}".format(0,  'cover',
      mimetypes.guess_extension(lsb.image.mimetype))
    self.out.writestr(cv_path, lsb.image.content)


  def export_chapter(self, ch):
    pass


  def export_page(self, pa):
    pa_path = "{0.chapter.num:>03}_{0.num:>03}{1}".format(pa,
        mimetypes.guess_extension(pa.image.mimetype))
    self.out.writestr(pa_path, pa.image.content)


actions.register_writter(CbzWritter)
