#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
decorator code for logging arguments passed to functions
"""

from functools import wraps
import logging

def arglogger(func):
    """
    decorator to log argument calls to functions
    """
    @wraps(func)
    def inner(*args, **kwargs): 
        logger = logging.getLogger(func.__name__)
        logger.debug("called with arguments: %s, %s" % (args, kwargs))
        return func(*args, **kwargs) 
    return inner    


