#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nosetests for creating contact sheets for isaw.images packages
tests code in isaw.images/isaw/images/proof_sheet.py
"""

from isaw.images import proof_sheet
import logging
from nose.tools import assert_equals, assert_not_equal, assert_in, assert_is
import os
from isaw.images import package
import shutil

logging.basicConfig(level=logging.DEBUG)

def test_instantiate_proof_sheet():
    """
    verify that we can instantiate a proof_sheet.Proof object
    """
    s = proof_sheet.Proof()

def test_generate_proof_sheet():
    """
    create a directory containing some packages and see if we can generate a proof_sheet.Proof
    """

    # set up the test directory and its contents
    current = os.path.dirname(os.path.abspath(__file__))
    temp = os.path.join(current, 'temp')
    os.makedirs(temp)
    original_path = os.path.join(current, 'data', 'turkey_road.jpg')
    for x in range(0, 3):
        p = package.Package(temp, 'test{0}'.format(x), original_path)

    # try to generate the proof sheet
    s = proof_sheet.Proof(temp)
    
    # clean up the test/temp directory
    shutil.rmtree(temp)
