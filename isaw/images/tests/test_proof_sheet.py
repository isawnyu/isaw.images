#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nosetests for creating contact sheets for isaw.images packages
tests code in isaw.images/isaw/images/proof_sheet.py
"""

from isaw.images import proof_sheet
import logging
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_is
    
logging.basicConfig(level=logging.DEBUG)

def test_instantiate_proof_sheet():
    s = proof_sheet.Proof()
    