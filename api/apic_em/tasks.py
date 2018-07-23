from api.handlers import ResponseHandler
from api.conditioners import HTTPCodeConditioner
from api.builders import RequestBuilder
from api.entities import HTTPMethod
from api.errors import TaskTimeoutError
from api.apic_em.model.task import TaskFactory,Task
from api.apic_em.conditioners import APICEMConditioner,UniqueResourceConditioner
from api.apic_em.constants import APIC_EM_Settings
from time import sleep

class ValidTaskHandler(ResponseHandler):
    def process(self,response):
        return TaskFactory.fromDict(response.document['response'])     
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=ValidTaskConditioner()
        ).process(response)

class TaskHandler(ResponseHandler):
    BY_TASK_ID = '/api/v1/task/{task_id}'
    def __init__(self,builder:RequestBuilder,next_handler:ResponseHandler=None):
        super().__init__(next_handler)
        self.builder = builder
    def check_task(self,task_id):
        self.builder.reset()
        self.builder.resource = TaskHandler.BY_TASK_ID.format(task_id=task_id)
        self.builder.method = HTTPMethod.GET
        request = self.builder.build()
        return request.send()

class MonitorTaskHandler(TaskHandler):
    def process(self,response):
        data = response.document['response']
        task = self.check_task(data['taskId'])
        self.prepare_monitoring(task)
        return self.start_monitoring(task)
    def prepare_monitoring(self,response):
        pass
    def start_monitoring(self,response):
        return TaskProgressHandler(self.builder).handle_response(response)
    def is_processable(self,response):
        return HTTPCodeConditioner(
            202,
            next_conditioner=StartTaskConditioner()
        ).process(response)

class StartTaskConditioner(APICEMConditioner):
    def condition(self,response):
        return super().condition(response) and 'taskId' in response.document['response'] and 'url' in response.document['response']

class ValidTaskConditioner(UniqueResourceConditioner):
    def condition(self,response):
        return super().condition(response) and 'isError' in response.document['response']

class TaskMonitoringHandler(TaskHandler):
    pass

class TaskProgressHandler(TaskMonitoringHandler):
    def process(self,response):
        total = APIC_EM_Settings.TASK_TIMEOUT
        while total > 0 :
            task = ValidTaskHandler().handle_response(response)
            self.progress(task,total)
            if task.end:
                return task
            sleep(APIC_EM_Settings.TASK_POLLING_INTERVAL)
            response = self.check_task(task.id)
            total -= APIC_EM_Settings.TASK_POLLING_INTERVAL
        raise TaskTimeoutError()
    def progress(self,task:Task,total):
        pass
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=ValidTaskConditioner()
        ).process(response)