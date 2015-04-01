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

def test_read_metadata():
    current = os.path.dirname(os.path.abspath(__file__))
    meta_path = os.path.join(current, 'data', 'kalabsha', '201107061813531', 'meta.xml')
    m=metadata.Metadata(meta_path)
    assert_equals(m.data, {'status': 'ready', 'isaw-publish-cleared': 'yes', 'license': 'cc-by', 'title': 'The Temple at Kalabsha (I)', 'photographer': {'given-name': 'Iris', 'family-name': 'Fernandez'}, 'copyright-holder': 'Iris Fernandez', 'flickr-url': 'http://www.flickr.com/photos/isawnyu/5913197834/in/set-72157627140459102', 'copyright-date': '2009-02-27', 'date-photographed': '2009-02-27', 'change-history': [{'date': '2011-07-06', 'description': 'created this metadata file automatically, using (where available) information extracted from the original image headers', 'agent': 'script'}, {'date': '2011-07-06', 'description': 'entered in isaw information, geography and typology, and uploaded to Flickr.', 'agent': 'Nate Nagy'}], 'license-release-verified': 'yes', 'geography': {'photographed-place': {'modern-name': 'Kalabsha', 'ancient-name': 'Talmis', 'uri': 'http://pleiades.stoa.org/places/795868'}}, 'typology': ['ancient', 'history', 'civilization', 'Egypt', 'Egyptology', 'Talmis', 'Kalabsha', 'temple', 'Roman', 'Nile', 'architecture', 'masonry', 'stone', 'mandulis', 'structure', 'pylon'], 'description': 'The pylon and sacred walkway of the Roman-era temple at Kalabsha, now located at New Kalabsha after being moved from ancient Talmis.'})
    del m    
