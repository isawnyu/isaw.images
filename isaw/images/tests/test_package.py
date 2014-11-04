#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nose tests for code in isaw.images/isaw/images/package.py
"""

from io import BytesIO
from isaw.images import package
import logging
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_not_in, assert_is
import os
from PIL import Image
from PIL.ImageCms import getOpenProfile, getProfileName
import shutil

logging.basicConfig(level=logging.DEBUG)

def test_instantiate_package():
    p = package.Package()

def test_create_package():
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'turkey_road.jpg')

    # are all component files for the package created?
    p = package.Package(temp, 'test_package', original_path)
    manifest_path = os.path.join(temp, 'test_package', 'manifest-sha1.txt')
    assert_equals(os.path.isfile(manifest_path), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'history.txt')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'original.jpg')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'original.sha1')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'original-exif.json')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'original-exif.sha1')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'master.tif')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'master.sha1')), True)

    # does manifest file contain expected content (TBD)

    # are ICC color profiles handled as expected
    # i.e., assumed/forced to sRGBv2 in original and converted to sRGBv4 in master
    im = Image.open(original_path)
    assert_not_in('icc_profile', im.info.keys())
    im = Image.open(os.path.join(temp, 'test_package', 'original.jpg'))
    assert_not_in('icc_profile', im.info.keys())
    im = Image.open(os.path.join(temp, 'test_package', 'master.tif'))
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'sRGB v4 ICC preference perceptual intent beta')

    p = None
    shutil.rmtree(temp)

def test_create_with_profile():
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')

    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'turkey_road_adobergb.tif')
    im = Image.open(original_path)
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'Adobe RGB (1998)')
    p = package.Package(temp, 'test_package', original_path)
    p = None
    im = Image.open(os.path.join(temp, 'test_package', 'original.tif'))
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'Adobe RGB (1998)')
    im = Image.open(os.path.join(temp, 'test_package', 'master.tif'))
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'sRGB v4 ICC preference perceptual intent beta')
    shutil.rmtree(temp)

    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'turkey_road_srgb.tif')
    im = Image.open(original_path)
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'IEC 61966-2.1 Default RGB colour space - sRGB')
    p = package.Package(temp, 'test_package', original_path)
    p = None
    im = Image.open(os.path.join(temp, 'test_package', 'original.tif'))
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'IEC 61966-2.1 Default RGB colour space - sRGB')
    im = Image.open(os.path.join(temp, 'test_package', 'master.tif'))
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'sRGB v4 ICC preference perceptual intent beta')
    shutil.rmtree(temp)


