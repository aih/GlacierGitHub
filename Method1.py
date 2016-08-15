import os
import gdal
import time
import numpy as np
import matplotlib.pyplot as plt
import pylab
from scipy.ndimage.filters import gaussian_filter1d
import math
import rpy2.robjects as robjects
from rpy2.robjects.numpy2ri import numpy2ri
try:
    from PIL import Image
except:
    from pillow import Image 

import ConnectedComponentAStar
robjects.numpy2ri.activate()

def getDimensions(filename):
	im = Image.open(filename)
	return (im.size[0],im.size[1])


def beginningPoint(maxLon,maxLat,minLon,minLat,Lon,Lat,ncol,nrow,margin):
	# print maxLon,maxLat,minLon,minLat
	minLon1 = minLon - margin*(maxLon-minLon)
	maxLon1 = maxLon + margin*(maxLon-minLon)
	minLat1 = minLat - margin*(maxLat-minLat)
	maxLat1 = maxLat + margin*(maxLat-minLat)
	# print maxLon1,maxLat1,minLon1,minLat1
	beg_col = round(ncol*(Lon-minLon1)/(maxLon1-minLon1))
	beg_row = round(nrow*(Lat-minLat1)/(maxLat1-minLat1))
	# print (beg_row,beg_col)
	return (beg_row,beg_col)


def findPath(DEMpath,start_x,start_y,flowline,DEMfile):
	DEM = np.array(gdal.Open(DEMpath).ReadAsArray())
	mean = np.mean(DEM)
	# print mean
	rotated = np.rot90(DEM,3)
#	print DEM[start_x][start_y]
	DEMmatrix = robjects.r.matrix(rotated,nrow = len(rotated))
	# print DEMmatrix.nrow,DEMmatrix.ncol
	# print start_x, start_y
#	print DEM[start_x][start_y],DEM[0][0],DEM[427][0],DEM[0][735],DEM[427][735]
	start = robjects.IntVector([start_x,start_y])
	robjects.r('''source('gd_linear.R')''')
	r_path = robjects.globalenv['GD.linear.sample']
	glacier_path = r_path(DEMmatrix,start,0,450,flowline,30)
	path1 = np.array(glacier_path[0])
	#print len(path1)
	#print path1
	if int(glacier_path[1][0]) == 1:
		GLpath = path1
	else:
		path2 = np.array(ConnectedComponentAStar.completePathUsingAStar(start_x,start_y,path1,DEMpath,DEMfile))
		#flipped = np.fliplr(path2)
	#	print path2[0]
		GLpath = np.vstack([path1.astype(float),path2])
	#	print GLpath
	return GLpath

def smoothPath(glacier_path, step_size):
	robjects.r('''source('gd_linear.R')''')
	r_smooth = robjects.globalenv['path_smooth']
	pathVector = r_smooth(glacier_path,step_size,3)
	#print len(pathVector)
	return pathVector #np.array(pathVector)

def parallelPath(pathVector, DEMpath, numParallel):
	DEM = gdal.Open(DEMpath, gdal.GA_Update).ReadAsArray()
	rotated = np.rot90(DEM,3)
	DEMmatrix = robjects.r.matrix(rotated,nrow = len(rotated))
	robjects.r('''source('gd_linear.R')''')
	r_parallel = robjects.globalenv['path_parallel']
	pathVectors = r_parallel(pathVector,DEMmatrix,2.5,numParallel)
	#print pathVectors
	return pathVectors

def plotPaths(pathVectors,direc,glacier,landsatpath,numparallel,invert,Input,lower,upper):
	landsat = gdal.Open(landsatpath, gdal.GA_Update).ReadAsArray()
	if Input != "ndsi":
		landsat = np.int_(landsat)
	rotlandsat = np.rot90(landsat,3)
	# print "coming here"
	direc = direc
	if not os.path.exists(direc): os.makedirs(direc)
	landsatmatrix = robjects.r.matrix(rotlandsat,nrow = len(rotlandsat))
	robjects.r('''source('gd_linear.R')''')
	r_plot = robjects.globalenv['plot_allpath']
	r_plot(landsatmatrix,direc,glacier,pathVectors,numparallel,lower,upper,invert)


def plotPathsDEM(pathVectors,direc,glacier,DEMpath,numparallel,invert):
	DEM = gdal.Open(DEMpath, gdal.GA_Update).ReadAsArray()
#	landsat1 = np.int_(landsat)
	rotDEM = np.rot90(DEM,3)
	# print "coming here"
	if not os.path.exists(direc): os.makedirs(direc)
	DEMmatrix = robjects.r.matrix(rotDEM,nrow = len(rotDEM))
	robjects.r('''source('gd_linear.R')''')
	r_plot = robjects.globalenv['plot_allpathDEM']
	r_plot(DEMmatrix,direc,glacier,pathVectors,numparallel,invert)
