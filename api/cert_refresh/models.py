class Device:
    def __init__(self,serial_number,hostname,platform_id,mgmt_ip):
        self.serial_number = serial_number
        self.hostname = hostname
        self.platform_id = platform_id
        self.mgmt_ip = mgmt_ip

class Trustpoint:
    def __init__(self,tid,profile_name,controller):
        self.tid = tid 
        self.profile_name = profile_name