isaw.images
===========

By Tom Elliott (tom.elliott@nyu.edu) and Uttara Chavan.

Copyright 2014, 2015 New York University.

For rights and licensing, see LICENSE.txt file.

This package is intended to house various routines for managing the digital imagery collections of the [Institute for the Study of the Ancient World](http://isaw.nyu.edu) at New York University. It manages "image packages" on the file system: each notional image is housed in a package (directory) that contains a number of standard files used to house the image data (at various resolutions), descriptive metadata, and technical metadata for ensuring fixity and facilitating preservation. The code in isaw.images facilitates the creation, manipulation, modification, and publication of such image packages.


Installation, Requirements, and Dependencies
---------------------------------------------

This Python package has been tested under Python 2.7.8 running on Mac OSX 10.9.5 and on Ubuntu Linux 14.04.2 LTS; however, the ```migrate.sh``` script expects a modern version of bash and associated utilities and therefore only runs successfully on Linux.

**Note** that some of the Python requirements discussed below have their own dependencies on non-Python packages. So, you will need to ensure at least the following **before running pip**:

 * Install libraries needed by the Pillow package to support TIFF and JPEG image formats and color management (i.e., libtiff, libjpeg, and littlecms): visit the [Pillow Installation page](https://pillow.readthedocs.org/installation.html) and scroll down to the appropriate section for your platform (Mac or Ubuntu) for instructions on how to install these libraries. Failure to install libtiff, libjpeg, and littlecms first will cause pip to fail to install requirements. You do not need to install Pillow separately from the ```pip install``` step below.

 * Install the [ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/	) utility, which is wrapped by the pyexiftool package included via requirements.txt. Failure to install ExifTool first will cause pip to fail to install requirements. You do not need to install pyexiftool separately from the ```pip install``` step below.

Use of a [Python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) pinned to 2.7.8, with [pip](https://pip.pypa.io/en/latest/) installed in order to manage package installations, is highly recommended. Python dependencies are detailed in ```requirements.txt```, so that they can be installed easily into the virtual environment (after activation thereof) using this simple command:

```
	pip install -r requirements.txt
```

Once everything is succesfully installed, try running the built-in code tests to make sure everything is operating right. This package uses the [nose](https://nose.readthedocs.org/en/latest/) Python unit test environment. It will have been installed along with the other requirements by pip. At the command line, enter the top-level directory of isaw.images package, activate the associated virtual environment, and type:

```
	nosetests
```


If you get any errors, double-check installation steps above and, if you can't find the problem, contact the isaw.images package developer.

Getting Started
----------------

To open an existing image package:

```python
	>>> from isaw.images import package
	>>> pkg = package.Package(path/to/package/directory)
```

An attempt open a directory that does not conform to the basic structure of an ISAW image package will elicit an IOError. You can check for further completeness, including fixity of managed files, with the ```validate``` method:

```python
	>>> pkg.validate()
	True
```

The successfully opened ```Package``` object includes a ```Manifest``` object that lists filenames and checksums for the files managed inside the package directory on disk:

```python
	>>> pkg.manifest.path
	'/absolute/path/to/package/directory/manifest-sha1.txt'
	>>> import pprint
	>>> pp = pprint.PrettyPrinter(indent=4)
	>>> pp.pprint(pkg.manifest.data)
	{   'flickr_old.jpg': 'f263038954ebe4b4d96e1c49719c55d9983bb75f',
	    'history.txt': '51e48a772aad62c206fa803eddd484bbcde6ea33',
	    'master.tif': 'ebe5128920636d8e525757ec83a98ced85988b00',
	    'meta.xml': '177707846a57f3f7039d4bdc47e14b4d4548885c',
	    'original-exiftool.xml': '231556650077a3c8162e3f71de3c21224a791e00',
	    'original.jpg': '0702c97990832df58a591f7a3f9a70bb948c5d92',
	    'preview.jpg': '79f767641e42379cbbbce7022e653d5edb7e9265',
	    'thumb.jpg': '81943c65643690f958c44f22eaed0cf1c0f7519b'}
```

Any modifications you make to the contents of the package on disk using methods of the ```Package``` object will automatically update the manifest, both in memory and on disk. For example, you can (re)generate the derivative versions of the image, jpeg files that are derived from ```master.tif```:

```python
	>>> preview_hash = pkg.manifest.data['preview.jpg']
	>>> thumb_hash = pkg.manifest.data['thumb.jpg']
	>>> pkg.make_derivatives()
	True
	>>> preview_hash == pkg.manifest.data['preview.jpg']
	False
	>>> thumb_hash == pkg.manifest.data['thumb.jpg']
	False
```

The ```Package``` object also provides a method for writing a human-readable summary of the package content to ```index.html``` inside the package directory.

```python
	>>> pkg.make_overview()
``` 

The ```Package``` object also includes a ```Metadata``` object, which carries methods to read and modify the content of the ```meta.xml``` file in the package on disk.

```python
	>>> pkg.metadata.path
	'/Users/paregorios/Documents/files/I/isaw.images/isaw/images/tests/data/kalabsha/201107061813531/meta.xml'
	>>> pp.pprint(pkg.metadata.data)
	{   'change-history': [   {   'agent': 'script',
	                              'date': '2011-07-06',
	                              'description': 'created this metadata file automatically, using (where available) 	information extracted from the original image headers'},
	                          {   'agent': 'Nate Nagy',
	                              'date': '2011-07-06',
	                              'description': 'entered in isaw information, geography and typology, and uploaded to 	Flickr.'}],
	    'copyright-date': '2009-02-27',
	    'copyright-holder': 'Iris Fernandez',
	    'date-photographed': '2009-02-27',
	    'description': 'The pylon and sacred walkway of the Roman-era temple at Kalabsha, now located at New Kalabsha after 	being moved from ancient Talmis.',
	    'flickr-url': 'http://www.flickr.com/photos/isawnyu/5913197834/in/set-72157627140459102',
	    'geography': {   'photographed-place': {   'ancient-name': 'Talmis',
	                                               'modern-name': 'Kalabsha',
	                                               'uri': 'http://pleiades.stoa.org/places/795868'}},
	    'isaw-publish-cleared': 'yes',
	    'license': 'cc-by',
	    'license-release-verified': 'yes',
	    'photographer': {   'family-name': 'Fernandez', 'given-name': 'Iris'},
	    'status': 'ready',
	    'title': 'The Temple at Kalabsha (I)',
	    'typology': [   'ancient',
	                    'history',
	                    'civilization',
	                    'Egypt',
	                    'Egyptology',
	                    'Talmis',
	                    'Kalabsha',
	                    'temple',
	                    'Roman',
	                    'Nile',
	                    'architecture',
	                    'masonry',
	                    'stone',
	                    'mandulis',
	                    'structure',
	                    'pylon']}
```

More to come here ...



Filesystem Structure
---------------------

We start with a filesystem structure for managing each notional image as an "isaw image package" (IIP): a directory that contains multiple files related to a single notional image. This IIP directory has the following components:

 * manifest-sha1.txt = a text file containing filenames and corresponding sha1 hashes for each file in the IIP. Format must conform to that specified for the [BagIt](https://github.com/jkunze/bagitspec) manifest.

 * original.[EXT] = the unchanged original image file, in whatever its original format, the only changes being: normalizing the filename to the string "original" and lower-casing the extension

 * original-exif.json = a dump of all the EXIF data found in the original image at time of import (if any), extracted with EXIFTool and dumped to disk in its default JSON output serialization.

 * master.tif = a TIFF file created from original.[EXT] at time of import. The main purpose of this file is to provide a color-managed, digital-preservation-friendly version of the image, captured as early as possible in the lifecycle. The only changes made to the image in converting from original to TIFF are the format itself, the standardization of header content, and the conversion from the original color profile (if any) to the [sRGB v4 Preference Profile](http://www.color.org/srgbprofiles.xalter#v4pref).

 * preview.jpg = a JPEG file derived from master.tif at time of import, maximum length of long axis: 800 pixels at 72dpi. The main purpose of this file is to provide a ready image of legible but minimal size to facilitate rapid preview in application and reuse contexts. 

 * thumbnail.jpg = a JPEG file derived from master.tif at time of import, maximum length of long axis: 200 pixels at 72dpi. The main purpose of this file is to provide a ready image of standard dimensions suitable for use in browse contexts, search results, contact sheets, and the like.

 * metadata.xml = an XML file, conforming to the [ISAW Images Metadata Schema](./isaw/images/meta/meta-schema.rnc), that contains descriptive information about the image.

 * history.txt = a text file to which is appended a single-line notice about each major change to the IIP

 ![image showing structure of example directory](./documentation/file-structure.png)


Classes and Methods
--------------------

The Package class, defined in isaw/images/package.py, provides the brains for managing ISAW Image Packages on a local filesystem. It defines the following outward-facing methods:

 * create: create a new image package at the targeted path (implemented: see isaw/images/tests/test_package.py)

 * open: open an existing image package at the targeted path (stubbed, but not yet implemented)

 * delete: delete the current image package (stubbed, but not yet implemented): assumes Package.open() has already been called.

 * validate: verify completeness and fixity of the current package (stubbed, but not yet implemented): assumes Package.open() has already been called.



