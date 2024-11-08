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
    logger.info("-----------------------------------------------")
    logger.info('Starting Program Timelapse.py - HOSTS: %s' % IP_LIST)

    post_frame_count = 0

    # Request Session setup
    session = requests.Session()
    retries = Retry(total = 5, backoff_factor = 0.5, status_forcelist = [429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries = retries))

    printer_manager = PrinterManager(IP_LIST, session)

    print("Initial Printer Status:")
    for printer in printer_manager.printers:
        logger.info('Printer: %s', printer)
        print(f"Printer: {printer}")

    while True:
        for printer in printer_manager.printers:
            printer_status, job_state = printer_manager.update_printer(printer)

            if printer.is_online:
                if printer_status["prev"] != printer_status["curr"]:
                    logging.info('%s - Status Change: %s -> %s', (printer.name or printer.ip), printer_status["prev"], printer_status["curr"])
                    if printer_status["curr"] == "pre_print":
                        printer_manager.start_job(printer)
                
                if printer_status["curr"] == "printing" and job_state["curr"] != 'none': 
                    if job_state["prev"] != job_state["curr"]:
                        logging.info('%s - Job State Change: %s -> %s\n%s', (printer.name or printer.ip), job_state["prev"], job_state["curr"], printer)
                        if job_state["curr"] == "post_print":
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
                    if(job_state["curr"] == "printing"):
                        printer_manager.save_image(printer)

if __name__ == "__main__":
    main()