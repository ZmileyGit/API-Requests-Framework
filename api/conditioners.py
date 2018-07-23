from api.entities import Operator,Comparator
from api.tools import EnumBooleanOperations
from api.responses import Response
from abc import ABC,abstractmethod

class Conditioner(ABC):
    def __init__(self,next_conditioner=None,operator:Operator=Operator.AND):
        self.next_conditioner = next_conditioner
        self.operator = operator
    def process(self,response):
        result = self.condition(response)
        if self.next_conditioner:
            result = EnumBooleanOperations.join(
                result,
                self.next_conditioner.process(response),
                self.operator
            )
        return result
    @abstractmethod
    def condition(self,response:Response):
        pass

class ComparingConditioner(Conditioner):
    def __init__(self,next_conditioner=None,operator=Operator.AND,comparator=Comparator.EQ):
        super().__init__(next_conditioner=next_conditioner,operator=operator)
        self.comparator = comparator

class HTTPCodeConditioner(ComparingConditioner):
    def __init__(self,code:int,next_conditioner=None,operator=Operator.AND,comparator=Comparator.EQ):
        super().__init__(next_conditioner=next_conditioner,operator=operator,comparator=comparator)
        self.code = code
    def condition(self,response:Response):
        return EnumBooleanOperations.compare(response.code,self.code,self.comparator)

class JSONConditioner(Conditioner):
    def condition(self,response:Response):
        return response.document