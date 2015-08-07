#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A cbz writter
'''

from mgdpck import actions
import os
import mimetypes
import zipfile

class CbzWritter(actions.DummyWritter):
  @classmethod
  def get_name(cls):
    return 'cbz'

  def __init__(self, outdir, lsb, chapter_min, chapter_max):
    self.out_file = os.path.join(outdir, "{0.book.short_name}_{1.num:>03}_{2.num:>03}.cbz".format(lsb, chapter_min, chapter_max))
    self.out = zipfile.ZipFile(self.out_file, "w", compression=zipfile.ZIP_DEFLATED)

  def done(self):
    self.out.close()

  def export_cover(self, lsb):
    cv_path = "{:>03}_{:>03}_{}{}".format(0, 0, 'cover', mimetypes.guess_extension(lsb.type_cover))
    self.out.writestr(cv_path, lsb.cover)

  def export_chapter(self, ch):
    self.ch_path = os.path.join(ch.lsb.book.short_name, "{:>03}".format(ch.num))

  def export_content(self, co):
    co_path = os.path.join(self.ch_path, "{:>03}{}".format(co.num, mimetypes.guess_extension(co.type_content)))
    self.out.writestr(co_path, co.content)

actions.register_writter(CbzWritter)
