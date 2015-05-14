#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test template for nosetests
"""

from nose.tools import *
from isaw.images import flickr
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
    f.authenticate(u'12345', u'67890', dry_run=True)
    assert_is_not_none(f.flickr_key)
    assert_is_not_none(f.flickr_secret)

@raises(ValueError)
def test_authentication_pass_no_key():
    """
    ensure error gets raised when we pass only the secret via the authenticate method
    """
    f = flickr.Flickr()
    f.authenticate(secret=u'67890', dry_run=True)

@raises(ValueError)
def test_authentication_pass_no_secret():
    """
    ensure error gets raised when we pass only the key via the authenticate method
    """
    f = flickr.Flickr()
    f.authenticate(key=u'12345', dry_run=True)

def test_authentication_load():
    """
    ensure we can load key and secret from default disk location
    """
    f = flickr.Flickr()
    f.authenticate(dry_run=True)
    assert_is_not_none(f.flickr_key)
    assert_is_not_none(f.flickr_secret)

def test_authentication_writeaccess():
    """
    ensure we actually authenticate with flickr and get write access
    """
    f = flickr.Flickr()
    f.authenticate()  # dry_run defaults to False, so we're actually pinging flickr here
    assert_is_not_none(f.flickr_key)
    assert_is_not_none(f.flickr_secret)
    assert_is_not_none(f.flickr_api)

def test_upload():
    """
    ensure we can actually upload a test image to flickr
    """
    f = flickr.Flickr()
    f.authenticate()
    image_path = os.path.join(os.getcwd(), 'isaw', 'images', 'tests', 'data', 'turkey_road.jpg')
    assert_true(os.path.isfile(image_path))
    id = f.upload(
        unicode(image_path),
        title=u'Turkey Road', 
        description=u'Wild turkeys crossing Moontown Rd. in Madison County, Alabama',
        tags=[u'Moontown', u'wild turkeys', u'asphalt'])
    assert_is_not_none(id)


