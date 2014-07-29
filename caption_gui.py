#!/usr/bin/python -tt

import sys, os
import json
from Tkinter import *
import tkMessageBox
import Image
import ImageTk


JSON_FILE = 'imageinfo.json'


########################################################################

import image_metadata


def readIptcInfo (filename):
  if os.path.isfile(filename):
    try:
      metadata = image_metadata.readMetadata(filename)
      
    except Exception, e:
        # This is used to skip anything not an image.
        # Image.open generates an exception if it cannot open a file.
        # Warning, this will hide other errors as well.
        print e
        pass
        
    return(metadata['credit'], metadata['date']+" "+metadata['caption'])
  

def pilResize(im, newsize):
    im.thumbnail((newsize, newsize), Image.ANTIALIAS)
    return im


########################################################################

class Model(object):
  def __init__(self, image_dir):
    self.controllers = []
    self.imageDir = image_dir;

    
  def loadImageInfo(self):
    # find all the images and load any info embedded in them  
    filelist = os.listdir(self.imageDir)
    image_info = self.findImages(filelist)

    # If there's a json file, open it and load its image info
    if JSON_FILE in filelist:
      f = open(os.path.join(self.imageDir, JSON_FILE), 'r')
      json_info = json.loads(f.read())
      # use the info from the json file 
      for k,v in json_info.iteritems():
        if k in image_info:
          image_info[k] = v

    # save the image info as the data mode and return a list of files
    self.imageInfo = image_info
    #print self.imageInfo
    return sorted(self.imageInfo.keys())

    
  def findImages(self, filelist):
    image_info = {}
    for f in filelist:
      fullpath = os.path.join(self.imageDir, f)
      try:
        im = Image.open(fullpath)
        image_info[f] = readIptcInfo(fullpath)
      
      except Exception, e:
        # This is used to skip anything not an image.
        # Image.open generates an exception if it cannot open a file.
        # Warning, this will hide other errors as well.
        pass
        
    return image_info

  
  def setImageInfo(self, image, credit, caption):
    if image in self.imageInfo:
      self.imageInfo[image] = (credit, caption)
    #print self.imageInfo

    
  def getImageInfo(self, image):
    if image in self.imageInfo:
      im = Image.open(os.path.join(self.imageDir, image))
      info = self.imageInfo[image]
      return (info[0], info[1], im) 
    else:
      return ("", "", None)
  
  
  def writeImageInfo(self):
    f = open(os.path.join(self.imageDir, JSON_FILE), 'w')
    serialized = json.dumps(self.imageInfo, sort_keys=True, indent=2, separators=(',', ': '))
    f.write(serialized)
    #print serialized 
    f.close()
    
  def changed(self):
    for controller in self.controllers:
      controller.update()    


########################################################################

class Controller(object):
  def __init__(self, model):
    self.views = []
    self.model = model
    
    # TODO: handle no image in curren directory case, duh!
    self.imageIndex = 0
    self.images = model.loadImageInfo();
    if len(self.images) > 0:
      self.currentImage = self.images[self.imageIndex]
    else:
      self.currentImage = None
    
  def storeInfo(self, credit, caption):
    self.model.setImageInfo(self.currentImage, credit, caption)
    
  def prevImage(self):
    self.imageIndex = max(0, self.imageIndex-1)
    self.currentImage = self.images[self.imageIndex]
    #print "get previous image:", self.currentImage
    self.update()

  def nextImage(self):
    self.imageIndex = min(len(self.images)-1, self.imageIndex+1)
    self.currentImage = self.images[self.imageIndex]
    #print "get next image:", self.currentImage
    self.update()

  def writeImageInfo(self):
    self.model.writeImageInfo()
    
  def update(self):
    for view in self.views:
      info = self.model.getImageInfo(self.currentImage)
      view.update(self.currentImage, info[2], info[0], info[1])


########################################################################

class View(object):
  def __init__(self, master, controller):
    self.controller = controller
    self.master = master
    self.master.geometry('480x525')
    self.filename = self.controller.currentImage
    
    self.icon = Label(self.master, height=400)
    self.label0a = Label(self.master, text="Filename:")
    self.label0b = Label(self.master, text=self.filename)
    self.label1 = Label(self.master, text="Credit:")
    self.label2 = Label(self.master, text="Caption:")

    # make some text entry boxes for caption and credits strings
    self.entry1 = Entry(self.master)
    self.entry2 = Entry(self.master, width=50)

    # some basic navigations
    self.button1 = Button(self.master, text="<-", command=self.backHandler)
    self.button2 = Button(self.master, text="->", command=self.nextHandler)
    self.button3 = Button(self.master, text="save", command=self.saveHandler)

    # Grid layout for all the widgets (move to a helper?)
    self.icon.grid(row=0, column=0, columnspan=4,  padx=8, pady=5)
    self.label0a.grid(row=1, column=0, sticky=E)
    self.label0b.grid(row=1, column=1, sticky=W)
    self.label1.grid(row=2, column=0, sticky=E)
    self.entry1.grid(row=2, column=1, columnspan=2, sticky=W)
    self.label2.grid(row=3, column=0, sticky=E)
    self.entry2.grid(row=3, column=1, columnspan=2, sticky=W)
    self.button1.grid(row=4, column=0, sticky=E)
    self.button2.grid(row=4, column=1, sticky=W)
    self.button3.grid(row=4, column=2)      
    
  def backHandler(self):
    self.controller.storeInfo(self.entry1.get(), self.entry2.get())
    self.controller.prevImage()

  def nextHandler(self):
    self.controller.storeInfo(self.entry1.get(), self.entry2.get())
    self.controller.nextImage()

  def saveHandler(self):
    self.controller.storeInfo(self.entry1.get(), self.entry2.get())
    self.controller.writeImageInfo()

  def update(self, filename, im, credit="", caption=""):
    self.filename = filename
    self.master.title(self.filename)         
    self.label0b.config(text=self.filename)
    
    if filename == '' or not im:
      return False
    else:
      im = pilResize(im, 400)
      tkpi = ImageTk.PhotoImage(im)
      self.icon.configure(image=tkpi)
      self.icon.image = tkpi # keep a reference
      
      self.entry1.delete(0, END)
      self.entry1.insert(0, credit)
      self.entry2.delete(0, END)
      self.entry2.insert(0, caption)
      return True

########################################################################


def main(argv):
  root = Tk()

  image_dir = '.'
  if len(argv) > 1:
    image_dir = argv[1]
    
  model = Model(image_dir)
  controller = Controller(model)
  view = View(root, controller)
  model.controllers.append(controller)
  controller.views.append(view)
  
  if controller.update():
    root.mainloop()
  else:
    print "Image files not found"
    tkMessageBox.showerror('No Images', 'Image files not found')

if __name__ == '__main__':
  main(sys.argv)

    
