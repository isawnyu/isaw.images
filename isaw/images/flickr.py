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
    def flickr_upload(self, meta, thumbnail=False):
        """
        upload a new image to flickr
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)

        if not self.flickr_capable:
            logger.error('flickr upload aborted: upload_to_flickr was called when package was not flickr-capable')
            return False

        try:
            if meta['status'] != 'ready' or meta['license-release-verified'] != 'yes' or meta['isaw-publish-cleared'] != 'yes':
                logger.warning('flickr upload denied because of status, license release verification or isaw publication clearance settings in meta.xml')
                return False
        except KeyError:
            logger.error("flickr upload aborted: could not get status, license release verification, or isaw publication clearance values from meta.xml")
            return False


        self.flickr_authenticate()

        params = {
            'is_public': 0,     # no
            'is_family': 0,     # no
            'is_friends': 0,    # no
            'content_type': 1,  # photo
        }

        # determine path to file to upload
        if thumbnail:
            # primarily here to speed tests/debugging
            image_filename = os.path.join(self.path, 'thumb.jpg')
        else:
            image_filename = os.path.join(self.path, 'maximum.jpg') 

        # assign title
        try:
            params['title'] = meta['title']
        except KeyError:
            logger.warning("no title found for image {0}".format(self.id))
            params['title'] = "[[ no title ]]"
        
        # assemble typology keywords as flickr tags    
        tags = []    
        try:
            tags = meta['typology']
        except KeyError:
            pass
        try:
            pid = unicode(meta['geography']['photographed-place']['uri'])
        except KeyError:
            pass
        else:
            if u'pleiades' in pid:
                pid = pid.rstrip(u'/').split(u'/')[-1].strip()
                if unicode(int(pid)) == pid:
                    pid = u'pleiades:depicts={0}'.format(pid)
                    tags.append(pid)
        if len(tags) > 0:
            params['tags'] = ' '.join([[tag, '"{0}"'.format(tag)][' ' in tag] for tag in tags])

        # assemble flickr description from metadata
        flickr_description = u""
        # description
        try:
            description = unicode(meta['description'])
        except KeyError:
            pass
        else:
            flickr_description += u"{0}.\n\n".format(description.rstrip(u'.'))
        # photographer
        try:
            photographer = meta['photographer']
        except KeyError:
            photographer_name = u'an unknown photographer'
        else:
            try:
                photographer_name = unicode(photographer['name'])
            except KeyError:
                try:
                    photographer_name = u" ".join((unicode(photographer['given-name']), unicode(photographer['family-name'])))
                except KeyError:
                    photographer_name = u'an unknown photographer'
        if 'url' in photographer.keys():
            flickr_description += u'Photographed by <a href="{0}">{1}</a>'.format(unicode(photographer['url']), photographer-name)
        else:
            flickr_description += u'Photographed by {0}'.format(photographer_name)
        # date photographed
        try:
            date_photographed = meta['date-photographed']
        except KeyError:
            date_photographed = u'unknown'
        if 'photographer_name' == u'an unknown photographer':
            flickr_description += u'\nDate photographed: {0}.'.format(date_photographed)
        else:
            flickr_description += u' ({0}).'.format(date_photographed)
        flickr_description += u'\n'
        # copyright
        try:
            copyright = u'© Copyright {0} by {1}. Used with permission.'.format(unicode(meta['copyright-date']), unicode(meta['copyright-holder']))
        except KeyError:
            pass
        else:
            flickr_description += copyright
            flickr_description += u'\n'
        # license
        # place
        try:
            place = meta['geography']['photographed-place']
            logger.debug(repr(place))
        except KeyError:
            pass
        else:
            flickr_description += u'Photographed place: '
            try:
                flickr_description += u'<a href="{0}">{1} (modern {2})</a>'.format(
                    place['uri'], place['ancient-name'], place['modern-name'])
            except KeyError:
                raise
                try:
                    flickr_description += u'<a href="{0}">{1}</a>'.format(
                        place['uri'], place['modern-name'])
                except KeyError:
                    try:
                        flickr_description += u'<a href="{0}">ancient {1}</a>'.format(
                            place['uri'], place['ancient-name'])
                    except KeyError:
                        try:
                            flickr_description += u'{0} (modern {1})'.format(
                                place['ancient-name'], place['modern-name'])
                        except KeyError:
                            try:
                                flickr_description += u'{0}'.format(place['modern-name'])
                            except KeyError:
                                flickr_description += u'ancient {0}'.format(place['ancient-name'])
            flickr_description += u'.\n'
        # authority 
        try:
            authority = unicode(meta['authority'])
        except KeyError:
            pass
        else:
            flickr_description += u'{0}'.format(authority)
            flickr_description += u'\n'

        flickr_description += u'\n'
        flickr_description += u'<i>This image has been published by the <a href="http://isaw.nyu.edu">Institute for the Study of the Ancient World</a> under the auspices of its <a href="http://isaw.nyu.edu/awib/">Ancient World Image Bank (AWIB) project</a>.</i>'
        params['description'] = flickr_description

        logger.debug("calling flickrapi.upload with params: {0}".format(repr(params)))
        response = self.flickr_api.upload(filename=image_filename, **params)
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
