'''
Created on Mar 28, 2015

@author: Sandhya

Method inputs: starting point x,y, DEM
Method procedure:
    1) Find connected component from original starting point
    2) Find minimum on boundary in that connected component
    3) A* from starting point to the minimum on boundary (which is the new end point)
Method output

'''
import gdal
from skimage import measure
from matplotlib import pyplot as plt
import numpy
import math
import time
import pqdict
import os
from copy import deepcopy

def astar(dataset,src,goal,DEMfile,sample):

    #back up of original original src 
    origsrc = src

    #downsampling
    src = point((int)(math.floor(src.x/sample)),(int)(math.floor(src.y/sample)))
    goal = point((int)(math.floor(goal.x/sample)),(int)(math.floor(goal.y/sample)))
    x_beg = origsrc.x%sample
    y_beg = origsrc.y%sample
    downsampled = dataset[x_beg::sample]
    d = downsampled.transpose()
    downsampled = d[(y_beg)::sample]
    dataset = downsampled.transpose()
    
    
    if goal.x < 0:
        goal.x = 0
    if goal.x > len(dataset)-1:
        goal.x = len(dataset)-1
    if goal.y < 0:
        goal.y = 0
    if goal.y > len(dataset[0])-1:
        goal.y = len(dataset[0])-1
        
    #open and close lists     
    close = pqdict.PQDict()
    open = pqdict.PQDict()

    #array that keeps the points in the path
    path = []
    path.append(src)                                   #source pixel
    
# calculates sld as just the negative of height difference i.e.  -(from-to)
    sld = heuristic(dataset,src,goal)
    cost = 0
    toAdd = PathCost(path,cost)
    open.additem(toAdd, (cost+sld))                                            #add m with priority cost+heuristic
    
    
    while len(open)>0    :
        pathCost,dist = open.popitem()                        #pop smallest length path
        path = pathCost.path
        cost = pathCost.cost
        last = path[len(path)-1]                        #find last pixel on path
        if (last.x == goal.x and last.y == goal.y):                                    #if goal has been reached
            return path
        presentInClosed = False
        presentInOpen = False

        lastX = last.x                                          #x value of last pixel
        lastY = last.y                                          #y value of last pixel\
        for x in range(0,3):
            for y in range(0,3):
                
                nextX = lastX-1+x                    #next pixel's x value
                nextY = lastY-1+y                    #next pixel's y value
                
                if ((x == 1 & y != 1) | (x != 1 & y == 1) | (x!=1 & y!=1)):
                    if nextX < 0:
                        nextX = 0
                    if nextX > len(dataset)-1:
                        nextX = len(dataset)-1
                    if nextY < 0:
                        nextY = 0
                    if nextY > len(dataset[0])-1:
                        nextY = len(dataset[0])-1
                    if (DEMfile == 'srtm90_v4.elevation.tif' and dataset[nextX][nextY]!=0) or (DEMfile == 'GMTED2010.be75.tif'):            # where gorner is giving issue!!! possibly all others also
                        new = point(nextX,nextY)
                         
                        newpath = deepcopy(path)
                        presentInClosed = False
                        presentInOpen = False
                        endNodeHeuristic = heuristic(dataset, new, goal)
                        endNodeCost = cost + distance(dataset, last, new)
                        
                        
                        #find if any path exists where last point is new
                        for key,value in open.items():
                            openRec = key
                            openPath = key.path
                            if openPath[len(openPath)-1].x == new.x and openPath[len(openPath)-1].y== new.y:
                                presentInOpen = True
                                break
                            
                        for key,value in close.items():
                            closeRec = key
                            closePath = key.path
                            if closePath[len(closePath)-1].x == new.x and closePath[len(closePath)-1].y== new.y:
                                presentInClosed = True
                                break
                        
                        if presentInClosed:
                            endNodeRecord = closeRec
                            if(closeRec.cost <= endNodeCost):
                                continue
                            close.pop(endNodeRecord)
                        
                        else:
                            if presentInOpen:
                                endNodeRecord = openRec
                                if(openRec.cost <= endNodeCost):
                                    continue
                            else:
                                endNodeRecord = PathCost(newpath,0)
                        
                        endNodeRecord.cost = endNodeCost
                        newpath.append(new)
                        endNodeRecord.path = newpath
                        if presentInOpen == False:
                            open.additem(endNodeRecord,endNodeCost+endNodeHeuristic)
        close.additem(pathCost,dist)
    if path[len(path)-1].x == goal.x and path[len(path)-1].y == goal.y:
        return path
    else:
        return None


class PathCost:
    def __init__(self,path,cost):
        self.path = path
        self.cost = cost
        
class point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
    
#gives height difference
def distance(dataset,fro,to):
    heightDiff= (dataset[fro.x][fro.y]-dataset[to.x][to.y])/30
    #value = -heightDiff
    value = math.sqrt(abs(math.pow(fro.x-to.x,2) + math.pow(fro.y-to.y,2)))
    return value

#gives euclidean distance in (x,y)
def heuristic(dataset,fro,to, weight=1):
    #set default of weight as 1
    value = weight * math.sqrt(abs(math.pow(fro.x-to.x,2) + math.pow(fro.y-to.y,2)))     #multiply by a weight factor, pass it to the method
    return value

def findEndPointOnBoundary(start_x,start_y,end_x,end_y,dataset):
    # funding connected component containing the starting point
    f2 = numpy.zeros(numpy.shape(dataset))
    for i in range(len(dataset)):
        for j in range(len(dataset[0])):
            if (0 < dataset[i, j] <= dataset[end_x, end_y]):
                f2[i, j] = 1
    L = measure.label(f2,connectivity = 2)
    # #===========================================================================
    # fig = plt.figure()
    # ax = plt.Axes(fig, [0., 0., 1., 1.])
    # ax.set_axis_off()
    # fig.add_axes(ax)
    # ax.imshow(L,cmap="jet")
    # ax.plot(start_y,start_x,'go')
    # plt.savefig(os.getcwd()+"/"+glacier_name+"/"+glacier_name+" connected componentsL1.tif")
    # #===========================================================================
    
    f2 = numpy.zeros(numpy.shape(dataset))
    num = L[end_x,end_y]
    for i in range(len(L)):
        for j in range(len(L[0])):
            if (L[i, j] == num):
                f2[i, j] = 1
    #just the connected component
    dataset2 = f2*dataset

    # # ===========================================================================
    # fig = plt.figure()
    # ax = plt.Axes(fig, [0., 0., 1., 1.])
    # ax.set_axis_off()
    # fig.add_axes(ax)
    # ax.imshow(dataset2,cmap="gray")
    # ax.plot(start_y,start_x,'go')
    # plt.savefig(os.getcwd()+"/"+glacier_name+"/"+glacier_name+"_connected_components1.tif")
    # # ===========================================================================

    #just the boundary
    for i in range(len(dataset2)):
        for j in range(len(dataset2[0])):
            if (i>0 and i < len(dataset2)-1 and j>0 and j < len(dataset2[0])-1  ):
                dataset2[i,j] = None
    
    dataset2[dataset2==0] = None
    
    # #===========================================================================
    # fig = plt.figure()
    # ax = plt.Axes(fig, [0., 0., 1., 1.])
    # ax.set_axis_off()
    # fig.add_axes(ax)
    # ax.imshow(dataset2,cmap="gray")
    # plt.savefig(os.getcwd()+"/"+glacier_name+"/"+glacier_name+"_boundary1.tif")
    # #===========================================================================
    
    
    #top bottom left right
    boundaryDistance = pqdict.PQDict()
    boundaryDistance.additem("top", end_x)
    #print("top", end_x)
    boundaryDistance.additem("bottom", len(dataset2)-end_x)
    #print("bottom", len(dataset2)-end_x)
    boundaryDistance.additem("left", end_y)
    #print("left", end_y)
    boundaryDistance.additem("right", len(dataset2[0])-end_y)
    #print("right", len(dataset2[0])-end_y)

    notFound = True
    while(notFound):
        if(len(boundaryDistance.values())==0): break
        currentBoundary,value = boundaryDistance.popitem()
        dataset3 = numpy.copy(dataset2)
        if(currentBoundary=="top"):
            # print("top")
            for i in range(len(dataset3)):
                for j in range(len(dataset3[0])):
                    if (i>0):
                        dataset3[i,j] = None
                    else:
                        dataset3[i,j] = dataset2[i,j]
            minVal = numpy.nanmin(dataset3)
            endPoints = zip(*numpy.where(dataset3==minVal))
            if len(endPoints) >1:
                notFound = False
        if(currentBoundary=="bottom"):
            # print("bottom")
            for i in range(len(dataset3)-1):
                for j in range(len(dataset3[0])):
                    if (i<len(dataset3)-1):
                        dataset3[i,j] = None
                    else:
                        dataset3[i,j] = dataset2[i,j]
            minVal = numpy.nanmin(dataset3)
            endPoints = zip(*numpy.where(dataset3==minVal))
            if len(endPoints) >1:
                notFound = False
        if(currentBoundary=="left"):
            # print("left")
            for i in range(len(dataset3)):
                for j in range(len(dataset3[0])):
                    if (j>0):
                        dataset3[i,j] = None
                    else:
                        dataset3[i,j] = dataset2[i,j]
            minVal = numpy.nanmin(dataset3)
            endPoints = zip(*numpy.where(dataset3==minVal))
            if len(endPoints) >1:
                notFound = False
        if(currentBoundary=="right"):
            # print("right")
            for i in range(len(dataset3)):
                for j in range(len(dataset3[0])-1):
                    if (j<len(dataset3[0])-1):
                        dataset3[i,j] = None
                    else:
                        dataset3[i,j] = dataset2[i,j]
            minVal = numpy.nanmin(dataset3)
            endPoints = zip(*numpy.where(dataset3==minVal))
            if len(endPoints) >1:
                notFound = False

    if notFound:
        f2 = numpy.zeros(numpy.shape(dataset))
        for i in range(len(dataset)):
            for j in range(len(dataset[0])):
                if (0 < dataset[i, j] <= dataset[end_x, end_y]):
                    f2[i, j] = 1
        L = measure.label(f2,connectivity = 2)
        # #===========================================================================
        # fig = plt.figure()
        # ax = plt.Axes(fig, [0., 0., 1., 1.])
        # ax.set_axis_off()
        # fig.add_axes(ax)
        # ax.imshow(L,cmap="jet")
        # ax.plot(start_y,start_x,'go')
        # plt.savefig(os.getcwd()+"/"+glacier_name+"/"+glacier_name+" connected componentsL2.tif")
        # #===========================================================================

        f2 = numpy.zeros(numpy.shape(dataset))
        num = L[end_x,end_y]
        for i in range(len(L)):
            for j in range(len(L[0])):
                if (L[i, j] != 0):
                    f2[i, j] = 1
        #just the connected component
        dataset2 = f2*dataset
        # # ===========================================================================
        # fig = plt.figure()
        # ax = plt.Axes(fig, [0., 0., 1., 1.])
        # ax.set_axis_off()
        # fig.add_axes(ax)
        # ax.imshow(dataset2,cmap="gray")
        # ax.plot(start_y,start_x,'go')
        # plt.savefig(os.getcwd()+"/"+glacier_name+"/"+glacier_name+"_connected_components2.tif")
        # # ===========================================================================


        for i in range(len(dataset2)):
            for j in range(len(dataset2[0])):
                if (i>0 and i < len(dataset2)-1 and j>0 and j < len(dataset2[0])-1  ):
                    dataset2[i,j] = None

        dataset2[dataset2==0] = None

        # #===========================================================================
        # fig = plt.figure()
        # ax = plt.Axes(fig, [0., 0., 1., 1.])
        # ax.set_axis_off()
        # fig.add_axes(ax)
        # ax.imshow(dataset2,cmap="gray")
        # plt.savefig(os.getcwd()+"/"+glacier_name+"/"+glacier_name+"_boundary2.tif")
        # #===========================================================================


        boundaryDistance.additem("top", end_x)
        #print("top", end_x)
        boundaryDistance.additem("bottom", len(dataset2)-end_x)
        #print("bottom", len(dataset2)-end_x)
        boundaryDistance.additem("left", end_y)
        #print("left", end_y)
        boundaryDistance.additem("right", len(dataset2[0])-end_y)


        while(notFound):
        	if(len(boundaryDistance.values())==0): 
        		break
        	currentBoundary,value = boundaryDistance.popitem()
	        dataset3 = numpy.copy(dataset2)
	        if(currentBoundary=="top"):
	            # print("top")
	            for i in range(len(dataset3)):
	                for j in range(len(dataset3[0])):
	                    if (i>0):
	                        dataset3[i,j] = None
	                    else:
	                        dataset3[i,j] = dataset2[i,j]
	            minVal = numpy.nanmin(dataset3)
	            endPoints = zip(*numpy.where(dataset3==minVal))
	            if len(endPoints) >1:
	                notFound = False
	        if(currentBoundary=="bottom"):
	            # print("bottom")
	            for i in range(len(dataset3)-1):
	                for j in range(len(dataset3[0])):
	                    if (i<len(dataset3)-1):
	                        dataset3[i,j] = None
	                    else:
	                        dataset3[i,j] = dataset2[i,j]
	            minVal = numpy.nanmin(dataset3)
	            endPoints = zip(*numpy.where(dataset3==minVal))
	            if len(endPoints) >1:
	                notFound = False
	        if(currentBoundary=="left"):
	            # print("left")
	            for i in range(len(dataset3)):
	                for j in range(len(dataset3[0])):
	                    if (j>0):
	                        dataset3[i,j] = None
	                    else:
	                        dataset3[i,j] = dataset2[i,j]
	            minVal = numpy.nanmin(dataset3)
	            endPoints = zip(*numpy.where(dataset3==minVal))
	            if len(endPoints) >1:
	                notFound = False
	        if(currentBoundary=="right"):
	            # print("right")
	            for i in range(len(dataset3)):
	                for j in range(len(dataset3[0])-1):
	                    if (j<len(dataset3[0])-1):
	                        dataset3[i,j] = None
	                    else:
	                        dataset3[i,j] = dataset2[i,j]
	            minVal = numpy.nanmin(dataset3)
	            endPoints = zip(*numpy.where(dataset3==minVal))
	            if len(endPoints) >1:
	                notFound = False
    
    
    if notFound:
    	return None, None
    else:           
	    end = point(end_x,end_y)
	   
	    dist = numpy.zeros(len(endPoints))
	    # print endPoints
	    #to find closest min point
	    for i in range(len(endPoints)):
	        x = numpy.array(endPoints[i])
	        dist[i] = math.sqrt(abs(math.pow(end.x-x[0],2) + math.pow(end.y-x[1],2)))
	    dist = numpy.array(dist)
	    x = numpy.argmin(dist)
	    
	    goal = numpy.array(endPoints[x])
	    goal_x = goal[0]
	    goal_y = goal[1]
	    return goal_x,goal_y

def completePathUsingAStar(startX,startY,path1,DEMpath,DEMfile,sample = 4):
    dataset = gdal.Open(DEMpath, gdal.GA_Update).ReadAsArray()
    #dataset = numpy.rot90(dataset1,3)
    start_y = startX
    start_x = len(dataset) - startY

    i = -1
    while True:
        #print i
        endX = path1[i][0]
        endY = path1[i][1]
        #print endX, endY
        end_y = endX
        end_x = len(dataset) - endY
        goal_x,goal_y = findEndPointOnBoundary(start_x,start_y,end_x,end_y,dataset)

        if goal_x == None and goal_y == None:
        	i = i - 1
        else :
        	break

    start = point(end_x,end_y)
    end = point(goal_x,goal_y)
    path = astar(dataset,start,end,DEMfile,sample)
    z = []
    for i in range(len(path)-1):
        z.append([path[i].y*sample,path[i].x*sample])
    z = numpy.array(z)
    # #===========================================================================
    # fig = plt.figure()
    # ax = plt.Axes(fig, [0., 0., 1., 1.])
    # ax.set_axis_off()
    # fig.add_axes(ax)
    # ax.imshow(dataset,cmap="gray")
    # ax.plot(z[:,0],z[:,1])
    # plt.savefig(os.getcwd()+"/"+glacier_name+"/"+glacier_name+" path.tif")
    # #===========================================================================
    for i in range(len(path)-1):
        z[i,1] = len(dataset)-z[i,1]
    z = numpy.array(z)
#    f = open('C:\\Users\\Sandhya\\Desktop\\5 glaciers\\'+glacier_name+'.txt', 'w')
#    for i in range(len(z)-1):
#        x = str(z[i,0])+" "+str(z[i,1])+"\n"
#        f.write(x)
#    f.close()
    return z

# if __name__== '__main__':
    
#     glacier = ['MURCHISON','Fassett','GAULIGLETSCHER','Ferebee','Fraenkel']
#     startX = [438,200,348,528,89]
#     startY = [326,170,453,118,131]
#     endX = [288.1,100.4,307.5,637.3,108.4]
#     endY = [123.6,44.2,116.1,25.9,147.0]
#     for i in range(len(glacier)):
#         glacier_name = glacier[i]
#         DEMpath = os.getcwd()+"/"+glacier_name+"/srtm90_v4.elevation.tif"
#         start_time = time.time()
#         path = completePathUsingAStar(startX[i],startY[i],endX[i],endY[i],DEMpath)
#         print(glacier[i],time.time()-start_time)
        
    
