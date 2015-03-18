#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
code to create an HTML proof sheet from a folder full of isaw.image packages
"""

from arglogger import arglogger
import logging

class Proof():
    """
    HTML proof sheet for isaw.images
    """

    @arglogger
    def __init__(self, path=None):
        if path is not None:
            pass
