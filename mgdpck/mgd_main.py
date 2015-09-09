#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import operator
import itertools
import webbrowser

from mgdpck import logging_util
# init logger first
logging_util.init_logger()
logging_util.add_except_name('run_script')
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from mgdpck import model
from mgdpck import actions
from mgdpck import data_access
# init of all readers
from mgdpck.readers import *
from mgdpck.writters import *

def _get_parser_sync_level(parser):
  parser.add_argument('-sm', '--meta',
    action='store_true', dest='sync_meta',
    help='Sync and update meta data (list of books, etc.)')

  parser.add_argument('-ss', '--struct',
    action='store_true', dest='sync_struct',
    help='Sync structures of followed books (chapters, page structure etc.)')

  parser.add_argument('-si', '--images',
    action='store_true', dest='sync_images',
    help='Sync all images')

  parser.add_argument('-sa', '--all',
    action='store_true', dest='sync_all', default=True,
    help='Sync meta data, structures and images; equal to -sm -ss -si (default: True with action "follow" or "export")')

  parser.add_argument('-sn', '--none',
    action='store_true', dest='sync_none',
    help='Do not sync anything, disable -sa / -ss / -sm / -si (default: True with others actions than "follow" or "export")')


def _get_parser_selection(parser):
  parser.add_argument('-a', '--all-books',
    dest='all_books', action='store_true',
    help='Export all followed books')

  parser.add_argument('-b', '--book-name',
    dest='book_name',
    help='Search the book with the given name (use %% for any)')

  parser.add_argument('-i', '--book-id',
    dest='book_id',
    help='Search the book with the given id.')

  parser.add_argument('-s', '--site-name',
    dest='site_name',
    help='Search the books from the given site (use %% for any)')

  parser.add_argument('-sc', '--start-chapter',
    dest='chapter_start', type=int,
    help='If the search result return only one element: the chapter to start with (included).')

  parser.add_argument('-ec', '--end-chapter',
    dest='chapter_end', type=int,
    help='If the search result return only one element: the chapter to end with (included); even if new chapters appears, we will skip them')


def _get_parser_actions(parser):
  group_ex = parser.add_mutually_exclusive_group()

  group_ex.add_argument('--site',
    dest='list_site', action='store_true',
    help='Liste all known site with their id (disable sync operations).')

  group_ex.add_argument('-l', '--list',
    dest='list_book', action='store_true',
    help='List all know book (disable sync operations)')

  group_ex.add_argument('-lf', '--list-followed',
    dest='list_followed_book', action='store_true',
    help='List followed book (disable sync operations)')

  group_ex.add_argument('-f', '--follow',
    dest='follow', action='store_true',
    help='Mark as follow every book found')

  group_ex.add_argument('-u', '--unfollow',
    dest='unfollow', action='store_true',
    help='Mark as unfollow every book found. (Disable sync operations)')

  group_ex.add_argument('-d', '--delete',
    dest='delete_book', action='store_true',
    help='Delete every book found. (Disable sync operations)')

  group_ex.add_argument('-w', '--web',
    dest='web', action='store_true',
    help='Open web browser on it. (Disable sync operations)')

  for w in sorted(actions.REG_WRITTER.values(), key=operator.methodcaller('get_name')):
    group_ex.add_argument('--{}'.format(w.get_name()),
      dest='exporter', action='store_const',
      const=w,
      help='Export as "{}".'.format(w.get_name()))

  default_output = os.path.join(os.path.abspath('.'), 'export_output')
  parser.add_argument('-o', '--output-dir',
    dest='output', action='store',
    help='The output directory path. (default to: "{}")'.format(default_output),
    default=default_output)


def get_parser():
  parser = argparse.ArgumentParser(prog='mgd', conflict_handler='resolve')

  default_store = os.path.join(os.path.abspath('.'), model.DEFAULT_FILE_DB_NAME)
  parser.add_argument('--data',
    dest='data_store', action='store',
    help='the output where to store all data (default to: "{}")'.format(default_store),
    default=default_store)

  parser.add_argument('-v', '--verbose',
    dest='verbose', action='store_true',
    help='Enable verbose output'.format(default_store),
    default=False)

  _get_parser_sync_level(parser)

  _get_parser_selection(parser)

  _get_parser_actions(parser)

  return parser


def init_default_data_store(args):
  sm = model.StoreManager(args.data_store, default=True)
  sm.create_db()
  return sm


def _find_books(args, s):
  lsbs = []
  if args.all_books:
    lsbs = data_access.find_books_followed(s)
  elif args.book_name:
    lsbs = data_access.search_book(args.book_name,  args.site_name, s)
  elif args.book_id:
    lsbs = [data_access.find_link_with_id(args.book_id, s)]

  return lsbs


def _update_chapter_info(lsbs, args, s):
  if args.chapter_start or args.chapter_end:
    for lsb in lsbs:
      actions.update_one_book_chapters(lsb.id, s)
      s.commit()
      # we do the search again for updating result
      r = find_link_with_id(lsb.id)
      if args.chapter_start:
        r.min_chapter = args.chapter_start
      if args.chapter_end:
        r.max_chapter = args.chapter_end


def _make_actions(args, s):
  if args.list_site:
    for si in data_access.find_all_site(s):
      print_site(si)

  elif args.list_book:
    for lsb in data_access.find_books(s):
      print_lsb(lsb, s)

  elif args.list_followed_book:
    for lsb in data_access.find_books_followed(s):
      print_lsb(lsb, s)

  elif args.follow:
    print('Following book')
    for lsb in _find_books(args, s):
      print_lsb(lsb, s)
      lsb.followed = True
    s.commit()

  elif args.unfollow:
    print('Unfollowing book')
    for lsb in _find_books(args, s):
      print_lsb(lsb, s)
      lsb.followed = False
    s.commit()

  elif args.delete_book:
    print('Deleting book')
    for lsb in _find_books(args, s):
      print_lsb(lsb, s)
      actions.delete_book(r, s)
    s.commit()

  elif args.web:
    for lsb in _find_books(args, s):
      webbrowser.open(lsb.url)

  else:
    for lsb in _find_books(args, s):
      print_lsb(lsb, s)


def handle_default(parser, args):
  logger.debug('out default')
  sm = init_default_data_store(args)

  with sm.session_scope() as s:
    actions.create_all_site(s)
    s.commit()

    if not args.follow or args.exporter is None:
      args.sync_none = True

    if not args.sync_none and (args.sync_all or args.sync_meta):
      logger.info('update all books')
      actions.update_books_all_site(s)
      s.commit()

    _make_actions(args, s)

    if not args.sync_none and (args.sync_all or args.sync_struct):
      logger.info('update chapters')
      actions.update_all_chapters(s)
      s.commit()
      logger.info('update pages')
      actions.update_all_pages(s)
      s.commit()

    if not args.sync_none and (args.sync_all or args.sync_images):
      logger.info('update all images')
      # /!\ we use sm and not s because we have threads after this
      # data are commited after the update
      actions.update_all_images(sm)

    if args.exporter:
      lsbs = _find_books(args, s)
      if len(lsbs) > 0:
        actions.export_book(args.exporter, args.output, lsbs, args.chapter_start, args.chapter_end, s)


def print_lsb(lsb, s):
  print('{0.id:>6} {1} '.format(lsb, '+' if lsb.followed else ' '), end='')
  sys.stdout.buffer.write(lsb.book.short_name.encode('utf8'))
  print(' on {0.site.name}'.format(lsb))
  if data_access.count_book_chapters(lsb, s) > 0:
    print('\tchapters: {0:0>3} - {1:0>3} [{2}, {3}]'.format(
        lsb.chapters[0].num,
        lsb.chapters[-1].num,
        lsb.min_chapter if lsb.min_chapter is not None else 1,
        lsb.max_chapter if lsb.max_chapter is not None else '*'
      ))


def print_site(si):
  print('Site: "{0.name}" @ {0.hostname}'.format(si))


def main():
  parser = get_parser()
  args = parser.parse_args()

  if not hasattr(args, 'func'):
    args.func = handle_default

  if args.verbose:
    logging_util.make_verbose()

  args.func(parser, args)
