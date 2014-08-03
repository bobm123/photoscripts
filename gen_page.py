#!/usr/bin/python

import os, sys
import glob
import Image
import json

# 20140726 - move all the Metadat stuff to the caption_gui tools, now
# Just read json file
#from PIL.ExifTags import TAGS
#from PIL import IptcImagePlugin


#tsize = 100, 100
T_HEIGHT = 200.0
S_HEIGHT = 800.0
fmt_line = "    <a href=\"small/%s\"><img src=\"thumbs/%s\" data-description=\"%s\" data-title=\"%s\" data-big=\"original/%s\" ></a>\n"

def create_dir(path):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def get_favorites(imageinfo, count):
  
  favList = sorted(imageinfo, reverse=True,  key=lambda k: imageinfo[k][2])
  #for fn in favList:
  #  print "%s, likes: %d" % (fn, imageinfo[fn][2])
  return favList[0:count]

  
def gen_page(work_dir, count):

    create_dir(work_dir + '/original')
    create_dir(work_dir + '/small')
    create_dir(work_dir + '/thumbs')

    tags = open(work_dir + '/tags.html', 'w')
    tags.write("  <div class=\"galleria\">\n")

    try:
      jsonfile = os.path.join(work_dir, 'imageinfo.json')
      f = open(jsonfile, 'r')
      imageinfo = json.loads(f.read())
      
    except:
      print "could not read image info from", jsonfile
      return
    
    # Use the votes to create a list of the N best images
    fav_images = get_favorites(imageinfo, count)
    for fn in sorted(fav_images):
        base_name = os.path.splitext(os.path.basename(fn))[0]+'.jpg'
        
        original_file = os.path.join(work_dir, 'original', base_name)
        small_file = os.path.join(work_dir, 'small', base_name)
        thumb_file = os.path.join(work_dir, 'thumbs', base_name)

        try:
          im = Image.open(os.path.join(work_dir, fn))
          
        except:
          print "could not open image file:", fn
          continue
          
        im.save(original_file, "JPEG")

        credit = imageinfo[base_name][0]
        caption =imageinfo[base_name][1]        
        if len(caption) == 0:
          caption = base_name
          
        description = caption
        if len(credit) > 0:
            description += ", photo: "+credit
            
        # Show a sample of the galaria photo carosel's caption area     
        print base_name
        print description

        # Make the snall photos S_HEIGHT high by various width
        im_scale = S_HEIGHT / float(im.size[1]);
        im.thumbnail((int(im.size[0]*im_scale), S_HEIGHT), Image.ANTIALIAS)
        im.save(small_file, "JPEG")

        # Make the thumbnails T_HEIGHT high by various width
        im_scale = T_HEIGHT / float(im.size[1]);
        #print im.size
        #print im_scale
        #print (int(im.size[0]*im_scale), T_HEIGHT)
        im.thumbnail((int(im.size[0]*im_scale), T_HEIGHT), Image.ANTIALIAS)
        im.save(thumb_file, "JPEG")

        tags.write(fmt_line % (base_name, base_name, description, base_name, base_name))

    tags.write("  </div>\n")
    tags.close


def main():
  count = int(sys.argv[2]) if len(sys.argv) > 2 else 50
  gen_page(sys.argv[1], count)
    

if __name__ == '__main__':
  main()

    


