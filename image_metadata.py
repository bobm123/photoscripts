#!/usr/bin/python -tt

import os, sys
#import Image
from PIL import Image, ExifTags

from iptcinfo import IPTCInfo
 
########################################################################
# Code shamelessly lifted from web
# http://twigstechtips.blogspot.com/2014/06/python-reading-exif-and-iptc-tags-from.html

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

# End of code shamelessly lifted from web
########################################################################
     

def add_exif_tags(filename, metadata):
  '''
  Attempts to exatract tags from EXIF data in <filename> and adds them
  to date, caption and credits keys in <metadata>. Uses the python image
  library (PIL). May find WinXP tag keys in tag_name_to_id above
  '''

  # print "Exif Tags"
  im = Image.open(filename)
  im.verify()
  
  exif = convert_exif_to_dict(im._getexif())
  if 'Artist' in exif:
    metadata['credit'] += exif['Artist']
  if 'DateTime' in exif and exif['DateTime']:
    taken_on = exif['DateTime'].split(' ')[0]
    taken_on = taken_on.split(':')
    metadata['date'] += "%s/%s/%s" % (taken_on[1], taken_on[2], taken_on[0]) 
  if 'XPTitle' in exif:
    metadata['caption'] += exif['XPTitle']

  # dump any exif tags in case there's something of interest
  #for k in exif:
  #  print k, exif[k]
  
  return metadata
  
  
def add_iptc_tags(filename, metadata):
  '''
  Uses iptcdata.py IPTC data in <filename> and adds them caption and 
  credits keys in <metadata>. 
  '''

  # this library throw up a lot (of errors)
  try:
    iptc = IPTCInfo(filename, force=True)
    
    if len(iptc.data) > 4:
      #print iptc
      metadata['credit'] += iptc.data['credit'] or ''
      metadata['caption'] += iptc.data['caption/abstract'] or ''
     
    # dump any iptc tags in case there's something of interest
    #for k in iptc.data:
    #  print k, iptc.data[k]
    
  except Exception, e:
    # This is used to skip anything not an image.
    # Image.open will generate an exception if it cannot open a file.
    # Warning, this will hide other errors as well.
    pass
        
  return metadata


 # Attempt to read file metadata: Exif, Iptc or other things
def readMetadata(filename):
  metadata = {'credit': '', 'caption':'', 'date':''}
  
  #print filename
  if os.path.isfile(filename):
    metadata = add_iptc_tags(filename, metadata)
    #metadata = add_exif_tags(filename, metadata)
        
  return metadata


def main():
  if len(sys.argv) > 1:
    print readMetadata(sys.argv[1])

if __name__ == '__main__':
  main()
