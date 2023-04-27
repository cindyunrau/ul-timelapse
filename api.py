import os

API_PREFIX = "/api/v1/"
SYSTEM = API_PREFIX + "system"
PRINTER = API_PREFIX + "printer"
PRINT_JOB = API_PREFIX + "print_job"
CAMERA = API_PREFIX + "camera"
HISTORY = API_PREFIX + "history"

class Printer:
    def __init__(self, session, ip):
        self.ip = ip
        self.host = "http://" + ip
        self.session = session

        self.name = self.req_name()
        self.guid = self.req_guid()
        self.status = self.req_status()
    
    def get(self, url):
        try:
            res = self.session.get(url)
            res.raise_for_status()
        except Exception as e:
            print(e)
            return 'none'

        return res

    def req_status(self):
        res = self.get(self.host + PRINTER + "/status")
        return res.text.strip('"')

    def update(self):
        self.status = self.req_status()
    
    def req_guid(self):
        res = self.get(self.host + SYSTEM + "/guid")
        return res.json()
    
    def req_name(self):
        res = self.get(self.host + SYSTEM + "/name")
        return res.json()
    
    def snapshot(self):
        res = self.get(self.host + CAMERA + "/0/snapshot")
        return res.content
    
    def __str__(self):
        return f"Printer: {self.name}  GUID: {self.guid}  Status: {self.status}"
        

class PrintJob:
    def __init__(self, printer, temp_dir):
        self.host = printer.host
        self.session = printer.session

        self.content = self.get_job()
        self.state = self.content['state']
        self.name = self.content['name']
        self.uuid = self.content['uuid']
        self.progress = float(self.content['progress']) * 100
        self.interval = 5 + 5*float(self.content['time_total'])/60
        
        self.path = os.path.join(temp_dir, self.uuid)

        if os.path.exists(self.path):
            self.image_count = len(os.listdir(self.path))
        else:
            self.image_count = 0

    def get_job(self):
        res = self.session.get(self.host + PRINT_JOB)
        res.raise_for_status()
  
        return res.json()
    
    def update(self):
        self.content = self.get_job()
        self.state = self.content['state']
        self.name = self.content['name']
        self.uuid = self.content['uuid']
        self.progress = float(self.content['progress']) * 100

    def increment_count(self):
        self.image_count += 1
    
    def __str__(self):
        try:
            return f"Print Job: {self.name}  UUID: {self.uuid}  State: {self.state}  Progress: {round(self.progress,2)}%"
        except:
            return f"Print Job: None"
