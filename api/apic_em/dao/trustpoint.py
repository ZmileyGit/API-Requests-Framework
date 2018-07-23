from api.dao.base import DAO
from api.entities import HTTPMethod
from api.conditioners import HTTPCodeConditioner
from api.apic_em.handlers import ResponseHandler,UnknownResourceHandler,InvalidRequestHandler
from api.apic_em.conditioners import UniqueResourceConditioner
from api.apic_em.model.trustpoint import TrustpointFactory
from api.apic_em.tasks import MonitorTaskHandler

class TrustpointDAO(DAO):
    BY_SERIAL_NUMBER = '/api/v1/trust-point/serial-number/{serial_number}'
    MAIN = '/api/v1/trust-point'
    def get_by_serial_number(self,serial_number:str):
        self.builder.reset()
        self.builder.resource = TrustpointDAO.BY_SERIAL_NUMBER.format(serial_number=serial_number)
        self.builder.method = HTTPMethod.GET
        request = self.builder.build()
        response = request.send()
        return ValidTrustpointHandler.handler_chain().handle_response(response)
    def delete_by_serial_number(self,serial_number:str):
        self.builder.reset()
        self.builder.resource = TrustpointDAO.BY_SERIAL_NUMBER.format(serial_number=serial_number)
        self.builder.method = HTTPMethod.DELETE
        request = self.builder.build()
        response = request.send()
        return MonitorTaskHandler(self.builder).handle_response(response)
    def create_trustpoint(
        self,
        hostname:str,
        serial_number:str,
        platform_id:str,
        trust_profile:str=None,
        controller:str=None
    ):
        self.builder.reset()
        self.builder.resource = TrustpointDAO.MAIN
        self.builder.method = HTTPMethod.POST
        self.builder.data = {
            "entityName": hostname,
            "serialNumber": serial_number,
            "platformId": platform_id
        }
        if trust_profile:
            self.builder.data['trustProfileName'] = trust_profile
        if controller:
            self.builder.data['controllerIpAddress'] = controller
        request = self.builder.build()
        response = request.send()
        return MonitorTaskHandler(self.builder).handle_response(response)

class TrustpointHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return ValidTrustpointHandler(
            UnknownResourceHandler(
                InvalidRequestHandler()
            )
        )

class ValidTrustpointHandler(TrustpointHandler):
    def process(self,response):
        return TrustpointFactory.fromDict(response.document['response'])
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=ValidTrustpointConditioner()
        ).process(response)

class ValidTrustpointConditioner(UniqueResourceConditioner):
    def condition(self,response):
        return super().condition(response) and 'trustProfileName' in response.document['response'] and 'entityName' in response.document['response'] and 'serialNumber' in response.document['response']