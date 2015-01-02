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

def get_parser():
  main_parser = argparse.ArgumentParser(prog='mgd', conflict_handler='resolve')

  cmd_parser = main_parser.add_subparsers(help='sub-command help')
  default_store = join('.', 'mgd_store.db')

  parser_sy = cmd_parser.add_parser('sy', help='cmd for sync comics in db')
  parser_sy.set_defaults(func=handle_sy)
  parser_sy.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: %s)' % default_store,
    default=default_store)
  group = parser_sy.add_mutually_exclusive_group()
  group.add_argument('--all',
    dest='site_2_sync',
    action='store_const', const='all',
    help='Sync all known sites')
  group.add_argument('-s', '--site',
    dest='site_2_sync',
    action='append',
    help='the site hostname to sync')

  parser_dl = cmd_parser.add_parser('dl', help='cmd for dl comics in db')
  parser_dl.set_defaults(func=handle_dl)
  parser_dl.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: %s)' % default_store,
    default=default_store)

  parser_out = cmd_parser.add_parser('out', help='cmd for writting comics too ouput')
  parser_out.set_defaults(func=handle_out)
  parser_out.add_argument('-d', '--data',
    dest='data_store',
    help='the output where to store all data (default to: %s)' % default_store,
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


def handle_sy(args):
  logger.debug('sy cmd')
  if args.site_2_sync == 'all':
    logger.info('update all site')
    args.site_2_sync = info.update_books_all_site()


def handle_dl(args):
  logger.debug('dl cmd')
  pass


def handle_out(args):
  logger.debug('out cmd')
  pass



def main():
  logger.debug('starting mgd')
  parser = get_parser()
  args = parser.parse_args()
  logger.debug('Parsing arguments: %s', args)

  init_data_store(args)

  info.create_all_site()
  args.func(args)


if __name__ == '__main__':
  main()
