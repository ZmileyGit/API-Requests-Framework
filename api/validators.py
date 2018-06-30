from abc import ABC,abstractmethod
from api.builders import JSONRequestBuilder
from api.entities import Server,HTTPMethod
from api.constants import APIC_EM_Settings,Headers
from api.handlers import ValidationResponseHandler

class TokenValidator(ABC):
    def __init__(self,server:Server):
        self.server = server
    @abstractmethod
    def validate(self,token,**kwargs):
        pass

class APIC_EMTokenValidator(TokenValidator):
    def _request(self,token,resource=APIC_EM_Settings.DEFAULT_TOKEN_VALIDATION_RESOURCE,ssl_context=None,certificate_check=None):
        request = JSONRequestBuilder(self.server)
        if certificate_check is not None:
            request.certificate_check = certificate_check
        request.method = HTTPMethod.GET.value
        request.resource = resource
        request.headers.add_header(
            Headers.TOKEN_HEADER,
            token
        )
        request = request.build()
        request.context = ssl_context if ssl_context else request.context
        return request
    def validate(self,token,**kwargs):
        response = self._request(token,**kwargs).send()
        return ValidationResponseHandler.handler_chain().handle_response(response)