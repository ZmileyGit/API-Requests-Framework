from api.validators import TokenValidator
from api.builders import JSONRequestBuilder
from api.entities import HTTPMethod
from api.constants import Headers
from api.apic_em.constants import APIC_EM_Settings
from api.apic_em.handlers import ValidationResponseHandler

class APIC_EMTokenValidator(TokenValidator):
    def _request(self,token,resource=APIC_EM_Settings.DEFAULT_TOKEN_VALIDATION_RESOURCE,ssl_context=None,certificate_check=None):
        request = JSONRequestBuilder(self.server)
        request.certificate_check = certificate_check if certificate_check else request.certificate_check
        request.context = ssl_context if ssl_context else request.context
        request.method = HTTPMethod.GET
        request.resource = resource
        request.headers.add_header(
            Headers.TOKEN_HEADER,
            token
        )
        request = request.build()
        return request
    def validate(self,token,**kwargs):
        response = self._request(token,**kwargs).send()
        return ValidationResponseHandler.handler_chain().handle_response(response)