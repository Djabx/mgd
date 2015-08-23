#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A flat dir writter
'''

import os
import logging
import mimetypes
from mgdpck import actions

logger = logging.getLogger(__name__)

class FlatWritter(actions.AbsWritter):
  @classmethod
  def get_name(cls):
    return 'flat-dir'


  def __init__(self, outdir):
    self.outdir = outdir


  def export_book(self, lsb, chapter_min, chapter_max):
    self.lsb_path = os.path.join(self.outdir, lsb.book.short_name)
    if not os.path.exists(self.lsb_path):
      os.makedirs(self.lsb_path)


  def export_cover(self, lsb):
    f_name = "{0:>03}_{0:>03}_{1}{2}".format(0, 'cover',
      mimetypes.guess_extension(lsb.image.mimetype))
    cv_path = os.path.join(self.lsb_path, f_name)
    if os.path.exists(cv_path):
      os.remove(cv_path)
    with open(cv_path, 'wb') as cvfh:
      cvfh.write(lsb.image.content)


  def export_chapter(self, ch):
    self.ch_path = os.path.join(self.lsb_path, "{:>03}".format(ch.num))
    if not os.path.exists(self.ch_path):
      os.makedirs(self.ch_path)


  def export_page(self, pa):
    f_name = "{0.num:>03}{1}".format(pa,
      mimetypes.guess_extension(pa.image.mimetype))
    pa_path = os.path.join(self.ch_path, f_name)
    if os.path.exists(pa_path):
      os.remove(pa_path)
    with open(pa_path, 'wb') as pafh:
      pafh.write(pa.image.content)


actions.register_writter(FlatWritter)
