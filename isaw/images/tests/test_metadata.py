#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nosetests for metadata.py
"""

from isaw.images import metadata
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_is
import logging
import os
import shutil

logging.basicConfig(level=logging.DEBUG)

def test_create_metadata():
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    meta_path=os.path.join(temp, 'meta.xml')
    # by default, the file should *not* get created
    try:
        m=metadata.Metadata(meta_path)
    except IOError:
        pass
    assert_equals(os.path.isfile(meta_path), False)
    # we can force creation of the file, if desired
    m=metadata.Metadata(meta_path, create=True)
    assert_equals(os.path.isfile(meta_path), True)
    assert_equals(m.data, {'status': 'draft', 'license': 'undetermined', 'isaw-publish-cleared': 'no', 'license-release-verified': 'no'})
    del m
    shutil.rmtree(temp)

