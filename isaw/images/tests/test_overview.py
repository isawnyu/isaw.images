#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nosetests for overview.py: html overview pages for image packages
"""

from isaw.images import overview
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_is
import logging
import os
import shutil

logging.basicConfig(level=logging.DEBUG)

def test_instantiate_overview():
    o = overview.Overview()
    