#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ISAW Images: Image Package
"""

from arglogger import arglogger
from io import BytesIO
import datetime
import exiftool
from functools import wraps
import hashlib
from PIL.ImageCms import getOpenProfile, getProfileName, profileToProfile, ImageCmsProfile
import json
import logging
import os
from PIL import Image, TiffImagePlugin
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

EXTENSIONS = {}
for k in IMAGETYPES.keys():
    for ext in IMAGETYPES[k]['extensions']:
        try:
            r = IMAGETYPES[k]['write_extension']
        except:
            r = ext
        EXTENSIONS[ext] = r


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

class Package:
    """
    manage an ISAW image Package
    """


    @arglogger
    def __init__(self, path=None, id=None, original_path=None):
        if path is not None and id is not None and original_path is not None:
            self.create(path, id, original_path)

    @arglogger
    def __del__(self):
        try:
            manifest_f = self.manifest_file
        except AttributeError:
            pass
        else:
            manifest_f.close()
        try:
            history_f = self.history_file
        except AttributeError:            
            pass
        else:
            history_f.close()


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
        self.__append_to_manifest__(self.original, hash_orig)

        # save the sha1 hash of the file for future fixity tests
        hashfile_path = os.path.join(self.path, 'original.sha1')
        with open(hashfile_path, 'wb') as hash_f:
            hash_f.write(hash_orig)
        self.__append_event__('wrote sha1 checksum for original file on {hash_path}'.format(hash_path=hashfile_path))
        self.__append_to_manifest__('original.sha1')
        
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
        self.__append_to_manifest__('original-exif.json', hash_exif)

        # save the sha1 hash of the file for future fixity tests
        hashfile_path = os.path.join(self.path, 'original-exif.sha1')
        with open(hashfile_path, 'wb') as hash_f:
            hash_f.write(hash_exif)
        self.__append_event__('wrote sha1 checksum for exif file on {hash_path}'.format(hash_path=hashfile_path))
        self.__append_to_manifest__('original-exif.sha1')

        # capture and store technical metadata using jhove (TBD)


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
        self.__append_to_manifest__('master.tif', hash_master)

        # save the sha1 hash of the file for future fixity tests
        hashfile_path = os.path.join(self.path, 'master.sha1')
        with open(hashfile_path, 'wb') as hash_f:
            hash_f.write(hash_master)
        self.__append_event__('wrote sha1 checksum for master file on {hash_path}'.format(hash_path=hashfile_path))
        self.__append_to_manifest__('master.sha1')



    def __append_event__(self, msg):
        """
        append an event notice to the package history
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        logger.debug(msg)
        event = '"{stamp}","{message}"\n'.format(stamp=datetime.datetime.now(), message=msg)
        try:
            history_f = self.history_file
        except AttributeError:            
            logger.debug("history file is not yet opened")
            history_path = os.path.join(self.path, "history.txt")
            self.history_file = open(history_path, "a")
            logger.debug("opened history file at {path}".format(path=history_path))
            history_f = self.history_file
        history_f.write(event)
        history_f.flush()


    def __append_to_manifest__(self, filename, filehash=None):
        """
        add filename to bagit-style manifest
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        if filehash is not None:
            checksum = filehash
        else:
            checksum = hash_of_file(os.path.join(self.path, filename))
        line = '{checksum} {filename}\n'.format(checksum=checksum, filename=filename)
        logger.debug('appending to manifest: "{line}"'.format(line=line))
        try:
            manifest_f = self.manifest_file
        except AttributeError:
            logger.debug("manifest file is not yet opened")
            manifest_path = os.path.join(self.path, "manifest-sha1.txt")
            self.manifest_file = open(manifest_path, "a")
            logger.debug("opened manifest file at {path}".format(path=manifest_path))
            manifest_f = self.manifest_file
        manifest_f.write(line)
        manifest_f.flush()


    @arglogger
    def create(self, path, id, original_path):
        """
        create a new image package at the targeted path
        """
        real_path = validate_path(path, 'directory')
        os.makedirs(os.path.join(real_path, id, 'temp')) # don't we need to destroy this?
        self.path = os.path.join(real_path, id)
        self.__append_event__('created package at {path}'.format(path=self.path))
        self.__import_original__(original_path)
        self.master = self.__generate_master__()



    @arglogger
    def open(self, path):
        """
        open an existing image package at the targeted path
        """
        logger = logging.getLogger(sys._getframe().f_code.co_name)        
        self.path = validate_path(path, 'directory')
        # verify original and master and metadata and checksums
        # open manifest
        manifest_path = validate_path(os.path.join(self.path, "manifest-sha1.txt"), 'file')
        try:
            manifest_file = open(manifest_path, "r")
        except IOError:
            raise IOError("could not open package manifest file at {0}".format(manifest_path))
        self.manifest = manifest_file.readlines()
        manifest_file.close()
        logger.debug('manifest file contents: ' + ''.join(self.manifest) + '\n')
        print('manifest file contents: ' + ''.join(self.manifest) + '\n')
        return self


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
        pass

