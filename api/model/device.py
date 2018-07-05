from enum import Enum

class Device:
    def __init__(
        self,
        did,
        serial_number,
        series,
        platform_id,
        hostname,
        management_ip,
        mac_address,
        up_time,
        reachability_status
    ):
        self.id = did
        self.serial_number = serial_number
        self.product_series = series
        self.platform_id = platform_id
        self.hostname = hostname
        self.management_ip = management_ip
        self.mac_address = mac_address
        self.up_time = up_time
        self.reachability_status = reachability_status
    def __str__(self):
        name = self.hostname if self.hostname else self.management_ip
        return "{name} -> Platform: {platform_id} SN: {serial_number} ".format(
            name=name,
            serial_number=self.serial_number,
            platform_id=self.platform_id
        )

class ReachabilityStatus(Enum):
    REACHABLE = 'Reachable'
    UNREACHABLE = 'Unreachable'
    UNKNOWN = 'Unknown'

class DeviceFactory:
    @staticmethod
    def fromDict(document):
        dev_id = document['id']
        management_ip = document['managementIpAddress']
        serial_number = document['serialNumber'] if 'serialNumber' in document else None
        series = document['series'] if 'series' in document else None
        platform_id = document['platformId'] if 'platformId' in document else None
        hostname = document['hostname'] if 'hostname' in document else None
        mac_address = document['macAddress'] if 'macAddress' in document else None
        up_time = document['upTime'] if 'upTime' in document else None
        if document['reachabilityStatus'] == ReachabilityStatus.REACHABLE.value:
            reachability_status = ReachabilityStatus.REACHABLE
        elif document['reachabilityStatus'] == ReachabilityStatus.UNREACHABLE.value:
            reachability_status = ReachabilityStatus.UNREACHABLE
        else:
            reachability_status = ReachabilityStatus.UNKNOWN
        return Device(
            dev_id,
            serial_number,
            series,
            platform_id,
            hostname,
            management_ip,
            mac_address,
            up_time,
            reachability_status
        )