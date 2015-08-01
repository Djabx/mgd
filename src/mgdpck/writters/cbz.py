#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A cbz writter
'''

from mgdpck import actions
import os
import mimetypes
import logging
import zipfile

logger = logging.getLogger(__name__)

class CbzWritter:
  def __init__(self):
    self.name = 'cbz'

  def export(self, output, to_export):
    for lsb, chapters in to_export:
      logger.info('exporting: %s in cbz', lsb.book.short_name)
      out_file = os.path.join(output, "{0}_{1.num:>03}_{2.num:>03}.cbz".format(lsb.book.short_name, chapters[0], chapters[-1]))

      with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as out:
        if lsb.cover is not None:
          cv_path = "{:>03}_{:>03}_{}{}".format(0, 0, 'cover', mimetypes.guess_extension(lsb.type_cover))
          out.writestr(cv_path, lsb.cover)

        for ch in chapters:
          ch_path = os.path.join(lsb.book.short_name, "{:>03}".format(ch.num))

          for co in ch.contents:
            co_path = os.path.join(ch_path, "{:>03}{}".format(co.num, mimetypes.guess_extension(co.type_content)))
            out.writestr(co_path, co.content)

actions.register_writter(CbzWritter())
