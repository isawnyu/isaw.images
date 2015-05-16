#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ISAW Images: Image Package
"""

from arglogger import arglogger # part of isaw.images
from io import BytesIO
import datetime
import dominate
from dominate.tags import *
import exiftool
from filehashing import hash_of_file, safe_copy
from flickr import Flickr # part of isaw.images
from functools import wraps
import json
import logging
import manifest # part of isaw.images
import metadata # part of isaw.images
import os
from PIL import Image, TiffImagePlugin
from PIL.ImageCms import getOpenProfile, getProfileName, profileToProfile, ImageCmsProfile
from pilkit.utils import save_image
import pytz
import shutil
import sys
from validate_path import validate_path

IMAGETYPES = {
    'BMP' : {'mimetype' : 'image/bmp', 'description' : 'Windows or OS/2 Bitmap', 'write' : True, 'extensions' : ['bmp',]},
    'EXR' : {'mimetype' : 'image/x-exr', 'description' : 'ILM OpenEXR', 'write' : True, 'extensions' : ['exr',]},
    'GIF' : {'mimetype' : 'image/gif', 'description' : 'Graphics Interchange Format', 'write' : True, 'extensions' : ['gif',]},
    'HDR' : {'mimetype' : 'image/vnd.radiance', 'description' : 'High Dynamic Range Image', 'write' : True, 'extensions' : ['hdr',]},
    'ICO' : {'mimetype' : 'image/vnd.microsoft.icon', 'description' : 'Windows Icon', 'write' : True, 'extensions' : ['ico',]},
    'IFF' : {'mimetype' : 'image/x-iff', 'description' : 'IFF Interleaved Bitmap', 'write' : False, 'extensions' : ['iff', 'lbm'], 'write_extension' : 'iff'},
    'J2K' : {'mimetype' : 'image/j2k', 'description' : 'JPEG-2000 codestream', 'write' : True, 'extensions' : ['j2k', 'j2c'], 'write_extension' : 'j2k'},
    'JNG' : {'mimetype' : 'image/x-mng', 'description' : 'JPEG Network Graphics', 'write' : True, 'extensions' : ['jng',]},
    'JP2' : {'mimetype' : 'image/jp2', 'description' : 'JPEG-2000 File Format', 'write' : True, 'extensions' : ['jp2',]},
    'JPEG' : {'mimetype' : 'image/jpeg', 'description' : 'JPEG - JFIF Compliant', 'write' : True, 'extensions' : ['jpg', 'jif', 'jpeg', 'jpe'], 'write_extension' : 'jpg'},
    'KOALA' : {'mimetype' : 'image/x-koala', 'description' : 'C64 Koala Graphics', 'write' : False, 'extensions' : ['koa',]},
    'PBM' : {'mimetype' : 'image/freeimage-pnm', 'description' : 'Portable Bitmap (ASCII)', 'write' : True, 'extensions' : ['pbm',]},
    'PBMRAW' : {'mimetype' : 'image/freeimage-pnm', 'description' : 'Portable Bitmap (RAW)', 'write' : True, 'extensions' : ['pbm',]},
    'PCD' : {'mimetype' : 'image/x-photo-cd', 'description' : 'Kodak PhotoCD', 'write' : False, 'extensions' : ['pcd',]},
    'PCX' : {'mimetype' : 'image/x-pcx', 'description' : 'Zsoft Paintbrush', 'write' : False, 'extensions' : ['pcx',]},
    'PFM' : {'mimetype' : 'image/x-portable-floatmap', 'description' : 'Portable floatmap', 'write' : True, 'extensions' : ['pfm',]},
    'PGM' : {'mimetype' : 'image/freeimage-pnm', 'description' : 'Portable Greymap', 'write' : True, 'extensions' : ['pgm',]},
    'PICT' : {'mimetype' : 'image/x-pict', 'description' : 'Macintosh PICT', 'write' : False, 'extensions' : ['pct', 'pict', 'pic'], 'write_extension' : 'pct'},
    'PNG' : {'mimetype' : 'image/png', 'description' : 'Portable Network Graphics', 'write' : True, 'extensions' : ['png',]},
    'PPM' : {'mimetype' : 'image/freeimage-pnm', 'description' : 'Portable Pixelmap', 'write' : True, 'extensions' : ['ppm',]},
    'PSD' : {'mimetype' : 'image/vnd.adobe.photoshop', 'description' : 'Adobe Photoshop', 'write' : False, 'extensions' : ['psd',]},
    'RAS' : {'mimetype' : 'image/x-cmu-raster', 'description' : 'Sun Raster Image', 'write' : False, 'extensions' : ['ras',]},
    'RAW' : {'mimetype' : 'image/x-dcraw', 'description' :  'RAW camera image', 'write' : False, 'extensions' : ['3fr', 'arw', 'bay', 'bmq', 'cap', 'cine', 'cr2', 'crw', 'cs1', 'dc2', 'dcr', 'drf', 'dsc', 'dng', 'erf', 'fff', 'ia', 'iiq', 'k25', 'kc2', 'kdc', 'mdc', 'mef', 'mos', 'mrw', 'nef', 'nrw', 'orf', 'pef', 'ptx', 'pxn', 'qtk', 'raf', 'raw', 'rdc', 'rw2', 'rwl', 'rwz', 'sr2', 'srf', 'srw', 'sti'] },
    'SGI' : {'mimetype' : 'image/x-sgi', 'description' : 'SGI Image Format', 'write' : False, 'extensions' : ['sgi',]},
    'TARGA' : {'mimetype' : 'image/x-tga', 'description' : 'Truevision Targa', 'write' : True, 'extensions' : ['tga', 'targa']},
    'TIFF' : {'mimetype' : 'image/tiff', 'description' : 'Tagged Image File Format', 'write' : True, 'extensions' : ['tif', 'tiff']},
    'WBMP' : {'mimetype' : 'image/vnd.wap.wbmp', 'description' : 'Wireless Bitmap', 'write' : True, 'extensions' : ['wap', 'wbmp', 'wbm']},
    'XBM' : {'mimetype' : 'image/x-xbitmap', 'description' : 'X11 Bitmap Format', 'write' : False, 'extensions' : ['xbm',]},
    'XPM' : {'mimetype' : 'image/x-xpixmap', 'description' : 'X11 Pixmap Format', 'write' : True, 'extensions' : ['xpm',]}
}

# the following list governs the order of presentation of items in the html overview for the package
OVERVIEWKEYS = [
    'title',
    'status',
    'isaw-publish-cleared',
    'license',
    'license-release-verified',
    'copyright',
    'copyright-holder',
    'copyright-date',
    'photographer',
    'date-photographed',
    'description',
    'geography',
    'typology',
    'change-history'
]

EXTENSIONS = {}
for k in IMAGETYPES.keys():
    for ext in IMAGETYPES[k]['extensions']:
        try:
            r = IMAGETYPES[k]['write_extension']
        except:
            r = ext
        EXTENSIONS[ext] = r

SIZEPREVIEW = 800, 600
SIZETHUMB = 128, 128


class Package(Flickr):
    """
    manage an ISAW image Package
    """


    @arglogger
    def __init__(self, path=None, id=None, original_path=None):
        if path is not None and id is not None and original_path is not None:
            self.create(path, id, original_path)
        elif path is not None and id is None and original_path is None:
            self.open(path)
        self.flickr_capable = False
        Flickr.__init__(self)


    @arglogger
    def __import_original__(self, original_path):
        """
        safe-copy an image from original_path into the package and set all metadata
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)

        # verify and copy the original image
        real_path = validate_path(original_path, 'file')
        filename, extension = os.path.splitext(real_path)
        self.original = '.'.join(('original', EXTENSIONS[extension[1:].lower()]))
        dest_path = os.path.join(self.path, self.original) # fix up filename extensions
        hash_orig = safe_copy(real_path, dest_path)
        self.__append_event__('copied original file from {src} to {dest}'.format(src=real_path, dest=dest_path))
        self.manifest.set(self.original, hash_orig)

        # capture and store metadata from the original file using exiftool
        # note this could be optimized by re-using a single exiftool instance, but code refactoring will have to happen
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata_batch([dest_path,])
        exif_path = os.path.join(self.path, 'original-exif.json')
        with open(exif_path, 'w') as exif_file:
            for d in metadata:
                json.dump(d, exif_file, sort_keys=True, indent=4)
                logger.debug('wrote exiftool metadata for original file on {exif_path}'.format(exif_path=exif_path))
                for k in d.keys():
                    logger.debug("exiftool found: {key}='{value}'".format(key=k, value=d[k]))
        hash_exif = hash_of_file(exif_path)
        self.__append_event__('wrote exif extracted from original file in json format on {exif_path}'.format(exif_path=exif_path))
        self.manifest.set('original-exif.json', hash_exif)

        # capture and store technical metadata using jhove (TBD)
        logger.warning('no jhove metadata is created')

    @arglogger
    def __generate_master__(self):
        """
        create a master file from the original already in the package and set all metadata
        """
        # open original
        # capture existing ICC profile (if there is one)
        # if no ICC profile, assign sRGB
        # if ICC profile and != sRGB, convert to sRGB
        # save as uncompressed TIFF

        logger = logging.getLogger(sys._getframe().f_code.co_name)

        profile_srgb2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icc', 'sRGB_IEC61966-2-1_black_scaled.icc')
        profile_srgb4 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icc', 'sRGB_v4_ICC_preference.icc')
        original_path = os.path.join(self.path, self.original)
        original_image = Image.open(original_path)
        try:
            raw_profile = original_image.info['icc_profile']
        except KeyError:
            raw_profile = getOpenProfile(profile_srgb2).tobytes()
            logger.warning('{original} does not have an internal ICC color profile'.format(original=self.original))
        else:
            logger.debug('detected internal ICC color profile in {original}'.format(original=self.original))
        original_profile = getOpenProfile(BytesIO(raw_profile))
        original_profile_name = getProfileName(original_profile).strip()
        target_profile = getOpenProfile(profile_srgb4)
        target_profile_name = getProfileName(target_profile).strip()
        logger.debug('attempting to convert from "{original}" to "{target}"'.format(original=original_profile_name, target=target_profile_name))
        converted_image = profileToProfile(original_image, original_profile, target_profile)
        master_path = os.path.join(self.path, 'master.tif')
        tiffinfo = TiffImagePlugin.ImageFileDirectory()
        tiffinfo[TiffImagePlugin.ICCPROFILE] = target_profile.tobytes()
        tiffinfo.tagtype[TiffImagePlugin.ICCPROFILE] = 1 # byte according to TiffTags.TYPES
        converted_image.DEBUG=True
        converted_image.save(master_path, tiffinfo=tiffinfo)
        hash_master = hash_of_file(master_path)
        logger.debug('saved converted master image to {master}'.format(master=master_path))
        self.__append_event__('created master.tif file at {master}'.format(master=master_path))
        self.manifest.set('master.tif', hash_master)


    def __append_event__(self, msg):
        """
        append an event notice to the package history
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        logger.debug(msg)
        event = '{stamp} {message}\n'.format(stamp=datetime.datetime.now(pytz.timezone('US/Eastern')).isoformat(), message=msg)
        with open(os.path.join(self.path, 'history.txt'), 'a') as hf:
            hf.write(event)
        self.manifest.set('history.txt', hash_of_file(os.path.join(self.path, "history.txt")))

    @arglogger
    def create(self, path, id, original_path):
        """
        create a new image package at the targeted path
        """
        real_path = validate_path(path, 'directory')
        os.makedirs(os.path.join(real_path, id, 'temp')) # don't we need to destroy this when done? what is it for?
        self.path = os.path.join(real_path, id)
        self.id = id
        self.manifest = manifest.Manifest(os.path.join(self.path, 'manifest-sha1.txt'), create=True)
        self.__import_original__(original_path)
        self.master = self.__generate_master__()
        self.original = os.path.basename(original_path)
        self.make_derivatives()
        self.metadata = metadata.Metadata(os.path.join(self.path, 'meta.xml'), create=True, exiftool_json=os.path.join(self.path, 'original-exif.json'))
        self.make_overview()
        self.__append_event__('created package at {path}'.format(path=self.path))

    @arglogger
    def open(self, path):
        """
        open an existing image package at the targeted path
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)        
        self.path = validate_path(path, 'directory')
        self.id = os.path.basename(self.path)
        # verify original and master and metadata and checksums
        # TBD
        # open manifest and metadata
        self.manifest = manifest.Manifest(os.path.join(self.path, 'manifest-sha1.txt'))
        try:
            self.metadata = metadata.Metadata(os.path.join(self.path, 'meta.xml'))
        except IOError:
            logger.warning("no meta.xml file was found in the package for this image ({0})".format(self.id))

            raise 
        # see if there is an original file yet
        filenames = self.manifest.get_all().keys()
        for filename in filenames:
            if 'original.' in filename:
                front, extension = os.path.splitext(filename)
                if 'sha1' not in extension:
                    self.original = filename
        try:
            o = self.original
        except AttributeError:
            logger.error("no original image file was found in the package for this image ({0})".format(self.id))
            raise
        self.make_overview()


    @arglogger
    def make_derivatives(self, overwrite=False):
        """
        create derivative images
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)   
        try:
            thumbnail = self.thumbnail
        except AttributeError:
            pass
        else:
            if not overwrite:
                return False
        master_path = os.path.join(self.path, 'master.tif')
        master_image = Image.open(master_path)
        master_profile = master_image.info.get('icc_profile')

        # make and save "maximum" image, a jpeg same resolution as the master
        maximum_image = master_image.copy()
        maximum_path = os.path.join(self.path, 'maximum.jpg')
        try:
            save_image(maximum_image, maximum_path, 'JPEG', options={'optimize':True, 'progressive':False, 'quality':95, 'icc_profile':master_profile})
        except IOError:
            save_image(preview_image, preview_path, 'JPEG', options={'optimize':True, 'progressive':False, 'icc_profile':master_profile})
        self.maximum = True
        maximum_hash = hash_of_file(maximum_path)
        self.__append_event__("Wrote derivative 'maximum' jpeg file on {0}".format(maximum_path))
        self.manifest.set('maximum.jpg', maximum_hash)
        del maximum_image # save RAM

        # make and save preview image
        # Note: the resampling algorithm that gives the highest quality result (bicubic)
        # is expensive in terms of compute time, and that expense is proportional to the
        # size of the original image and the relative size of the target image. 
        # Consequently, if the starting image is significantly larger than the desired 
        # down-sampled image, we'll make a first pass with the much less expensive 
        # "nearest neighbor" resampling algorithm to get an image that is only twice the
        # size of the target, then use "bicubic" on it to get the desired outcome. The
        # wisdom of the Internet seems to point to this as a time-saving step that 
        # sacrifices little or nothing in quality. Caveat lector. Of course, if we 
        # really wanted to do this fast, we'd write it in C.
        preview_image = master_image.copy()
        del master_image # save RAM
        size = preview_image.size
        logger.debug("master size: {0}, {1}".format(size[0], size[1]))
        if size[0] > 3* SIZEPREVIEW[0] or size[1] > 3* SIZEPREVIEW[1]:
            preview_image.thumbnail(tuple(s*2 for s in SIZEPREVIEW), Image.NEAREST)
            logger.debug("did nearest pre-shrink for preview, resulting size: {0}, {1}".format(preview_image.size[0], preview_image.size[1]))
        preview_image.thumbnail(SIZEPREVIEW)
        logger.debug("resulting preview size: {0}, {1}".format(preview_image.size[0], preview_image.size[1]))
        preview_path = os.path.join(self.path, 'preview.jpg')
        try:
            save_image(preview_image, preview_path, 'JPEG', options={'optimize':True, 'progressive':True, 'quality':80, 'icc_profile':master_profile})
        except IOError:
            save_image(preview_image, preview_path, 'JPEG', options={'optimize':True, 'progressive':True, 'icc_profile':master_profile})
            logger.warning("preview image could not be written at quality 80; using defaults")
        self.preview = True
        preview_hash = hash_of_file(preview_path)
        self.__append_event__("wrote derivative 'preview' jpeg file on {0}".format(preview_path))
        self.manifest.set('preview.jpg', preview_hash)

        # make and save thumbnail image
        # Note: use the same approach as above, but start with the preview image, which
        # is surely much smaller than the master.
        thumbnail_image = preview_image.copy()
        del preview_image # save the RAMs!
        thumbnail_image.thumbnail(SIZETHUMB)
        thumbnail_path = os.path.join(self.path, 'thumb.jpg')
        try:
            save_image(thumbnail_image, thumbnail_path, 'JPEG', options={'optimize':True, 'progressive':True, 'quality':80, 'icc_profile':master_profile})
        except IOError:
            save_image(thumbnail_image, thumbnail_path, 'JPEG', options={'optimize':True, 'progressive':True, 'icc_profile':master_profile})
            logger.warning("preview image could not be written at quality 80; using defaults")
        self.thumbnail = True
        thumbnail_hash = hash_of_file(thumbnail_path)
        self.__append_event__("wrote derivative 'thumbnail' jpeg file on {0}".format(thumbnail_path))
        self.manifest.set('thumb.jpg', thumbnail_hash)

        del thumbnail_image # probably not necessary to save the RAM here cuz gc will get it but anyway...
        return True
        
    @arglogger
    def make_overview(self):
        self.doc = dominate.document(title="Overview '{0}'".format(self.id))
        with self.doc.head:
            style(""" 
                body {
                    background-color: #F9F9F9;
                    padding: 10px;
                    font-family: Arial, sans-serif;
                }                
                .image {
                    float: right;
                    margin-left: 10px;
                }
                img {
                    border: 1px solid #CCCCCC;
                    box-shadow: 1px 1px 1px rgba(255, 255, 255, 0.25) inset, 0px 1px 2px rgba(0, 0, 0, 0.5);                    
                }
                .metadata p, .metadata ul {
                    margin-bottom: 0.25em;
                    margin-top: 0px;
                }
                .metadata p {
                    padding-left: 2em ;
                    text-indent: -2em ;
                }
                """)
        m = self.metadata.data
        with self.doc:
            h1("Overview for '{0}'".format(self.id))
            with div(cls='image'):
                img(src="{0}".format('preview.jpg'), alt="preview of image with id='{0}'".format(self.id))
            with div(cls='metadata'):
                p("id: {0}".format(self.id))
                for k in OVERVIEWKEYS:
                    try:
                        val = m[k]
                    except KeyError:
                        p("{0}: [[no {1}]]".format(k, k))
                    else:
                        if k == 'photographer':
                            if 'name' in val.keys():
                                text = val['name']                        
                            elif 'given-name' in val.keys() and 'family-name' in val.keys():
                                text = "{0} {1}".format(val['given-name'], val['family-name'])
                            else:
                                logger.error("unexpected construct for photographer: {0}".format(val))
                                raise Exception
                            if 'uri' in val.keys():
                                with p('photographer: '):
                                    a(text, href="{0}".format(val['uri']))
                            else:                                
                                p("{0}: {1}".format(k, text))
                        elif k == 'geography':
                            if 'photographed-place' in val.keys():
                                geo = val['photographed-place']
                                try:
                                    modern = geo['modern-name']
                                except KeyError:
                                    modern = ''
                                try:
                                    ancient = geo['ancient-name']
                                except KeyError:
                                    ancient = ''
                                if modern != '':
                                    text = modern
                                else:
                                    text = ''
                                if modern != '' and ancient != '':
                                    text = "{0}, ancient ".format(text)
                                if ancient != '':
                                    text = "{0}{1}".format(text, ancient)                                
                                if 'uri' in geo.keys():
                                    with p('photographed place: '):
                                        a(text, href="{0}".format(geo['uri']))
                                else:
                                    p('photographed place: {0}'.format(text))
                            else:
                                logger.error("unexpected construct for geography: {0}".format(val))
                                raise Exception
                        elif k == 'typology':
                            with p('typology:'):
                                with ul():
                                    for term in sorted(val, key=lambda v: v.lower()):
                                        li(term)
                        elif k == 'change-history':
                            with p('change history:'):
                                with ul():
                                    for d in sorted(val, key=lambda kk: kk['date']):
                                        li("{0}: {1} {2}".format(d['date'], d['agent'], d['description']))
                        else:
                            p("{0}: {1}".format(k, val))


        outfn = os.path.join(self.path, 'index.html')
        outf = open(outfn, 'w')
        outf.write(self.doc.render())
        outf.close()        


    @arglogger
    def delete(self):
        """
        delete the current image package
        """
        pass


    @arglogger
    def validate(self):
        """
        verify completeness and fixity of the current package
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)  
        try:
            path = self.path
        except AttributeError:
            logger.warning('Package.validate() was called before Package.path was set.')
            return False
        try:
            manifest = self.manifest
        except AttributeError:
            logger.warning('Package.validate() was called before Package.manifest was set.')
            return False
        result = True

        # make sure the minimally required components are present and have been successfully opened
        filenames=self.manifest.get_all().keys()
        if 'master.tif' not in filenames:
            result = False
            logger.error("Validation failed to find 'master.tif' in manifest")
        if self.original not in filenames:
            result = False
            logger.error("Validation failed to find '{0}' in manifest".format(self.original))

        # verify that checksums are valid for every item in the manifest
        for filename in filenames:
            checksum = self.manifest.get(filename)
            filepath = os.path.join(path, filename)
            real_filepath = validate_path(filepath, 'file')
            if checksum != hash_of_file(real_filepath):
                logger.error("checksum verification FAILED on '{0}' in Package.validate()".format(real_filepath))
                result = False

        return result




