#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
code to create an HTML proof sheet from a folder full of isaw.image packages
"""

from arglogger import arglogger
import datetime
import dominate
from dominate.tags import *
import logging
import os
import package
import pytz
import sys
from validate_path import validate_path

METAKEYS = [
    'status',
    'isaw-publish-cleared',
    'license',
    'license-release-verified'
    'flickr-url'
]

class Proof():
    """
    HTML proof sheet for isaw.images
    """

    @arglogger
    def __init__(self, path=None):
        logger = logging.getLogger(sys._getframe().f_code.co_name)
        if path is not None:
            self.__generate__(path)
        else:
            logger.warning("Proof.init called with path=None")

    @arglogger
    def __generate__(self, path):
        """
        create the proof sheet
        """

        logger = logging.getLogger(sys._getframe().f_code.co_name)

        real_path = validate_path(path, 'directory')
        # get a list of all the directories at path and determine which are image packages
        directories = [o for o in os.listdir(real_path) if os.path.isdir(os.path.join(real_path,o))]
        self.packages = []
        self.other_directories = []
        for d in directories:
            pkg = package.Package()
            try:
                pkg.open(os.path.join(path,d))
            except IOError, e:
                logger.warning("failed trying to open directory '{0}' as a package: {1}".format(d, e))
                self.other_directories.append(d)
            else:
                if pkg.validate():
                    self.packages.append(pkg)
                else:
                    logger.warning("successfully opened directory '{0}' as a package, but it failed to validate".format(d))
                    self.other_directories.append(d)

        # create the HTML proof sheet
        dirname = os.path.basename(real_path)
        self.doc = dominate.document(title="Proof '{0}'".format(dirname))
        with self.doc.head:
            style(""" 
                body {
                    background-color: #F9F9F9;
                    padding: 10px;
                    font-family: Arial, sans-serif;
                }                
                .package {
                    background-color: white;
                    float: left;
                    padding: 0 15px;
                    margin: 7px;
                    border: 1px solid #AAAAAA;
                    box-shadow: 1px 1px 1px rgba(255, 255, 255, 0.25) inset, 0px 1px 2px rgba(0, 0, 0, 0.5);  
                    width: 160px;                  
                    height: 320px;
                    overflow: hidden;
                }
                .package .image img {
                    border: 1px solid #CCCCCC;
                    box-shadow: 1px 1px 1px rgba(255, 255, 255, 0.25) inset, 0px 1px 2px rgba(0, 0, 0, 0.5);
                    max-height: 120px;   
                    display: block;
                    margin-left: auto;
                    margin-right: auto;                 
                }
                .caption {
                    font-weight: bold;
                }
                .metadata p {
                    margin: 0px;
                    padding: 0px;
                    font-size: smaller;
                    padding-left: 2em ;
                    text-indent: -2em ;                    
                }
                .package .image img:hover {
                    box-shadow: none;
                }
                #stats, #images {
                    margin: 15px;
                }
                #stats {
                    clear: both;
                    padding-top: 15px;
                }
                """)
        with self.doc:
            h1("Proof Sheet for '{0}'".format(dirname))
            with div(id='images'):
                h2("Image packages in this folder:")
                for pkg in self.packages:
                    with div(id=pkg.id, cls='package'):
                        try:
                            title=pkg.metadata.data['title']
                        except KeyError:
                            title='[[no title]]'
                        p("{0} ({1}".format(title, pkg.id), cls='caption')
                        pkg.make_derivatives(overwrite=False)
                        with div(cls='image'):
                            with a(href="./{0}/{1}".format(pkg.id, 'index.html')):
                                img(src="./{0}/{1}".format(pkg.id, 'thumb.jpg'), alt="thumbnail of image with id='{0}'".format(pkg.id))
                        with div(cls='metadata'):
                            try:        
                                m=pkg.metadata.data
                            except AttributeError:
                                p('[[no valid metadata!]]')
                            else:
                                for k in METAKEYS:
                                    try:
                                        val = m[k]
                                    except KeyError:
                                        p("{0}: [[no {1}]]".format(k, k))
                                    else:
                                        if k == 'flickr-url':
                                            with p():
                                                a("flickr", href="{0}".format(val))
                                        else:
                                            p("{0}: {1}".format(k, val))

                                
                                
            with div(id='stats'):
                h2("Statistics and information:")
                p("Proof sheet created at: {0}".format(datetime.datetime.now(pytz.timezone('US/Eastern')).isoformat()))
                p("Full path: {0}".format(real_path))
                p("Number of image packages: {0}".format(len(self.packages)))
                p("Other non-package directories found herein: {0}".format(len(self.other_directories)))
                if len(self.other_directories) > 0:
                    with ul():
                        for d in self.other_directories:
                            li(d)
        outfn = os.path.join(real_path, 'index.html')
        outf = open(outfn, 'w')
        outf.write(self.doc.render())
        outf.close()

        

