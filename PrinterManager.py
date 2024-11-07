from Printer import Printer
import os
import shutil
from datetime import datetime
import subprocess

class PrinterManager:
    def __init__(self, ip_list, session):
        self.printers = []

        if not os.path.exists(os.path.join(os.getcwd(), "temp")):
            os.mkdir(os.path.join(os.getcwd(), "temp"))
        self.temp_dir = os.path.join(os.getcwd(), "temp")

        for ip in ip_list:
            self.add_printer(ip, session)

        for printer in self.printers:
            if(printer.status in ["pre-print", "printing"]):
                self.start_job(printer)
                printer.update()

            if os.path.exists(self.get_printer_path(printer)):
                printer.image_count = len(os.listdir(self.get_printer_path(printer)))
            else:
                printer.image_count = 0

    def add_printer(self, ip, session):
        printer = Printer(ip, session)
        self.printers.append(printer)
        return printer
        
    def get_img_path(self, printer):
        return os.path.join(self.temp_dir, printer.uuid, "%05d.jpg") % printer.image_count
    
    def get_printer_path(self, printer):
        return os.path.join(self.temp_dir, printer.uuid)
    
    def start_job(self, printer):
        dir = self.get_printer_path(printer)
        if not os.path.exists(dir):
            os.mkdir(dir)

    def save_image(self, printer):
        curr_time = datetime.now().timestamp()
        if curr_time - printer.last_image_timestamp > printer.interval:
            filename = self.get_img_path(printer)
            f = open(filename,'bw')
            f.write(printer.snapshot())
            f.close

            printer.last_image_timestamp = curr_time
            printer.increment_img_count()
    
    def generate_timelapse(self, printer, outdir):
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date}_{(printer.job_name).strip().replace(' ', '_')}.mp4"
        out_path = f"{outdir}/{filename}"

        ffmpegcmd = ["ffmpeg", "-loglevel", "level+warning", "-r", "30", "-i", self.get_img_path(printer), out_path]
        subprocess.run(ffmpegcmd,check = True)

        return filename

    def end_job(self, printer):
        shutil.rmtree(os.path.join(self.temp_dir, printer.uuid))
        printer.reset()