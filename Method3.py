import rpy2.robjects as robjects
from rpy2.robjects.numpy2ri import numpy2ri
import os
from PIL import Image
import gdal
import numpy
robjects.numpy2ri.activate()

def arcLengthVector(pathVector, stepSize, resolution):
	arcVector = []
	for i in range(len(pathVector)):
		arcVector.append(round(i*stepSize*resolution,1));
	# print len(pathVector), len(arcVector)
	return arcVector

def isLeap(year):
	if ((year%100==0 and year%400==0) or (year%100!=0 and year%4==0)):
		return 1
	return 0

def intensityProfile(imagespath,path,Input,weights,pmissing):
	robjects.r('''source('IntensityProfile.r')''')
	r_ip = robjects.globalenv['IPBL']
	timeline = []
	landsatFiles = {}
	IPTimeSeries = {}
	for images in os.listdir(imagespath):
		for fn in os.listdir(imagespath+'/'+images):
			if fn.endswith('.'+Input+'.tif') or (Input == "B6_VCID_1" and fn.endswith('.B6.tif')):
				# print fn
				time = int(fn[9:13])
				if(isLeap(int(fn[13:16]))):
					time = time + int(fn[13:16])/366.0
				else:
					time = time + int(fn[13:16])/365.0
				# print time
				if(time not in timeline):
					landsat = gdal.Open(imagespath+'/'+images+'/'+fn, gdal.GA_Update).ReadAsArray()
					#if Input != "ndsi":
					landsat = numpy.int_(landsat)
					rotlandsat = numpy.rot90(landsat,3)
					where_are_nan = numpy.isnan(rotlandsat) # this is questionable? there is really nan?
					rotlandsat[where_are_nan] = 0
					# print rotlandsat
					#print im.size
					#image_array = numpy.asarray(im,dtype=int)
					#path = numpy.array(path)
					#print image_array
					#print rotlandsat.shape
					#print rotlandsat
					IP = r_ip(rotlandsat,path,pmissing,weights)
					#print len(IP)
					IParray = numpy.asarray(IP)
					if numpy.sum(IParray) > 0:
						timeline.append(time)
						IPTimeSeries[timeline[-1]] = IP
						landsatFiles[timeline[-1]] = imagespath+'/'+images+'/'+fn
	return (timeline,IPTimeSeries,landsatFiles)

