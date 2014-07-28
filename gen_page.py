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
fmt_line = "    <a href=\"small/%s.jpg\"><img src=\"thumbs/%s.png\" data-big=\"original/%s.jpg\" data-title=\"%s\" data-description=\"%s\"></a>\n"

def create_dir(path):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def read_image_metadata (filename):
  meta = {}
  if os.path.isfile(filename):
    f = open(filename, 'r')
    meta = json.loads(f.read())
    
  print meta
  return meta
  

def main(args):

    work_dir = args[1]

    create_dir(work_dir + '/original')
    create_dir(work_dir + '/small')
    create_dir(work_dir + '/thumbs')

    tags = open(work_dir + '/tags.html', 'w')
    tags.write("  <div class=\"galleria\">\n")

    imageinfo = read_image_metadata(os.path.join(work_dir,'imageinfo.json'))

    files = sorted(glob.glob(work_dir +'/*.jpg'))
    for img_file in files:
        base_name = os.path.splitext(os.path.basename(img_file))[0]

        original_file = work_dir + '/original/' + base_name + '.jpg'
        small_file = work_dir + '/small/' + base_name + '.jpg'
        thumb_file = work_dir + '/thumbs/' + base_name + '.jpg'

        im = Image.open(img_file)
        im.save(original_file, "JPEG")

#        iptc= IptcImagePlugin.getiptcinfo(im) or {}
#        caption = iptc.get((2,120), "")
#        credit = iptc.get((2,110), "")

        credit = ''
        caption = ''
        print base_name
        if base_name in imageinfo:
          credit = imageinfo[base_name][0]
          caption =imageinfo[base_name][1]
        #print "credit: " + credit
        #print "caption:" + caption
        description = caption
        if len(credit) > 0:
            description += " photo: "+credit
        print "description: "+description

        # Make the thumbnails S_HEIGHT high by various width
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

        tags.write(fmt_line % (base_name, base_name, base_name, base_name, description))

    tags.write("  </div>\n")
    tags.close


if __name__ == '__main__':
  main(sys.argv)

    


