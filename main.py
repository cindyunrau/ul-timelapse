from PrinterManager import PrinterManager
from Printer import Printer
import argparse
import logging
import requests
from requests.adapters import HTTPAdapter, Retry

argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
argParser.add_argument('-ip', type=str, nargs='+',
    help='IP Addresses of the Ultimaker 3D Printers')
argParser.add_argument('--out_dir', type=str, default="video", required=False,
    help='Frames per second')
args = argParser.parse_args()

IP_LIST = args.ip
OUT_DIR = args.out_dir
LOG_FILE = "print.log"

logging.basicConfig(filename= LOG_FILE, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger("logger")

def main():
    print("Starting Program Timelapse.py with IP addresses: %s" % IP_LIST)
    print("All logs saved in %s\n" % LOG_FILE)
    logger.info('Starting Program Timelapse.py - HOSTS: %s' % IP_LIST)

    post_frame_count = 0

    # Request Session setup
    session = requests.Session()
    retries = Retry(total = 5, backoff_factor = 0.5, status_forcelist = [429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries = retries))

    printer_manager = PrinterManager(IP_LIST, session)

    for printer in printer_manager.printers:
        logger.info('Printer: %s', printer)

    while True:
        for printer in printer_manager.printers:
            prev_printer_status = printer.status
            prev_job_state = printer.job_state
            printer_manager.update_printer(printer)

            if prev_printer_status != printer.status:
                logging.info('%s - Status Change: %s -> %s', printer.name, prev_printer_status, printer.status)
                if printer.status == "pre_print":
                    printer_manager.start_job(printer)
            
            if printer.status == "printing" and printer.job_state != 'none': 
                if prev_job_state != printer.job_state:
                    logging.info('%s - Job State Change: %s -> %s\n%s', printer.name, prev_job_state, printer.job_state, printer)
                    if printer.job_state == "post_print":
                        # Capture an extra second after print is completed
                        if post_frame_count < 30:
                            post_frame_count += 1
                            printer_manager.save_image(printer)
                        else:
                            post_frame_count = 0
                            try:
                                printer_manager.end_job(printer)
                            except OSError as e:
                                logging.error("Error Ending Job: %s - %s - %s.", printer.name, e.filename, e.strerror)
                            try: 
                                filename = printer_manager.generate_timelapse(printer, OUT_DIR)
                                logging.info(f"Timelapse Generated: Saved Video as {filename}")
                            except:
                                logging.error("Error Generating Timelapse: %s - %s.", printer.name, e.filename, e.strerror)

                            logging.info(f"Print {printer.job_name} Finished")
                if(printer.job_state == "printing"):
                    printer_manager.save_image(printer)

if __name__ == "__main__":
    main()