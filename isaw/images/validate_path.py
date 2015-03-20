#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate a file or directory path
"""

from arglogger import arglogger
import os

@arglogger
def validate_path(path, type='file'):
    """
    make sure path exists
    """

    real_path = os.path.realpath(path)
    if not os.path.exists(real_path):
        raise IOError("non-existant path '{0}'".format(real_path))
    if type=='file':
        if not os.path.isfile(real_path):
            raise IOError("item at path '{0}' is not a file".format(real_path))
    elif type=='directory':
        if not os.path.isdir(real_path):
            raise IOError("item at path '{0}' is not a directory".format(real_path))
    else:
        raise ValueError("unrecognized type=='{0}' passed to validate_path()".format(type))
    return real_path

