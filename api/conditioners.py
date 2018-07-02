from api.entities import Operator,Comparator
from api.tools import EnumBooleanOperations
from api.responses import Response
from abc import ABC,abstractmethod

class Conditioner(ABC):
    def __init__(self,next_conditioner=None,operator:Operator=Operator.AND):
        self.next_conditioner = None
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

class APICEMConditioner(JSONConditioner):
    def condition(self,response:Response):
        return super().condition(response) and 'response' in response.document

class APICEMTokenConditioner(APICEMConditioner):
    def condition(self,response:Response):
        return super().condition(response) and 'serviceTicket' in response.document['response']

class UniqueResourceConditioner(APICEMConditioner):
    def condition(self,response):
        return super().condition(response) and 'id' in response.document['response']

class APICEMErrorConditioner(APICEMConditioner):
    def condition(self,response):
        return super().condition(response) and 'errorCode' in response.document['response']

class APICEMInvalidRequestConditioner(APICEMErrorConditioner):
    def condition(self,response):
        return super().condition(response) and response.document['response']['errorCode'] == 'Bad request'

class UnknownResourceConditioner(APICEMErrorConditioner):
    def condition(self,response):
        return super().condition(response) and response.document['response']['errorCode'] == 'Not found'

class APICEMInvalidCredentialsConditioner(APICEMErrorConditioner):
    def condition(self,response):
        return super().condition(response) and response.document['response']['errorCode'] == 'INVALID_CREDENTIALS'

