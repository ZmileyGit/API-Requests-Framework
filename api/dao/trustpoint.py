from api.dao.base import DAO
from api.entities import HTTPMethod
from api.handlers import ResponseHandler,UnknownResourceHandler,InvalidRequestHandler
from api.conditioners import UniqueResourceConditioner,HTTPCodeConditioner
from api.model.trustpoint import TrustpointFactory

class TrustpointDAO(DAO):
    BY_SERIAL_NUMBER = '/api/v1/trust-point/serial-number/{serial_number}'
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
        response = request.send
        return response

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