import os
import gdal
import time
import numpy as np
import rpy2.robjects as robjects
import rpy2.rinterface as ri
from rpy2.robjects.numpy2ri import numpy2ri
from rpy2.robjects.conversion import py2ri
from images2gif import writeGif
try:
    from PIL import Image
except:
    from pillow import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
robjects.numpy2ri.activate()

def terminusImages(pathVectors,landsatFiles,GlacierName,terminus,timeline,direc,invert,Input):
	ri.initr()
	robjects.r('''source('plot_terminus.R')''')
	r_lt = robjects.globalenv['loc_terminus']
	loc_terminus = r_lt(pathVectors,0.2,terminus[1])
	# print loc_terminus1
	#print loc_terminus[1][0], loc_terminus[1][len(loc_terminus[1])/2]
	r_mtp = robjects.globalenv['mark_terminus_plot1']
	newpath = direc+"/terminus_images"
	if not os.path.exists(newpath): os.makedirs(newpath)
	i=0
	for time in timeline:
		landsat = gdal.Open(landsatFiles[time], gdal.GA_Update).ReadAsArray()
		if Input != "ndsi":
			landsat = np.int_(landsat)
		rotlandsat = np.rot90(landsat,3)
		# print time, loc_terminus[1][i],loc_terminus[1][len(loc_terminus[1])/2 + i]
		r_mtp(rotlandsat,loc_terminus[0],loc_terminus[1][i],loc_terminus[1][len(loc_terminus[1])/2 + i],terminus[8],terminus[9],GlacierName,time,newpath,invert,Input,landsatFiles[time].replace(Input,"rgb")) #,
		i = i+1

	# createGif(newpath,GlacierName)


def createGif(direc,GlacierName):
	file_names = sorted((fn for fn in os.listdir(direc) if fn.endswith('.png')))
	#print file_names
	images = [Image.open(fn) for fn in file_names]
	filename = GlacierName+".GIF"
	writeGif(filename, images, duration=0.2)
