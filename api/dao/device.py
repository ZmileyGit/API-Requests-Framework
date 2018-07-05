from api.dao.base import DAO
from api.model.device import Device,DeviceFactory
from api.entities import HTTPMethod
from api.handlers import ResponseHandler,UnknownResourceHandler,InvalidRequestHandler
from api.conditioners import UniqueResourceConditioner,HTTPCodeConditioner

class DeviceDAO(DAO):
    BY_SERIAL_NUMBER = '/api/v1/network-device/serial-number/{serial_number}'
    BY_IP_ADDRESS = '/api/v1/network-device/ip-address/{ip_address}'
    def get_by_serial_number(self,serial_number:str):
        self.builder.reset()
        self.builder.resource = DeviceDAO.BY_SERIAL_NUMBER.format(serial_number=serial_number)
        self.builder.method = HTTPMethod.GET
        request = self.builder.build()
        response = request.send()
        return DeviceHandler.handler_chain().handle_response(response)
    def get_by_management_ip_address(self,ip_address:str):
        self.builder.reset()
        self.builder.resource = DeviceDAO.BY_IP_ADDRESS.format(ip_address=ip_address)
        self.builder.method = HTTPMethod.GET
        request = self.builder.build()
        response = request.send()
        return DeviceHandler.handler_chain().handle_response(response)

class DeviceHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return ValidDeviceHandler(
            UnknownResourceHandler(
                InvalidRequestHandler()
            )
        )
        
class ValidDeviceHandler(DeviceHandler):
    def process(self,response):
        return DeviceFactory.fromDict(response.document['response'])
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=ValidDeviceConditioner()
        ).process(response)

class ValidDeviceConditioner(UniqueResourceConditioner):
    def condition(self,response):
        return super().condition(response) and 'managementIpAddress' in response.document['response']