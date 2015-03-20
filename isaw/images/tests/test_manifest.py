#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test manifest
"""
from isaw.images import manifest
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_is
import os
import shutil

def test_instantiate_manifest():
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    m=manifest.Manifest(os.path.join(temp, 'manifest-sha1.txt'), create=True)
    shutil.rmtree(temp)
