#---------------------------------------------------------------------------------
# updated to take in the data frame outputed from path_parallel, and calculate 
# an average intensity profile from the parallel paths 
# input updated to take in coord.parallel ( output from path_parallel) instead
# of path.mat, add input parameter "weight = c(0.8,0.05,0.05,0.05,0.05)"
#-----------------------------------------------------------------------------
#---------------Method 3: Extract intensity profile from B61------------------
#-----------------------------------------------------------------------------
library(mgcv)
# Use bilinear iterpolation to find intensity profile as weighted avarge 
# of parallel paths 
# input - B61: B61 matrix
#        - coord.parallel: a dataframe returned by path_parallel function 
#                         contains coordinates for 4 paralle paths and original
#                         smoothed path 
#        - pmissing: percentage of missing value on the intensity profile 
#        - weight: weight assigned to the orginal paths and 4 parallel paths to average the 
#                  intensity profiles. The order the weight correspond to are:
#                  orginial smoothed path, two inner parallel paths, two outer parallel paths
#       
#output - value: intensity profile as matrix of 1 columns of intensity along the path 

IPBL<- function(B61, coord.parallel, pmissing , weighting = "linear"){
  # use bilinear interpolation to find intensity from B61
  # Assumes that missing values are set to 0
  numparallel <- ncol(coord.parallel)/2
  if (weighting == "linear") {
    weight = c((numparallel+1)/2, rep(((numparallel-1)/2) : 1, each = 2))
  }
  else if(weighting == "central") {
    weight = c(1, rep(0,(numparallel-1)))
  }
  else if(weighting == "equal") {
    weight = rep(1/numparallel, numparallel)
  }
  nrow <- nrow(coord.parallel)
  value <- matrix(0, ncol = 1, nrow = nrow )
  c = 0
  for (i in 1: nrow){
    intensity_list = rep(0, numparallel)
    for (j in 1:numparallel ){
      x = coord.parallel[i, (2*j-1)]
      y = coord.parallel[i, (2*j)]
      xmin <- max(floor(x),1)
      ymin <- max(floor(y),1)
      a <- x - xmin
      b <- y - ymin
      block <- c(0,0,0,0)
      block[1] <- ifelse(xmin>=1 & xmin<=nrow(B61) & ymin>=1 & ymin<=ncol(B61), B61[xmin,ymin], 0)
      block[2] <- ifelse((xmin+1)>=1 & (xmin+1)<=nrow(B61) & ymin>=1 & ymin<=ncol(B61), B61[xmin+1,ymin], 0)
      block[3] <- ifelse(xmin>=1 & xmin<=nrow(B61) & (ymin+1)>=1 & (ymin+1)<=ncol(B61), B61[xmin,ymin+1], 0)
      block[4] <- ifelse((xmin+1)>=1 & (xmin+1)<=nrow(B61) & (ymin+1)>=1 & (ymin+1)<=ncol(B61), B61[xmin+1,ymin+1], 0)
      #block <- c(B61[xmin:(xmin+1),ymin:(ymin+1)])
      ind1 <- (block > 0)*1  # Indicator of non-missing values
      weight1 <- c((1-a)*(1-b), (1-b)*a, b*(1-a),a*b)   # bilinear interpolation
      # (xmin, ymin),(xmin+1,ymin),(xmin,ymin+1),(xmin+1,ymin+1)
      weight1 <- weight1 * ind1
      if(sum(weight1)==0){
        intensity_list[j] = 0
      }else{
        intensity_list[j] = sum(block*weight1)/sum(weight1) 
      }
    }
    ind= (intensity_list >0)*1  # Indicator of non-missing values
    if(sum(ind*weight)==0){
      c = c+1
      value[i, 1] <- 0 
    }else{
      value[i,1] <- sum(intensity_list*weight)/sum(ind*weight)
    }   
  }
  
  # use gam to interporlate missing values from existing valeus
  y = value
  if(c>0){
    if(c<=pmissing*nrow){
      y1 = y[which(!y==0)]
      x1 = which(!y==0)
      x2 = which(y==0)
      g = gam(y1~s(x1, k= round(length(x1)/10)))
      y[which(y==0)] <- predict(g,data.frame(x1=x2))
    }else{ y = 0}  # value is 0 if more than 20% is missing on the intensity profile 
    
  }
  value = y 
  return(value)
}
