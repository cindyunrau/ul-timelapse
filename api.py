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

        return res

    def req_status(self):
        res = self.get(self.host + PRINTER + "/status")
        return res.text.strip('"')
    
    def set_status(self, status):
        self.status = status

    def update(self):
        self.status = self.req_status()

    def req_history(self):
        res = self.get(self.host + HISTORY)
        return res.json()
    
    def req_guid(self):
        res = self.get(self.host + SYSTEM + "/guid")
        return res.json()
    
    def req_name(self):
        res = self.get(self.host + SYSTEM + "/name")
        return res.json()
    
    def req_snapshot(self):
        res = self.get(self.host + CAMERA + "/0/snapshot")
        return res.content
    
    def __str__(self):
        return f"Printer: {self.name}  GUID: {self.guid}  Status: {self.status}"
        

class PrintJob:
    def __init__(self, printer, temp_dir, num_images):
        self.host = printer.host
        self.session = printer.session

        self.content = self.req_job()
        self.name = self.content['name']
        self.uuid = self.content['uuid']
        self.state = self.content['state']
        self.shoot_interval = self.content['time_total'] / num_images
        self.progress = float(self.content['progress']) * 100

        self.image_count = 0
        self.path = os.path.join(temp_dir, self.uuid)

    def get(self, url):
        try:
            res = self.session.get(url)
            res.raise_for_status()
        except Exception as e:
            print(e)

        return res

    def req_job(self):
        res = self.get(self.host + PRINT_JOB)
        return res.json()
    
    def update(self):
        self.content = self.req_job()
        self.name = self.content['name']
        self.uuid = self.content['uuid']
        self.state = self.content['state']
        self.progress = float(self.content['progress']) * 100

    def req_name(self):
        res = self.get(self.host + PRINT_JOB + "/name")
        return res.text

    def increment_count(self):
        self.image_count += 1
    
    def __str__(self):
        return f"Print Job: {self.name}  UUID: {self.uuid}  State: {self.state}  Progress: {round(self.progress,2)}%"
