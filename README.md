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

 * original-exif.json = a dump of all the EXIF data found in the original image at time of import (if any), extracted with EXIFTool and dumped to disk in its default JSON output serialization.

 * original-exif.sha1 = file containing the sha1 hash for original.[EXT], to be used for fixity tests etc.

 * master.tif = a TIFF file created from original.[EXT] at time of import. The main purpose of this file is to provide a color-managed, digital-preservation-friendly version of the image, captured as early as possible in the lifecycle. The only changes made to the image in converting from original to TIFF are the format itself and the conversion from the original color profile (if any) to the [sRGB v4 Preference Profile](http://www.color.org/srgbprofiles.xalter#v4pref).

 * master.sha1 = file containing the sha1 hash for master.tif, to be used for fixity tests etc.

 * history.txt = a text file to which is appended a single-line notice about each major change to the IIP

Classes and Methods
--------------------

to be added...



