#!/usr/bin/python
import flickrapi 
import urllib3
import webbrowser
import os
import xml.etree.ElementTree as ET

"""
Upload images to Flickr using flickrapi
"""

class Flickr_image_upload: 

    def __init__(self, api_key, api_secret):
	self.flickr = flickrapi.FlickrAPI(api_key, api_secret)
	if not self.flickr.token_valid(perms='write'):
	    # Get a request token
	    self.flickr.get_request_token(oauth_callback='oob')

	    # Open a browser at the authentication URL. Do this however
	    # you want, as long as the user visits that URL.
	    self.authorize_url = self.flickr.auth_url(perms=u'write')
	    webbrowser.open_new_tab(self.authorize_url)

	    # Get the verifier code from the user. Do this however you
	    # want, as long as the user gives the application the code.
	    self.verifier = unicode(raw_input('Verifier code: '))

	    print type(self.verifier)
	    # Trade the request token for an access token
	    self.flickr.get_access_token(self.verifier)
	
    def uploadImage(self, pkgimg):
        print 'in upload method'
	self.params  = {'filename':pkgimg}
	self.rsp = self.flickr.upload(self.params['filename'])
	print "Photo ID: ", self.rsp.find('photoid').text
	return self.rsp.find('photoid').text

    def createFolder(self, photoID):
	self.param_title = unicode(raw_input('Enter title for the folder: '))
	self.param_description = unicode(raw_input('Enter description: '))
	self.rsp = self.flickr.photosets.create(title=self.param_title, description=self.param_description, primary_photo_id=photoID)
	print "Photoset ID: ", self.rsp.find('photoset').attrib['id']
	return self.rsp.find('photoset').attrib['id']

    def createCollection(self):
	self.param_collection_title = unicode(raw_input('Enter collection title: '))
	self.param_collection_description = unicode(raw_input('Enter collection description: '))
	self.rsp = self.flickr.collections.create(title=self.param_collection_title, description=self.param_collection_description)
	print "Collection ID: ", self.rsp.find('collection').attrib['id']
	return self.rsp.find('collection').attrib['id']

    def replaceImage(self, newImagePath, photoID):
	print newImagePath
	self.rsp = self.flickr.replace(filename=newImagePath, photo_id=photoID, format='etree')
	print "Replaced image ID: ", self.rsp.find('photoid').text
	return self.rsp.find('photoid').text

    def addImageToExistingAlbum(self, imagePath, photosetID):
	self.streamUploadedImage = self.uploadImage(imagePath)
	self.rsp = self.flickr.photosets.addPhoto(photoset_id=photosetID, photo_id=self.streamUploadedImage)

    def movePhotosetToCollection(self, collectionListItem, photoSetID):
	self.collectionList = self.flickr.collections.getTree()
	for c in self.collectionList[0]:
		if collectionListItem == c.attrib['id']:
			print c.attrib['id']
			self.collectionPassed = c
	self.photsetList = self.collectionPassed.findall('set')

	self.photoIDList = ""
	for i in self.photsetList:
		print i.attrib['id']
		self.photoIDList = self.photoIDList + i.attrib['id'] + ", "
	self.photsetList = self.photoIDList + photoSetID
		
	self.flickr.collections.editSets(collection_id=collectionListItem, do_remove=0, photoset_ids=self.photsetList)
	self.displayCollectionContents(collectionListItem)


    def displayCollectionContents(self, collectionItem):
	print 'In display method'
	self.collectionList = self.flickr.collections.getTree()
	for c in self.collectionList[0]:
		if collectionItem == c.attrib['id']:
			print c.attrib['id']
			self.collectionPassed = c
	self.photsetList = self.collectionPassed.findall('set')

	for i in self.photsetList:
		print i.attrib['id']


    def deleteCollection(self, collID):
	self.flickr.collections.delete(collection_id=collID)	


	

