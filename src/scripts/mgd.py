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
from mgdpck.readers import *

def _get_parser_sy(main_parser, default_store):
  parser_sy = main_parser.add_parser('sy', help='command for syncing books in db')
  parser_sy.set_defaults(func=handle_sy)

  parser_sy.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: {})'.format(default_store),
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
  group.add_argument('--chapter',
    action='store_true',
    help='Sync chapters for books mark has followed')
  group.add_argument('--content',
    action='store_true',
    help='Sync content structure (not images!) for books mark has followed')


def get_parser():
  main_parser = argparse.ArgumentParser(prog='mgd', conflict_handler='resolve')

  cmd_parser = main_parser.add_subparsers(help='sub-command help')
  default_store = join('.', 'mgd_store.db')

  _get_parser_sy(cmd_parser, default_store)

  parser_dl = cmd_parser.add_parser('dl', help='command for download comics in datastore')
  parser_dl.set_defaults(func=handle_dl)
  parser_dl.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: {})'.format(default_store),
    default=default_store)

  parser_out = cmd_parser.add_parser('out', help='command for writting comics to ouput')
  parser_out.set_defaults(func=handle_out)
  parser_out.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: {})'.format(default_store),
    default=default_store)

  return main_parser


def init_data_store(args):
  from mgdpck import model
  store_file = args.data_store
  if not os.path.exists(store_file):
    parent_dir = os.path.dirname(store_file)
    if not os.path.exists(parent_dir):
      os.makedirs(parent_dir)
  model.create_db(args.data_store)


def handle_sy(parser, args):
  logger.debug('sy cmd')
  logger.debug('args: %s', args)
  init_data_store(args)
  if not args.nothing:
    if args.all or args.site:
      logger.info('update all site')
      info.create_all_site()

    if args.all or args.books:
      logger.info('update all books')
      info.update_books_all_site()


def handle_dl(parser, args):
  logger.debug('dl cmd')
  init_data_store(args)
  pass


def handle_out(parser, args):
  logger.debug('out cmd')
  init_data_store(args)
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
