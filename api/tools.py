from api.handlers import ValidationResponseHandler,TokenResponseHandler
from api.entities import Server,HTTPMethod
from api.constants import Settings,Headers
import re


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
        content_type = RequestTools.search_header(headers,Headers.CONTENT_TYPE_HEADER)
        if content_type:
            for value in content_type:
                regex = re.search('charset=([A-Za-z0-9_-]+)',value)
                if regex:
                    return regex.group(1)
        return Settings.DEFAULT_ENCODING