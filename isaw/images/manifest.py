#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
manage manifest file
"""

from arglogger import arglogger
from filehashing import hash_of_file
import logging
import os
from validate_path import validate_path

class Manifest():
    """
    a class for managing manifest files
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
        with open(self.path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            filehash, filename = line.split()
            self.data[filename.strip()]=filehash.strip()
        return len(self.data)

    @arglogger
    def __write__(self):
        with open(self.path, 'w') as f:
            for filename in sorted(self.data.keys()):
                line = "{0} {1}\n".format(self.data[filename], filename)
                f.write(line)

    @arglogger
    def regenerate(self, create=False):
        """
        generates a bagit-style manifest for all files in the directory
        warning: overwrites!
        """
        # assumes there is an existing manifest-sha1.txt file, either legacy
        # or because this manifest object was instantiated with create=True
        if create:
            self.data={}
        dirpath = os.path.dirname(self.path)
        filenames = [o for o in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath,o))]
        for filename in filenames:
            if filename not in ['manifest-sha1.txt', '.DS_Store']:
                filehash = hash_of_file(os.path.join(dirpath,filename))
                self.set(filename, filehash)

    @arglogger
    def set(self, filename, filehash):
        self.data[filename]=filehash
        self.__write__()

    @arglogger
    def get(self, filename):
        return self.data[filename]

    @arglogger
    def get_all(self):
        """
        get a *copy* of the full manifest data dictionary
        """
        d = dict(self.data)
        return d

    @arglogger
    def remove(self, filename):
        del self.data[filename]
        self.__write__()


