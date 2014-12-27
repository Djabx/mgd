#! /usr/bin/python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)

#===============================================================================
# Warning when we import the debug module...
#===============================================================================
logger.critical("#" * 60)
logger.critical("'%s' module MUST only be used for debuging purpose", __name__)
logger.critical("#" * 60)

import inspect
import sys
import os
import util


#===============================================================================
# flush
#===============================================================================
def flush(logger):
    '''
    Flush all the handlers of a logger
    '''
    for handler in logger.handlers:
        handler.flush()


#===============================================================================
# log_all_frames
#===============================================================================
def log_all_frames():
    frames = inspect.getouterframes(inspect.currentframe())
    l = []
    # 0: result of outerframes is: [(frame, other...)] we want only the frame
    # 1: we don't want this frame to be display
    # 4 we want at most 3 frame (1, 2, 3)
    util._get_frame_string_list((f[0] for f in reversed(frames[1:])), l)
    msg = util._format_frame_string_list(l)
    logger.debug('Trace back info:\n%s', msg)


#===============================================================================
# log_caller_info
#===============================================================================
def log_caller_info(depth=4):
    frames = inspect.getouterframes(inspect.currentframe())
    l = []
    # 0: result of outerframes is: [(frame, other...)] we want only the frame
    # 1: we don't want this frame to be display
    # +1: ex if we want at most 4 frames (1, 2, 3, 4) 5
    util._get_frame_string_list((f[0] for f in reversed(frames[1:depth+1])), l)
    msg = util._format_frame_string_list(l)
    logger.debug('Trace back info:\n%s', msg)



#===============================================================================
# log_current_frame
#===============================================================================
def log_current_frame():
    frames = inspect.getouterframes(inspect.currentframe())
    l = []
    # 0: result of outerframes is: [(frame, other...)] we want only the frame
    # 1: we don't want this frame to be display
    util._get_frame_string_list((frames[1][0],), l)
    msg = util._format_frame_string_list(l)
    logger.debug('Trace back info:\n%s', msg)
