#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys


LOG_LVL_WS = 1
LOG_NAME_WS = 'WEBSERVICE'

LOG_LVL_ULTRA = 2
LOG_NAME_ULTRA = 'ULTRA'



#===============================================================================
# StreamToLogger
#===============================================================================
class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   #============================================================================
   # __init__
   #============================================================================
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level


   #============================================================================
   # write
   #============================================================================
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())


#===============================================================================
# IndentFormatter
#===============================================================================
class IndentFormatter(logging.Formatter):
    '''
    Dummy formatter, that prefix the
    %(message)s
    with:
    <indentation_level> %(message)s

    ex:
    hello_world -> ....hello_world
    '''
    #===========================================================================
    # __init__
    #===========================================================================
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)


    #===========================================================================
    # format
    #===========================================================================
    def format(self, rec):
        import inspect
        rec.indent = '.' * (len(inspect.stack()) - 3)
        out = logging.Formatter.format(self, rec)
        del rec.indent
        return out


#===============================================================================
# EMPTY_LOGGING
#===============================================================================
EMPTY_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # formatters
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    # filters
    'filters': {
    },
    # handlers
    'handlers': {
        'null': {
            'class':'logging.NullHandler',
        },
    },
    # loggers
    'loggers': {
    },
    # root
    'root' : {
        'handlers': ['null'],
        'level':'WARNING',
    }
}


#===============================================================================
# UNITEST_LOGGING
#===============================================================================
UNITEST_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # formatters
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s'
        },
    },
    # filters
    'filters': {
    },
    # handlers
    'handlers': {
        'null': {
            'class':'logging.NullHandler',
        },
        'console':{
            'level': 1,
            'class':'logging.StreamHandler',
            'formatter': 'simple',
            'stream':sys.stderr,
        },
    },
    # loggers
    'loggers': {
    },
    # root
    'root' : {
        'handlers': ['console'],
        'level': 'DEBUG',
    }
}


#===============================================================================
# load_config
#===============================================================================
def load_config(conf):
    from logging import config
    try:
        from qgis import utils

        # qgis change the __import__ builtin function
        # that make logging crash
        # The purpose of the qgis function
        # is just to know witch plugin is loaded if it's a plugin
        # so... we make logging use the real builtin import function
        # and not the one from qgis

        config.BaseConfigurator.importer = __import__ \
            if __import__.__module__ == '__builtin__' \
            else utils._builtin_import # pylint: disable=W0212
    except ImportError:
        # No qgis present... we don't care
        pass
    config.dictConfig(conf)


#===============================================================================
# log_std_stream
#===============================================================================
def log_std_stream():
    l = logging.getLogger('tsk_common.logging.stderr')
    sys.stderr = StreamToLogger(l, logging.ERROR)
    l = logging.getLogger('tsk_common.logging.stdout')
    sys.stdout = StreamToLogger(l, logging.INFO)


#===============================================================================
# indent_log_formatter
#===============================================================================
def indent_log_formatter(handler_name):
    handler = logging._handlers.get(handler_name)
    if handler is not None and handler.formatter is not None:
        form = IndentFormatter()
        old_formatter = handler.formatter
        handler.formatter = form
        form._fmt = old_formatter._fmt.replace('%(message)s', '%(indent)s%(message)s')


#===============================================================================
# main
#===============================================================================
if __name__ == '__main__':
    load_config(UNITEST_LOGGING)
    for h in logging._handlers.keys():
        indent_log_formatter(h)

    logger = logging.getLogger('tsk')
    logger.debug('test debug')
    logger.info('test info')
    logger.warning('test warning')
    logger.error('test error')
    logger.critical('test critical')
