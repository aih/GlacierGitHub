import os

path = os.path.abspath('..')+"/"

glaciers = os.listdir(path+'Data/')

for glacier in glaciers:
	landsat = os.listdir(path+'Data/'+glacier+'/Landsat/')
	for image in landsat:
		try:
			os.remove(path+'Data/'+glacier+'/Landsat/'+image+'/Code.ndsi.tif')
			os.remove(path+'Data/'+glacier+'/Landsat/'+image+'/Code.rgb.tif')
		except:
			continue