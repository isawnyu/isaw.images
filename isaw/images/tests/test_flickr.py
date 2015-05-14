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
    f.authenticate('12345', '67890')
    assert_is_not_none(f.key)
    assert_is_not_none(f.secret)

@raises(ValueError)
def test_authentication_pass_no_key():
    """
    ensure error gets raised when we pass only the secret via the authenticate method
    """
    f = flickr.Flickr()
    f.authenticate(secret='67890')

@raises(ValueError)
def test_authentication_pass_no_secret():
    """
    ensure error gets raised when we pass only the key via the authenticate method
    """
    f = flickr.Flickr()
    f.authenticate(key='12345')

def test_authentication_load():
    """
    ensure we can load key and secret from default disk location
    """
    f = flickr.Flickr()
    f.authenticate()
    assert_is_not_none(f.key)
    assert_is_not_none(f.secret)
    


