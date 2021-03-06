#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
from os.path import join, expanduser

from mgdpck import logging_util
# init logger first
logging_util.init_logger()
logging_util.add_except_name('run_script')
logger = logging.getLogger(__name__)

from mgdpck import info
from mgdpck import model
from mgdpck import data_access
from mgdpck.readers import *

def _get_parser_sy(cmd_parser, parent_parser):
  parser_sy = cmd_parser.add_parser('sy', help='command for syncing books in db')
  parser_sy.set_defaults(func=handle_sy)

  parser_sy.add_argument('-m', '--meta',
    action='store_true',
    help='Sync and update meta data (list of books, etc.)')
  parser_sy.add_argument('-s', '--struct',
    action='store_true',
    help='Sync structures of followed books (chapters, content structure etc.)')
  parser_sy.add_argument('-c', '--contents',
    action='store_true',
    help='Sync all images')
  parser_sy.add_argument('-a', '--all',
    action='store_true',
    help='Sync meta data, structures and images; equal to -m -s -c')


def _get_parser_se(main_parser, default_store):
  parser_se = main_parser.add_parser('se', help='command for searching DB')
  parser_se.set_defaults(func=handle_se)

  group_ex = parser_se.add_mutually_exclusive_group()

  group_search = group_ex.add_argument_group()
  group_search.add_argument('-b', '--book-name',
    dest='book_name',
    help='Search the book with the given name (use %% for any)')

  group_search.add_argument('-s', '--site-name',
    dest='site_name',
    help='Search the books from the given site (use %% for any)')

  group_search.add_argument('-c', '--chapters',
    dest='chapters', action='store_true',
    help='If the search result return only one element: search chapter information about it.')

  group_search.add_argument('-f', '--follow',
    dest='follow', action='store_true',
    help='If the search result return only one element: mark as folow')

  group_search.add_argument('-sc', '--start-chapter',
    dest='chapter_start', type=int,
    help='If the search result return only one element: the chapter to start with (included).')

  group_search.add_argument('-ec', '--end-chapter',
    dest='chapter_end', type=int,
    help='If the search result return only one element: the chapter to end with (included); even if new chapters appears, we will skip them')


  group_ex.add_argument('--site',
    dest='list_site', action='store_true',
    help='Liste all known site with their id.')

  group_ex.add_argument('--list', '-l',
    dest='list_book', action='store_true',
    help='List all know book')

  group_ex.add_argument('--list-followed', '-lf',
    dest='list_followed_book', action='store_true',
    help='List followed book')


def get_parser():
  main_parser = argparse.ArgumentParser(prog='mgd', conflict_handler='resolve')

  default_store = join('.', 'mgd_store.db')
  main_parser.add_argument('-d', '--data',
    dest='data_store', action='store',
    help='the output where to store all data (default to: "{}")'.format(default_store),
    default=default_store)

  cmd_parser = main_parser.add_subparsers(help='sub-command help')

  _get_parser_sy(cmd_parser, main_parser)

  _get_parser_se(cmd_parser, main_parser)

  parser_out = cmd_parser.add_parser('out', help='command for writting comics to ouput')
  parser_out.set_defaults(func=handle_out)
  parser_out.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: "{}")'.format(default_store),
    default=default_store)

  return main_parser


def init_data_store(args):
  from mgdpck import model
  model.create_db(args.data_store)


def handle_sy(parser, args):
  if not (args.all or args.meta or args.struct or args.contents):
    parser.print_help()
    return

  init_data_store(args)
  with model.session_scope() as s:
    info.create_all_site(s)

    if args.all or args.meta:
      logger.info('update all books')
      info.update_books_all_site(s)

    if args.all or args.struct:
      logger.info('update chapters')
      info.update_all_chapters(s)
      logger.info('update contents')
      info.update_all_contents(s)

    if args.all or args.contents:
      logger.info('update all images')
      info.update_all_images(s)


def handle_se(parser, args):
  logger.debug('se cmd')
  init_data_store(args)
  with model.session_scope() as s:
    info.create_all_site(s)

    def print_lsb(lsb):
      print('{0.id:<6} {1} {0.book.short_name}'.format(lsb, '+' if lsb.followed else ' '))
      if len(lsb.chapters) > 0:
        print('\tchapters: {0} - {1}'.format(lsb.chapters[0].num, lsb.chapters[-1].num),
          '[{},'.format(lsb.min_chapter if lsb.min_chapter is not None else 1),
          '{}]'.format(lsb.max_chapter if lsb.max_chapter is not None else '*')
          )

    def print_site(si):
      print('Site: "{0.name}" @ {0.hostname}'.format(si))

    if args.list_followed_book:
      for r in data_access.find_books_followed(s):
        print_lsb(r)

    elif args.list_book:
      for r in data_access.find_books(s):
        print_lsb(r)

    elif args.list_site:
      for s in data_access.find_all_site(s):
        print_site(s)

    elif args.book_name or args.site_name:
      results = data_access.search_book(args.book_name, args.site_name, s)

      if len(results) == 1:
        r = results[0]
        if args.chapters:
          info.update_one_book_chapters(r.id)
          # we do the search again for updating result
          results = data_access.search_book(args.book_name, args.site_name, s)
          r = results[0]
        if args.follow:
          r.followed = True
        if args.chapter_start:
          r.min_chapter = args.chapter_start
        if args.chapter_end:
          r.max_chapter = args.chapter_end
        s.commit()

      for r in results:
        print_lsb(r)
    else:
      parser.print_help()


def handle_out(parser, args):
  logger.debug('out cmd')
  init_data_store(args)
  if not args.nothing:
    with model.session_scope() as s:
      pass


def handle_default(parser, args):
  logger.debug('out default')
  parser.print_help()



def main():
  logger.debug('starting mgd')
  parser = get_parser()
  args = parser.parse_args()
  logger.debug('Parsing arguments: %s', args)

  if not hasattr(args, 'func'):
    args.func = handle_default

  args.func(parser, args)


if __name__ == '__main__':
  main()
