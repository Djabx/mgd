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

class FlatWritter:
  def __init__(self):
    self.name = 'flat-dir'

  def export(self, output, to_export):
    for lsb, chapters in to_export:
      lsb_path = os.path.join(output, lsb.book.short_name)
      if lsb.cover is not None:
        if not os.path.exists(lsb_path):
          os.makedirs(lsb_path)
        cv_path = os.path.join(lsb_path, "{:>03}_{:>03}_{}{}".format(0, 0, 'cover', mimetypes.guess_extension(co.type_cover)))
        if os.path.exists(cv_path):
          os.remove(cv_path)
        with open(cv_path, 'wb') as cvfh:
          cvfh.write(lsb.cover)

      for ch in chapters:
        ch_path = os.path.join(lsb_path, "{:>03}".format(ch.num))
        if not os.path.exists(ch_path):
          os.makedirs(ch_path)

        for co in ch.contents:
          co_path = os.path.join(ch_path, "{:>03}{}".format(co.num, mimetypes.guess_extension(co.type_content)))
          if os.path.exists(co_path):
            os.remove(co_path)
          with open(co_path, 'wb') as cofh:
            cofh.write(co.content)

actions.register_writter(FlatWritter())
