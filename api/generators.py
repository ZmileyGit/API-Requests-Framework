from abc import ABC,abstractmethod
from api.entities import Server

class TokenGenerator(ABC):
    def __init__(self,server:Server):
        self.server = server
    @abstractmethod
    def generate(self,**kwargs):
        pass
