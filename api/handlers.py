from api.errors import UnexpectedResponseError,APIAuthenticationError
from api.responses import Response
from abc import ABC,abstractmethod

class ResponseHandler(ABC):
    def __init__(self,next_handler=None):
        self.next_handler = next_handler
    @abstractmethod
    def process(self,response:Response):
        pass
    @abstractmethod
    def is_processable(self,response:Response):
        pass
    def handle_response(self,response:Response,default=None):
        if self.is_processable(response):
            return self.process(response)
        elif self.next_handler:
            return self.next_handler.handle_response(response,default)
        elif default:
            return default
        raise UnexpectedResponseError()

class TokenResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return SuccessfulTokenRetrievalHandler(
            InvalidCredentialsHandler())

class InvalidCredentialsHandler(TokenResponseHandler):
    def process(self,response):
        raise APIAuthenticationError()
    def is_processable(self,response):
        return response.code == 401 and response.document and 'response' in response.document and 'errorCode' in response.document['response']

class SuccessfulTokenRetrievalHandler(TokenResponseHandler):
    def process(self,response):
        return response.document['response']['serviceTicket']
    def is_processable(self,response):
        return response.code == 200 and response.document and 'response' in response.document and 'serviceTicket' in response.document['response']

class ValidationResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return SuccesfulValidationHandler(
            UnsuccessfulValidationHandler()
        )

class SuccesfulValidationHandler(ValidationResponseHandler):
    def process(self,response):
        return True
    def is_processable(self,response):
        return response.code == 200

class UnsuccessfulValidationHandler(ValidationResponseHandler):
    def process(self,response):
        return False
    def is_processable(self,response):
        return response.code != 200