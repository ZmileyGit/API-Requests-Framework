from api.conditioners import JSONConditioner
from api.responses import Response

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
        return super().condition(response) and (response.document['response']['errorCode'] == 'Bad request' or response.document['response']['errorCode'] == 'BadRequest') or response.reason == 'Bad request'

class UnknownResourceConditioner(APICEMErrorConditioner):
    def condition(self,response):
        return super().condition(response) and response.document['response']['errorCode'] == 'Not found'

class APICEMInvalidCredentialsConditioner(APICEMErrorConditioner):
    def condition(self,response):
        return super().condition(response) and response.document['response']['errorCode'] == 'INVALID_CREDENTIALS'