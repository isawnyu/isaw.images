#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
provide a class with flickr functionality
"""

from arglogger import arglogger
import codecs
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
        self.flickr_capable = True

    @arglogger
    def flickr_authenticate(self, key=None, secret=None, dry_run=False):
        """
        authenticate with flickr
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)

        # get flickr api key and secret
        if key is None and secret is None:
            self.__flickr_load_credentials__()
        elif key is None or secret is None:
            err = "unexpected mix of credential values: key={0}, secret={1}".format(key, secret)
            raise ValueError(err)
        else:
            self.flickr_key = key
            self.flickr_secret = secret

        # initialize the api wrapper and go through whatever authentication
        # process is needed to get write access (or fail trying)
        if not dry_run:
            fapi = flickrapi.FlickrAPI(self.flickr_key, self.flickr_secret)
            if not fapi.token_valid(perms='write'):
                # Get a request token
                fapi.get_request_token(oauth_callback='oob')

                # Open a browser at the authentication URL. Do this however
                # you want, as long as the user visits that URL.
                authorize_url = self.flickr.auth_url(perms=u'write')
                webbrowser.open_new_tab(authorize_url)

                # Get the verifier code from the user. Do this however you
                # want, as long as the user gives the application the code.
                verifier = unicode(raw_input('Verifier code: '))

                # Trade the request token for an access token
                fapi.get_access_token(verifier)

            self.flickr_api = fapi


    @arglogger
    def flickr_upload(self, 
        image_filename, 
        title=None, 
        description=None, 
        tags=None, 
        public=False, 
        family=False, 
        friends=False, 
        content_type='photo'):
        """
        upload a new image to flickr
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)

        params = {}
        params['filename'] = image_filename
        if title is not None:
            params['title'] = title
        if description is not None:
            params['description'] = description
        if tags is not None:
            if len(tags) > 0:
                params['tags'] = ' '.join([[tag, '"{0}"'.format(tag)][' ' in tag] for tag in tags])
        params['is_public'] = [0,1][public]
        if not public:
            params['is_family'] = [0,1][family]
            params['is_friends'] = [0,1][friends]
        if content_type == 'photo':
            params['content_type'] = 1
        elif content_type == 'screenshot':
            params['content_type'] = 2
        else:
            params['content_type'] = 3
        logger.debug("calling flickrapi.upload with params: {0}".format(repr(params)))
        response = self.flickr_api.upload(**params)
        logger.debug("raw flickrapi response: {0}".format(repr(response)))
        photoid = response.find('photoid').text
        logger.debug("flickr photoid parsed from response: {0}".format(photoid))
        self.flickr_id = photoid
        return photoid

    @arglogger
    def flickr_replace(self):
        """
        replace an image on flickr
        """
        pass

    @arglogger
    def flickr_generate(self):
        """
        create what we consider to be a flickr-ready image
        """
        pass

    @arglogger
    def __flickr_load_credentials__(self, key_path=DEFAULT_KEY_PATH, secret_path=DEFAULT_SECRET_PATH):
        """
        load flickr api key and secret from file 
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)

        path = os.path.realpath(key_path)
        with codecs.open(path, encoding='utf-8', mode='r') as keyf:
            self.flickr_key = keyf.read().rstrip()

        path = os.path.realpath(secret_path)
        with codecs.open(path, encoding='utf-8', mode='r') as secretf:
            self.flickr_secret = secretf.read().rstrip()


    # more methods here to set/change metadata
