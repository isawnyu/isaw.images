#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
code to create an overview html page for an image package
"""

from arglogger import arglogger
import dominate
from dominate.tags import *
import logging
import package
import sys

class Overview():
    """
    HTML overview page for isaw.images
    """

    @arglogger
    def __init__(self, path=None):
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        if path is not None:
            self.__generate__(path)
        else:
            logger.warning("Overview.init called with path=None")
    


        