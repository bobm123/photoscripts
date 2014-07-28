#!/usr/bin/python -tt

import os, sys
#import Image
from PIL import Image, ExifTags

from iptcinfo import IPTCInfo
 

tag_name_to_id = dict([ (v, k) for k, v in ExifTags.TAGS.items() ])
 
# These I got from reading in files and matching to http://www.exiv2.org/tags.html
# You'll have to map your own if something isn't recognised
tag_name_to_id[270] = 'ImageDescription'
tag_name_to_id[306] = 'DateTime'
tag_name_to_id[256] = 'ImageWidth'
tag_name_to_id[257] = 'ImageLength'
tag_name_to_id[258] = 'BitsPerSample'
tag_name_to_id[40962] = 'PixelXDimension'
tag_name_to_id[40963] = 'PixelYDimension'
tag_name_to_id[305] = 'Software'
tag_name_to_id[37510] = 'UserComment'
tag_name_to_id[40091] = 'XPTitle'
tag_name_to_id[40092] = 'XPComment'
tag_name_to_id[40093] = 'XPAuthor'
tag_name_to_id[40094] = 'XPKeywords'
tag_name_to_id[40095] = 'XPSubject'
tag_name_to_id[40961] = 'ColorSpace' # Bit depth
tag_name_to_id[315] = 'Artist'
tag_name_to_id[33432] = 'Copyright'


def convert_exif_to_dict(exif):
    """
    This helper function converts the dictionary keys from
    IDs to strings so your code is easier to read.
    """
    data = {}

    if exif is None:
        return data

    for k,v in exif.items():
       if k in tag_name_to_id:
           data[tag_name_to_id[k]] = v
       else:
           data[k] = v

    # These fields are in UCS2/UTF-16, convert to something usable within python
    for k in ['XPTitle', 'XPComment', 'XPAuthor', 'XPKeywords', 'XPSubject']:
        if k in data:
            data[k] = data[k].decode('utf-16').rstrip('\x00')

    return data
     
 
 # Attempt to read file metadata: Exif, Iptc or other things
def readMetadata(filename):
  metadata = {'credit': '', 'caption':'', 'date':''}
  
  print filename
    
  if os.path.isfile(filename):
    # first try the IPTC tags
    print "IPTC Tags"
    iptc = IPTCInfo(filename, force=True)
    if len(iptc.data) > 4:
      metadata['credit'] += iptc.data['credit']
      metadata['caption'] += iptc.data['caption/abstract']
      
      # dump any exif tags in case therr's something of interest
      #for k in iptc.data:
      #  print k, iptc.data[k]

    # Next try to read Exif tags
    print "Exif Tags"
    im = Image.open(filename)
    im.verify()
    
    exif = convert_exif_to_dict(im._getexif())
    if 'Artist' in exif:
      metadata['credit'] += exif['Artist']
    if 'DateTime' in exif:
      taken_on = exif['DateTime'].split(' ')[0]
      taken_on = taken_on.split(':')
      print taken_on
      metadata['date'] += "%s/%s/%s" % (taken_on[1], taken_on[2], taken_on[0]) 
    if 'XPTitle' in exif:
      metadata['caption'] += exif['XPTitle']

    # dump any exif tags in case there's something of interest
    #for k in exif:
    #  print k, exif[k]
        
  return metadata


def main():
  if len(sys.argv) > 1:
    print readMetadata(sys.argv[1])

if __name__ == '__main__':
  main()





    
'''  
  try:
    iptc = IPTCInfo(filename)
    im_caption = iptc.data['caption/abstract']
    im_credit = iptc.data['credit']
    print im_caption
    print im_credit
    
  except Exception, e:
    if str(e) != "No IPTC data found.":
      raise
 
#im = Image.open(filename)
#im.verify()
'''






def foo():
     
  # Not sure what other formats are supported, I never looked into it.
  if im.format in ['JPG', 'TIFF']:
    try:
      iptc = iptcinfo.IPTCInfo(filename)
   
      im_caption = iptc.data.get('caption/abstract', '')
      im_credit = iptc.data.get('credit', '')
      image_tags = iptc.keywords
   
    except Exception, e:
      print "caught exception", e
#      if str(e) != "No IPTC data found.":
#        raise
    
    print im_caption
    print im_credit
   

def readIptcInfo (im):
  iptc= IptcImagePlugin.getiptcinfo(im) or {}
  caption = iptc.get((2,120), "")
  credit = iptc.get((2,110), "")
  #print "caption:" + caption
  #print "credit: " + credit
  return(credit, caption)

