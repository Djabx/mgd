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

def _get_parser_sy(main_parser, default_store):
  parser_sy = main_parser.add_parser('sy', help='command for syncing books in db')
  parser_sy.set_defaults(func=handle_sy)

  parser_sy.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: "{}")'.format(default_store),
    default=default_store)

  group = parser_sy.add_mutually_exclusive_group(required=True)
  group.add_argument('--nothing',
    action='store_true',
    help='Does nothing')
  group.add_argument('--all',
    action='store_true',
    help='Do all sync operations')
  group.add_argument('--site',
    action='store_true',
    help='Sync all known sites')
  group.add_argument('--books',
    action='store_true',
    help='Sync all books')
  group.add_argument('--chapters',
    action='store_true',
    help='Sync chapters for books mark has followed')
  group.add_argument('--content',
    action='store_true',
    help='Sync content structure (not images!) for books mark has followed')
  group.add_argument('--images',
    action='store_true',
    help='Sync images for books mark has followed')


def _get_parser_se(main_parser, default_store):
  parser_se = main_parser.add_parser('se', help='command for searching DB')
  parser_se.set_defaults(func=handle_se)
  parser_se.add_argument('-d', '--data',
    dest='data_store',
    help='the file where to store all data (default to: "{}")'.format(default_store),
    default=default_store)

  parser_se.add_argument('-bn',
    dest='book_name',
    help='Search the book with the given name')


def _get_parser_sub(main_parser, default_store):
  parser_sub = main_parser.add_parser('sub', help='command for managing subscriptions')
  parser_sub.set_defaults(func=handle_sub)
  parser_sub.add_argument('-d', '--data',
    dest='data_store',
    help='the file where to store all data (default to: "{}")'.format(default_store),
    default=default_store)

  parser_sub.add_argument('--id',
    required=True,
    dest='fl_id', action='store',
    help='Specify the id to manage')

  parser_sub.add_argument('--follow',
    dest='follow', action='store_true',
    help='If the search result return only one element, mark as folow')


def get_parser():
  main_parser = argparse.ArgumentParser(prog='mgd', conflict_handler='resolve')

  cmd_parser = main_parser.add_subparsers(help='sub-command help')
  default_store = join('.', 'mgd_store.db')

  _get_parser_sy(cmd_parser, default_store)

  _get_parser_se(cmd_parser, default_store)

  _get_parser_sub(cmd_parser, default_store)

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
  logger.debug('sy cmd')
  logger.debug('args: %s', args)
  init_data_store(args)
  if not args.nothing:
    with model.session_scope() as s:
      if args.all or args.site:
        logger.info('update all site')
        info.create_all_site(s)

      if args.all or args.books:
        logger.info('update all books')
        info.update_books_all_site(s)

      if args.all or args.chapters:
        logger.info('update all chapters')
        info.update_all_chapters(s)


def handle_se(parser, args):
  logger.debug('se cmd')
  init_data_store(args)
  with model.session_scope() as s:
    for r in data_access.search_book(args.book_name, s):
      print('''
  Book:
    name: {0.short_name}
    full name: {0.full_name}'''.format(r))
      for lsb in r.site_links:
        print('''    Site: "{0.site.name}" : id -> {0.id}'''.format(lsb))


def handle_sub(parser, args):
  logger.debug('sub cmd')
  init_data_store(args)
  with model.session_scope() as s:
    lsbs = data_access.find_link_with_id(args.fl_id, s)
    if len(lsbs) != 1:
      raise Exception('Not found...')
    lsb = lsbs[0]
    if args.follow:
      lsb.followed = True


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
