#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A flat writter
'''

import os
import logging
import mimetypes
from mgdpck import info

logger = logging.getLogger(__name__)

class FlatWritter:
  def __init__(self):
    self.name = 'flat'

  def export(self, output, chapters):
    for ch in chapters:
      ch_path = os.path.join(output, ch.lsb.book.short_name)
      if not os.path.exists(ch_path):
        os.makedirs(ch_path)

      for co in ch.contents:
        co_path = os.path.join(ch_path, "{:>03}_{:>03}{}".format(ch.num, co.num, mimetypes.guess_extension(co.type_content)))
        if os.path.exists(co_path):
          os.remove(co_path)
        with open(co_path, 'wb') as cofh:
          cofh.write(co.content)

info.register_writter(FlatWritter())
