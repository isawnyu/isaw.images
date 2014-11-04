isaw.images
===========

By Tom Elliott (tom.elliott@nyu.edu)

Copyright 2014 New York University.

For rights and licensing, see LICENSE.txt file.

This package is intended to house various routines for managing ISAW's imagery collections. 

Filesystem Structure
---------------------

We start with a filesystem structure for for managing each notional image as an "isaw image package" (IIP): a directory that contains multiple files related to a single notional image. This IIP directory has the following components:

 * manifest-sha1.txt = a text file containing filenames and corresponding sha1 hashes for each file in the IIP

 * original.[EXT] = the unchanged original image file, in whatever its original format, the only changes being: normalizing the filename to the string "original" and lower-casing the extension

 * original.sha1 = file containing the sha1 hash for original.[EXT], to be used for fixity tests, etc.

 * original-exif.json = a dump of all the EXIF data found in the original image at time of import (if any), extracted with EXIFTool and dumped to disk in its default JSON output serialization.

 * original-exif.sha1 = file containing the sha1 hash for original-exif.json, to be used for fixity tests etc.

 * master.tif = a TIFF file created from original.[EXT] at time of import. The main purpose of this file is to provide a color-managed, digital-preservation-friendly version of the image, captured as early as possible in the lifecycle. The only changes made to the image in converting from original to TIFF are the format itself and the conversion from the original color profile (if any) to the [sRGB v4 Preference Profile](http://www.color.org/srgbprofiles.xalter#v4pref).

 * master.sha1 = file containing the sha1 hash for master.tif, to be used for fixity tests etc.

 * history.txt = a text file to which is appended a single-line notice about each major change to the IIP

Dependencies
-------------

This software has been tested under Python 2.7.8 running on Mac OSX 10.9.5 in a virtual environment. The following packages are installed:

 * nose 1.3.3, installed with pip
 
 * wsgiref 0.1.2, auto-installed with nose
 
 * a fork of head thread of Pillow, installed with pip -e from a local clone of https://github.com/paregorios/Pillow
 
 * pyexiftool, installed with pip -e from a local clone of git://github.com/smarnach/pyexiftool.git because it's not in pypi


Classes and Methods
--------------------

The Package class, defined in isaw/images/package.py, provides the brains for managing ISAW Image Packages on a local filesystem. It defines the following outward-facing methods:

 * create: create a new image package at the targeted path (implemented: see isaw/images/tests/test_package.py)

 * open: open an existing image package at the targeted path (stubbed, but not yet implemented)

 * delete: delete the current image package (stubbed, but not yet implemented): assumes Package.open() has already been called.

 * validate: verify completeness and fixity of the current package (stubbed, but not yet implemented): assumes Package.open() has already been called.



