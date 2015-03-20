#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
utility functions to create and exploit file checksums
"""

import hashlib
import shutil

def hash_of_file(filepath):
    """
    generate sha1 hash for a file
    """
    with open(filepath, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()

def safe_copy(src, dest, tries=2):
    """
    verify checksums on file copy
    """
    i = 0
    while i < tries:
        hash_src = hash_of_file(src)
        shutil.copy2(src, dest)
        hash_dest = hash_of_file(dest)
        if hash_src == hash_dest:
            return hash_dest
        i += 1
    raise IOError("could not verify safe-copy from {source} to {dest}".format(source=src, dest=dest))

