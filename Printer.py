from math import sqrt
from time import strftime, gmtime
from datetime import datetime

API_PREFIX = "/api/v1/"
SYSTEM = API_PREFIX + "system"
PRINTER = API_PREFIX + "printer"
PRINT_JOB = API_PREFIX + "print_job"
CAMERA = API_PREFIX + "camera"
HISTORY = API_PREFIX + "history"

class Printer:
    def __init__(self, ip, session):
        self.ip = ip
        self.host = "http://" + ip
        self.session = session

        self.status = 'starting'
        self.name = 'none'
        self.guid = 'none'
        self.job_state = 'none'
        self.job_name = 'none'
        self.uuid = 'none'
        self.progress = 'none'
        self.interval = 'none'

        self.image_count = 0
        self.last_image_timestamp = 0

        self.reconnect_time = 0

        self.is_online = True

    def get(self, url):
        res = self.session.get(url, timeout=5)
        res.raise_for_status()
        return res
    
    def req_status(self):
        res = self.get(self.host + PRINTER + "/status")
        try:
            return res.text.strip('"')
        except:
            return res
    
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
        self.name = self.req_name()
        self.guid = self.req_guid()
        if self.status in ["pre-print", "printing"]:
            self.job_state = self.req_job_state()
            self.job_name = self.req_job_name()
            self.uuid = self.req_uuid()
            self.job_time = self.req_job_time()
            self.progress = float(self.req_job_progress()) * 100
            self.interval = sqrt(float(self.req_job_time()))/8 + 15
        self.is_online = True
    
    def set_offline(self):
        self.reconnect_time = datetime.now().timestamp()
        self.is_online = False
        self.status = 'none'
        self.name = 'none'
        self.guid = 'none'
        self.job_state = 'none'
        self.job_name = 'none'
        self.uuid = 'none'
        self.job_time = 'none'
        self.progress = 'none'
        self.interval = 'none'
        
    def reset(self):
        self.reconnect_time = 1
        self.is_online = False
        self.status = 'reset'
        self.job_state = 'none'
        self.job_name = 'none'
        self.uuid = 'none'
        self.progress = 'none'
        self.interval = 'none'

    def increment_img_count(self):
        self.image_count += 1
    
    def __str__(self):
        if self.is_online:
            if self.status == 'printing':
                return f"{self.ip}  NAME: {self.name} GUID: {self.guid}  Status: {self.status}\n\tPrint Job: {self.job_name}  UUID: {self.uuid}  State: {self.job_state}  Total Time: {strftime('%H:%M', gmtime(self.job_time))} Progress: {round(self.progress,2)}%"
            else:
                return f"{self.ip} NAME: {self.name} GUID: {self.guid}  Status: {self.status}"
        else:
            return f"{self.ip} Status: Offline"   