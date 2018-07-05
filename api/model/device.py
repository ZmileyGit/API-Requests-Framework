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
        reachability_status,
        collection_status
    ):
        self.id = did
        self.serial_number = serial_number
        self.product_series = series
        self.platform_id = platform_id,
        self.hostname = hostname
        self.management_ip = management_ip
        self.mac_address = mac_address
        self.up_time = up_time
        self.reachability_status = reachability_status
        self.collection_status = collection_status


class ReachabilityStatus(Enum):
    Reachable = 'Reachable'
    Unrechable = 'Unreachable'

class CollectionStatus(Enum):
    Managed = 'Managed'
    InProgress = 'In Progress'
    DevUnreached = 'DEV-UNREACHED'
    Unknown = 'UNKNOWN'