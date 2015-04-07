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
import re
import shutil
import textwrap

logging.basicConfig(level=logging.DEBUG)

RWHITESPACE = re.compile(r"\s+", re.MULTILINE)
RDQUOTES = re.compile(r"\"")

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
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'original-exif.json')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'master.tif')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'preview.jpg')), True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'thumb.jpg')), True)
    
    # make sure the open manifest dict is as expected
    filenames = sorted(p.manifest.get_all().keys())
    assert_equals(len(filenames),6)
    assert_in('history.txt', filenames[0])
    assert_in('master.tif', filenames[1])    
    assert_in('original-exif.json', filenames[2])
    assert_in('original.jpg', filenames[3])
    assert_in('preview.jpg', filenames[4])
    assert_in('thumb.jpg', filenames[5])

    # does manifest file contain expected content
    with open(manifest_path, 'r') as mf:
        manifest=mf.readlines()
    assert_equals(len(manifest),6)
    assert_in('history.txt', manifest[0])
    assert_in('master.tif', manifest[1])
    assert_in('original-exif.json', manifest[2])
    assert_in('original.jpg', manifest[3])
    assert_in('preview.jpg', manifest[4])
    assert_in('thumb.jpg', manifest[5])

    # are ICC color profiles handled as expected
    # i.e., assumed/forced to sRGBv2 in original and converted to sRGBv4 in master
    im = Image.open(original_path)
    assert_not_in('icc_profile', im.info.keys())
    im = Image.open(os.path.join(temp, 'test_package', 'original.jpg'))
    assert_not_in('icc_profile', im.info.keys())
    im = Image.open(os.path.join(temp, 'test_package', 'master.tif'))
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'sRGB v4 ICC preference perceptual intent beta')
    im = Image.open(os.path.join(temp, 'test_package', 'preview.jpg'))
    assert_in('icc_profile', im.info.keys())
    assert_equals(getProfileName(getOpenProfile(BytesIO(im.info['icc_profile']))).strip(), 'sRGB v4 ICC preference perceptual intent beta')
    im = Image.open(os.path.join(temp, 'test_package', 'thumb.jpg'))
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

def test_open_package():
    # create a package in the temp directory
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'turkey_road.jpg')
    p = package.Package(temp, 'test_package', original_path)    
    # try to open the package we just created
    pp = package.Package()
    pp.open(os.path.join(temp, 'test_package'))
    # make sure the manifest file is as expected
    filenames = sorted(pp.manifest.get_all().keys())
    assert_equals(len(filenames),6)
    assert_in('history.txt', filenames[0])    
    assert_in('master.tif', filenames[1])    
    assert_in('original-exif.json', filenames[2])
    assert_in('original.jpg', filenames[3])
    assert_in('preview.jpg', filenames[4])
    assert_in('thumb.jpg', filenames[5])
    # did id get set?
    assert_equals(pp.id, 'test_package')
    shutil.rmtree(temp)

def test_validate_package():
    # create and open a package in the temp directory
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'turkey_road.jpg')
    p = package.Package(temp, 'test_package', original_path)    
    del p
    pp = package.Package()
    # trying to validate before open should fail
    assert_equals(pp.validate(), False)
    # opening a properly created package should succeed
    pp.open(os.path.join(temp, 'test_package'))
    assert_equals(pp.validate(), True)
    # clobber a file in that package; opening it should fail
    del pp
    f = open(os.path.join(temp, 'test_package', 'master.tif'), 'w')
    f.write("foo")
    f.close()
    pp = package.Package()
    pp.open(os.path.join(temp, 'test_package'))
    assert_equals(pp.validate(), False)
    del pp

    shutil.rmtree(temp)

def test_make_derivatives():
    # create a package in the temp directory
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'kalabsha', '201107061813531', 'master.tif')
    p = package.Package(temp, 'test_package', original_path)    
    # make derivatives should just work if there aren't any yet (which there aren't)
    p.make_derivatives()
    assert_equals(p.thumbnail, True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'thumb.jpg')), True)
    assert_equals(p.preview, True)
    assert_equals(os.path.isfile(os.path.join(temp, 'test_package', 'preview.jpg')), True)
    # make derivatives should say 'no' if the derviative files already exist
    assert_equals(p.make_derivatives(), False)
    # make derivatives should go ahead and work if we override
    assert_equals(p.make_derivatives(overwrite=True), True)
    del p
    # verify that manifest file was correctly written
    manifest_path = os.path.join(temp, 'test_package', 'manifest-sha1.txt')
    try:
        manifest_file = open(manifest_path, "r")
    except IOError:
        raise IOError("could not open package manifest file at {0}".format(manifest_path))
    manifest = manifest_file.readlines()
    manifest_file.close()
    assert_equals(len(manifest),6)
    assert_in('preview.jpg', manifest[4])
    assert_in('thumb.jpg', manifest[5])
    shutil.rmtree(temp)

def test_make_overview():
    # create a package in the temp directory
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'turkey_road.jpg')
    p = package.Package(temp, 'test_package', original_path)    
    # package creation should have created an overview with expected contents
    overview_path = os.path.join(current, 'temp', 'test_package', 'index.html')
    assert_equals(os.path.isfile(overview_path), True)
    with open(overview_path, 'r') as f:
        guts = f.read()
    guts = RWHITESPACE.sub('', guts).strip()
    guts = RDQUOTES.sub('', guts)
    assert_equals(guts, "<!DOCTYPEhtml><html><head><title>Overview'test_package'</title><style>body{background-color:#F9F9F9;padding:10px;font-family:Arial,sans-serif;}.image{float:right;margin-left:10px;}img{border:1pxsolid#CCCCCC;box-shadow:1px1px1pxrgba(255,255,255,0.25)inset,0px1px2pxrgba(0,0,0,0.5);}.metadatap,.metadataul{margin-bottom:0.25em;margin-top:0px;}.metadatap{padding-left:2em;text-indent:-2em;}</style></head><body><h1>Overviewfor'test_package'</h1><divclass=image><imgalt=previewofimagewithid='test_package'src=preview.jpg></div><divclass=metadata><p>id:test_package</p><p>title:[[notitle]]</p><p>status:draft</p><p>isaw-publish-cleared:no</p><p>license:undetermined</p><p>license-release-verified:no</p><p>copyright:[[nocopyright]]</p><p>copyright-holder:[[nocopyright-holder]]</p><p>copyright-date:[[nocopyright-date]]</p><p>photographer:Picasa</p><p>date-photographed:[[nodate-photographed]]</p><p>description:Moontownroadalbum</p><p>geography:[[nogeography]]</p><p>typology:[[notypology]]</p><p>change-history:[[nochange-history]]</p></div></body></html>")
    # get rid of that package and open one that's got some metadata
    shutil.rmtree(temp)
    os.makedirs(temp)
    srcpath = os.path.join(current, 'data', 'kalabsha', '201107061813531')
    destpath = os.path.join(temp, '201107061813531')
    shutil.copytree(srcpath, destpath)
    assert_equals(os.path.isdir(destpath), True)
    p = package.Package()
    p.open(destpath)
    overview_path = os.path.join(destpath, 'index.html')
    assert_equals(os.path.isfile(overview_path), True)
    with open(overview_path, 'r') as f:
        guts = f.read()
    guts = RWHITESPACE.sub('', guts).strip()
    guts = RDQUOTES.sub('', guts)
    assert_equals(guts, "<!DOCTYPEhtml><html><head><title>Overview'201107061813531'</title><style>body{background-color:#F9F9F9;padding:10px;font-family:Arial,sans-serif;}.image{float:right;margin-left:10px;}img{border:1pxsolid#CCCCCC;box-shadow:1px1px1pxrgba(255,255,255,0.25)inset,0px1px2pxrgba(0,0,0,0.5);}.metadatap,.metadataul{margin-bottom:0.25em;margin-top:0px;}.metadatap{padding-left:2em;text-indent:-2em;}</style></head><body><h1>Overviewfor'201107061813531'</h1><divclass=image><imgalt=previewofimagewithid='201107061813531'src=preview.jpg></div><divclass=metadata><p>id:201107061813531</p><p>title:TheTempleatKalabsha(I)</p><p>status:ready</p><p>isaw-publish-cleared:yes</p><p>license:cc-by</p><p>license-release-verified:yes</p><p>copyright:[[nocopyright]]</p><p>copyright-holder:IrisFernandez</p><p>copyright-date:2009-02-27</p><p>photographer:IrisFernandez</p><p>date-photographed:2009-02-27</p><p>description:ThepylonandsacredwalkwayoftheRoman-eratempleatKalabsha,nowlocatedatNewKalabshaafterbeingmovedfromancientTalmis.</p><p>photographedplace:<ahref=http://pleiades.stoa.org/places/795868>Kalabsha,ancientTalmis</a></p><p>typology:<ul><li>ancient</li><li>architecture</li><li>civilization</li><li>Egypt</li><li>Egyptology</li><li>history</li><li>Kalabsha</li><li>mandulis</li><li>masonry</li><li>Nile</li><li>pylon</li><li>Roman</li><li>stone</li><li>structure</li><li>Talmis</li><li>temple</li></ul></p><p>changehistory:<ul><li>2011-07-06:scriptcreatedthismetadatafileautomatically,using(whereavailable)informationextractedfromtheoriginalimageheaders</li><li>2011-07-06:NateNagyenteredinisawinformation,geographyandtypology,anduploadedtoFlickr.</li></ul></p></div></body></html>")
    shutil.rmtree(temp)
