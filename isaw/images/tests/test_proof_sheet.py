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
    del s

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
    os.makedirs(os.path.join(temp, 'foobar'))

    # try to generate the proof sheet
    s = proof_sheet.Proof(temp)

    # the proof sheet should find 3 packages and one other directory
    assert_equals(len(s.packages), 3) 
    assert_equals(len(s.other_directories), 1)

    # get rid of that proof sheet, mess up a package, try again
    del s
    f = open(os.path.join(temp, 'test1', 'master.tif'), 'w')
    f.write("foo")
    f.close()
    s = proof_sheet.Proof(temp)
    assert_equals(len(s.packages), 2) 
    assert_equals(len(s.other_directories), 2)
    del s
    
    # clean up the test/temp directory
    shutil.rmtree(temp)
