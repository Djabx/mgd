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

class FlatWritter:
  def __init__(self):
    self.name = 'flat'

  def export(self, output, to_export, session):
    for lsb, chapters in to_export:
      lsb_path = os.path.join(output, lsb.book.short_name)
      if lsb.cover is not None:
        cv_path = os.path.join(lsb_path, "{:>03}_{:>03}_{}{}".format(0, 0, 'cover', mimetypes.guess_extension(co.type_cover)))
        if os.path.exists(cv_path):
          os.remove(cv_path)
        with open(cv_path, 'wb') as cvfh:
          cvfh.write(lsb.cover)

      length_bar = data_access.count_book_contents(lsb, session)
      with progress.Bar(label='exporting "{}" in flat: '.format(lsb.book.short_name), expected_size=length_bar)  as bar:
        for ch in chapters:
          if not os.path.exists(lsb_path):
            os.makedirs(lsb_path)

          for co in ch.contents:
            co_path = os.path.join(lsb_path, "{:>03}_{:>03}{}".format(ch.num, co.num, mimetypes.guess_extension(co.type_content)))
            if os.path.exists(co_path):
              os.remove(co_path)
            with open(co_path, 'wb') as cofh:
              cofh.write(co.content)
            counter += 1
            bar.show(counter)
          session.expunge(ch)

actions.register_writter(FlatWritter())
