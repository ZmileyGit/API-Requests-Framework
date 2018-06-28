from ssl import create_default_context,CERT_NONE,Purpose,SSLContext,CERT_REQUIRED
from urllib import parse,request as api,error
from http import client
from abc import ABC,abstractmethod,ABCMeta
from enum import Enum
import base64
import json
import time
import re

class Protocol(Enum):
    HTTP = "http"
    HTTPS = "https"

class HTTPMethod(Enum):
    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"

class Server:
    def __init__(self,protocol:str,ip:str,port:int):
        self.protocol = protocol
        self.ip = ip
        self.port = port

class Credentials:
    def __init__(self,username:str,password:str):
        self.username = username
        self.password = password

class HTTPSServer(Server):
    PROTOCOL = Protocol.HTTPS.value
    def __init__(self,ip:str,port:int=443):
        super().__init__(self.PROTOCOL,ip,port)

class HTTPServer(Server):
    PROTOCOL = Protocol.HTTP.value
    def __init__(self,ip:str,port:int=80):
        super().__init__(self.PROTOCOL,ip,port)

class RequestTools:
    @staticmethod
    def search_header(tuples:list,needle:str):
        result = []
        for tupl in tuples:
            if tupl[0] == needle:
                result.append(tupl[1])
        return result if len(result) > 0 else None
    @staticmethod
    def get_response_encoding(headers:list):
        content_type = RequestTools.search_header(headers,TextRequestBuilder.CONTENT_TYPE_HEADER)
        if content_type:
            for value in content_type:
                regex = re.search('charset=([A-Za-z0-9_-]+)',value)
                if regex:
                    return regex.group(1)
        return TextRequestBuilder.DEFAULT_ENCODING
class Request:
    def __init__(self,server:Server,resource:str,method:str,headers,queries,data,context:SSLContext):
        self.server = server
        self.resource = resource
        self.method =  method
        self.headers = headers
        self.queries = queries
        self.data = data
        self.context = context
    @property
    def url(self):
        template = "{0}://{1}:{2}{3}" if self.queries.is_empty() else "{0}://{1}:{2}{3}?{4}"
        return template.format(
            self.server.protocol,
            self.server.ip,
            self.server.port,
            self.resource,
            self.queries.as_url_query()
        )
    @property
    def raw_request(self):
        return api.Request(
            self.url,
            data=self.data,
            headers=self.headers.as_dict(),
            method=self.method
        )
    def success(self,data:client.HTTPResponse) -> dict:
        return {
            'code' : data.status,
            'reason' : data.reason,
            'headers' : data.getheaders(),
            'data' : data.read()
        }
    def error(self,err:error.HTTPError) -> dict:
        return {
            'code' : err.code,
            'reason' : err.reason,
            'headers' : err.headers.items(),
            'data' : err.read()
        }
    def create_response(self,response_data:dict):
        return Response(**response_data)
    def send(self):
        response_data = None
        try:
            api_response = api.urlopen(
                self.raw_request,
                context=self.context
            )
            with api_response as data:
                response_data = self.success(data)
        except error.HTTPError as http_err:
            response_data = self.error(http_err)
        return self.create_response(response_data) if response_data else None

class TextRequest(Request):
    def __init__(self,server:Server,resource:str,method:str,headers,queries,data,context:SSLContext):
        super().__init__(server,resource,method,headers,queries,data,context)
    def success(self,data):
        base = super().success(data)
        encoding = RequestTools.get_response_encoding(base['headers'])
        text = None
        if base['data']:
            try:
                text = base['data'].decode(encoding)
            except UnicodeError:
                text = None
        base['text'] = text
        return base
    def error(self,err):
        return self.success(err)
    def create_response(self,response_data):
        return TextResponse(**response_data)

class JSONRequest(TextRequest):
    def __init__(self,server:Server,resource:str,method:str,headers,queries,data,context:SSLContext):
        super().__init__(server,resource,method,headers,queries,data,context)
    def success(self,data):
        base = super().success(data)
        document = None
        if base['text']:
            try:
                document = json.JSONDecoder().decode(base['text'])
            except json.JSONDecodeError:
                document = None
        base['document'] = document
        return base
    def error(self,err):
        return self.success(err)
    def create_response(self,response_data):
        return JSONResponse(**response_data)

class Response:
    def __init__(self,code,reason,headers,data=None):
        self.code = code
        self.reason = reason
        self.headers = headers
        self.data = data

class TextResponse(Response):
    def __init__(self,code,reason,headers,data=None,text=None):
        super().__init__(code,reason,headers,data)
        self.text = text

class JSONResponse(TextResponse):
    def __init__(self,code,reason,headers,data=None,text=None,document=None):
        super().__init__(code,reason,headers,data,text)
        self.document = document

class Headers:
    def __init__(self,headers:client.HTTPMessage):
        self.headers = headers
    @staticmethod
    def instance():
        return Headers(client.HTTPMessage())
    def add_header(self,key:str,value:str,replace=True):
        if replace:
            del self.headers[key]
        self.headers[key] = value
        return (key,self.get(key))
    def get_header(self,key):
        return self.headers[key]
    def get(self,key):
        return self.headers.get_all(key)
    def delete_header(self,key:str):
        values = self.get(key)
        if values:
            header = (key,values)
            del self.headers[key]
            return header
        return None
    def as_dict(self):
        headers = {}
        keys = self.headers.keys()
        for key in keys:
            headers[key] = ','.join(self.get(key))
        return headers

class Queries:
    def __init__(self,queries:list):
        self.queries = queries
    @staticmethod
    def instance():
        return Queries([])
    def add_query(self,key:str,value:str):
        self.queries.append((key,value))
    def search_query(self,key:str,value:str=None):
        positions = []
        for count,query in enumerate(self.queries):
            if key == query[0]:
                if value and value == query[1]:
                    positions.append(count)
                else:
                    positions.append(count)
        return positions
    def get_query(self,key:str,value:str=None):
        positions = self.search_query(key,value)
        return [self.queries[count] for count in positions]
    def delete_query(self,key:str,value:str=None):
        positions = self.search_query(key,value)
        deleted = []
        for count,position in enumerate(positions):
            current = position-count
            deleted.append(self.queries[current])
            del self.queries[current]
        return deleted
    def is_empty(self):
        return len(self.queries) == 0
    def as_url_query(self):
        return parse.urlencode(
            self.queries,
            doseq=True
        )


class RequestBuilder(ABC):
    DEFAULT_ENCODING = 'utf-8'
    ENCODING_HEADER = 'Accept-Charset'
    def __init__(self,server:Server):
        self.server = server
        self.resource = "/"
        self.headers = Headers.instance()
        self.queries = Queries.instance()
        self.method = HTTPMethod.GET.value
        self.data = None
        self.set_encoding(RequestBuilder.DEFAULT_ENCODING)
        self.context = create_default_context(purpose=Purpose.SERVER_AUTH)
        self.certificate_check = True
    def reset(self):
        self.resource = "/"
        self.headers = Headers.instance()
        self.queries = Queries.instance()
        self.method = HTTPMethod.GET.value
        self.data = None
        self.set_encoding(RequestBuilder.DEFAULT_ENCODING)
        self.context = create_default_context(purpose=Purpose.SERVER_AUTH)
        self.certificate_check = True
    def get_encoding(self):
        encoding = self.headers.get_header(RequestBuilder.ENCODING_HEADER)
        return encoding if encoding else RequestBuilder.DEFAULT_ENCODING
    def set_encoding(self,encoding:str):
        self.headers.add_header(RequestBuilder.ENCODING_HEADER,encoding)
    @property
    def certificate_check(self):
        return False if self.context.verify_mode == CERT_NONE else True
    @certificate_check.setter
    def certificate_check(self,check:bool):
        self.context.check_hostname = check
        self.context.verify_mode = CERT_REQUIRED if check else CERT_NONE
    def season(self):
        self.headers.add_header(RequestBuilder.ENCODING_HEADER,self.get_encoding())
    @abstractmethod
    def request(self):
        pass    
    def build(self):
        self.season()
        return self.request()

class GenericRequestBuilder(RequestBuilder):
    def request(self):
        return Request(
            self.server,
            self.resource,
            self.method,
            self.headers,
            self.queries,
            self.data,
            self.context    
        )

class TextRequestBuilder(RequestBuilder):
    ACCEPT_HEADER = "Accept"
    CONTENT_TYPE_HEADER = "Content-Type"
    CONTENT_TYPE = "text/plain"
    CONTENT_TYPE_TEMPLATE = "{0};charset={1}"
    def content_type(self):
        return TextRequestBuilder.CONTENT_TYPE
    def season(self):
        self.headers.add_header(
            TextRequestBuilder.ACCEPT_HEADER,
            self.content_type()
        )
        self.headers.add_header(
            TextRequestBuilder.CONTENT_TYPE_HEADER,
            TextRequestBuilder.CONTENT_TYPE_TEMPLATE.format(self.content_type(),self.get_encoding())
        )
    def request(self):
        return TextRequest(
            self.server,
            self.resource,
            self.method,
            self.headers,
            self.queries,
            self.data,
            self.context    
        )
    
class JSONRequestBuilder(TextRequestBuilder):
    CONTENT_TYPE = "application/json"
    def content_type(self):
        return JSONRequestBuilder.CONTENT_TYPE
    def season(self):
        super().season()
        if self.data:
            encoding = self.get_encoding()
            self.data = json.JSONEncoder().encode(self.data).encode(encoding)
    def request(self):
        return JSONRequest(
            self.server,
            self.resource,
            self.method,
            self.headers,
            self.queries,
            self.data,
            self.context
        )

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
    def get_encoding(self):
        return self.builder.get_encoding()
    def set_encoding(self,encoding:str):
        self.builder.set_encoding(encoding)
    @property
    def certificate_check(self):
        return self.builder.certificate_check
    @certificate_check.setter
    def certificate_check(self,check):
        self.builder.certificate_check = check
    def request(self):
        return self.builder.request()

class CredentialsDecorator(RequestBuilderDecorator):
    AUTH_HEADER = "Authorization"
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
    BASIC_AUTH_TEMPLATE = "Basic {0}"
    BASIC_AUTH_USRPASSWD = "{0}:{1}"
    def authentication(self):
        credentials = BasicAuthDecorator.BASIC_AUTH_USRPASSWD.format(
            self.credentials.username,
            self.credentials.password
        )
        encoding = self.get_encoding()
        credentials = base64.b64encode(credentials.encode(encoding))
        self.headers.add_header(
            CredentialsDecorator.AUTH_HEADER,
            BasicAuthDecorator.BASIC_AUTH_TEMPLATE.format(credentials.decode(encoding))
        )

class APIC_EMDecorator(CredentialsDecorator):
    TOKEN_HEADER = "X-Auth-Token"
    def __init__(self,builder:RequestBuilder,credentials:Credentials):
        super().__init__(builder,credentials)
        self.token = None
    def verify_token(self):
        valid_token = False
        if self.token:
            valid_token = APIC_EMTokenValidator(self.server).validate(self.token,ssl_context=self.context)
        if not valid_token:
            self.token = APIC_EMTokenGenerator(self.server,self.credentials).generate(ssl_context=self.context)
    def authentication(self):
        self.verify_token()
        self.headers.add_header(
            APIC_EMDecorator.TOKEN_HEADER,
            self.token
        )


class TokenValidator(ABC):
    def __init__(self,server:Server):
        self.server = server
    @abstractmethod
    def validate(self,token,**kwargs):
        pass

class APIC_EMTokenValidator(TokenValidator):
    DEFAULT_VALIDATION_RESOURCE = "/api/v1/ticket/attribute/idletimeout"
    def _request(self,token,resource=DEFAULT_VALIDATION_RESOURCE,ssl_context=None):
        request = JSONRequestBuilder(self.server)
        if ssl_context:
            request.context = ssl_context
        request.method = HTTPMethod.GET.value
        request.resource = resource
        request.headers.add_header(
            APIC_EMDecorator.TOKEN_HEADER,
            token
        )
        request = request.build()
        return request
    def validate(self,token,**kwargs):
        response = self._request(token,**kwargs).send()
        return ValidationResponseHandler.handler_chain().handle_response(response)

class TokenGenerator(ABC):
    def __init__(self,server:Server):
        self.server = server
    @abstractmethod
    def generate(self,**kwargs):
        pass

class APIC_EMTokenGenerator(TokenGenerator):
    TICKET_URI = "/api/v1/ticket"
    def __init__(self,server,credentials):
        super().__init__(server)
        self.credentials = credentials
    def _request(self,ssl_context=None):
        request = JSONRequestBuilder(self.server)
        request.method = HTTPMethod.POST.value
        if ssl_context:
            request.context = ssl_context
        request.resource = APIC_EMTokenGenerator.TICKET_URI
        request.data = {
            "username" : self.credentials.username,
            "password" : self.credentials.password
        }
        request = request.build()
        return request
    def generate(self,**kwargs):
        response = self._request(**kwargs).send()
        return TokenResponseHandler.handler_chain().handle_response(response)

class CustomAcceptDecorator(RequestBuilderDecorator):
    def __init__(self,builder:RequestBuilder,accept:str):
        super().__init__(builder)
        self.accept = accept
    def season(self):
        self.builder.season()
        self.headers.add_header(TextRequestBuilder.ACCEPT_HEADER,self.accept)

class CustomContentTypeDecorator(RequestBuilderDecorator):
    def __init__(self,builder:RequestBuilder,content_type:str):
        super().__init__(builder)
        self.content_type = content_type
    def season(self):
        self.builder.season()
        self.headers.add_header(
            TextRequestBuilder.CONTENT_TYPE_HEADER,
            TextRequestBuilder.CONTENT_TYPE_TEMPLATE.format(self.content_type,self.get_encoding())
        )

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

class APIError(Exception):
    pass

class APIAuthenticationError(APIError):
    pass

class UnexpectedResponseError(APIError):
    pass