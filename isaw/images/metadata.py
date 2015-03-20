#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
manage metadata file
"""

from arglogger import arglogger
import logging
import os
import re
from validate_path import validate_path
import xml.etree.ElementTree as ET

R = re.compile(r"\s+", re.MULTILINE)
def cleanval(raw):
    try:
        cooked=raw.strip()
    except AttributeError:
        raise
    clean= R.sub(' ',cooked)
    return clean


def xml2dict(d, element):
    if element.tag=='typology':
        dl=[]
        for child in element:
            try:
                dl.append(cleanval(child.text))
            except AttributeError:
                pass
        if len(dl) > 0:
            d[element.tag]=dl
    elif element.getchildren():
        dd={}
        for child in element:
            xml2dict(dd, child)
        if len(dd) > 0:
            d[element.tag]=dd
    else:
        try:
            d[element.tag]=cleanval(element.text)
        except AttributeError:
            pass



class Metadata():
    """
    a class for managing metadata files
    """

    @arglogger
    def __init__(self, path, create=False):
        self.path=os.path.realpath(path)
        if create:
            open(self.path, 'w').close()
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
    def __write__(self):
        pass

    @arglogger
    def set(self, key, value):
        self.data[filename]=filehash
        self.__write__()

    @arglogger
    def set_photographer(self, given_name=None, family_name=None, viaf_id=None, name_string=None):
        d={}
        if given_name is not None:
            d['given-name']=given_name
        if family_name is not None:
            d['family-name']=family_name
        if viaf_id is not None:
            d['viaf-id']=viaf_id
        if name_string is not None:
            d['name']=name_string
        self.data['photographer']=d
        self.__write__()

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


