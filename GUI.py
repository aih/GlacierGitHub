import os
import matplotlib
matplotlib.use('Agg')
from Tkinter import *
try:
    from PIL import ImageTk
except:
    from pillow import ImageTk

class App:

	def __init__(self, master):
		self.glacier = None
		self.img = None
		self.disp = None
		self.plot = None
		self.path = os.path.abspath('..')+"/"
		self.type = None
		self.band = None
		self.plot = None
		self.date = None
		self.landsat = []
		self.rgb = []


		self.inputFrame = Frame(master)
		self.inputFrame.pack(side=TOP,)

		self.inputLabel = Label(self.inputFrame, text = "Select the glacier")
		self.inputLabel.pack(side=LEFT)

		self.default = StringVar(self.inputFrame)
		self.default.set("Rhonegletscher")

		self.optionBox = OptionMenu(self.inputFrame,self.default,"Athabasca Glacier","Chaba Glacier","COXE","David Glacier","Fassett","Fox, Explorer","Litian glacier","North Canoe Glacier","CORBASSIERE GLACIER DE","FERPECLE GLACIER DE","FIESCHERGLETSCHER VS","Findelengletscher","FORNO VADREC DEL","FRANZ JOSE","GAULIGLETSCHER","GORNERGLETSCHER","GROSSER ALETSCH GLETSCHER","MONT MINE GLACIER DU","MORTERATSCH VADRET DA","OTEMMA","Rhonegletscher","Ferebee","Fraenkel","Mer de Glace","MURCHISON","Torre")
		self.optionBox.pack(side=LEFT)

		self.loadButton = Button(self.inputFrame, text = "Load", command=self.loadGlacier)
		self.loadButton.pack()

		
		self.imageSelectionFrame = Frame(master)
		self.imageSelectionFrame.pack(side=LEFT)

		self.dateFrame = Frame(self.imageSelectionFrame)
		self.dateFrame.pack(side=BOTTOM,padx=10,pady=10)

		self.dateScrollBar = Scrollbar(self.dateFrame)
		self.dateScrollBar.pack(side=RIGHT,fill=Y)

		self.dateListBox = Listbox(self.dateFrame, yscrollcommand=self.dateScrollBar.set)
		self.dateListBox.pack()
		self.dateScrollBar.config(command=self.dateListBox.yview)
		self.dateListBox.bind('<<ListboxSelect>>', self.loadImage)

		self.typeFrame = Frame(self.imageSelectionFrame)
		self.typeFrame.pack(side=TOP,padx=10,pady=10)

		self.typeScrollBar = Scrollbar(self.typeFrame)
		self.typeScrollBar.pack(side=RIGHT,fill=Y)

		self.typeListBox = Listbox(self.typeFrame, yscrollcommand=self.typeScrollBar.set)
		self.typeListBox.pack()
		self.typeScrollBar.config(command=self.typeListBox.yview)
		self.typeListBox.bind('<<ListboxSelect>>', self.loadImages)


		self.imageFrame = Frame(master)
		self.imageFrame.pack(side=LEFT)

		self.it = StringVar()
		self.imageTitle = Label(self.imageFrame, textvariable=self.it)
		self.imageTitle.pack()

		self.imageCanvas = Canvas(self.imageFrame, width=500, height=600, borderwidth=5, background='white', relief='ridge')
		self.imageCanvas.pack(padx=10,pady=10)


		self.analysisFrame = Frame(master)
		self.analysisFrame.pack(side=LEFT)

		self.at = StringVar()
		self.analysisTitle = Label(self.analysisFrame, textvariable=self.at)
		self.analysisTitle.pack()

		self.analysisCanvas = Canvas(self.analysisFrame, width=500, height=600, borderwidth=5, background='white', relief='ridge')
		self.analysisCanvas.pack(padx=10,pady=10)


		self.analysisSelectionFrame = Frame(master)
		self.analysisSelectionFrame.pack(side=LEFT)

		self.plotScrollBar = Scrollbar(self.analysisSelectionFrame)
		self.plotScrollBar.pack(side=RIGHT,fill=Y)

		self.plotListBox = Listbox(self.analysisSelectionFrame, yscrollcommand=self.plotScrollBar.set)
		self.plotListBox.pack(padx=10,pady=10)
		self.plotScrollBar.config(command=self.plotListBox.yview)
		self.plotListBox.bind('<<ListboxSelect>>', self.loadPlot)

		
	def loadImage(self,event):
		#loads the image based on date
		self.date = self.dateListBox.curselection()
		self.it.set(self.type+" "+self.dateListBox.get(self.date)) 
		self.imageCanvas.delete("all")

		imgpath = os.getcwd()+'/'+self.band+"/terminus_images/"
		if self.type == "RGB":
			imgpath = imgpath+self.rgb[self.date[0]]
		else:
			imgpath = imgpath+self.landsat[self.date[0]]
		
		
		self.img = PhotoImage(file=imgpath)
		h = self.img.height()
		w = self.img.width()
		self.img = self.img.subsample(w/500,h/600)
		self.imageCanvas.create_image(0,0,anchor=NW,image=self.img)
		self.imageCanvas.update()


	def loadPlot(self,event):
		#loads the plot for analysis
		self.plot = self.plotListBox.get(self.plotListBox.curselection())
		self.at.set(self.plot)
		self.analysisCanvas.delete("all")
		imgpath = ""
		if self.plot == "Intensity profiles":
			imgpath = os.getcwd()+"/"+self.band+'/'+self.glacier+" intensity profile.png"
		elif self.plot == "First derivative":
			imgpath = os.getcwd()+"/"+self.band+'/'+self.glacier+" first derivative candidate.png"
		elif self.plot == "Terminus estimate":
			imgpath = os.getcwd()+"/"+self.band+'/'+self.glacier+" terminus estimate candidate.png"
		elif self.plot == "Zoomed terminus estimate":
			imgpath = os.getcwd()+"/"+self.band+'/'+self.glacier+" terminus estimate zoomed candidate.png"

		self.plot = PhotoImage(file=imgpath)
		self.plot = self.plot.subsample(4,4)
		self.analysisCanvas.create_image(0,0,anchor=NW,image=self.plot)
		self.analysisCanvas.update()


	def loadImages(self,event):
		#loads the dates of images for a type
		self.type = self.typeListBox.get(self.typeListBox.curselection())
		if self.type != "RGB":
			self.band = self.type
		files = os.listdir(os.getcwd()+'/'+self.band+"/terminus_images")
		self.dateListBox.delete(0,END)

		self.landsat = []
		self.rgb = []

		for f in files:
			fsp = f.split(" ")
			if fsp[-1] == ".png":
				self.landsat.append(f)
			elif fsp[-1] == "_rgb.png":
				self.rgb.append(f)

		self.landsat.sort()
		self.rgb.sort()

		if self.type == "DEM":
			self.imageCanvas.delete("all")
			imgpath = os.getcwd()+"/"+self.glacier+" with parallel paths on DEM .png"
			self.img = PhotoImage(file=imgpath)
			h = self.img.height()
			w = self.img.width()
			self.img = self.img.subsample(w/500,h/600)
			self.imageCanvas.create_image(0,0,anchor=NW,image=self.img)
			self.imageCanvas.update()
		else:
			dates = self.landsat
			for d in dates:
				dsp = d.replace(self.glacier,"").split(" ")
				self.dateListBox.insert(END,dsp[1])
			self.dateListBox.select_set(END)
			self.dateListBox.event_generate("<<ListboxSelect>>")



	def loadGlacier(self):
		#loads the glacierr upon loading
		self.glacier = self.default.get()
		os.chdir(self.path+'Results/'+self.glacier)

		types = ["B2","B3","B4","B5","B6_VCID_1","ndsi","RGB","DEM"]
		plots = ["Intensity profiles","First derivative","Terminus estimate","Zoomed terminus estimate"]

		self.plot = "Intensity profiles"
		self.type = "ndsi"
		self.band = "ndsi"

		self.typeListBox.delete(0,END)
		self.plotListBox.delete(0,END)
		self.dateListBox.delete(0,END)
		self.imageCanvas.delete("all")
		self.analysisCanvas.delete("all")

		for t in types:
			self.typeListBox.insert(END,t)

		for p in plots:
			self.plotListBox.insert(END,p)

		#default operations
		self.typeListBox.select_set(types.index(self.type))
		self.typeListBox.event_generate("<<ListboxSelect>>")
		self.plotListBox.select_set(plots.index(self.plot))
		self.plotListBox.event_generate("<<ListboxSelect>>")




root = Tk()
app = App(root)
root.mainloop()
