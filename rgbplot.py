import os
import numpy as np
import scipy.misc as mi
try:
    from PIL import Image
except:
    from pillow import Image
from libtiff import TIFF
import matplotlib.pyplot as plt
import matplotlib.cm as cm
try:
    import pylab
except:
    from matplotlib import pylab
import gdal
import shutil

import ee_download
import Method2

def rgbPlot(image):
	files = os.listdir(image)
	for im in files:
		if im.endswith('.B3.tif'): 
			b3 = gdal.Open(image+"/"+im, gdal.GA_Update).ReadAsArray()
		if im.endswith('.B4.tif'): 
			b4 = gdal.Open(image+"/"+im, gdal.GA_Update).ReadAsArray()
		if im.endswith('.B5.tif'): 
			b5 = gdal.Open(image+"/"+im, gdal.GA_Update).ReadAsArray()

	direc = image
	dirsplit = direc.split('/')
	n = len(dirsplit)
	folder = dirsplit[n-1]
	rgb = np.dstack((b5,b4,b3))
	my_dpi=100.0
	f = plt.figure(frameon = False)
	f.set_size_inches(rgb.shape[1]/my_dpi, rgb.shape[0]/my_dpi)

	ax = plt.Axes(f, [0., 0., 1., 1.])
	ax.set_axis_off()
	f.add_axes(ax)

	ax.imshow(rgb, aspect='normal')
	f.savefig(image+"/"+folder+".rgb.tif")
	plt.close()


def ndsi(image):
	files = os.listdir(image)

	for im in files:
		if im.endswith('.B2.tif'): 
			b2 = gdal.Open(image+"/"+im, gdal.GA_Update).ReadAsArray()
		if im.endswith('.B5.tif'): 
			b5 = gdal.Open(image+"/"+im, gdal.GA_Update).ReadAsArray()

	direc = image
	dirsplit = direc.split('/')
	n = len(dirsplit)
	folder = dirsplit[n-1]
	b2f = b2.astype(np.float)
	b5f = b5.astype(np.float)
	nrf = np.subtract(b2f, b5f)
	drf = np.add(b2f,b5f)
	np.seterr(divide='ignore', invalid='ignore')
	ndsi = np.divide(nrf,drf) 
	ndsi = np.nan_to_num(ndsi)
	ndsi1 = mi.bytescale(ndsi) # interpolate image to [0,255]
	ndsi_ind = np.int64(drf>0)
	ndsi1 = np.multiply(ndsi_ind, ndsi1)
	ndsi1 = mi.bytescale(ndsi1)
	tif = TIFF.open(image+"/"+folder+".ndsi.tif", mode = 'w')
	tif.write_image(ndsi1)


def downloadAndClassifyLandsat(GlacierName, path, BoundingBox):
	ee_download.ee_download_Allbands(path,GlacierName,float(BoundingBox[0]),float(BoundingBox[2]),float(BoundingBox[1]),float(BoundingBox[3]))
	Method2.classify(path+"Data/"+GlacierName+"/Landsat/",0.7,-21.153,0.176,0.550)
	images = [x[0] for x in os.walk(path+"Data/"+GlacierName+"/Landsat/")]
	for image in images[1:]:
		rgbPlot(image)
		ndsi(image)
	

