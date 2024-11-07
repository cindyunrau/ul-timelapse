from math import sqrt
from time import strftime, gmtime

API_PREFIX = "/api/v1/"
SYSTEM = API_PREFIX + "system"
PRINTER = API_PREFIX + "printer"
PRINT_JOB = API_PREFIX + "print_job"
CAMERA = API_PREFIX + "camera"
HISTORY = API_PREFIX + "history"
class Printer:
    def __init__(self, ip, session):
        self.host = "http://" + ip
        self.session = session

        self.name = self.req_name()
        self.guid = self.req_guid()
        self.status = self.req_status()
        self.job_state = 'none'
        self.job_name = 'none'
        self.uuid = 'none'
        self.progress = 'none'
        self.interval = 'none'

        self.image_count = 0
        self.last_image_timestamp = 0

        self.update()

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
    
    def req_guid(self):
        res = self.get(self.host + SYSTEM + "/guid")
        return res.json()
    
    def req_uuid(self):
        res = self.get(self.host + PRINT_JOB + "/uuid")
        return res.json()
    
    def req_name(self):
        res = self.get(self.host + SYSTEM + "/name")
        return res.json()
    
    def req_job_name(self):
        res = self.get(self.host + PRINT_JOB + "/name")
        return res.json()
    
    def req_job_state(self):
        res = self.get(self.host + PRINT_JOB + "/state")
        return res.json()
    
    def req_job_progress(self):
        res = self.get(self.host + PRINT_JOB + "/progress")
        return res.json()
    
    def req_job_time(self):
        res = self.get(self.host + PRINT_JOB + "/time_total")
        return res.json()

    def snapshot(self):
        res = self.get(self.host + CAMERA + "/0/snapshot")
        return res.content
    
    def update(self):
        self.status = self.req_status()
        if self.status in ["pre-print", "printing"]:
            self.job_state = self.req_job_state()
            self.job_name = self.req_job_name()
            self.uuid = self.req_uuid()
            self.job_time = self.req_job_time()
            self.progress = float(self.req_job_progress()) * 100
            self.interval = sqrt(float(self.req_job_time()))/8 + 15
    
    def reset(self):
        self.status = self.req_status()
        self.job_state = 'none'
        self.job_name = 'none'
        self.uuid = 'none'
        self.progress = 'none'
        self.interval = 'none'

    def increment_img_count(self):
        self.image_count += 1
    
    def __str__(self):
        try:
            return f"{self.name}  GUID: {self.guid}  Status: {self.status}\n\tPrint Job: {self.job_name}  UUID: {self.uuid}  State: {self.job_state}  Total Time: {strftime('%H:%M', gmtime(self.job_time))} Progress: {round(self.progress,2)}%"
        except:
            return f"{self.name}  GUID: {self.guid}  Status: {self.status}"