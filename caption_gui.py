#!/usr/bin/python -tt

import sys, os
import json
from Tkinter import *
import tkMessageBox, tkFileDialog
import Image
import ImageTk
import os.path
import time

import image_metadata


JSON_FILE = 'imageinfo.json'

########################################################################
#
# TODOs:
# Hide main when in file dialog open: root.widthdraw(), .deiconify()
# Help merge inputs from several json files (open oldest first)
# Define some kind of next dir behavior instead of always exit?
#
########################################################################

########################################################################
# Global Utility functions  

def pilResize(im, newsize):
    im.thumbnail((newsize, newsize), Image.ANTIALIAS)
    return im


def chooseDirectory(root):
    return tkFileDialog.askdirectory(parent=root, initialdir='.', mustexist=True, title='Image directory')


def loadAllJson (filelist):
  """
  load all the .json files in the dir, starting with the oldest
  """
  all_info = {}
  
  # make a timestamped listing of all json files
  fileorder = {}
  for fn in filelist:
    if '.json' in fn:
      fileorder[os.path.getmtime(fn)] = fn
  
  # open each json file, oldest first and update the info
  for filetime in sorted(fileorder.iterkeys()):
    
    nextfile = fileorder[filetime]
    f = open(nextfile, 'r')
    json_info = json.loads(f.read())
    
    # TODO: may want update only when new info != ['','']
    all_info.update(json_info)
    
  return all_info
  
  

########################################################################
# Definition of the data model class for this MVC style gui application

class Model(object):
  def __init__(self, image_dir):
    self.controllers = []
    self.imageDir = image_dir;

    
  def loadImageInfo(self):
    # find all the images and load any info embedded in them  
    filelist = os.listdir(self.imageDir)
    image_info = self.findImages(filelist)

    # load their info from all the json files
    jfiles = [os.path.join(self.imageDir,fn) for fn in filelist]
    json_info = loadAllJson(jfiles)

    # add the json file info to the image files. Ignores info if there
    # isn't an image file to go with it.
    for fn in image_info:
      if fn in json_info:
        image_info[fn] = json_info[fn]

    # Add a field the like votes
    for fn in image_info:
      if len(image_info[fn]) < 3:
        image_info[fn].append(0)
    print image_info
    
    # save the image info as the data mode and return a list of files
    self.imageInfo = image_info
    #print self.imageInfo
    return sorted(self.imageInfo.keys())

    
  def findImages(self, filelist):
    '''
    attempts to open each file in the filelist (usually the files in the
    target directory) and extracts the caption and credit info from the
    matadata. Returns dicitonary of all the imagefiles (keys) and
    a list of strings [credit, caption]' (values)
    '''
    image_info = {}
    for f in filelist:
      fullpath = os.path.join(self.imageDir, f)
      try:
        im = Image.open(fullpath)
      
      except Exception, e:
        # This is used to skip anything not an image.
        # Image.open generates an exception if it cannot open a file.
        # Warning, this will hide other errors as well.
        #print "not an image file ", fullpath
        pass
        
      else:
        metadata = image_metadata.readMetadata(fullpath)
        image_info[f] = [metadata['credit'], metadata['date']+" "+metadata['caption']]
        #print "image created: %s" %time.ctime(os.path.getctime(fullpath))
          
    return image_info

  
  def setImageInfo(self, image, credit, caption):
    if image in self.imageInfo:
      self.imageInfo[image][0] = credit 
      self.imageInfo[image][1] = caption
    #print self.imageInfo


  def recordVote(self, v, fn):
    likes = self.imageInfo[fn][2] + v
    likes = 0 if likes < 0 else likes
    likes = 5 if likes > 5 else likes
    self.imageInfo[fn][2] = likes
    
    
  def getImageInfo(self, image):
    '''
    Main interface to the data model. given the full path to an image
    returns a 3-tupel or the credit string, caption string, and an
    image handle. If image not contains in model returns safe null 
    values
    TODO: This interface is kind of klunky with the vote field added,
          either return a struct or let Controller grab whatever
    '''
    if image in self.imageInfo:
      im = Image.open(os.path.join(self.imageDir, image))
      info = self.imageInfo[image]
      return (info[0], info[1], info[2], im)
    else:
      return ("", "", 0, None)
  
  
  def writeImageInfo(self):
    '''
    dump the data model to a .json file. Avoids overwriting previous
    work by first renaming any existing imageinfo.json with a date code
    TODO: only bother with this if the data actually changed
    '''
    fullpath = os.path.join(self.imageDir, JSON_FILE)
    if os.path.exists(fullpath):
      timestamp =  time.gmtime(os.path.getctime(fullpath))
      backupfile = time.strftime("%Y%m%d-%H%M%S", timestamp)+'.json'
      print "rename json file: %s" % backupfile
      os.rename(fullpath, os.path.join(self.imageDir, backupfile))
      
    f = open(fullpath, 'w')
    serialized = json.dumps(self.imageInfo, sort_keys=True, indent=2, separators=(',', ': '))
    f.write(serialized)
    #print serialized 
    f.close()
    
  def changed(self):
    for controller in self.controllers:
      controller.update()    


########################################################################
# Definition of the controller class for this MVC style gui application

class Controller(object):
  def __init__(self, model):
    self.views = []
    self.model = model
    
    # TODO: handle no image in current directory case, duh!
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
    
  def recordVote(self, v):
    self.model.recordVote(v, self.currentImage)
    self.update()
    
  def update(self):
    # assume controller has a single view 
    info = self.model.getImageInfo(self.currentImage)
    rval = self.views[0].update(self.currentImage, info[3], info[0], info[1], info[2])
    return rval
    
#    for view in self.views:
#      info = self.model.getImageInfo(self.currentImage)
#      view.update(self.currentImage, info[2], info[0], info[1])


########################################################################
# Definition of the view class for this MVC style gui application

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
    self.label3 = Label(self.master, text="Likes: 0")

    # make some text entry boxes for caption and credits strings
    self.entry1 = Entry(self.master, width=15)
    self.entry2 = Entry(self.master, width=50)

    # some basic navigations
    self.button1 = Button(self.master, text="<-", command=self.backHandler)
    self.button2 = Button(self.master, text="->", command=self.nextHandler)
    self.button3 = Button(self.master, text="Save", command=self.saveHandler)
    self.button4 = Button(self.master, text="Done", command=self.exitHandler)
    self.button5 = Button(self.master, text="+", command=self.voteUp)
    self.button6 = Button(self.master, text="-", command=self.voteDown)

    # Grid layout for all the widgets (move to a helper?)
    self.icon.grid(row=0, column=0, columnspan=6,  padx=8, pady=5)
    self.label0a.grid(row=1, column=0, sticky=E)
    self.label0b.grid(row=1, column=1, sticky=W, columnspan=5)
    self.label1.grid(row=2, column=0, sticky=E)
    self.entry1.grid(row=2, column=1, columnspan=6, sticky=W)
    self.label2.grid(row=3, column=0, sticky=E)
    self.entry2.grid(row=3, column=1, columnspan=6, sticky=W)
    
    self.button1.grid(row=4, column=0, sticky=E)
    self.button2.grid(row=4, column=1, sticky=W)
    self.label3.grid(row=4, column=2, sticky=E)
    self.button5.grid(row=4, column=3, sticky=E)      
    self.button6.grid(row=4, column=4, sticky=W)      
    self.button3.grid(row=4, column=5)      
    self.button4.grid(row=4, column=6)      

    
  def backHandler(self):
    self.controller.storeInfo(self.entry1.get(), self.entry2.get())
    self.controller.prevImage()

  def nextHandler(self):
    self.controller.storeInfo(self.entry1.get(), self.entry2.get())
    self.controller.nextImage()

  def exitHandler(self):
    # TODO: May want to pass this back to controller
    self.master.quit()

  def voteUp(self):
    self.controller.recordVote(1)

  def voteDown(self):
    self.controller.recordVote(-1)

  def saveHandler(self):
    self.controller.storeInfo(self.entry1.get(), self.entry2.get())
    self.controller.writeImageInfo()

  def update(self, filename, im, credit="", caption="", votes=0):
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
      
      self.label3.configure(text="Likes: %d" % votes)
      
      self.entry1.delete(0, END)
      self.entry1.insert(0, credit)
      self.entry2.delete(0, END)
      self.entry2.insert(0, caption)
      return True

########################################################################

def mvcSession(root, image_dir):
    model = Model(image_dir)
    controller = Controller(model)
    view = View(root, controller)
    model.controllers.append(controller)
    controller.views.append(view)
    
    # initial update returns false when nothing to do
    if controller.update():
      root.mainloop()
    else:
      print "Image files not found"
      tkMessageBox.showerror('No Images', 'Image files not found')
  

########################################################################


def main(argv):
  root = Tk()

  if len(argv) > 1:
    image_dir = argv[1]
  else:
    image_dir = chooseDirectory(root)
    
  if os.path.exists(image_dir):    
    mvcSession(root, image_dir)
  else:
    print "file path does not exist"
      

if __name__ == '__main__':
  main(sys.argv)

    
