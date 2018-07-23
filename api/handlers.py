from api.responses import Response
from api.errors import UnexpectedResponseError
from abc import ABC,abstractmethod

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
        elif default is not None:
            return default
        raise UnexpectedResponseError()