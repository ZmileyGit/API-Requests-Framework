from api.builders import RequestBuilder
from api.handlers import ResponseHandler,InvalidRequestHandler
from api.conditioners import APICEMConditioner,HTTPCodeConditioner

class DAO:
    def __init__(self,builder:RequestBuilder):
        self.builder = builder

class Task:
    def __init__(
        self,
        task_id,
        is_error,
        progress,
        service,
        start,
        end):
        self.id = task_id
        self.is_error = is_error
        self.process = progress
        self.service = service
        self.start = start
        self.end = end

class TaskHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        MonitorTaskHandler(
            InvalidRequestHandler()
        )

class MonitorTaskHandler(TaskHandler):
    def process(self,response):
        pass
    def is_processable(self,response):
        return HTTPCodeConditioner(
            202,
            next_conditioner=ValidTaskConditioner()
        ).process(response)

class ValidTaskConditioner(APICEMConditioner):
    def condition(self,response):
        return super().condition(response) and 'taskId' in response.document['response'] and 'url' in response.document['response']