import os
import requests
from time import sleep
from urllib.request import urlopen
import logging
import argparse
import json
from datetime import datetime
import shutil

argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
argParser.add_argument('NAME', type=str, 
    help='Name of the Ultimaker 3D Printer')
argParser.add_argument('IP', type=str, 
    help='Name of the Ultimaker 3D Printer')

args = argParser.parse_args()

HTTP = "http://"
SNAPSHOT = ":8080/?action=snapshot"
PRINTER = "/api/v1/printer"
PRINTER_STATUS = "/api/v1/printer/status"
PRINT_JOB = "/api/v1/print_job"

TEMP_DIR = "temp_files"
OUT_DIR = "video_files"
IMAGE_FORMAT = "%05d.jpg"

NAME = args.NAME.upper()
HOST = HTTP + args.IP

logging.basicConfig(filename= NAME.lower()+".log", filemode='a', format='%(asctime)s - %(levelname)s - ' + NAME + ' - %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

def connection_error(err):
    logging.error('Connection Error: %s', err)
    logging.error('Retrying in 5 seconds...')
    sleep(5)

def init_directory(directory_name):
    dir = os.path.join(os.getcwd(),directory_name)
    if not os.path.exists(dir):
        os.mkdir(dir)
        print("Directory '% s' created" % dir) 
    print("Directory '% s' exists" % dir)
    return dir

def get_status():
    while True:
        try:
            res = requests.get(HOST + PRINTER_STATUS)
            res.raise_for_status() 
            return res.text.strip('\"') 
        except Exception as e:
            connection_error(e)

def get_job():
    res = requests.get(HOST + PRINT_JOB)
    if(res.status_code == 404):
        return None
    return json.loads(res.content)

def start_print(tmpdir, job_name):
    logging.info('New Print Started:')
    logging.info('Printer = %s, File = %s' % (NAME, job_name))

    logging.info('Saving images to temp directory %s', tmpdir)
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

def end_print(path,name):
    logging.info('Print Done or Stopped') 

    init_directory(OUT_DIR)

    date = datetime.now()
    out_file = f"{OUT_DIR}/{date.year}-{date.month}-{date.day}_{name.strip().replace(' ', '_')}_{date.microsecond}.mp4"
    in_files = os.path.join(path,IMAGE_FORMAT)
    logging.info("Starting Timelapse Generation")
    logging.info(f"Saving Video as {out_file} to {in_files}")

    ffmpegcmd = f"ffmpeg -r 30 -i {in_files} {out_file}"
    logging.info(f"Executing ffmpeg command: {ffmpegcmd}")
    try:
        os.system(ffmpegcmd)
        pass
    except Exception as e:
        logging.error("\tError: %s - %s." % (e.filename, e.strerror))
    logging.info("Done Encoding Video")

    try:
        logging.info(f"Deleting temp folder {path}")
        shutil.rmtree(path)
    except OSError as e:
        logging.error("\tError: %s - %s." % (e.filename, e.strerror))
    logging.info(f"Finished deleting temp folder")

    logging.info(f"Print {name} Finished")
    
def save_image(path,count,job):
    res = urlopen(HOST + SNAPSHOT)
    filename = os.path.join(path,IMAGE_FORMAT) % count
    f = open(filename,'bw')
    f.write(res.read())
    f.close
    print("Image #: %05i Progress: %2.2f%%" % (count,job["progress"]), end='\r')
    if job["time_total"] < 14400:  
        sleep(15)
    else:
        sleep(30)

def main():
    directory = init_directory(TEMP_DIR)
    count = 0
    job_path = None

    print('Starting Timelapse.py - NAME = \"%s\", HOST = %s' % (NAME, HOST))
    logging.info('Starting Timelapse.py - NAME = \"%s\", HOST = %s' % (NAME, HOST))

    printer_status = get_status()
    job = get_job()
    job_state, job_uuid = (job["state"], job["uuid"]) if job != None else (None, None)

    if job_state != None:
        logging.info('Initial Job: Name: %s UUID: %s Progress: %.2f%%', job["name"],job_uuid,job["progress"])
        path = os.path.join(os.path.join(os.getcwd(),TEMP_DIR),job_uuid)
        if os.path.exists(path):
            images = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            count = int(max(images).split('.')[0])
        job_path = os.path.join(directory, job_uuid)

        if printer_status == "printing" and job_state == "printing":
            job_path = os.path.join(directory, job_uuid)
            start_print(job_path,job["name"])

    while True:
        printer_status_new = get_status()
        job = get_job()
        job_state_new, job_uuid_new = (job["state"], job["uuid"]) if job != None else (None, None)

        if printer_status_new != printer_status:
            logging.info('Printer Status Change: %s -> %s', printer_status, printer_status_new)
            printer_status = printer_status_new
                
        if printer_status == "printing":
            if job_state_new != job_state or job_uuid_new != job_uuid:
                if job_state_new != job_state:
                    logging.info('Job State Change: %s -> %s', job_state, job_state_new)
                elif job_uuid_new != job_uuid:
                    logging.info('Job UUID Change: %s -> %s', job_uuid, job_uuid_new)

                job_state, job_uuid = job_state_new, job_uuid_new

                if job_state == "pre_print":
                    count = 0
                    job_path = os.path.join(directory, job_uuid)
                    start_print(job_path,job["name"])
                
                if job_state == "post_print":
                    end_print(job_path,job["name"])

            if job_state == "printing":
                count += 1
                save_image(job_path,count,job)


if __name__ == "__main__":
    main()
