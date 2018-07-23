class APIError(Exception):
    pass

class APIAuthenticationError(APIError):
    pass

class UnexpectedResponseError(APIError):
    pass

class InvalidRequestError(APIError):
    pass

class UnknownResourceError(APIError):
    pass

class TaskTimeoutError(APIError):
    pass