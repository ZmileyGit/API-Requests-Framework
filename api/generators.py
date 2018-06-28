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
    def _request(self,ssl_context=None):
        request = JSONRequestBuilder(self.server)
        request.method = HTTPMethod.POST.value
        if ssl_context:
            request.context = ssl_context
            request.certificate_check = None
        request.resource = APIC_EM_Settings.TICKET_URI
        request.data = {
            "username" : self.credentials.username,
            "password" : self.credentials.password
        }
        request = request.build()
        return request
    def generate(self,**kwargs):
        request = self._request(**kwargs)
        print(request.url)
        print(request.headers.as_dict())
        print(request.method)
        response = request.send()
        return TokenResponseHandler.handler_chain().handle_response(response)