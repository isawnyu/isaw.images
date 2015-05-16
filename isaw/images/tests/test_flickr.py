#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test template for nosetests
"""

from nose.tools import *
from isaw.images import flickr, package
import logging
import os
import shutil

logging.basicConfig(level=logging.DEBUG)

def test_instantiate_package():
    f = flickr.Flickr()

def test_authentication_pass():
    """
    ensure we can pass key and secret via the authenticate method
    """
    f = flickr.Flickr()
    f.flickr_authenticate(u'12345', u'67890', dry_run=True)
    assert_is_not_none(f.flickr_key)
    assert_is_not_none(f.flickr_secret)

@raises(ValueError)
def test_authentication_pass_no_key():
    """
    ensure error gets raised when we pass only the secret via the authenticate method
    """
    f = flickr.Flickr()
    f.flickr_authenticate(secret=u'67890', dry_run=True)

@raises(ValueError)
def test_authentication_pass_no_secret():
    """
    ensure error gets raised when we pass only the key via the authenticate method
    """
    f = flickr.Flickr()
    f.flickr_authenticate(key=u'12345', dry_run=True)

def test_authentication_load():
    """
    ensure we can load key and secret from default disk location
    """
    f = flickr.Flickr()
    f.flickr_authenticate(dry_run=True)
    assert_is_not_none(f.flickr_key)
    assert_is_not_none(f.flickr_secret)

def test_authentication_writeaccess():
    """
    ensure we actually authenticate with flickr and get write access
    """
    f = flickr.Flickr()
    f.flickr_authenticate()  # dry_run defaults to False, so we're actually pinging flickr here
    assert_is_not_none(f.flickr_key)
    assert_is_not_none(f.flickr_secret)
    assert_is_not_none(f.flickr_api)

def test_upload():
    """
    ensure we can actually upload a test image to flickr
    """
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    srcpath = os.path.join(current, 'data', 'kalabsha', '201107061813531')
    destpath = os.path.join(temp, '201107061813531')
    shutil.copytree(srcpath, destpath)
    assert_equals(os.path.isdir(destpath), True)
    p = package.Package()
    p.open(destpath)
    p.make_derivatives()
    p.flickr_upload(p.metadata.data, thumbnail=True)
    shutil.rmtree(temp)
    
