#!/bin/python
import os, zipfile, logging, ee , urllib2, datetime, gdal
import numpy as np 
import scipy as sp
import matplotlib.pyplot as plt

# modified July 20, 2014 
import glob
import xlrd
try:
    from PIL import Image
except:
    from Pillow import Image
xml.etree.ElementTree as treeObj
from xml.dom.minidom import parseString,parse




def ee_download_DEM(path,glacier,MaxLon,MinLon,MaxLat,MinLat):
	# define margin added to bounding box for downloading image 
	margin = 0.1 
	folder = path+"/Data/"
	
	#-----------------------------------------------------------------------
	#                         access EE
	#-----------------------------------------------------------------------
	with open(path+'/Code/GoogleAccount.txt','r') as f: 
		MY_SERVICE_ACCOUNT = f.readline() 
	
	MY_PRIVATE_KEY_FILE = path + '/Code/GoogleKey.p12'
	ee.Initialize(ee.ServiceAccountCredentials(MY_SERVICE_ACCOUNT, MY_PRIVATE_KEY_FILE))
	
	#-----------------------------------------------------------------------
	#                 determine glacier boundry from excel file
	#-----------------------------------------------------------------------
	print glacier
	glacier = glacier.encode('ascii','ignore')
	LonLen = MaxLon-MinLon
	LatLen = MaxLat-MinLat
	MaxLon1 = MaxLon + margin*LonLen
	MinLon1 = MinLon - margin*LonLen
	MaxLat1 = MaxLat + margin*LatLen
	MinLat1 = MinLat - margin*LatLen
	bounds = [[MinLon1,MinLat1],[MaxLon1,MinLat1],[MaxLon1,MaxLat1],[MinLon1,MaxLat1]]
	print(bounds)

	newpath = folder+glacier
	if not os.path.exists(newpath): os.makedirs(newpath)

	#-----------------------------------------------------------------------
	#                        download DEM
	#-----------------------------------------------------------------------
	try:	
		image = ee.Image('srtm90_v4')
		dlPath = image.getDownloadUrl({
				'scale': 30,
				'crs': 'EPSG:4326',
				'region': bounds,
			})
		demzip = urllib2.urlopen(dlPath)
		# download the zip file to document folder 
		workingDir = newpath
		if not os.path.exists(workingDir):
			os.mkdir(workingDir)
		with open(workingDir + '.zip', "wb") as local_file:
			local_file.write(demzip.read())
		# unzip the contents
		zfile = zipfile.ZipFile(workingDir + '.zip')
		for j in zfile.namelist():
			fd = open(workingDir + '/' + j,"w")
			fd.write(zfile.read(j))
			fd.close()
		# delete the zip file
		os.remove(workingDir + '.zip')
		DEM = np.array(gdal.Open(workingDir+"/srtm90_v4.elevation.tif").ReadAsArray())
		count = np.count_nonzero(DEM)
		if count == 0:
			os.remove(workingDir+"/srtm90_v4.elevation.tif")
			image = ee.Image('USGS/GMTED2010')
			dlPath = image.getDownloadUrl({
					'scale': 30,
					'crs': 'EPSG:4326',
					'region': bounds,
				})
			demzip = urllib2.urlopen(dlPath)
			# download the zip file to document folder 
			workingDir = newpath
			if not os.path.exists(workingDir):
				os.mkdir(workingDir)
			with open(workingDir + '.zip', "wb") as local_file:
				local_file.write(demzip.read())
			# unzip the contents
			zfile = zipfile.ZipFile(workingDir + '.zip')
			for j in zfile.namelist():
				fd = open(workingDir + '/' + j,"w")
				fd.write(zfile.read(j))
				fd.close()
			# delete the zip file
			os.remove(workingDir + '.zip')
			return "GMTED2010.be75.tif"
		else:
			return "srtm90_v4.elevation.tif"
	except:
		print "error"



# def ee_download(path,glacier,MaxLon,MinLon,MaxLat,MinLat):
	
# 	# define margin added to bounding box for downloading image 
# 	margin = 0.1 
# 	folder = path+"/Data/"
	
	
# 	#-----------------------------------------------------------------------
# 	#                         access EE
# 	#-----------------------------------------------------------------------
# 	with open(path+'/Code/GoogleAccount.txt','r') as f: 
# 		MY_SERVICE_ACCOUNT = f.readline() 
	
# 	MY_PRIVATE_KEY_FILE = path+'/Code/GoogleKey.p12'
# 	ee.Initialize(ee.ServiceAccountCredentials(MY_SERVICE_ACCOUNT, MY_PRIVATE_KEY_FILE))
	
# 	#-----------------------------------------------------------------------
# 	#                 determine glacier boundry from excel file
# 	#-----------------------------------------------------------------------
# 	print glacier
# 	glacier = glacier.encode('ascii','ignore')
# 	LonLen = MaxLon-MinLon
# 	LatLen = MaxLat-MinLat
# 	MaxLon1 = MaxLon + margin*LonLen
# 	MinLon1 = MinLon - margin*LonLen
# 	MaxLat1 = MaxLat + margin*LatLen
# 	MinLat1 = MinLat - margin*LatLen
# 	bounds = [[MinLon1,MinLat1],[MaxLon1,MinLat1],[MaxLon1,MaxLat1],[MinLon1,MaxLat1]]
# 	print(bounds)

# 	#------------------------------------------------------------------------
# 	#                       download L7 images from EE
# 	#------------------------------------------------------------------------
# 	# define time period of images
# 	beg_date = datetime.datetime(1999,1,1)
# 	end_date = datetime.datetime(2014,1,1)
# 	collection = ee.ImageCollection('LE7_L1T').filterDate(beg_date,end_date) 
# 	polygon = ee.Feature.MultiPolygon([[bounds]])
# 	collection = collection.filterBounds(polygon)
# 	metadata = collection.getInfo()
# 	print metadata.keys()
# 	print metadata['features'][0]['id']

# 	newpath = folder+glacier
# 	if not os.path.exists(newpath): os.makedirs(newpath)

# 	#------------------------------------------------------------------------
# 	#                      download Band 61 of the Landsat
# 	#-----------------------------------------------------------------------

# 	for i in range(len(metadata['features'])):
# 		try:
# 			sceneName = metadata['features'][i]['id']
# 			print sceneName + ': Scene ' + str(i+1) + ' of ' + str(len(metadata['features']))
# 			workingScene = ee.Image(sceneName)    
# 			dlPath = workingScene.getDownloadUrl({
# 				'scale': 30,
# 				'bands':[{'id':'B6_VCID_1'}],
# 				'crs': 'EPSG:4326',
# 				'region': bounds,
# 			})
# 			scenezip = urllib2.urlopen(dlPath)
# 			# download the zip file to documnet folder
# 			workingDir = newpath+'/'+sceneName.split('/')[1] 
# 			#if not os.path.exists(workingDir):
# 				#os.mkdir(workingDir)
# 			with open(workingDir + '.zip', "wb") as local_file:
# 				local_file.write(scenezip.read())
# 			# unzip the contents
# 			zfile = zipfile.ZipFile(workingDir + '.zip')
# 			for j in zfile.namelist():
# 				jstring = j.encode('ascii','ignore')
# 				jsp = jstring.split(".")
# 				if jsp[1] == 'B6_VCID_1' and jsp[2] =='tif': 
# 					fd = open(newpath + '/' + j,"w")
# 					fd.write(zfile.read(j))
# 					fd.close()
					
# 			# delete the zip file
# 			os.remove(workingDir + '.zip')
# 		except:
# 			continue
	# #------------------------------------------------------------------------
	# #                       download L5 images from EE
	# #------------------------------------------------------------------------
	# # define time period of images
	# beg_date = datetime.datetime(1984,1,1)
	# end_date = datetime.datetime(2012,5,5)
	# collection = ee.ImageCollection('LT5_L1T').filterDate(beg_date,end_date) 
	# polygon = ee.Feature.MultiPolygon([[bounds]])
	# collection = collection.filterBounds(polygon)
	# metadata = collection.getInfo()
	# print metadata.keys()
	# print metadata['features'][0]['id']

	# newpath = folder+glacier
	# if not os.path.exists(newpath): os.makedirs(newpath)

	# #------------------------------------------------------------------------
	# #                      download Band 6 of the Landsat
	# #-----------------------------------------------------------------------

	# for i in range(len(metadata['features'])):
	# 	try:
	# 		sceneName = metadata['features'][i]['id']
	# 		print sceneName + ': Scene ' + str(i+1) + ' of ' + str(len(metadata['features']))
	# 		workingScene = ee.Image(sceneName)    
	# 		dlPath = workingScene.getDownloadUrl({
	# 			'scale': 30,
	# 			'bands':[{'id':'B6'}],
	# 			'crs': 'EPSG:4326',
	# 			'region': bounds,
	# 		})
	# 		scenezip = urllib2.urlopen(dlPath)
	# 		# download the zip file to documnet folder
	# 		workingDir = newpath+'/'+sceneName.split('/')[1] 
	# 		#if not os.path.exists(workingDir):
	# 			#os.mkdir(workingDir)
	# 		with open(workingDir + '.zip', "wb") as local_file:
	# 			local_file.write(scenezip.read())
	# 		# unzip the contents
	# 		zfile = zipfile.ZipFile(workingDir + '.zip')
	# 		for j in zfile.namelist():
	# 			jstring = j.encode('ascii','ignore')
	# 			jsp = jstring.split(".")
	# 			if jsp[1] == 'B6' and jsp[2] =='tif': 
	# 				fd = open(newpath + '/' + j,"w")
	# 				fd.write(zfile.read(j))
	# 				fd.close()
					
	# 		# delete the zip file
	# 		os.remove(workingDir + '.zip')
	# 	except:
	# 		continue

	# #------------------------------------------------------------------------
	# #                       download L4 images from EE
	# #------------------------------------------------------------------------
	# # define time period of images
	# beg_date = datetime.datetime(1982,8,22)
	# end_date = datetime.datetime(1993,12,14)
	# collection = ee.ImageCollection('LT4_L1T').filterDate(beg_date,end_date) 
	# polygon = ee.Feature.MultiPolygon([[bounds]])
	# collection = collection.filterBounds(polygon)
	# metadata = collection.getInfo()
	# print metadata.keys()
	# print metadata['features'][0]['id']

	# newpath = folder+glacier
	# if not os.path.exists(newpath): os.makedirs(newpath)

	# #------------------------------------------------------------------------
	# #                      download Band 6 of the Landsat
	# #-----------------------------------------------------------------------

	# for i in range(len(metadata['features'])):
	# 	try:
	# 		sceneName = metadata['features'][i]['id']
	# 		print sceneName + ': Scene ' + str(i+1) + ' of ' + str(len(metadata['features']))
	# 		workingScene = ee.Image(sceneName)    
	# 		dlPath = workingScene.getDownloadUrl({
	# 			'scale': 30,
	# 			'bands':[{'id':'B6'}],
	# 			'crs': 'EPSG:4326',
	# 			'region': bounds,
	# 		})
	# 		scenezip = urllib2.urlopen(dlPath)
	# 		# download the zip file to documnet folder
	# 		workingDir = newpath+'/'+sceneName.split('/')[1] 
	# 		#if not os.path.exists(workingDir):
	# 			#os.mkdir(workingDir)
	# 		with open(workingDir + '.zip', "wb") as local_file:
	# 			local_file.write(scenezip.read())
	# 		# unzip the contents
	# 		zfile = zipfile.ZipFile(workingDir + '.zip')
	# 		for j in zfile.namelist():
	# 			jstring = j.encode('ascii','ignore')
	# 			jsp = jstring.split(".")
	# 			if jsp[1] == 'B6' and jsp[2] =='tif': 
	# 				fd = open(newpath + '/' + j,"w")
	# 				fd.write(zfile.read(j))
	# 				fd.close()
					
	# 		# delete the zip file
	# 		os.remove(workingDir + '.zip')
	# 	except:
	# 		continue
	# return (MaxLon1,MaxLat1,MinLon1,MinLat1)



def ee_download_Allbands(path,glacier,MaxLon,MinLon,MaxLat,MinLat):
	
	# define margin added to bounding box for downloading image 
	margin = 0.1 
	folder = path+"/Data/"
	
	#-----------------------------------------------------------------------
	#                         access EE
	#-----------------------------------------------------------------------
	with open(path+'/Code/GoogleAccount.txt','r') as f: 
		MY_SERVICE_ACCOUNT = f.readline() 
	
	MY_PRIVATE_KEY_FILE = path+'/Code/GoogleKey.p12'
	ee.Initialize(ee.ServiceAccountCredentials(MY_SERVICE_ACCOUNT, MY_PRIVATE_KEY_FILE))

	#-----------------------------------------------------------------------
	#                 determine glacier boundry from excel file
	#-----------------------------------------------------------------------
	print glacier
	glacier = glacier.encode('ascii','ignore')
	LonLen = MaxLon-MinLon
	LatLen = MaxLat-MinLat
	MaxLon1 = MaxLon + margin*LonLen
	MinLon1 = MinLon - margin*LonLen
	MaxLat1 = MaxLat + margin*LatLen
	MinLat1 = MinLat - margin*LatLen
	bounds = [[MinLon1,MinLat1],[MaxLon1,MinLat1],[MaxLon1,MaxLat1],[MinLon1,MaxLat1]]
	print(bounds)

	#------------------------------------------------------------------------
	#                       download L7 images from EE
	#------------------------------------------------------------------------
	# define time period of images
	beg_date = datetime.datetime(1999,1,1)
	end_date = datetime.datetime(2014,1,1)
	collection = ee.ImageCollection('LE7_L1T').filterDate(beg_date,end_date) 
	polygon = ee.Feature.MultiPolygon([[bounds]])
	collection = collection.filterBounds(polygon)
	metadata = collection.getInfo()
	print metadata.keys()
	print metadata['features'][0]['id']

	newpath = folder+glacier+"/Landsat"
	if not os.path.exists(newpath): os.makedirs(newpath)

	#------------------------------------------------------------------------
	#                      download Band 61 of the Landsat
	#-----------------------------------------------------------------------

	for i in range(len(metadata['features'])):
		try:
			sceneName = metadata['features'][i]['id']
			print sceneName + ': Scene ' + str(i+1) + ' of ' + str(len(metadata['features']))
			workingScene = ee.Image(sceneName)    
			dlPath = workingScene.getDownloadUrl({
				'scale': 30,
				'bands':[{'id':'B6_VCID_1'},{'id':'B5'},{'id':'B4'},{'id':'B3'},{'id':'B2'}],
				'crs': 'EPSG:4326',
				'region': bounds,
			})
			scenezip = urllib2.urlopen(dlPath)
			# download the zip file to documnet folder
			workingDir = newpath+'/'+sceneName.split('/')[1] 
			# print workingDir
			if not os.path.exists(workingDir):
				os.mkdir(workingDir)
			with open(workingDir + '.zip', "wb") as local_file:
				local_file.write(scenezip.read())
			# unzip the contents
			zfile = zipfile.ZipFile(workingDir + '.zip')
			for j in zfile.namelist():
				jstring = j.encode('ascii','ignore')
				jsp = jstring.split(".")
				if jsp[2] =='tif': 
					fd = open(workingDir + '/' + j,"w")
					fd.write(zfile.read(j))
					fd.close()
					
			# delete the zip file
			os.remove(workingDir + '.zip')
		except:
			continue

	#------------------------------------------------------------------------
	#                       download L5 images from EE
	#------------------------------------------------------------------------
	# define time period of images
	beg_date = datetime.datetime(1984,1,1)
	end_date = datetime.datetime(2012,5,5)
	collection = ee.ImageCollection('LT5_L1T').filterDate(beg_date,end_date) 
	polygon = ee.Feature.MultiPolygon([[bounds]])
	collection = collection.filterBounds(polygon)
	metadata = collection.getInfo()
	print metadata.keys()
	print metadata['features'][0]['id']

	newpath = folder+glacier+"/Landsat"
	if not os.path.exists(newpath): os.makedirs(newpath)

	#------------------------------------------------------------------------
	#                      download Band 6 of the Landsat
	#-----------------------------------------------------------------------

	for i in range(len(metadata['features'])):
		try:
			sceneName = metadata['features'][i]['id']
			print sceneName + ': Scene ' + str(i+1) + ' of ' + str(len(metadata['features']))
			workingScene = ee.Image(sceneName)    
			dlPath = workingScene.getDownloadUrl({
				'scale': 30,
				'bands':[{'id':'B6'},{'id':'B5'},{'id':'B4'},{'id':'B3'},{'id':'B2'}],
				'crs': 'EPSG:4326',
				'region': bounds,
			})
			scenezip = urllib2.urlopen(dlPath)
			# download the zip file to documnet folder
			workingDir = newpath+'/'+sceneName.split('/')[1] 
			if not os.path.exists(workingDir):
				os.mkdir(workingDir)
			with open(workingDir + '.zip', "wb") as local_file:
				local_file.write(scenezip.read())
			# unzip the contents
			zfile = zipfile.ZipFile(workingDir + '.zip')
			for j in zfile.namelist():
				jstring = j.encode('ascii','ignore')
				jsp = jstring.split(".")
				if jsp[2] =='tif': 
					fd = open(workingDir + '/' + j,"w")
					fd.write(zfile.read(j))
					fd.close()
					
			# delete the zip file
			os.remove(workingDir + '.zip')
		except:
			continue

	#------------------------------------------------------------------------
	#                       download L4 images from EE
	#------------------------------------------------------------------------
	# define time period of images
	beg_date = datetime.datetime(1982,8,22)
	end_date = datetime.datetime(1993,12,14)
	collection = ee.ImageCollection('LT4_L1T').filterDate(beg_date,end_date) 
	polygon = ee.Feature.MultiPolygon([[bounds]])
	collection = collection.filterBounds(polygon)
	metadata = collection.getInfo()
	print metadata.keys()
	print metadata['features'][0]['id']

	newpath = folder+glacier+"/Landsat"
	if not os.path.exists(newpath): os.makedirs(newpath)

	#------------------------------------------------------------------------
	#                      download Band 6 of the Landsat
	#-----------------------------------------------------------------------

	for i in range(len(metadata['features'])):
		try:
			sceneName = metadata['features'][i]['id']
			print sceneName + ': Scene ' + str(i+1) + ' of ' + str(len(metadata['features']))
			workingScene = ee.Image(sceneName)    
			dlPath = workingScene.getDownloadUrl({
				'scale': 30,
				'bands':[{'id':'B6'},{'id':'B5'},{'id':'B4'},{'id':'B3'},{'id':'B2'}],
				'crs': 'EPSG:4326',
				'region': bounds,
			})
			scenezip = urllib2.urlopen(dlPath)
			# download the zip file to documnet folder
			workingDir = newpath+'/'+sceneName.split('/')[1] 
			if not os.path.exists(workingDir):
				os.mkdir(workingDir)
			with open(workingDir + '.zip', "wb") as local_file:
				local_file.write(scenezip.read())
			# unzip the contents
			zfile = zipfile.ZipFile(workingDir + '.zip')
			for j in zfile.namelist():
				jstring = j.encode('ascii','ignore')
				jsp = jstring.split(".")
				if jsp[2] =='tif': 
					fd = open(workingDir + '/' + j,"w")
					fd.write(zfile.read(j))
					fd.close()
					
			# delete the zip file
			os.remove(workingDir + '.zip')
		except:
			continue



#ee_download('/home/aseshad/RA/Pipeline/','Rhonegletscher',7.881253,7.707613,45.985001,45.916481)

