#! /usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import sys
import inspect
import pprint
import traceback
import datetime

logger = logging.getLogger(__name__)
formater = pprint.PrettyPrinter()

_old_hook = sys.excepthook
_MAX_VAR_LENGTH = 4000
_EXECEPTED_METHOD = []
_NUM_LINE_TO_SHOW = None
_DISPLAY_LOCAL = False
_DISPLAY_CODE = False
_SKIPPING = True

LOGGING_CONF={
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
    'console_info':{
      'level': logging.WARNING,
      'class':'logging.StreamHandler',
      'formatter': 'simple',
      'stream':sys.stderr,
    },
    'console_debug':{
      'level': logging.DEBUG,
      'class':'logging.StreamHandler',
      'formatter': 'simple',
      'stream':sys.stdout,
    },
  },
  # loggers
  'loggers': {
  },
  # root
  'root' : {
    'handlers': [
      'console_info',
      'console_debug',
      'null'],
    'level': 'DEBUG',
  }
}


def init_logger(conf_logging=LOGGING_CONF):
    # now we init the logging module, this should be done only once
    from logging import config
    config.dictConfig(conf_logging)

    change_except_hook()

    #logger.debug('logging init with: %s', formater.pformat(conf_logging))



def change_except_hook(length=2, local=True, code=True,
                       skipping=True):
    """
    Change the exception hook (how we handle uncaught exceptions)
    The new hook, display local variables, and a bit more code

    :param length: how many lines of code we want to display before and after the bad line
        if 0 display only the bad line
    :param logger: the logger (see logging module) to use, if None, not use
        in every case, the exception is also printed on sys.stderr
    :param local: a boolean to set if we want to display local variable or not
    :param skipping: a boolean to set if we want to skip some method (added with
        add_except_name(name))
    """
    global _NUM_LINE_TO_SHOW, _DISPLAY_LOCAL, _SKIPPING, _DISPLAY_CODE
    _NUM_LINE_TO_SHOW = length
    _DISPLAY_LOCAL = local
    _DISPLAY_CODE = code
    _SKIPPING = skipping
    sys.excepthook = _my_excepthook
    logger.info('exception hook changed.')



def print_current_exception_information():
    '''
    Print the current exception stack trace
    '''
    _log_traceback(*sys.exc_info())



def is_except_hook_changed():
    """
    Test if the except hook as been changed or not.
    """
    return sys.excepthook == _my_excepthook



def add_except_name(name):
    """
    add the given name to excepted method

    When an exception not catch will occur, if a method/function in the stack as
    her name in the list, it will be skip.
    """
    _EXECEPTED_METHOD.append(name)


################################################################################
# Private functions
################################################################################

def _get_src_string(tb_frame):
    """
    Return a string for the given frame that represent his code section

    Sometimes, code is illisible, or unfoundable
    so we return an empty string and a false boolean (true oserwise)
    """
    bad_line_num = tb_frame.f_lineno
    src_str = []
    display = True
    try:
        src_, start_line = inspect.getsourcelines(
            inspect.getmodule(tb_frame.f_code))
    except TypeError:
        display = False
    else:
        new_bad_line_num = bad_line_num - start_line
        begin = max(new_bad_line_num - _NUM_LINE_TO_SHOW - 1, 0)
        end = min(new_bad_line_num + _NUM_LINE_TO_SHOW, len(src_))

        for i, code_line in enumerate(src_[begin: end]):
            line_num = i + begin + 1
            src_str.append('%(indent)s%(num)04d%(sign)s%(code)s' %
                    {'num' : line_num,
                     'indent' : '%(indent_src)s',
                    'sign' : '  ' if line_num != new_bad_line_num else '->',
                    'code' : code_line.replace('%', '%%')})

    return ''.join(src_str).rstrip(), display



def _format_var(name, value, fmt="%20s = %s"):
    try:
        vs = formater.pformat(value).replace('%', '%%')
    except:
        vs = '<REPR ERROR>'
    return fmt % (name, vs[:_MAX_VAR_LENGTH] +
                          ('...' if len(vs) > _MAX_VAR_LENGTH else ''))




def _get_local_string(local_var):
    """
    Return a string that represent the local attributes of the given frame
    """
    locals_ = []
    self_var = local_var.pop('self', None)
    if self_var is not None:
        # if there is a self
        # we display attributes
        locals_.append(_format_var('self', self_var))

        for k, v in sorted(self_var.__dict__.iteritems(),
                           cmp=lambda x, y: cmp(x[0], y[0])):
            locals_.append(_format_var('self.' + k, v, "%40s = %s"))

    for k, v in sorted(local_var.iteritems(),
                       cmp=lambda x, y: cmp(x[0], y[0])):
        locals_.append(_format_var(k, v))

    if len(locals_) == 0:
        return '%20s' % 'None'
    return '\n'.join(locals_)




def _get_frame_string_list(frames, lresult):
    for frame in frames:
        if _SKIPPING and frame.f_code.co_name in _EXECEPTED_METHOD:
            # it's a methode/function name to skip
            lresult.append('  skipping: %s' % frame.f_code.co_name)
            continue

        # we get the source code
        src_, display_code = _get_src_string(frame)
        # we prepare the dict parameters
        d = {
             'file_':frame.f_code.co_filename,
             'line':frame.f_lineno,
             'locals':_get_local_string(frame.f_locals),
             'function':frame.f_code.co_name,
             'src':src_,
             'indent':'%(indent)s',
             'indent_src':'%(indent_src)s',
             'mark':'%(mark)s',
             }
        # the error location
        lresult.append('''  File "%(file_)s", line %(line)d, in %(function)s''' % d)
        if _DISPLAY_CODE and display_code:
            # we display the source code
            lresult.append('%(indent)s%(indent)s%(mark)s Code %(mark)s' % d)
            lresult.append('%(src)s' % d)

        if _DISPLAY_LOCAL:
            # we display local variables
            lresult.append('%(indent)s%(indent)s%(mark)s Locals %(mark)s' % d)
            lresult.append('%(locals)s' % d)




def _format_frame_string_list(lresult):
    # parameters for formating options
    d = {'indent':' ' * 4, 'indent_src':' ' * 8, 'mark':'#' * 5}
    # we gen he full error message
    error_msg = '\n'.join(lresult)
    return error_msg % d




def _log_traceback(except_type, value, traceback):
    # we unstack every context from traceback
    def iter_tb_frame(tb):
        while tb is not None:
            yield tb.tb_frame
            tb = tb.tb_next

    # now we get hrough
    lresult = ['Traceback (most recent call last):']
    _get_frame_string_list(iter_tb_frame(traceback), lresult)

    lresult.append('EXCEPTION : %s: %s' % (except_type.__name__, value))

    error_msg = _format_frame_string_list(lresult)

    if logger:
        # we use the logger
        logger.debug('Exception occured and was not catched:\n%s', error_msg)
        logger.critical('Exception occured and was not catched: %s: %s', except_type.__name__, value)
    else:
        # we write on stderr
        print(error_msg, file=sys.stderr)



def _my_excepthook(except_type, value, traceback):
    '''
    Function that will replace the sys.excepthook
    '''
    _log_traceback(except_type, value, traceback)
    # Now we call the old hook
    _old_hook(except_type, value, traceback)
