#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import util
import argparse
import logging
from os.path import join, expanduser

util.init_logger()
logger = logging.getLogger(__name__)


def get_parser():
  main_parser = argparse.ArgumentParser(prog='mgd')

  cmd_parser = main_parser.add_subparsers(help='sub-command help')
  default_store = join(expanduser('~'), '.mtd', 'store.db')

  parser_sy = cmd_parser.add_parser('sy', help='cmd for sync comics in db')
  parser_sy.set_defaults(func=handle_sy)
  parser_sy.add_argument('-d', '--data',
    help='the output where to store all data (default to: %s)' % default_store,
    default=default_store)

  parser_dl = cmd_parser.add_parser('dl', help='cmd for dl comics in db')
  parser_dl.set_defaults(func=handle_dl)
  parser_dl.add_argument('-d', '--data',
    help='the output where to store all data (default to: %s)' % default_store,
    default=default_store)

  parser_out = cmd_parser.add_parser('out', help='cmd for writting comics too ouput')
  parser_out.set_defaults(func=handle_out)
  parser_out.add_argument('-d', '--data',
    help='the output where to store all data (default to: %s)' % default_store,
    default=default_store)

  return main_parser


def handle_sy(args):
  logger.debug('sy cmd')
  pass


def handle_dl(args):
  logger.debug('dl cmd')
  pass


def handle_out(args):
  logger.debug('out cmd')
  pass



def main():
  logger.debug('starting')
  parser = get_parser()
  args = parser.parse_args()
  logger.debug('Parsing arguments: %s', args)
  args.func(args)


if __name__ == '__main__':
  main()
