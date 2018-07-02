from api.errors import UnexpectedResponseError,APIAuthenticationError
from api.responses import Response
from api.tools import EnumBooleanOperations
from api.entities import Comparator,Operator
from api.conditioners import HTTPCodeConditioner,APICEMTokenConditioner,APICEMInvalidCredentialsConditioner
from api.conditioners import APICEMInvalidRequestConditioner
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
        elif default is not None:
            return default
        raise UnexpectedResponseError()

class InvalidRequestHandler(ResponseHandler):
    def is_processable(self,response):
        return HTTPCodeConditioner(400,next_conditioner=APICEMInvalidRequestConditioner()).process(response)

class TokenResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return InvalidCredentialsHandler(
            SuccessfulTokenRetrievalHandler()
        )

class InvalidCredentialsHandler(TokenResponseHandler):
    def process(self,response):
        raise APIAuthenticationError()
    def is_processable(self,response):
        return HTTPCodeConditioner(
            401,
            next_conditioner=APICEMInvalidCredentialsConditioner()
        ).process(response)

class SuccessfulTokenRetrievalHandler(TokenResponseHandler):
    def process(self,response):
        return response.document['response']['serviceTicket']
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=APICEMTokenConditioner()
        ).process(response)

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
        return HTTPCodeConditioner(200).process(response)

class UnsuccessfulValidationHandler(ValidationResponseHandler):
    def process(self,response):
        return False
    def is_processable(self,response):
        return HTTPCodeConditioner(200,comparator=Comparator.NEQ).process(response)