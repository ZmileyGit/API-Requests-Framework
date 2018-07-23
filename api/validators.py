from abc import ABC,abstractmethod
from api.entities import Server

class TokenValidator(ABC):
    def __init__(self,server:Server):
        self.server = server
    @abstractmethod
    def validate(self,token,**kwargs):
        pass