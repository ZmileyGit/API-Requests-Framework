from api.decorators import CredentialsDecorator
from api.builders import RequestBuilder
from api.entities import Credentials,CertificateCheck
from api.constants import Headers as HeaderNames
from api.apic_em.validators import APIC_EMTokenValidator
from api.apic_em.generators import APIC_EMTokenGenerator

class APIC_EMDecorator(CredentialsDecorator):
    def __init__(self,builder:RequestBuilder,credentials:Credentials):
        super().__init__(builder,credentials)
        self.token = None
    def verify_token(self):
        valid_token = False
        if self.token:
            valid_token = APIC_EMTokenValidator(self.server).validate(self.token,ssl_context=self.context,certificate_check=CertificateCheck.CUSTOM)
        if not valid_token:
            self.token = APIC_EMTokenGenerator(self.server,self.credentials).generate(ssl_context=self.context,certificate_check=CertificateCheck.CUSTOM)
    def authentication(self):
        self.verify_token()
        self.headers.add_header(
            HeaderNames.TOKEN_HEADER,
            self.token
        )
