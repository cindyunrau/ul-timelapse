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

    ffmpegcmd = ["ffmpeg", "-loglevel", "level+warning", "-r", str(FPS), "-i", in_path, out_path]

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

def main():
    print("Starting program Timelapse.py\n\tPrinter: %s\n\tIP: %s" % (NAME, IP))
    print("All logs saved in %s\n" % LOG_FILE)

    logging.info('Starting program Timelapse.py - HOST: %s' % IP)

    t_path = init_directory(TEMP_DIR)
    o_path = init_directory(OUT_DIR)

    num_images = (FPS * VID_LENGTH)
    post_frame_count = 0

    session = requests.Session()
    retries = Retry(total = 5, backoff_factor = 0.5, status_forcelist = [429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries = retries))

    printer = Printer(session, IP)

    if(printer.status == "printing"):
        job = PrintJob(printer, t_path, num_images)

        if(job.state == "printing"):
            init_directory(job.path)

        if os.path.exists(job.path):
            job.image_count = len(os.listdir(job.path))

        logging.info('Job on start-up: %s' % job)

    while True:
        prev_printer_status = printer.status
        prev_job_state = job.state
        printer.update()
        job.update()

        if prev_printer_status != printer.status:
            logging.info('Printer Status Change: %s -> %s', prev_printer_status, printer.status)
                
        if printer.status == "printing":
            if prev_job_state != job.state:
                logging.info('Job State Change: %s -> %s', prev_job_state, job.state)

                if job.state == "pre_print":
                    job = PrintJob(printer, t_path, num_images)
                    start_print(job.path,str(job))
                
                if job.state == "post_print":
                    if post_frame_count < FPS:
                        post_frame_count += 1
                        save_image(job.path, printer.req_snapshot(),job.image_count)
                        sleep(job.shoot_interval)
                    else:
                        post_frame_count = 0
                        end_print(t_path,o_path,job.name)

            if job.state == "printing":
                print("Current Job:  %s" % str(job), end='\r')
                job.increment_count()
                save_image(job.path, printer.req_snapshot(),job.image_count)
                sleep(job.shoot_interval)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error('Main Crashed. %s: %s', type(e).__name__, e)
        print(f'Main Crashed. See {LOG_FILE} for info')
    except KeyboardInterrupt as k:
        logging.error('User Quit. %s', type(k).__name__)
        print(f'User Quit. See {LOG_FILE} for info')
