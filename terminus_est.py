import os
import itertools
import gdal
from matplotlib import pyplot as plt
import numpy
from scipy import ndimage as ndi
from pandas import Series
from matplotlib.pyplot import xticks
import math
try:
    import pylab
except:
    from matplotlib import pylab


def terminus_est(dd1,tt,distanceTab, invert, distPerYear,flip):
	dataset2 = numpy.asarray(dd1)
	dataset = dataset2.T
	# print dataset1
	# dataset = numpy.flipud(dataset1)
	# print dataset
	# #extra
	# dataset = numpy.flipud(dataset)
	# print dataset
	if flip:
		dataset = numpy.flipud(dataset)
	if invert:
		dataset = numpy.negative(dataset)

	yearTab = numpy.asarray(tt)
	# print yearTab
	yearTab.sort()
	# print len(yearTab)

	maxVal = numpy.zeros(numpy.shape(dataset))
	valFrom = numpy.zeros(numpy.shape(dataset))
	# print(distanceTab)
	jdiff = distanceTab[1] - distanceTab[0]
	#fullIdiff = yearTab[len(yearTab)-1]-yearTab[0]
	if flip:
		yearTab = numpy.flipud(yearTab)

	for i in range(len(dataset)):
	    if i==0:
	        maxVal[i,:] = dataset[i,:]
	        valFrom[i] = range(len(dataset[0])) 
	    else:
	    	if flip:
	    		idiff = yearTab[i-1]-yearTab[i]
	    	else:
	        	idiff = yearTab[i]-yearTab[i-1]
	        # 2000 per year
	        jrange = (distPerYear * idiff)/(jdiff)
	        #bounds on both sides
	        for j in range(4,len(dataset[0])-3):
	            minBound = max(j-jrange,4)
	            maxBound = min(j+jrange,len(dataset[0])-3)
	            # print minBound, maxBound
	            # both were initially 0
	            prev = maxVal[i-1,int(minBound)]
	            prevFrom = int(minBound)
	            for t in range(int(minBound),int(maxBound)):
	                prev = max(prev,maxVal[i-1,t])
	                if prev == maxVal[i-1,t]:
	                    prevFrom = t
	            maxVal[i,j] = prev + dataset[i,j]
	            valFrom[i,j] = prevFrom

	# print maxVal
	# print valFrom

	# dataset2 = numpy.fliplr(dataset2)
	# li = []
	# i = len(maxVal)-1
	#print i
	# curr = numpy.argmax(maxVal[i,:])
	lmax = (numpy.diff(numpy.sign(numpy.diff(maxVal[i]))) < 0).nonzero()[0] + 1
	ind = numpy.argsort(-maxVal[i,lmax])[:5]
	# print maxVal[i,lmax]
	# print lmax[ind]
	terminusPaths = []
	# numpy.savetxt("/home/aseshad/Desktop/last_row.csv",maxVal[i],delimiter = ",")
	for curr in lmax[ind]:
		li = []
		i = len(maxVal) - 1
		while(i>=0):
			# print i
			li.append(curr)
			# print dataset[i,curr]
			curr = valFrom[i,curr]
			i=i-1
		        
		li = numpy.asarray(li, dtype=int)
		if not flip:
			li = numpy.flipud(li)
		terminusPaths.append(li.tolist())
	numpy.savetxt("/home/aseshad/Desktop/path.csv",terminusPaths,delimiter = ",")

	# print terminusPaths

	if flip:
		dataset = numpy.flipud(dataset)
	if invert:
		dataset = numpy.negative(dataset)


	# X,Y=numpy.meshgrid(range(dataset2.shape[0]+1),range(dataset2.shape[1]+1))
	# im = pylab.pcolormesh(X,Y,dataset, cmap='jet')
	# pylab.colorbar(im, orientation='vertical')

	# t = numpy.array(range(len(maxVal)))
	# # print len(terminusPaths[0])

	# # print numpy.shape(t)
	# # print numpy.shape(li)
	# for li in terminusPaths:
	# 	pylab.plot(li,t)
	# if flip:
	# 	pylab.savefig("/home/aseshad/Desktop/Gauli flippedupdated500_try.tiff")
	# else:
	# 	pylab.savefig("/home/aseshad/Desktop/Gauli updated500_try.tiff")
	# pylab.show()
	return terminusPaths


def plotTerminusPaths(dd1,selectedPaths):
	dataset2 = numpy.asarray(dd1)
	dataset = dataset2.T

	X,Y=numpy.meshgrid(range(dataset2.shape[0]+1),range(dataset2.shape[1]+1))
	im = pylab.pcolormesh(X,Y,dataset, cmap='jet')
	pylab.colorbar(im, orientation='vertical')

	t = numpy.array(range(len(selectedPaths[0])))
	# print len(terminusPaths[0])

	# print numpy.shape(t)
	# print numpy.shape(li)
	for li in selectedPaths:
		pylab.plot(li,t)
	pylab.savefig("/home/aseshad/Desktop/Gauli_best3.tiff")
	pylab.show()

def pathCost(dd1,path):
	dataset2 = numpy.asarray(dd1)
	dataset = dataset2.T

	cost = 0
	for i in range(len(path)):
		cost += dataset[i][path[i]]

	return cost


# impath = "/home/aseshad/Desktop/-Gauli Intensity Profile First Derivative .txt"
# dataset2 = numpy.loadtxt(impath)
# yearTab = numpy.loadtxt("/home/aseshad/Desktop/-Gauli year .txt", delimiter=" ")
# distanceTab = numpy.loadtxt("/home/aseshad/Desktop/-Gauli distance along the flow line in meters .txt", delimiter=" ")
# dataset = dataset2[1300:1305,50:55]
# # print dataset
# year = yearTab[50:55]
# distance = distanceTab[1300:1305]
def terminus_paths(dataset2,yearTab, distanceTab,glacier,invert, distPerYear):
	term1 = terminus_est(dataset2,yearTab,distanceTab,invert,distPerYear,0)
	term2 = terminus_est(dataset2,yearTab,distanceTab,invert,distPerYear,1)

	# term1.sort(key = sum, reverse = True)
	# term2.sort(key = sum, reverse = True)
	selectedPaths = []

	selectedPaths.append(term1[0])
	selectedPaths.append(term2[0])

	terminusPaths = numpy.vstack((term1,term2))
	terminusPaths = terminusPaths.tolist()
	if invert:
		terminusPaths.sort(key = sum)
	else:
		terminusPaths.sort(key = sum, reverse = True)

	i=1
	while len(selectedPaths)<4:
		flag = 1
		for path in selectedPaths:
			diff = numpy.absolute(numpy.subtract(path,terminusPaths[i]))
			count = 0
			for val in diff:
				if val<=10:
					count=count+1
			if float(count)/len(diff) >= 0.5 or max(diff) < 10:
				flag = 0
		if flag == 1:
			selectedPaths.append(terminusPaths[i])
		i = i+1
		if i >= len(terminusPaths):
			break

	pathCosts = []
	for path in selectedPaths:
		pathCosts.append(pathCost(dataset2,path))
	
	if invert:
		bestPath = numpy.argmin(pathCosts)
	else:
		bestPath = numpy.argmax(pathCosts)

	# numpy.savetxt(os.getcwd()+"/"+glacier+"_pathcosts",pathCosts,delimiter=',')
	# plotTerminusPaths(dataset2,selectedPaths)
	# selectedPaths = numpy.array(selectedPaths)
	# selectedPathsMatrix = robjects.r.matrix(selectedPaths, nrow=len(selectedPaths))
	# print selectedPaths
	return selectedPaths[bestPath]
