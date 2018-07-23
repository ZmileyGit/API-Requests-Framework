from api.constants import StringTemplates,Headers as HeaderNames,Settings
from api.builders import RequestBuilder
from api.entities import Credentials,Server,Headers,Queries,CertificateCheck
from abc import abstractmethod
import base64


class RequestBuilderDecorator(RequestBuilder):
    def __init__(self,builder:RequestBuilder):
        self.builder = builder
    def reset(self):
        self.builder.reset()
    @property
    def method(self):
        return self.builder.method
    @method.setter
    def method(self,method:str):
        self.builder.method = method
    @property
    def server(self):
        return self.builder.server
    @server.setter
    def server(self,server:Server):
        self.builder.server = server
    @property
    def resource(self):
        return self.builder.resource
    @resource.setter
    def resource(self,resource:str):
        self.builder.resource = resource
    @property
    def headers(self):
        return self.builder.headers
    @headers.setter
    def headers(self,headers:Headers):
        self.builder.headers = headers
    @property
    def queries(self):
        return self.builder.queries
    @queries.setter
    def queries(self,queries:Queries):
        self.builder.queries = queries
    @property
    def data(self):
        return self.builder.data
    @data.setter
    def data(self,data):
        self.builder.data = data
    @property
    def context(self):
        return self.builder.context
    @context.setter
    def context(self,context):
        self.builder.context = context
    @property
    def certificate_check(self):
        return self.builder.certificate_check
    @certificate_check.setter
    def certificate_check(self,check):
        self.builder.certificate_check = check
    def request(self):
        return self.builder.request()

class CredentialsDecorator(RequestBuilderDecorator):
    def __init__(self,builder:RequestBuilder,credentials:Credentials):
        super().__init__(builder)
        self.credentials = credentials
    @abstractmethod
    def authentication(self):
        pass
    def season(self):
        self.builder.season()
        self.authentication()

class BasicAuthDecorator(CredentialsDecorator):
    def authentication(self):
        credentials = StringTemplates.BASIC_AUTH_USRPASSWD.format(
            self.credentials.username,
            self.credentials.password
        )
        encoding = Settings.DEFAULT_HEADER_ENCODING
        credentials = base64.b64encode(credentials.encode(encoding))
        self.headers.add_header(
            HeaderNames.AUTH_HEADER,
            StringTemplates.BASIC_AUTH_TEMPLATE.format(credentials.decode(encoding))
        )

class CustomAcceptDecorator(RequestBuilderDecorator):
    def __init__(self,builder:RequestBuilder,accept:str):
        super().__init__(builder)
        self.accept = accept
    def season(self):
        self.builder.season()
        self.headers.add_header(
            HeaderNames.ACCEPT_HEADER,
            self.accept
        )

class CustomContentTypeDecorator(RequestBuilderDecorator):
    def __init__(self,builder:RequestBuilder,content_type:str):
        super().__init__(builder)
        self.content_type = content_type
    def season(self):
        self.builder.season()
        self.headers.add_header(
            HeaderNames.CONTENT_TYPE_HEADER,
            self.content_type
        )