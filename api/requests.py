from api.entities import Server
from api.tools import RequestTools
from api.responses import Response,TextResponse,JSONResponse
from ssl import SSLContext
from urllib import request
from urllib.error import HTTPError
from http.client import HTTPMessage,HTTPResponse
import json

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
        return request.Request(
            self.url,
            data=self.data,
            headers=self.headers.as_dict(),
            method=self.method
        )
    def success(self,data:HTTPResponse) -> dict:
        return {
            'code' : data.status,
            'reason' : data.reason,
            'headers' : data.getheaders(),
            'data' : data.read()
        }
    def error(self,err:HTTPError) -> dict:
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
            api_response = request.urlopen(
                self.raw_request,
                context=self.context
            )
            with api_response as data:
                response_data = self.success(data)
        except HTTPError as http_err:
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