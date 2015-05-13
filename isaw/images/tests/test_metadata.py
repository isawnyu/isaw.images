#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nosetests for metadata.py
"""

from isaw.images import metadata, package
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_is
import logging
import os
from pprint import pprint
import re
import shutil

logging.basicConfig(level=logging.DEBUG)

RWHITESPACE = re.compile(r"\s+", re.MULTILINE)
RDQUOTES = re.compile(r"\"")

def test_read_metadata():
    current = os.path.dirname(os.path.abspath(__file__))
    meta_path = os.path.join(current, 'data', 'kalabsha', '201107061813531', 'meta.xml')
    m = metadata.Metadata(meta_path)
    assert_equals(sorted(m.data.keys()), ['change-history', 'copyright-date', 'copyright-holder', 'date-photographed', 'description', 'flickr-url', 'geography', 'isaw-publish-cleared', 'license', 'license-release-verified', 'photographer', 'status', 'title', 'typology'])    
    del m

def test_create_metadata():
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    meta_path=os.path.join(temp, 'meta.xml')
    # by default, the file should *not* get created, and throws an error if not found
    try:
        m=metadata.Metadata(meta_path)
    except IOError:
        pass
    assert_equals(os.path.isfile(meta_path), False)
    # we can force creation of the file, if desired
    m=metadata.Metadata(meta_path, create=True)
    assert_equals(os.path.isfile(meta_path), True)
    assert_equals(m.data, {'status': 'draft', 'license': 'undetermined', 'isaw-publish-cleared': 'no', 'license-release-verified': 'no'})    
    with open(meta_path, 'r') as f:
        guts = f.read()
    guts = RWHITESPACE.sub('', guts).strip()
    guts = RDQUOTES.sub('', guts)
    assert_equals(guts, "<?xmlversion=1.0encoding=UTF-8?><?xml-stylesheettype=text/csshref=meta-oxygen.csstitle=OxygenAuthoringCSSalternate=no?><?oxygenRNGSchema=meta-schema.rnctype=compact?><image-info><status>draft</status><license-release-verified>no</license-release-verified><isaw-publish-cleared>no</isaw-publish-cleared><review-notes></review-notes><image-files><imagetype=thumbnailhref=></image><imagetype=reviewhref=></image><imagetype=masterhref=></image><imagetype=originalhref=></image></image-files><infotype=original><original-file-name></original-file-name><origin>undetermined</origin><title></title><flickr-url></flickr-url><fda-handle></fda-handle><photographer><name></name></photographer><authority></authority><description></description><date-photographed></date-photographed><date-scanned></date-scanned><copyright-holder></copyright-holder><copyright-date></copyright-date><copyright-contact></copyright-contact><license>undetermined</license></info><infotype=isaw><title></title><flickr-url></flickr-url><fda-handle></fda-handle><photographer><given-name></given-name><family-name></family-name></photographer><authority></authority><description></description><date-photographed></date-photographed><date-scanned></date-scanned><copyright-holder></copyright-holder><copyright-date></copyright-date><copyright-contact></copyright-contact><license>undetermined</license><geography><photographed-place><ancient-name></ancient-name><modern-name></modern-name><uri></uri><institution></institution></photographed-place><find-place></find-place><original-place></original-place></geography><chronology></chronology><prosopography></prosopography><typology></typology><notes></notes></info><change-history></change-history></image-info>")
    del m
    shutil.rmtree(temp)
    # test with package creation and import of an image containing lots of metadata
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'oracle.jpg')
    p = package.Package(temp, 'test_package', original_path)    
    m = p.metadata
    d = m.data
    assert_equals(sorted(d.keys()), ['contributor', 'date-photographed', 'description', 'isaw-publish-cleared', 'license', 'license-release-verified', 'photographer', 'rights-statement', 'status', 'title', 'typology'])
    assert_equals(d['contributor']['name'], u'Tom Elliott')
    assert_equals(d['date-photographed'], '2014-11-15T17:39:19.457+00:00')
    assert_equals(d['description'], u'Interior of a Magic Hat #9 beer bottle cap bearing the slogan: "Banana costumes, by nature, are funny."')
    assert_equals(d['isaw-publish-cleared'], 'no')
    assert_equals(d['license'], u'https://creativecommons.org/licenses/by/3.0/us/')
    assert_equals(d['license-release-verified'], 'no')
    assert_equals(d['photographer']['email'], u'tom.elliott@nyu.edu')
    assert_equals(d['photographer']['name'], u'Tom Elliott')
    assert_equals(d['photographer']['title'], u'Associate Director for Digital Programs and Senior Research Scholar')
    assert_equals(d['photographer']['url'], u'http://www.paregorios.org/')
    assert_equals(d['rights-statement'], u'Copyright 2014. Tom Elliott')
    assert_equals(d['status'], 'draft')
    assert_equals(d['title'], u'The Oracle')
    assert_equals(sorted(d['typology']), [u'aphorisms', u'banana costumes', u'bananas', u'beer', u'bottle cap', u'costumes', u'humor', u'Magic Hat'])
    with open(m.path, 'r') as f:
        guts = f.read()
    guts = RWHITESPACE.sub('', guts).strip()
    guts = RDQUOTES.sub('', guts)
    assert_equals(guts, "<?xmlversion='1.0'encoding='UTF-8'?><image-info><status>draft</status><license-release-verified>no</license-release-verified><isaw-publish-cleared>no</isaw-publish-cleared><review-notes/><image-files><imagehref=type=thumbnail/><imagehref=type=review/><imagehref=type=master/><imagehref=type=original/></image-files><infotype=original><original-file-name/><origin>undetermined</origin><title>TheOracle</title><flickr-url/><fda-handle/><photographer><name>TomElliott</name><email>tom.elliott@nyu.edu</email><title>AssociateDirectorforDigitalPAssociateDirectorforDigitalProgramsandSeniorResearchScholar</title><url>http://www.paregorios.org/</url></photographer><authority/><description>InteriorofaMagicHat#9beerbottlecapbearingtheslogan:Bananacostumes,bynature,arefunny.</description><date-photographed>2014-11-15T17:39:19.457+00:00</date-photographed><date-scanned/><copyright-holder/><copyright-date/><copyright-contact/><license>https://creativecommons.org/licenses/by/3.0/us/</license><contributor><name>TomElliott</name></contributor><rights-statement>Copyright2014.TomElliott</rights-statement><typology/></info><infotype=isaw><title>TheOracle</title><flickr-url/><fda-handle/><photographer><given-name/><family-name/><email>tom.elliott@nyu.edu</email><name>TomElliott</name><title>AssociateDirectorforDigitalPAssociateDirectorforDigitalProgramsandSeniorResearchScholar</title><url>http://www.paregorios.org/</url></photographer><authority/><description>InteriorofaMagicHat#9beerbottlecapbearingtheslogan:Bananacostumes,bynature,arefunny.</description><date-photographed>2014-11-15T17:39:19.457+00:00</date-photographed><date-scanned/><copyright-holder/><copyright-date/><copyright-contact/><license>https://creativecommons.org/licenses/by/3.0/us/</license><geography><photographed-place><ancient-name/><modern-name/><uri/><institution/></photographed-place><find-place/><original-place/></geography><chronology></chronology><prosopography></prosopography><typology></typology><notes></notes><contributor><name>TomElliott</name></contributor><rights-statement>Copyright2014.TomElliott</rights-statement></info><change-history></change-history></image-info>")
    shutil.rmtree(temp)


