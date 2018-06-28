from abc import ABC,abstractmethod
from api.requests import Request,TextRequest,JSONRequest
from api.entities import Headers,Queries,Server,HTTPMethod
from api.constants import Settings,Headers as HeaderNames,ContentTypes,StringTemplates
from ssl import create_default_context,Purpose,CERT_NONE,CERT_REQUIRED
import json

class RequestBuilder(ABC):
    def __init__(self,server:Server):
        self.server = server
        self.resource = Settings.DEFAULT_RESOURCE_PATH
        self.headers = Headers.instance()
        self.queries = Queries.instance()
        self.method = HTTPMethod.GET.value
        self.data = None
        self.context = create_default_context(purpose=Purpose.SERVER_AUTH)
        self.certificate_check = True
    def reset(self):
        self.resource = Settings.DEFAULT_RESOURCE_PATH
        self.headers = Headers.instance()
        self.queries = Queries.instance()
        self.method = HTTPMethod.GET.value
        self.data = None
        self.context = create_default_context(purpose=Purpose.SERVER_AUTH)
        self.certificate_check = True
    def _prepare_context(self):
        if self.certificate_check is not None:
            self.context.check_hostname = self.certificate_check
            self.context.verify_mode = CERT_REQUIRED if self.certificate_check else CERT_NONE
    def season(self):
        self._prepare_context()
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
    def __init__(self,server:Server):
        super().__init__(server)
        self.encoding = Settings.DEFAULT_ENCODING
    def reset(self):
        super().reset()
        self.encoding = Settings.DEFAULT_ENCODING
    def content_type(self):
        return ContentTypes.PLAINTEXT_CONTENT_TYPE
    def season(self):
        super().season()
        self.headers.add_header(
            HeaderNames.ACCEPT_ENCODING_HEADER,
            self.encoding
        )
        self.headers.add_header(
            HeaderNames.ACCEPT_HEADER,
            self.content_type()
        )
        self.headers.add_header(
            HeaderNames.CONTENT_TYPE_HEADER,
            StringTemplates.CONTENT_TYPE_TEMPLATE.format(self.content_type(),self.encoding)
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
    def content_type(self):
        return ContentTypes.JSON_CONTENT_TYPE
    def season(self):
        super().season()
        if self.data:
            encoding = self.encoding
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