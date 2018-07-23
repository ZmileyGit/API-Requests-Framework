from api.handlers import ResponseHandler
from api.errors import InvalidRequestError,UnknownResourceError
from api.errors import APIAuthenticationError
from api.conditioners import HTTPCodeConditioner
from api.entities import Comparator
from api.apic_em.conditioners import APICEMInvalidRequestConditioner,UnknownResourceConditioner
from api.apic_em.conditioners import UniqueResourceConditioner,APICEMTokenConditioner
from api.apic_em.conditioners import APICEMInvalidCredentialsConditioner

class InvalidRequestHandler(ResponseHandler):
    def process(self,response):
        raise InvalidRequestError()
    def is_processable(self,response):
        return HTTPCodeConditioner(
            400,
            next_conditioner=APICEMInvalidRequestConditioner()
        ).process(response)

class UnknownResourceHandler(ResponseHandler):
    def process(self,response):
        raise UnknownResourceError()
    def is_processable(self,response):
        return HTTPCodeConditioner(
            404,
            next_conditioner=UnknownResourceConditioner()
        ).process(response)

class UniqueResourceHandler(ResponseHandler):
    def process(self,response):
        return response.document['response']['id']
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=UniqueResourceConditioner()
        ).process(response)

class TokenResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return InvalidCredentialsHandler(
            InvalidRequestHandler(
                SuccessfulTokenRetrievalHandler()
            )
        )

class SuccessfulTokenRetrievalHandler(TokenResponseHandler):
    def process(self,response):
        return response.document['response']['serviceTicket']
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=APICEMTokenConditioner()
        ).process(response)

class InvalidCredentialsHandler(TokenResponseHandler):
    def process(self,response):
        raise APIAuthenticationError()
    def is_processable(self,response):
        return HTTPCodeConditioner(
            401,
            next_conditioner=APICEMInvalidCredentialsConditioner()
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