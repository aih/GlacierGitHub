#--------------------------------------------------------------------------------------------------
#  Update GD.linear.sample to include the median option 
#--------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------
# This is a helper function called internally by GD.linear.sample
# input - matrix2: matrix to find gradient descend path from (DEM/ or resampled DEM)
#       - coord: starting coordinate
#       - block: block size to fit linear regression for calculating gradient
#       - step.size: distance between points on the path 
#--------------------------------------------------------------------------------------------------
library(matrixStats)

GD <- function(matrix2, coord, block, step.size, nrow, ncol){
  complete = 0
  b = block/2
  nrow2 <- nrow(matrix2)
  ncol2 <- ncol(matrix2)
  maxiters <- round((nrow2 + ncol2) / step.size)
  coord.matrix <- matrix(coord, nrow = 1)
  for(i in 1: maxiters){
    x <- coord[1]
    y <- coord[2]
    xmin <- max(round(x-b), 0)
    xmax <- min(round(x+b), nrow2)
    ymin <- max(round(y-b),0)
    ymax <- min(round(y+b), ncol2)
    block <- matrix2[xmin:xmax,ymin:ymax]
    nrow1 = nrow(block)
    ncol1 = ncol(block)
    Z<- as.vector(block) 
    X <- as.numeric(gl(nrow1,1,nrow1*ncol1))
    Y= as.numeric(gl(ncol1,nrow1,ncol1*nrow1))
    lm = lm(Z ~ X+Y ) 
    dx= summary(lm)[4][[1]][2,1]
    dy= summary(lm)[4][[1]][3,1]
    if(dx ==0 | dy ==0 ){break}
    multiplier <- step.size / sqrt(dx^2 + dy^2)
    x <- x - multiplier * dx
    y <- y - multiplier * dy
    coord <- c(x,y)
    new.coord <- matrix(coord, nrow=1)
    if(x<=1|x>=nrow2|y<=1|y>=ncol2){ complete = 1
                                     break} # terminate at boundary
    if(nrow(merge(coord.matrix,new.coord))>0){break} # terminate at loop
    coord.matrix <- rbind(coord.matrix, new.coord)  
  }
  coord = coord.matrix
#   print(coord)
  coord = coord[coord[,1] <= nrow,]
#   print(coord)
  coord = coord[coord[,2] <= ncol,]
#   print(coord)
  list(coord =coord, complete = complete)
}

#---------------------------------------------------------------------------------------------------
# find the glacier flow line using gradient descend method on sampled DEM matrix
# the gradient is found using bilinear regression on a neighbourbood block 
# input 
# - matrix: DEM matrix
# - initial coord: initial coordinates of the path. example: c(100,214)
# - sample = c(1, 0): 1=down sample the image, 0=do not down sample the image 
# - diag: diagnal length size of matrix after sampling
# - option = c("median","regular"): when median option used, the median location of 
#         multiple paths found using different block sizes is returned 
# - block: block size for bilinear regression for "regular" option
# - blocks: a vector of block sizes for "median" options
# output
# - coord: coordinate matrix of the path with two columns for x, y coordinates
# - complete: whether the path reach the boundry of the DEM
#             0 - path did not reach boundry
#             1 - path reached the boundry
#-------------------------------------------------------------------------------------------------------
#  Example usage: 
#  GD.linear.sample(matrix = DEM, initial.coord = initial.coord, sample = 0) gives default median path without resampling 
#  GD.linear.sample(matrix = DEM, initial.coord = initial.coord,sample =0, option ="regular", block = 30) gives default regular path 
#-------------------------------------------------------------------------------------------------------
GD.linear.sample <- function(matrix, initial.coord, sample = 1, diag = 450, option ="median", block= 30, blocks = c(30,40,50,60,70)){
    nrow <- nrow(matrix)
    ncol <- ncol(matrix)
    if(sample == 0){ 
        k = 1 
    }else{
        k = ceiling(norm(dim(matrix),type="2")/diag)
    }
    matrix2 = matrix[seq(1:ceiling(nrow/k))*k-(k-1),seq(1:ceiling(ncol/k))*k-(k-1)]
    coord = ceiling(initial.coord/k)
    step.size = ceiling(5/k)
    if(option == "regular"){
        result = GD(matrix2, coord, block, step.size, nrow, ncol)
        coord.matrix = result$coord
        complete = result$complete
    }
 
    if(option == "median"){
        coord.unsmooth = coord.smooth = coord.ele = NULL
        complete.list = c()
        for(j in 1:length(blocks)){
            path = GD(matrix2, coord, blocks[j], step.size, nrow, ncol)
            coord.unsmooth[[j]] = path$coord
            coord.smooth[[j]] = path_smooth(path$coord, step.size = step.size, thin = 5)
            complete.list = c(complete.list, path$complete)
        }
        coordx = coordy = matrix(NA,nrow = max(unlist(lapply(coord.smooth, nrow))),ncol = length(blocks))
        for(j in 1:length(blocks)){
           coordx[1:nrow(coord.smooth[[j]]), j] = coord.smooth[[j]][,1]
           coordy[1:nrow(coord.smooth[[j]]), j] = coord.smooth[[j]][,2]
        }
        coord.matrix = matrix(c(rowMedians(coordx, na.rm = T), rowMedians(coordy, na.rm = T)), ncol = 2)
        complete = max(complete.list)
    } 
    coord = k*coord.matrix
    list(coord = coord, complete = complete)
}

#-----------------------------------------------------------------------------------
#  produce a smooth path with fixed step size
#  input 
# - coord: coordinate matrix of unsmoothed path with two columns for x, y coordinates
# - step.size: arc length between consecutive steps (in pixels)
# - thin: steps per knots for gam function 
#  output
# - smoothed coordinate matrix with two columns
library(mgcv)
path_smooth <- function(coord, step.size = 0.5, thin = 3){
  arc = c(0,sqrt(rowSums((coord[2:nrow(coord),]-coord[1:nrow(coord)-1,])^2)))
  cumarc= sapply(1:length(arc), function(x) sum(arc[1:x]))
  fit_arc = seq(1,cumarc[length(cumarc)], 3)
  fit_x = matrix(predict(gam(c(coord[,1])~s(cumarc,k = round(length(cumarc)/thin))), data.frame(cumarc=fit_arc)), ncol = 1)
  fit_y = matrix(predict(gam(c(coord[,2])~s(cumarc,k = round(length(cumarc)/thin))), data.frame(cumarc=fit_arc)), ncol = 1) 
  coord = cbind(fit_x,fit_y)
  arc = c(0,sqrt(rowSums((coord[2:nrow(coord),]-coord[1:nrow(coord)-1,])^2)))
  cumarc= sapply(1:length(arc), function(x) sum(arc[1:x]))
  fit_arc = seq(1,cumarc[length(cumarc)], step.size)
  fit_x = matrix(predict(gam(c(coord[,1])~s(cumarc,k = round(length(cumarc)/thin))), data.frame(cumarc=fit_arc)), ncol = 1)
  fit_y = matrix(predict(gam(c(coord[,2])~s(cumarc,k = round(length(cumarc)/thin))), data.frame(cumarc=fit_arc)), ncol = 1) 
  return(cbind(fit_x,fit_y))
}


#--------------------------------------------------------------------------------
# update the function to return a single dataframe consists of 4 paralle paths
# and original smoothed path 
# output update to be return a single R dataframe
#--------------------------------------------------------------------------------
# find four paths parallel to the given smoothed path with two path on either sides
# input 
# - coord: smoothed path matrix
# - matrix: DEM matrix
# - dist: distance(in pixels) beteween parallel paths
# output 
# - df2: a data frame consists the coordinates for 4 paths with the following variables
#       x,y, x1, y1, x2, y2, x3, y3, x4, y4
path_parallel <- function(coord, matrix, dist = 2.5, numparallel = 2){
  m = nrow(coord)
  dcoord = rbind((coord[2:m,]- coord[1:(m-1),]), (coord[m,] - coord[(m-1),]))
  dcoord = dist*(dcoord/sqrt(dcoord[,1]^2 +dcoord[,2]^2))
  s1 = cbind(dcoord[,2],-dcoord[,1])
  s2 = cbind(-dcoord[,2],dcoord[,1])
#   coord1 = coord + s1
#   coord2 = coord + s2
#   coord3 = coord + 2*s1
#   coord4 = coord + 2*s2
#   coord5 = coord + 3*s1
#   coord6 = coord + 3*s2
  nrow = nrow(matrix)
  ncol = ncol(matrix)
  # delete points out of the image margin 
  df = data.frame(x = coord[,1], y = coord[,2])
  if (numparallel !=0) {
    for ( i in 1:numparallel) {
      coord.parallel = coord + i*s1
      df[paste("x",2*i -1,sep="")] = coord.parallel[,1]
      df[paste("y",2*i -1,sep="")] = coord.parallel[,2]
      
      coord.parallel = coord + i*s2
      df[paste("x",2*i,sep="")] = coord.parallel[,1]
      df[paste("y",2*i,sep="")] = coord.parallel[,2]
    }
  }
#                   x1 = coord1[,1], y1 = coord1[,2],
#                   x2 = coord2[,1], y2 = coord2[,2],
#                   x3 = coord3[,1], y3 = coord3[,2],
#                   x4 = coord4[,1], y4 = coord4[,2],
#                   x5 = coord5[,1], y5 = coord5[,2],
#                   x6 = coord6[,1], y6 = coord6[,2])
#   df1 = subset(df, x>=1 & x1>=1 & x2>=1 & x3>=1 & x4>=1 & x5>=1 & x6>=1 & x<=nrow & x1<= nrow & x2 <= nrow & x3 <= nrow & x4 <= nrow & x5 <= nrow & x6 <= nrow)
#   df2 = subset(df1, y>=1 & y1>=1 & y2>=1 & y3>=1 & y4>=1 & y5>=1 & y6>=1 & y<= ncol & y1<= ncol & y2 <= ncol & y3 <= ncol & y4 <= ncol & y5 <= ncol & y6 <= ncol)
  return(df)
}
#---------------------sample test code----------------------
# DEM = # input DEM
# B61 = # input B61 for plotting purpose
# init_coord = c(x,y)# input initial coord
# dir = # input directory to output image
# 
# # find path use bilinear regression gradient descend 
# path = GD.linear.sample(DEM, init_coord)
# coord = path$coord
# nrow = nrow(DEM)
# ncol = ncol(DEM)
# complete = path$complete 
# 
# # if complete = 0, use Sandhya's method to find the remaining path with last row of coord 
# # as the initial point, combine the two path and proceed to smoothing
#                          
# # if complete = 1, proceed to smoothing 
# 
# # smooth path 
# coord.smooth = path_smooth(coord, thin = 20)
# 
# # find parallel paths
# coord.parallel = path_parallel(coord.smooth,DEM, dist=100)
# coord.p1 = coord.parallel$coord1 # parallel path 1
# coord.p2 = coord.parallel$coord2 # parallel path 2
# 


#-------------------------------------------------------------------------------------
# updated to take the output from path_parallel function, and do no plot unsmoothed
# path 
# input updated to take the data frame produced by path_parallel (coord.parallel) 
# instead of seperate path coordinates ( coord, coord.smooth,coord.p1,coord.p2)
#-------------------------------------------------------------------------------------
# function to plot all paths on B61
# input - B61: B61 matrix
#       - dir: directory to save the image as a string
#       - glacier: glacier name as a string
#       - coord.parallel: a dataframe returned by path_parallel function 
#                         contains coordinates for 4 paralle paths and 
#                         orginal smoothed path 

library(fields)
library(grDevices)
plot_allpath <- function(B61, dir, glacier, coord.parallel,numparallel,lower,upper,invert){
  setwd(dir)
  main = paste(glacier," with parallel paths")
  nrow = nrow(B61)
  ncol = ncol(B61)
  col_B61<- colorRampPalette(c("tan4", "lightblue2"))
  B61[which(B61 > upper)] = upper
  B61[which(B61 < lower)] = lower
  if(invert == 1){
    col <- col_B61(20)
  }
  else {
    col <- col_B61(20)[20:1]
  }
  png(paste(main,'.png'), width=max(6,6*nrow/ncol)  ,height = max(6,6*ncol/nrow), units = 'in', res = 300)
  image.plot(1:nrow,1:ncol,B61,zlim = c(lower,upper),ann=T,asp = T, axes = F, col = col,cex =max(1, nrow/ncol), axis.args = list(cex.axis = 1),legend.shrink = 0.5, legend.width = 0.8)
  lines(c(coord.parallel$x),c(coord.parallel$y), col ="red",lwd = 2)# smoothed path
  if (numparallel !=0) {
    for ( i in 1:(ncol(coord.parallel)/2)-1 ){
      lines(c(coord.parallel[[paste("x",i,sep="")]]),c(coord.parallel[[paste("y",i,sep="")]]), col ="yellow",lwd = 2)# parallel paths
    }
  }
#   lines(c(coord.parallel$x1),c(coord.parallel$y1), col ="yellow",lwd = 2)# parallel path 1
#   lines(c(coord.parallel$x2),c(coord.parallel$y2), col ="yellow",lwd = 2)# parallel path 2
#   lines(c(coord.parallel$x3),c(coord.parallel$y3), col ="purple",lwd = 2)# parallel path 1
#   lines(c(coord.parallel$x4),c(coord.parallel$y4), col ="purple",lwd = 2)# parallel path 2
#   lines(c(coord.parallel$x5),c(coord.parallel$y5), col ="yellow",lwd = 2)# parallel path 1
#   lines(c(coord.parallel$x6),c(coord.parallel$y6), col ="yellow",lwd = 2)# parallel path 2
  dev.off()
}

# plot parallel paths on DEM
plot_allpathDEM <- function(DEM, dir, glacier, coord.parallel,numparallel,invert){
  nrow = nrow(DEM)
  ncol = ncol(DEM)
  col_B61<- colorRampPalette(c("tan4", "lightblue2"))
  if(invert == 1){
    col <- col_B61(20)
  }
  else {
    col <- col_B61(20)[20:1]
  }
  setwd(dir)
  main = paste(glacier," with parallel paths on DEM")
  png(paste(main,'.png'), width=max(6,6*nrow/ncol)  ,height = max(6,6*ncol/nrow), units = 'in', res = 300)
  image.plot(1:nrow,1:ncol,DEM,ann=F,asp = T, axes = F, col = col,cex =max(1, nrow/ncol), axis.args = list(cex.axis = 1),legend.shrink = 0.5, legend.width = 0.8)
  lines(c(coord.parallel$x),c(coord.parallel$y), col ="red",lwd = 2)# smoothed path
  if(numparallel !=0) {
    for ( i in 1:(ncol(coord.parallel)/2)-1 ){
      lines(c(coord.parallel[[paste("x",i,sep="")]]),c(coord.parallel[[paste("y",i,sep="")]]), col ="yellow",lwd = 2)# parallel paths
    }
  }
  dev.off()
  
}








