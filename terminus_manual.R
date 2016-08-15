# modified terminus_plot and terminus to take 3 candidate terminus
# will produce 3 seperate plot 2, plot 3, plot 4 corresponding to 3 candidate terminus 
# python.call("terminus_est",sSmooth$dd1,tt,ss,invert,distPerYear) need to return a matrix
# of 3 columns corresponding to best, second best, third best terminus 




########################################################################
#  AUTHOR: Adithya Seshadri
#   DATE : 15JUN2015
# PURPOSE: break down the Terminus Estimate step (originally path function) in 
#          the pipeline into 3 steps: 
#          (1) spacial smoothing
#          (2) terminus estimation
#          (3) temporal smoothing
# UPDATED FUNCTIONS IN PIPELINE
#          delete: Path
#          add: spatial_smooth, terminus_est, temporal_smooth
#          update: terminus
#          all updates are internal for functions, codes used for calling
#          function in main pipeline should be unchanged
##########################################################################


rm(list = ls())
# Method 4 Estimate Terminus
library(fda); library(splines); library(mgcv); library(MASS); library(fields)
library(grDevices)


# ------------------break path function into 3 functions-------------------
# Step 1:  spactial smoothing of intensitu profile time series matrix
# input  - obs: intensity profile time series matrix, with row corresponding to
#              intensity at same arc length
#        - ss: arc length vector (unit: meter)
#        - KnotS: number of knots
# output - dd1: first derivative matrix of intensity profile time series matrix 
#        - dd3: third derivative matrix of intensity profile time series matrix 
#        - est: spatial smoothed intensity profile time series matrix 
spatial_smooth <- function(obs, ss, knotS = 20){
  est = dd1 =dd2= dd3 = se2 = matrix( NA, nrow = nrow(obs), ncol = ncol(obs))
  rangS = c(ss[1], ss[length(ss)]); 
  knotsS <- quantile(ss[2:(length(ss)-1)], p = seq(0,1,length.out = knotS));
  bbasisS = create.bspline.basis(rangS, norder=6, breaks = knotsS)
  X = eval.basis(ss,bbasisS)
  X1 = eval.basis(ss,bbasisS,1)
  X2 = eval.basis(ss,bbasisS,2)
  X3 = eval.basis(ss,bbasisS,3)
  for( ii in 1:ncol(obs)){  
    Slist = list(X=list(diag(ncol(X))))
    out = gam(obs[,ii] ~ -1 + X, paraPen = Slist, family= gaussian(), method = "GCV.Cp")
    est[,ii] <- X %*% out$coefficients
    dd1[,ii] <- X1 %*% out$coefficients
    dd2[,ii] <- X2 %*% out$coefficients
    dd3[,ii] <- X3 %*% out$coefficients
    sigma2 <- sum(( obs[,ii] - est[,ii])^2)/(length(obs[,ii]) - ncol(X))
    ses <- diag( X2 %*% ginv( t(X) %*% X + out$sp*diag(ncol(X))) %*% t(X2) * sigma2 )
    se2[,ii] <- ses
  }
  list(dd1 = dd1, dd3=dd3, est = est)
}

#------------------------------------------------------------------------------
# Step 2: termius estimation:  find pilot path with greedy algorithm
# input:  - obs: intensity profile time series matrix, with row corresponding to
#              intensity at same arc length
#         - ss: arc length vector (unit: meter)
#         - tt: time vector (unit: year)
#         - dd1: first derivative matrix of intensity profile time series matrix 
#         - rho: glacier retreat/ advance restriction (meters/month)
# output  - pilot path 

#Being called in Python function terminus_est


#------------------------------------------------------------------------------
# Step 3: temporal smoothing 
# input   - ss: arc length vector (unit: meter)
#         - tt: time vector (unit: year)
#         - est: spatial smoothed intensity profile time series matrix 
#         - dd3: third derivative matrix of intensity profile time series matrix 
#         - theta0: pilot path 
#         - KnotsT: number of knots
#         - meas: ground measurement times
#        
# output  - 

temporal_smooth <- function(ss,tt, est,dd3,theta0, knotsT =-1, meas){
  # evaluate at path, time point k
  muT = function( obj, theta0, k){ obj[theta0[k],k]}
  wts <- sapply( seq(1,ncol(dd3),1), muT, obj = dd3, theta0 = theta0)
  wts[wts < 0] = 1e-06      
  b <- gam( ss[theta0] ~ s(tt, bs = "cr", k = knotsT) , weights = wts, method = "REML")#### change this step tp linear regression!
  knots <- b$smooth[[1]]$xp						
  ### predicted path values				
  out <- predict( b, se.fit = TRUE)
  pred <- out$fit 
  predSe <- out$se.fit
  
  ### predicted values over ground measurement times
  if(!is.null(meas)) {
    # newd = data.frame( tt = floor(min(tt, meas)):ceiling(max(tt,meas)))	#### need to update????
    newd = data.frame(tt = meas[,1])
    out <- predict( b, newd, se.fit = TRUE)	
    predMeas = out$fit
    predMeasSe = out$se.fit
  }
  else{
    predMeas = NULL
    predMeasSe = NULL
  }
  return(list(unsmooth = ss[theta0], pred = pred, predSe = predSe, predMeas = predMeas, predMeasSe = predMeasSe, knots = knots, wts = wts ))
  
}

terminus_plot <- function(direc,glacier,ss,tt,obs,out1,sSmooth,line.fit,meas,measAdj,temporal,linefit,invert) {
  col_B61<- colorRampPalette(c("tan4", "lightblue2"))
  setwd(direc)
  # plot 1 - profile intensity
  main = paste(glacier,"intensity profile")
  png(paste(main,'.png', sep =""), width = 6.5, height = 6, units = 'in', res = 300)
  matplot( ss, obs, col = "grey", type = "l", ylab = "Profile intensity", xlab = "Distance along the glacial flowline (meters)", cex.axis = 1.5, cex.lab = 1.5)
  dev.off()
  
  # plot 2 - first derivative
  dd1 = sSmooth$dd1
  main = paste(glacier,"first derivative candidate")
  png(paste(main,'.png', sep = ""), width = 6.5, height = 6, units = 'in', res = 300)
  par(oma=c( 0,1,0,0)) 
  dmax = quantile(abs(dd1), .99)
  dd1[which(dd1 > dmax)] = dmax
  dd1[which(dd1 < -dmax)] = -dmax
  image.plot( ss, tt, dd1,col = topo.colors(64),xlim = c(min(ss),max(ss)), ylim = c(min(tt), max(tt)), zlim = c(-dmax, dmax), xlab = "Distance along the glacial flowline (meters)", ylab = "Year", cex.axis = 1.5, cex.lab = 1.5)
  if(temporal ==  0){
    lines( out1$unsmooth, tt, col = "black", lwd = 3.5)
  }else if (temporal ==2){
    lines( out1$unsmooth, tt, col = "yellow", lwd = 3.5)
    lines( out1$pred, tt, col = "black", lwd = 3.5)
    lines( out1$pred + 2*out1$predSe, tt, lwd = 1.5, col = "purple")
    lines( out1$pred - 2*out1$predSe, tt, lwd = 1.5, col = "purple")
  }else{
    lines( out1$pred, tt, col = "black", lwd = 3.5)
    lines( out1$pred + 2*out1$predSe, tt, lwd = 1.5, col = "purple")
    lines( out1$pred - 2*out1$predSe, tt, lwd = 1.5, col = "purple")
  }
  dev.off()
  
  # plot 3 - estimate terminus 
  if(invert == 1){
    col <- col_B61(20)
  }
  else {
    col <- col_B61(20)[20:1]
  }
  main = paste(glacier,"terminus estimate candidate")
  png(paste(main,'.png', sep =""), width = 6.5, height = 6, units = 'in', res = 300)
  par(oma=c( 0,1,0,0))
  obsmat = as.matrix(obs)
  omax = quantile(abs(obsmat), .99)
  omin = quantile(abs(obsmat), .01)
  obsmat[which(obsmat > omax)] = omax
  obsmat[which(obsmat < omin)] = omin
  image.plot( ss, tt, obsmat,  col = col, xlim = c(min(ss),max(ss)), ylim = c(min(tt), max(tt)), zlim = c(omin, omax), xlab = "Distance along the glacial flowline (meters)", ylab = "Year", cex.axis = 1.5, cex.lab = 1.5)
  if(temporal ==  0){
    lines( out1$unsmooth, tt, col = "yellow", lwd = 3.5)
  }else if (temporal ==2){
    lines( out1$unsmooth, tt, col = "yellow", lwd = 3.5)
    lines( out1$pred, tt, col = "black", lwd = 3.5)
    lines( out1$pred + 2*out1$predSe,tt, lwd = 1.5 , col = "purple")
    lines( out1$pred  - 2*out1$predSe,tt, lwd = 1.5, col = "purple")
  }else{
    lines( out1$pred, tt, col = "yellow", lwd = 3.5)
    lines( out1$pred + 2*out1$predSe,tt, lwd = 1.5 , col = "purple")
    lines( out1$pred  - 2*out1$predSe,tt, lwd = 1.5, col = "purple")
  }
  if( linefit == 1){
    lines( line.fit, lwd = 2, tt, col = "green")
  }
  if(!is.null(meas)){
    points( measAdj[,2], measAdj[,1], lwd = 3, col = "red")
  }
  dev.off()
  
  # plot 4 - zoomed estimate terminus
  range = range(out1$unsmooth)
  lower = range[1] - 3*(range[2]-range[1])
  lower = max(lower,min(ss))
  upper = range[2] + 3*(range[2]-range[1])
  upper = min(upper, max(ss))
  
  main = paste(glacier,"terminus estimate zoomed candidate")
  png(paste(main,'.png', sep =""), width = 6.5, height = 6, units = 'in', res = 300)
  par(oma=c( 0,1,0,0))
  obsmat = as.matrix(obs)
  omax = quantile(abs(obsmat), .99)
  omin = quantile(abs(obsmat), .01)
  obsmat[which(obsmat > omax)] = omax
  obsmat[which(obsmat < omin)] = omin
  image.plot( ss, tt, obsmat,  col = col, xlim = c(lower, upper), ylim = c(min(tt), max(tt)), zlim = c(omin, omax), xlab = "Distance along the glacial flowline (meters)", ylab = "Year", cex.axis = 1.5, cex.lab = 1.5)
  if(temporal ==  0){
    lines( out1$unsmooth, tt, col = "yellow", lwd = 3.5)
  }else if(temporal ==2){
    lines( out1$unsmooth, tt, col = "yellow", lwd = 3.5)
    lines( out1$pred, tt, col = "black", lwd = 3.5)
    lines( out1$pred + 2*out1$predSe,tt, lwd = 1.5 , col = "purple")
    lines( out1$pred  - 2*out1$predSe,tt, lwd = 1.5, col = "purple")
  }else{
    lines( out1$pred, tt, col = "yellow", lwd = 3.5)
    lines( out1$pred + 2*out1$predSe,tt, lwd = 1.5 , col = "purple")
    lines( out1$pred  - 2*out1$predSe,tt, lwd = 1.5, col = "purple")
  }
  if( linefit == 1){
    lines( line.fit, lwd = 2, tt, col = "green")
  }
  if(!is.null(meas)){
    points( measAdj[,2], measAdj[,1], lwd = 3, col = "red")
  }
  dev.off()
  list(lower = unname(omin), upper = unname(omax))

}

#------------------------------------------------------------------------------------
# Update the terminus function to plot terminus location over first derviative plots
# Add option to plot the terminus location with and without temperal smoothing 
# Add input: temporal 
#-------------------the main analysis and plot functions --------------------------------
# Method 4 plot functions
# input - glacier: name of the glacier, ex: "gorner"
#       - obs: intensity time series matrixs with row correspond to arc length 
#       -      and column for year
#       - ss: arc length vector (in meters)
#       - tt: year vector 
#       - meas(optional): ground measurement with two columns: year, front variation (in meters)
#       - plot(optional): = c(TRUE, FALSE), whether to produce plot 
#       - dir( if plot = TRUE): directory to save the plots
#       - linefit = 1 ( default),  plot line fit of the terminus on the terminus plots, 
#         linefit = 0, do not plot line fit 
#       - temporal: temporal = 0 plot terminus location without temporal smoothing
#                   temporal = 1 plot terminus location with temporal smoothing 
#         the output terminus$pred will change correspondingly to this option
# 
# output - pred: predicted terminus in meters
#        - predSe: standard error for predicted terminus 
#        - slope: speed of terminus advance (meters/year)
#        - slopeSe: standard error of terminus advance
#        - dd1: first derivative of terminus 
#        - MIAE(if Meas is provided)
#        - MAD(if Meas is provided)
#        - sum: sum of first derivative across terminus locations 
# 
#  plots - if plot is set to TRUE: return 5 plots of png format in the desired directory:
#        - intensity profile time series plot
#        - two first derivative plots  
#        - terminus estimate
#        - terminus estimate zoomed
# txt.file - consists slope, slopese, MIAE&MAD (when ground measurement is available)

#----------------------------------------------------------------------

library(rPython)
terminus <- function(glacier, obs, ss, tt, meas= NULL, plot = FALSE, direc = NULL, linefit = 0, temporal = 0,invert = 0, distPerYear = 100, IP = 0){
  #time <- floor(min(tt)):ceiling(max(tt))
  if(IP == 1){
    current_dir = getwd()
    setwd("/home/aseshad/RA/manual_intensity")
    #glacier = "Rhonegletscher"
    IPTS = read.csv(paste(glacier, ".csv",sep = ""))
    nrow = nrow(IPTS)
    ncol = ncol(IPTS)
    obs = as.matrix(IPTS[2:nrow, 2:ncol] )
    rownames(obs)= NULL
    colnames(obs) = NULL
    tt = as.numeric(IPTS[1,2:ncol]) # 
    ss = as.numeric(as.character(IPTS[2:nrow,1]))    
    setwd(current_dir)
  }
  sSmooth = spatial_smooth(obs, ss, knotS = min( round(length(ss)/4)+4, 35+4))
  python.load("terminus_est.py")
#-------------------------------------------------------------------------------
# assume theta is a matrix of 3 columns corresponding to three candidate terminus 
  theta0 = python.call("terminus_paths",sSmooth$dd1,tt,ss,glacier,invert,distPerYear)
#----------------------------------------------------------------------------
      if (temporal == 1) {
        out1 = temporal_smooth(ss,tt,est = sSmooth$est, dd3 =sSmooth$dd3, theta0 = theta0, knotsT =round(length(tt)/4+2),meas)    
      }else if (temporal ==2){# here!
        list1 = temporal_smooth(ss,tt,est = sSmooth$est, dd3 =sSmooth$dd3, theta0 = theta0, knotsT =round(length(tt)/4+2),meas) 
        list2 = list(unsmooth = ss[theta0])
        out1 = c(list1, list2)
      }else {
        out1 = list(unsmooth = ss[theta0])
      }

      # fit a line through the terminus locations
      if (temporal == 1) {
        lm = lm(out1$pred ~ tt) # fit a line through the terminus 
      }
      else { # here! fit a line through unsmoothed path 
        lm = lm(out1$unsmooth ~ tt) # fit a line through the terminus 
      }
      slope= summary(lm)[4][[1]][2,1]
      slope.se= summary(lm)[4][[1]][2,2]
      line.fit = lm$fitted.values  

      # Ground measurement calculations
      if(!is.null(meas)){
        ind = which((meas[,1] > floor(min(tt)))*(meas[,1]<ceiling(max(tt)))==1)
        adj <- mean(out1$predMeas[ind]) - mean(cumsum(meas[ind,2]))# why use cumsum instead of sum????
        measAdj <- data.frame(tt = meas[ind,1], gm = cumsum(meas[ind,2]) + adj)  
        MIAE <- mean( abs(out1$predMeas[ind] - measAdj[,2]) )
        MAD <- max( abs(out1$predMeas[ind] - measAdj[,2]) )
      }
  
      if(is.null(meas)){
        mat <- matrix(c(slope,slope.se, NA, NA ), nrow = 1)
      }
      else{
        mat <- matrix(c(slope,slope.se, MIAE, MAD), nrow = 1)
      }
      colnames(mat) <- c("slope","slope.se", "MIAE", "MAD")
      print (mat)
      write.table(mat,paste(glacier,".txt", sep =""),col.name =TRUE,row.name=FALSE)  

      if(plot==1){
        bounds = terminus_plot(direc,glacier,ss,tt,obs,out1,sSmooth,line.fit,meas,measAdj,temporal,linefit,invert)
        write.table(obs, file = paste(glacier, "unsmoothed intensity.txt"), row.names =FALSE, col.names =FALSE)
        write.table(tt, file = paste(glacier, "year.txt"), row.names =FALSE ,col.names =FALSE)
        write.table(ss, file = paste(glacier, "distance.txt"), row.names =FALSE, col.names =FALSE)
      }
      
      list = list(line.fit = line.fit, pred = out1$pred, predSe = out1$predSe, slope = slope, slopeSe = slope.se, dd1 = sSmooth$dd1,
           MIAE = MIAE, MAD = MAD, lower = bounds$lower, upper = bounds$upper) 
  return(list)
 
}

# #----------------------Example Usage with Corbassiere----------------------------------------------------------------------------------------------------
# direc = "/home/aseshad/Desktop"
# setwd(direc)
# # 
# # glacier = "CORBASSIERE GLACIER DE"
# glacier ="FRANZ JOSE, GIEK"
# # glacier ="Findelengletscher"
# # 
# IPTS = as.matrix(read.table(paste(glacier,"IPTS.txt")))
# meas = as.matrix(read.table(paste(glacier,"_Front Variation.txt", sep = ""))) 
# obs = IPTS[2:nrow(IPTS), 2:ncol(IPTS)]
# tt = unname(c(IPTS[1, 2:ncol(IPTS)]))
# ss = c(IPTS[2: nrow(IPTS),1])
# t3 =  terminus(glacier= glacier, obs= obs, ss=ss, tt=tt,meas=meas, plot = TRUE, direc = direc,linefit = 1, temporal = 1, invert = 0)

#------------------ use the codes on manual extrated intensity profiles-----------------------------------------------------------------------
current_dir = getwd()
setwd("/home/aseshad/RA/manual_intensity")
glacier = "Rhonegletscher"
IPTS = read.csv(paste(glacier, ".csv",sep = ""))
nrow = nrow(IPTS)
ncol = ncol(IPTS)
obs = as.matrix(IPTS[2:nrow, 2:(ncol-1)] )
rownames(obs)= NULL
colnames(obs) = NULL
tt = as.numeric(IPTS[1,2:(ncol-1)]) # 
ss = as.numeric(as.character(IPTS[2:nrow,1]))    
setwd("/home/aseshad/RA/Pipeline21.0/Code")
dir = "/home/aseshad/RA/manual_intensity"
t =terminus("Rhonegletscher", obs, ss, tt, meas= NULL, plot = TRUE, direc = dir, linefit = 0, temporal = 1,invert = 1, distPerYear = 100, IP = 0)


image.plot(obs)




