from enum import Enum
from http.client import HTTPMessage
from urllib import parse

class Protocol(Enum):
    HTTP = "http"
    HTTPS = "https"

class HTTPMethod(Enum):
    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"
    def __str__(self):
        return self.value

class Operator(Enum):
    AND = 'AND'
    OR = 'OR'

class Comparator(Enum):
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    GT = 'GT'
    LTE = 'LTE'
    GTE = 'GTE'

class CertificateCheck(Enum):
    VALIDATE = "Validate Server's Certificate"
    IGNORE = "Ignore Server's Certificate"
    CUSTOM = 'Custom SSL Context'

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

class Headers:
    def __init__(self,headers:HTTPMessage):
        self.headers = headers
    @staticmethod
    def instance():
        return Headers(HTTPMessage())
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
