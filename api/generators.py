from abc import ABC,abstractmethod
from api.builders import JSONRequestBuilder
from api.entities import Server,HTTPMethod
from api.constants import APIC_EM_Settings
from api.handlers import TokenResponseHandler

class TokenGenerator(ABC):
    def __init__(self,server:Server):
        self.server = server
    @abstractmethod
    def generate(self,**kwargs):
        pass

class APIC_EMTokenGenerator(TokenGenerator):
    def __init__(self,server,credentials):
        super().__init__(server)
        self.credentials = credentials
    def _request(self,ssl_context=None,certificate_check=None):
        request = JSONRequestBuilder(self.server)
        request.method = HTTPMethod.POST.value
        if certificate_check is not None:
            request.certificate_check = certificate_check
        request.resource = APIC_EM_Settings.TICKET_URI
        request.data = {
            "username" : self.credentials.username,
            "password" : self.credentials.password
        }
        request = request.build()
        request.context = ssl_context if ssl_context else request.context
        return request
    def generate(self,**kwargs):
        request = self._request(**kwargs)
        response = request.send()
        return TokenResponseHandler.handler_chain().handle_response(response)