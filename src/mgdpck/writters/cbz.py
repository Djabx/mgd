#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
A cbz writter
'''

from mgdpck import info
import os
import mimetypes
import logging
import zipfile

logger = logging.getLogger(__name__)

class CbzWritter:
  def __init__(self):
    self.name = 'cbz'

  def export(self, output, chapters):
    books = {}
    for c in chapters:
      books.setdefault(c.lsb.book.short_name, []).append(c)

    for book_name, chs in books.items():
      logger.debug('exporting: %s in cbz', book_name)
      out_file = os.path.join(output, "{0}_{1.num:>03}_{2.num:>03}.cbz".format(book_name, chs[0], chs[-1]))

      with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as out:
        for ch in chs:
          ch_path = os.path.join(ch.lsb.book.short_name, "{:>03}".format(ch.num))

          for co in ch.contents:
            co_path = os.path.join(ch_path, "{:>03}{}".format(co.num, mimetypes.guess_extension(co.type_content)))
            out.writestr(co_path, co.content)

info.register_writter(CbzWritter())
