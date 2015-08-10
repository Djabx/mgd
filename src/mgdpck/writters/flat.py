#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A flat writter
'''

import os
import logging
import mimetypes
from mgdpck import actions

logger = logging.getLogger(__name__)

class FlatWritter(actions.DummyWritter):
  @classmethod
  def get_name(cls):
    return 'flat'


  def __init__(self, outdir, lsb, chapter_min, chapter_max):
    self.lsb_path = os.path.join(outdir, lsb.book.short_name)
    if not os.path.exists(self.lsb_path):
      os.makedirs(self.lsb_path)


  def done(self):
    pass


  def export_cover(self, lsb):
    cv_path = os.path.join(self.lsb_path, "{:>03}_{:>03}_{}{}".format(0, 0, 'cover', mimetypes.guess_extension(lsb.type_cover)))
    if os.path.exists(cv_path):
      os.remove(cv_path)
    with open(cv_path, 'wb') as cvfh:
      cvfh.write(lsb.cover)


  def export_chapter(self, ch):
    pass


  def export_content(self, co):
    co_path = os.path.join(self.lsb_path, "{:>03}_{:>03}{}".format(co.chapter.num, co.num, mimetypes.guess_extension(co.type_content)))
    if os.path.exists(co_path):
      os.remove(co_path)
    with open(co_path, 'wb') as cofh:
      cofh.write(co.content)


actions.register_writter(FlatWritter)
