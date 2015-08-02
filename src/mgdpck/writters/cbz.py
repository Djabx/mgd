#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A cbz writter
'''

from mgdpck import model
from mgdpck import actions
from mgdpck import data_access
import os
import mimetypes
import logging
import zipfile
from clint.textui import progress

logger = logging.getLogger(__name__)

class CbzWritter:
  def __init__(self):
    self.name = 'cbz'

  def export(self, output, to_export, session):
    for lsb, chapters in to_export:
      out_file = os.path.join(output, "{0}_{1.num:>03}_{2.num:>03}.cbz".format(lsb.book.short_name, chapters[0], chapters[-1]))

      length_bar = data_access.count_book_contents(lsb, session)
      with progress.Bar(label='exporting "{}" in cbz: '.format(lsb.book.short_name), expected_size=length_bar)  as bar:
        with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as out:
          if lsb.cover is not None:
            cv_path = "{:>03}_{:>03}_{}{}".format(0, 0, 'cover', mimetypes.guess_extension(lsb.type_cover))
            out.writestr(cv_path, lsb.cover)

          counter = 0

          for ch in chapters:
            ch_path = os.path.join(lsb.book.short_name, "{:>03}".format(ch.num))

            for co in ch.contents:
              co_path = os.path.join(ch_path, "{:>03}{}".format(co.num, mimetypes.guess_extension(co.type_content)))
              out.writestr(co_path, co.content)
              counter += 1
              bar.show(counter)
              session.expire(co)
            session.expire(ch)

actions.register_writter(CbzWritter())
