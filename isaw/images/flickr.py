#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
provide a class with flickr functionality
"""

from arglogger import arglogger
import flickrapi 
import logging
import os
import sys
import urllib3
import webbrowser
import xml.etree.ElementTree as ET

path_current = os.getcwd()
DEFAULT_KEY_PATH = os.path.join(path_current, 'flickr.key')
DEFAULT_SECRET_PATH = os.path.join(path_current, 'flickr.secret')

class Flickr():
    """
    a base class for providing flickr functionality to other classes
    """

    @arglogger
    def __init__(self):
        pass

    @arglogger
    def authenticate(self, key=None, secret=None):
        """
        authenticate with flickr
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        if key is None and secret is None:
            self.__load_credentials__()
        elif key is None or secret is None:
            err = "unexpected mix of credential values: key={0}, secret={1}".format(key, secret)
            raise ValueError(err)
        else:
            self.key = key
            self.secret = secret

    @arglogger
    def upload(self):
        """
        upload a new image to flickr
        """
        pass

    @arglogger
    def replace(self):
        """
        replace an image on flickr
        """
        pass

    @arglogger
    def generate(self):
        """
        create what we consider to be a flickr-ready image
        """
        pass

    @arglogger
    def __load_credentials__(self, key_path=DEFAULT_KEY_PATH, secret_path=DEFAULT_SECRET_PATH):
        """
        load flickr api key and secret from file 
        """
        path = os.path.realpath(key_path)
        with open(path, 'r') as keyf:
            self.key = keyf.read()
        self.key = self.key.rstrip()

        path = os.path.realpath(secret_path)
        with open(path, 'r') as secretf:
            self.secret = secretf.read()
        self.secret = self.secret.rstrip()


    # more methods here to set/change metadata
