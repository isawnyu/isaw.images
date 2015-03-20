#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test template for nosetests
"""

from isaw.images.validate_path import validate_path
import logging
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_is
import os
import shutil
    
logging.basicConfig(level=logging.DEBUG)

def test_validate_path():
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    try:
        real_path = validate_path(temp, 'file')
    except IOError:
        pass
    real_path = validate_path(temp, 'directory')
    assert_equals(real_path, os.path.realpath(temp))
    try:
        real_path = validate_path(temp, 'klingon')
    except ValueError:
        pass
    tempfile = os.path.join(temp,'workfile')
    with open(tempfile, 'w') as f:
        f.write("foo")
    try:
        real_path = validate_path(tempfile, 'directory')
    except IOError:
        pass
    real_path = validate_path(tempfile, 'file')
    assert_equals(real_path, os.path.realpath(tempfile))
    shutil.rmtree(temp)

