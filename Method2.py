from PIL import Image
import os
import numpy
from math import exp
import shutil

def classify(path,p_nonzero,b0,b1,b2):
	"This classifies the Band 61 images"
	print len(os.listdir(path))
	i=1
	for folder in os.listdir(path):
		for fn in os.listdir(path+folder):
			if fn.endswith('.B6_VCID_1.tif') or fn.endswith('.B6.tif'):
				im = Image.open(path+folder+'/'+fn)
				image_array = numpy.array(im)
				total = im.size[0]*im.size[1]
				arr_nonzero = []
				for row in image_array:
					for item in row:
						if item != 0:
							arr_nonzero.append(item)
				nonzero = float(len(arr_nonzero))/float(total)
				if nonzero > p_nonzero:
					t = b0 + b1*numpy.mean(arr_nonzero) + b2*numpy.std(arr_nonzero)
					p = 1/(1+exp(-1*t))
					if p <= 0.5:
						shutil.rmtree(path+folder)
						# print "removing "+path+folder, i
						# i=i+1
				else:
					shutil.rmtree(path+folder)
					# print "removing "+path+folder, i
					# i=i+1



#classify('/home/aseshad/earth engine download/GORNERGLETSCHER',0.75,-50.50,0.486,0.523)
