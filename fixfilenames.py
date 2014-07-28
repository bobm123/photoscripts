#!/usr/bin/python

import os, sys
import glob
import shutil


def main(args):

    work_dir = args[1]

    files = sorted(glob.glob(work_dir +'/*.JPG'))
    for img_file in files:
        base_name = os.path.splitext(os.path.basename(img_file))[0]
        dir_name = os.path.dirname(img_file)+"/"
        print "cp "+img_file+" "+dir_name+base_name+".jpg"
        shutil.move(img_file, dir_name+base_name+".jpg")

main(sys.argv)


