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
        self.progress = progress
        self.service = service
        self.start = start
        self.end = end

class TaskFactory:
    @staticmethod
    def fromDict(document):
        task_id = document['id']
        is_error = document['isError']
        progress = document['progress'] if 'progress' in document else None
        service = document['serviceType'] if 'serviceType' in document else None
        start = document['startTime']
        end = document['endTime'] if 'endTime' in document else None
        return Task(
            task_id,
            is_error,
            progress,
            service,
            start,
            end
        )