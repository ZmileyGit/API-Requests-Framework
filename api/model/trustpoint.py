class Trustpoint:
    def __init__(
        self,
        trustpoint_id,
        entity_name,
        serial_number,
        platform_id,
        profile_name,
        controller_ip
        ):
        self.id = trustpoint_id
        self.entity_name = entity_name
        self.serial_number = serial_number
        self.platform_id = platform_id
        self.profile_name = profile_name
        self.controller_ip = controller_ip

class TrustpointFactory:
    @staticmethod
    def fromDict(document):
        trustpoint_id = document['id']
        profile_name = document['trustProfileName']
        entity_name = document['entityName']
        serial_number = document['serialNumber']
        platform_id = document['platformId'] if 'platformId' in document else None
        controller_ip = document['controllerIpAddress'] if 'controllerIpAddress' in document else None
        return Trustpoint(
            trustpoint_id,
            entity_name,
            serial_number,
            platform_id,
            profile_name,
            controller_ip
        )