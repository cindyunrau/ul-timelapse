import os
import shutil
import logging
import argparse
from datetime import datetime
import subprocess
from time import sleep
import requests
from requests.adapters import HTTPAdapter, Retry

import functions
from api import Printer, PrintJob

TEMP_DIR = "temp_files"
OUT_DIR = "video_files"
IMG_TYPE = ".jpg"
IMAGE_FORMAT = "%05d" + IMG_TYPE
VID_TYPE = ".mp4"
FPS = 30
VID_LENGTH = 30

argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
argParser.add_argument('NAME', type=str, 
    help='Name of the Ultimaker 3D Printer')
argParser.add_argument('IP', type=str, 
    help='Name of the Ultimaker 3D Printer')
args = argParser.parse_args()

NAME = args.NAME.upper()
IP = args.IP

LOG_FILE = "print.log"

logging.basicConfig(filename= LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - ' + NAME + ' - %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def main():

    uuid = "94f0b12a-3471-4d6e-8efd-64837f7cdd21"
    functions.generate_video(uuid,"testvideo")

if __name__ == "__main__":
    main()


