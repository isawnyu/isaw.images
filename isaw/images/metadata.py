#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
manage metadata file
"""

from arglogger import arglogger
import json
import logging
import os
import re
import shutil
import sys
from validate_path import validate_path
import xml.etree.ElementTree as ET

# original file name? origin?
IMAGE_TAGS = {
    'IPTC' : {
        'By-line': 'photographer:name',
        # 'By-lineTitle': 'photographer:title', suppress, because gets truncated
        'Caption-Abstract': 'description',
        'Credit': 'photographer:name',
        'Source': 'description',
        'Writer-Editor': 'contributor:name',
        'ObjectName': 'title',
        'Keywords': '',     # special handling
        'CopyrightNotice': 'rights-statement',
        'DateCreated':'',     # special handling
        'TimeCreated':''     # special handling
    },
    'ExifIFD' : {
        'FileSource':'',     # special handling
        'CreateDate': '',     # special handling
        'UserComment': 'description',
        'ImageDescription': 'description',
        'Artist': 'photographer:name',
        'Copyright': 'rights-statement'
    },
    'XMP' : {
        'CreateDate': '',     # special handling
        'DateCreated': '',     # special handling
        'AuthorsPosition': 'photographer:title',
        'CaptionWriter': 'contributor:name',
        'WebStatement': 'description',
        'Description': 'description',
        'Title': 'title',
        'Creator': 'photographer:name',
        'Subject': '',     # special handling
        'Rights': 'rights-statement',
        'UsageTerms': 'license',
        'ImageCreatorName': 'photographer:name',
        'ImageCreatorID': 'photographer:uri',
        'CopyrightOwnerName': 'copyright-holder:name',
        'CopyrightOwnerID': 'copyright-holder:uri',
        'CreatorWorkEmail': 'photographer:email',
        'CreatorWorkURL': 'photographer:url',
        'LocationCreatedSublocation': 'geography:photographed-place:modern-name',
        'LocationCreatedCity': 'geography:photographed-place:modern-name',
        'LocationCreatedProvinceState': 'geography:photographed-place:modern-name',
        'LocationCreatedCountryName': 'geography:photographed-place:modern-name',
        'LocationShownSublocation': 'geography:photographed-place:modern-name',
        'LocationShownCity': 'geography:photographed-place:modern-name',
        'LocationShownProvinceState': 'geography:photographed-place:modern-name',
        'LocationShownCountryName': 'geography:photographed-place:modern-name'
    }
}

EXIF_FILESOURCE_CODES = {
    '1': 'Film Scanner',
    '2': 'Reflection Print Scanner',
    '3': 'Digital Camera'
}

TOPMETA_FRONT = [
    'status',
    'license-release-verified',
    'isaw-publish-cleared',
    'review-notes',
]

TOPMETA_BACK = [
    'change-history'
]

RPUNCT = re.compile(r"\W+")

R = re.compile(r"\s+", re.MULTILINE)
def cleanval(raw):
    try:
        cooked=raw.strip()
    except AttributeError:
        raise
    clean= R.sub(' ',cooked).strip()
    return clean

@arglogger
def dict2xml(item, parent):
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    if type(item)==dict:
        for k in item.keys():
            ele = parent.find(k)
            if ele is None:
                ele = ET.SubElement(parent, k)
            if k == 'typology':
                pass
            elif k == 'change-history':
                pass
            else:
                dict2xml(item[k], ele)
    elif type(item) == unicode or type(item) == str:
        v = cleanval(item)
        if len(v) > 0:
            parent.text = v
    else:
        logger.error("type is '{0}'".format(type(item)))
        raise TypeError

@arglogger
def xml2dict(d, element):
    if element.tag=='typology':
        dl=[]
        for child in element:
            try:
                v = cleanval(child.text)
                if len(v) > 0:
                    dl.append(v)
            except AttributeError:
                pass
        if len(dl) > 0:
            d[element.tag]=dl
    elif element.tag=='change-history':
        dl=[]
        for child in element:
            dd={}
            for grandchild in child:
                xml2dict(dd, grandchild)
            if len(dd) > 0:
                dl.append(dd)
        if len(dl) > 0:
            d[element.tag] = dl
    elif element.getchildren():
        dd={}
        for child in element:
            xml2dict(dd, child)
        if len(dd) > 0:
            d[element.tag]=dd
    else:
        try:
            v = cleanval(element.text)
            if len(v) > 0:
                d[element.tag]=v
        except AttributeError:
            pass



class Metadata():
    """
    a class for managing metadata files
    """

    @arglogger
    def __init__(self, path, create=False, exiftool_json=None):
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        self.path=os.path.realpath(path)
        if create:
            # copy template file and open it
            current = os.path.dirname(os.path.abspath(__file__))
            meta_template = os.path.join(current, 'meta', 'meta-template.xml')
            shutil.copyfile(meta_template, self.path)
            self.__read__()

            # parse any provided exiftool json into the new metadata file
            if exiftool_json is not None:
                with open(exiftool_json, 'r') as exif_file:
                    exif = json.load(exif_file)
                # figure out the source device, since that conditions how we handle some other tags
                try:
                    file_source_code = exif['ExifIFD:FileSource']
                except KeyError:
                    file_source_code = '3' # default is digital camera

                # create a conversion table from the json tags to isaw images metadata xml tags
                tagverts = []
                for vocabk in sorted(IMAGE_TAGS.keys()):
                    for termk in sorted(IMAGE_TAGS[vocabk].keys()):
                        tagverts.append((':'.join((vocabk, termk)), IMAGE_TAGS[vocabk][termk]))
                tagverts = [tagvert for tagvert in tagverts if tagvert[0] in exif.keys()]

                # create a list of xml tags to create by doing the conversions
                tags = {}
                for tagvert in tagverts:
                    etag = tagvert[0]
                    xtag = tagvert[1]
                    if etag == 'IPTC:Keywords' or etag == 'XMP:Subject':
                        if 'typology' not in tags.keys():
                            tags['typology'] = []
                        keywords = [cleanval(keyword) for keyword in exif[etag]]
                        for keyword in keywords:
                            if keyword not in tags['typology']:
                                tags['typology'].append(keyword)
                    elif etag in [
                        'EXIFIFD:CreateDate',
                        'IPTC:DateCreated',
                        'IPTC:TimeCreated',
                        'XMP:CreateDate',
                        'XMP:DateCreated'
                        ]:
                        val = exif[etag]
                        dateval = None
                        timeval = None
                        if 'T' in val:
                            dateval, timeval = val.split('T')
                        elif ' ' in val:
                            dateval, timeval = val.split(' ')
                        elif etag == 'IPTC:TimeCreated':
                            timeval = val
                        else:
                            dateval = val

                        if file_source_code == '3':
                            # digital camera
                            xmltag = 'date-photographed'
                        else:
                            xmltag = 'date-scanned'
                        if dateval is not None:
                            dateval = RPUNCT.sub('',dateval).strip()
                            dateval = '{0}-{1}-{2}'.format(dateval[0:4], dateval[4:6], dateval[6:])
                            if xmltag not in tags.keys():
                                tags[xmltag] = dateval
                            elif len(tags[xmltag]) == 0:
                                tags[xmltag] = dateval
                            elif tags[xmltag][0] == 'T':
                                tags[xmltag] = dateval + tags[xmltag]
                            elif 'T' in tags[xmltag]:
                                olddateval, oldtimeval = tags[xmltag].split('T')
                                if olddateval != dateval:
                                    raise Exception
                                else:
                                    tags[xmltag] = dateval + 'T' + oldtimeval
                            elif tags[xmltag] != dateval:
                                raise Exception
                        if timeval is not None:
                            timeval = 'T{0}'.format(timeval)
                            if xmltag not in tags.keys():
                                tags[xmltag] = timeval
                            elif len(tags[xmltag]) == 0:
                                tags[xmltag] = timeval
                            elif tags[xmltag][0] == 'T':
                                olddateval = tags[xmltag]
                                if len(olddateval) < len(timeval):
                                    if timeval[0:len(olddateval)] != tags[xmltag]:
                                        raise Exception
                                    else:
                                        tags[xmltag] = timeval
                                elif len(olddateval) > len(timeval):
                                    if olddateval[0:len(timeval)] != timeval:
                                        raise Exception
                                elif tags[xmltag] != timeval:
                                    raise Exception
                            elif 'T' in tags[xmltag]:
                                olddateval, oldtimeval = tags[xmltag].split('T')
                                oldtimeval = 'T' + oldtimeval
                                if len(oldtimeval) < len(timeval):
                                    if timeval[0:len(oldtimeval)] != oldtime:
                                        raise Exception
                                    else:
                                        tags[xmltag] = olddateval + timeval
                                elif len(oldtimeval) > len(timeval):
                                    if oldtimeval[0:len(timeval)] != timeval:
                                        logger.debug("oldtimeval: '{0}'".format(oldtimeval))
                                        logger.debug("timeval: '{0}'".format(timeval))
                                        if '+' in oldtimeval and not('+' in timeval):
                                            oldtimeval, tz = oldtimeval.split('+')
                                            if oldtimeval != timeval:
                                                if '.' in timeval and not('.' in oldtimeval):
                                                    timeval, timedecimal = timeval.split('.')
                                                    if timeval == oldtimeval:
                                                        tags[xmltag] = '+'.join(('.'.join((timeval,timedecimal)), tz))
                                        else:
                                            raise Exception
                                elif oldtimeval != timeval:
                                    raise Exception
                            elif len(tags[xmltag]) != 10:
                                raise Exception
                            else:
                                tags[xmltag] = tags[xmltag] + timeval
                    elif xtag == '':
                        # skip blanks because they are handled programmatically
                        logger.warning("skipped processing {0}".format(xtag))
                    else:
                        if xtag not in tags.keys():
                            tags[xtag] = ''
                        if cleanval(exif[etag]) not in tags[xtag]:
                            tags[xtag] += ' ' + exif[etag]
                        tags[xtag] = cleanval(tags[xtag])

                # write the conversions to the xml metadata file
                
                for k in sorted(tags.keys()):
                    if ':' in k:
                        hierarchy = k.split(':')
                        logger.debug("setting hierarchy for {0}".format(k))
                        self.set_hierarchy(hierarchy, tags[k])
                        logger.debug("writing to original")
                        self.__write__('original')
                    else:
                        logger.debug("setting {0}".format(k))
                        self.set(k, tags[k])
                        logger.debug("writing to original")
                        self.__write__('original')
                
        else:
            self.__read__()



    @arglogger
    def __read__(self):
        self.data={}
        try:
            validate_path(self.path)
        except IOError:
            raise    
        tree=ET.parse(self.path)    
        root= tree.getroot()
        for child in root:
            if child.tag=='info':
                if child.attrib['type']=='isaw':
                    for subchild in child:
                        xml2dict(self.data, subchild)
            else:
                xml2dict(self.data, child)
        return len(self.data)

    @arglogger
    def __write__(self, info_type='isaw'):
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        # split dictionary into top-level and info-level items
        topfd = {k:v for (k,v) in self.data.iteritems() if k in TOPMETA_FRONT}
        topbd = {k:v for (k,v) in self.data.iteritems() if k in TOPMETA_BACK}
        infod = {k:v for (k,v) in self.data.iteritems() if k not in TOPMETA_FRONT and k not in TOPMETA_BACK}
        tree=ET.parse(self.path)    
        root= tree.getroot()
        dict2xml(topfd, root)
        for child in root:
            if child.tag=='info':
                if child.attrib['type']==info_type:
                    dict2xml(infod, child)
        dict2xml(topbd, root)
        #logger.debug("info_type={0}".format(info_type))
        #logger.debug(ET.tostring(root))
        tree.write(self.path, encoding="UTF-8")

    @arglogger
    def set(self, key, value, flush=True, isaw_info=True, original_info=False):
        self.data[key]=value
        if flush:
            if isaw_info:
                self.__write__()
            if original_info:
                self.__write__('original')

    @arglogger
    def set_hierarchy(self, keys, value, d=None, flush=True, isaw_info=True, original_info=False, level=0):
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        if d is None:
            logger.debug("setting hierarchy dict == self.data")
            d = self.data
        if len(keys) == 1:
            logger.debug("only one item in keys ({0}); setting = '{1}'".format(keys[0], value))
            d[keys[0]]=value
        else:
            if keys[0] in d.keys():
                if type(d[keys[0]] == dict):
                    logger.debug("first key ({0}) yields a dictionary, recursing with child structure".format(keys[0]))
                    d[keys[0]]=self.set_hierarchy(keys[1:], value, d[keys[0]], level=level+1)
                else:
                    logger.error("first key {0} does not yield a dictionary!".format(keys[0]))
                    raise TypeError
            else:
                logger.debug("first key ({0}) is not in the parent dict, so recursing with a new dict".format(keys[0]))
                d[keys[0]]=self.set_hierarchy(keys[1:], value, {}, level=level+1)
        if level == 0:
            if flush:
                if isaw_info:
                    self.__write__()
                if original_info:
                    self.__write__('original')
        return d

    @arglogger
    def add_keyword(self, keyword):
        try:
            l=self.data['typology']
        except KeyError:
            l=[]
        l.append(keyword)
        self.data['typology']=l

    @arglogger
    def get(key, value):
        return self.data[filename]

    @arglogger
    def get_all(self):
        """
        get a *copy* of the full manifest data dictionary
        """
        d = dict(self.data)
        return d

    @arglogger
    def remove(self, key):
        del self.data[key]
        self.__write__()


