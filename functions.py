import os
import shutil
import logging
import argparse
from datetime import datetime
import subprocess
from time import sleep
import requests
from requests.adapters import HTTPAdapter, Retry

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

def init_directory(name):
    logging.info("Initializing Directory '%s'" % name)
    dir = os.path.join(os.getcwd(), name)
    if not os.path.exists(dir):
        os.mkdir(dir)

    return dir
    
def save_image(path, image, count):
    filename = os.path.join(path, IMAGE_FORMAT) % count
    f = open(filename,'bw')
    f.write(image)
    f.close

def generate_timelapse(tmpdir, outdir, job_name):
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date}_{job_name.strip().replace(' ', '_')}_0{VID_TYPE}"

    while os.path.isfile(f"{outdir}/{filename}"):
        filename = f"{filename[:-2-len(VID_TYPE)]}_{int(filename[-1-len(VID_TYPE)])+1}{VID_TYPE}"

    in_path = os.path.join(tmpdir, IMAGE_FORMAT)
    out_path = f"{outdir}/{filename}"

    logging.info(f"Starting Timelapse Generation: Saving Video as {filename}")

    ffmpegcmd = ["ffmpeg", "-r", str(FPS), "-i", in_path, out_path]
    # ffmpegcmd = ["ffmpeg", "-loglevel", "level+warning", "-r", str(FPS), "-i", in_path, out_path]
    
    logging.info(f"Executing ffmpeg command: {ffmpegcmd}")
    subprocess.run(ffmpegcmd,check = True)

    logging.info("Done Encoding Video")

def delete_temp_folder(path):
    logging.info(f"Deleting temp folder {path}")
    shutil.rmtree(path)
    logging.info(f"Finished deleting temp folder")

def start_print(tmpdir, job_str):
    logging.info('New Print Started: %s' % job_str)
    logging.info('Saving images to temp directory %s', tmpdir)
    init_directory(tmpdir)

def end_print(tmpdir,outdir,job_name):
    logging.info('Print Done or Stopped') 

    try:
        generate_timelapse(tmpdir, outdir, job_name)
    except OSError as e:
        logging.error(f"Error Encoding Video: {e}")
        return
    
    try:
        delete_temp_folder(tmpdir)
    except OSError as e:
        logging.error("\tError: %s - %s." % (e.filename, e.strerror))

    logging.info(f"Print {job_name} Finished")

def generate_video(job_uuid,job_name):
    temp_path = os.path.join(TEMP_DIR,job_uuid)
    out_path = os.getcwd()

    generate_timelapse(temp_path,out_path, job_name)
