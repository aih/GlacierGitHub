 #-----------------------------------------------------------------------------------------------
 # Version Jul 16, 2015
 # Note: this is a modification to plot terminus location on flow line 
 # for three best terminus candidate. Fisrt call function loc_terminus() for each pred, and produce 
 # tx1, tx2, tx3, ty1, ty2, ty3, input tx = list(tx1, tx2, tx3), ty=list(ty1, ty2, ty3) 
 #-----------------------------------------------------------------------------------------------
 # function to mark terminus location on glacier path over Landsat image
 # function1 - find termins loactaion over time corresponding to Landsat used 
 # input - coord.parallel: coord.parallel is the output from path_parallel function
 #       - step.size: step size in pixels
 #       - pred: terminus$pred, where terminus is the output from terminus function
 loc_terminus <- function(coord.parallel, step.size, pred){
    coord = cbind(c(coord.parallel$x),c(coord.parallel$y))
    step = step.size*30 
    terminus1 = coord[round(pred/step), ]
    list( coord = coord, t = terminus1) 
 } 

 # -------------------------------------------------------------------------
 # updates for plots to have the same range of lengend bar and year as caption
 # the idea is to set the plot value range the same for all B61s used for a given glacier    
 # Add inputs: lower & upper
 #----------------------------------------------------------------------------
 # plot glacier flow line with terminus location over Lansat image 
 # input - B61: landsat matrix
 #       - coord: loc_terminus$coord, output coord from previous function
 #       - tx, ty: row and column of the terminus, form output t from previous function 
 #         for the ith B61 in the sequence, tx = loc_terminus$t[i,1]
 #                                          ty = loc_terminus$t[i,2]  
 #       - lower: lower bound of plot value 
 #          = smallest non-zero pixel value among all B61s used for this glacier
 #       - upper: upper bound of lower value 
 #          = largest pixel value among all B61s used for this glacier
 #       - glacier: glacier name, ex. "Rhone"
 #       - year:  year of B61 in decimal, ex. "2012.316"
 #       - dir: directory to output the plot 
 # usage - use in a for loop with each B61 used to create the intensity profile time series 
 library(fields)
 library(grDevices)
 library(raster)
 library(rgdal)
 #-----------------------------------------------------------------------------------------------
 # Note: this is a modification of mark_terminus_plot1() to plot terminus location on flow line 
 # for three best terminus candidate. Fisrt call function loc_terminus() for each pred, and produce 
 # tx1, tx2, tx3, ty1, ty2, ty3, input tx = list(tx1, tx2, tx3), ty=list(ty1, ty2, ty3) 
 #-----------------------------------------------------------------------------------------------
 
 mark_terminus_plot1  <- function(B61, coord, tx, ty, lower, upper, glacier, year, dir,invert,input,rgbImage){ 
   col_B61<- colorRampPalette(c("tan4", "lightblue2"))
   setwd(dir)
   year = round(year,3)
   main = paste(glacier, year)
   ncol = ncol(B61)
   nrow = nrow(B61)
   B61[which(B61 > upper)] = upper
   B61[which(B61 < lower)] = lower
   if(invert == 1){
     col <- col_B61(20)
   }
   else {
     col <- col_B61(20)[20:1]
   }
   png(paste(main,'.png'), width=max(6,6*nrow/ncol)  ,height = max(6,6*ncol/nrow), units = 'in', res = 300)
   image.plot(1:nrow,1:ncol,B61,zlim=c(lower,upper),  main = paste(input,year), xlab= "", ylab="", ann=T,asp = T, axes = F, col = col,cex =max(1, nrow/ncol), axis.args = list(cex.axis = 1), legend.shrink = 0.5, legend.width = 0.8)
   lines(c(coord[,1]),c(coord[,2]), col ="blue", lwd = 2) # flow line 
   points( tx, ty, cex = 1.5, col = "red", pch = 20) # terminus  
   dev.off()
   
   png(paste(main,'_rgb.png'), width=max(6,6*nrow/ncol)  ,height = max(6,6*ncol/nrow), units = 'in', res = 300)
   rgbBrick <- brick(rgbImage)
   plotRGB(rgbBrick)   
   lines(c(coord[,1]),c(coord[,2]), col ="yellow", lwd = 2) # flow line 
   points( tx, ty, cex = 1.5, col = "red", pch = 20) # terminus 
   dev.off()
 }