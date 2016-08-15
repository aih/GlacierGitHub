import os
import querydb
import ee_download
import Method1
import Method2
import Method3
import Method4
import TI
import fnmatch
import glob
from PIL import Image
import rgbplot

# Used in step 7
def find(pattern, path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result = os.path.join(root, name)
    return result

# General parameters
GlacierID=""
GlacierNames= ["Athabasca Glacier","Chaba Glacier","COXE","David Glacier","Fassett","Fox, Explorer","Litian glacier","North Canoe Glacier","CORBASSIERE GLACIER DE","FERPECLE GLACIER DE","FIESCHERGLETSCHER VS","Findelengletscher","FORNO VADREC DEL","FRANZ JOSE","GAULIGLETSCHER","GORNERGLETSCHER","GROSSER ALETSCH GLETSCHER","MONT MINE GLACIER DU","MORTERATSCH VADRET DA","OTEMMA","Rhonegletscher","Ferebee","Fraenkel","Mer de Glace","MURCHISON","Torre"]

imageInv = ["B2","B3","B4","ndsi"]
noImageInv = ["B5","B6_VCID_1","61"]
Input = "B6_VCID_1"  #from the above list of bands
classification = "algorithm"   #algorithm or manual
flowline = "median"  #regular or median
numParallel = 0   #number of parallel paths on each side
distPerYear = 96   #max distance per year for retreat or advance in metres
weights = "central"    # Central, Linear or equal

path = os.path.abspath('..')+"\\"

# Main loop over glaciers
for GlacierName in GlacierNames:
	os.chdir(path+'/Code')
	print GlacierName
	if Input in imageInv:
		invert = 1
	else:
		invert = 0
	
	try:
		#1.From Glims Database
		print "1.Querying Database for glacier bounds"
		BoundingBox = querydb.findBoundingBoxByName(GlacierName)
		StartPoint =  querydb.findStartByName(GlacierName)
		
		#2.From Earth Engine
		print "2.Downloading from earth engine and classification"
		DEMfile = ee_download.ee_download_DEM(path,GlacierName,float(BoundingBox[0]),float(BoundingBox[2]),float(BoundingBox[1]),float(BoundingBox[3]))
		rgbplot.downloadAndClassifyLandsat(GlacierName,path,BoundingBox)
			
		#4.Method1 - Finding the path of the glacier
		print "4.Determining the flowline of the glacier"
		print os.getcwd()
		dim = Method1.getDimensions(path+'Data/'+GlacierName+'/'+DEMfile)
		start = Method1.beginningPoint(float(BoundingBox[0]),float(BoundingBox[1]),float(BoundingBox[2]),float(BoundingBox[3]),float(StartPoint[0]),float(StartPoint[1]),dim[0],dim[1],0.1)
		print start
		GLpath = Method1.findPath(path+'Data/'+GlacierName+'/'+DEMfile,int(start[1]),int(start[0]),flowline,DEMfile)
		pathVector = Method1.smoothPath(GLpath)
		pathVectors = Method1.parallelPath(pathVector,path+'Data/'+GlacierName+'/'+DEMfile,numParallel)

		#5.Method3 - Calculating the intensity profile time series
		print "5.Computing the Intensity profile Time Series"
		timeline,ipTimeSeries, landsatFiles = Method3.intensityProfile(path+'Data/'+GlacierName+'/Landsat/',pathVectors,Input,weights)
		timeline.sort()
		arcVector = Method3.arcLengthVector(ipTimeSeries[timeline[0]],0.2,30)

		#6.Method4 - Estimating the terminus
		print "6.Estimating Terminus and plot results"
		gm = querydb.findGroundMeasurement(GlacierName)
		grndmeas = {}
		list1 = []
		list2 = []
		for item in gm:
			list1.append(int(item[0]))
			list2.append(float(item[1]))
		grndmeas['year'] = list1
		grndmeas['gm'] = list2
		terminus = Method4.estimateTerminus(path+'Results/'+GlacierName+'/'+Input,GlacierName,arcVector,timeline,ipTimeSeries,grndmeas,invert,distPerYear)

		#7.Plotting flowline
		print "7.Plotting flowline"
		folder = os.listdir(path+'Data/'+GlacierName+'/Landsat/')
		if Input != 'B6_VCID_1':
			img = find('*.'+Input+'.tif',path+'Data/'+GlacierName+'/Landsat/'+folder[-1])
		else:
			img = find('*.B6.tif',path+'Data/'+GlacierName+'/Landsat/'+folder[-1])
		os.chdir(path+'/Code')
		Method1.plotPaths(pathVectors,path+'Results/'+GlacierName+'/'+Input,GlacierName,img,numParallel,invert,Input,terminus[8],terminus[9])
		os.chdir(path+'/Code')
		Method1.plotPathsDEM(pathVectors,path+'Results/'+GlacierName,GlacierName,path+'Data/'+GlacierName+'/'+DEMfile,numParallel,invert)

		#8. Create series of images with terminus location
		print "8.Generating terminus Plots"
		os.chdir(path+'/Code')
		TI.terminusImages(pathVectors,landsatFiles,GlacierName,terminus,timeline,path+'Results/'+GlacierName+'/'+Input,invert,Input)

	except:
		continue	
