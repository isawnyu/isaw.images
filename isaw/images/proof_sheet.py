#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
code to create an HTML proof sheet from a folder full of isaw.image packages
"""

from arglogger import arglogger
import dominate
from dominate.tags import *
import logging
import os
import package
import sys

class Proof():
    """
    HTML proof sheet for isaw.images
    """

    @arglogger
    def __init__(self, path=None):
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        if path is not None:
            self.__generate__(path)
        else:
            logger.warning("Proof.init called with path=None")

    @arglogger
    def __generate__(self, path):
        """
        create the proof sheet
        """
        #self.doc = dominate.document(title='Proof Sheet: {0}'.format(path))
        # get a list of all the directories at path and determine which are image packages
        directories = [o for o in os.listdir(path) if os.path.isdir(os.path.join(path,o))]
        self.packages = []
        self.other_directories = []
        for d in directories:
            p = package.Package()
            try:
                p.open(os.path.join(path,d))
            except IOError:
                self.other_directories.append(d)
            else:
                if p.validate():
                    self.packages.append(p)
                else:
                    self.other_directories.append(p)


        

