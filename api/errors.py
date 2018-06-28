class APIError(Exception):
    pass

class APIAuthenticationError(APIError):
    pass

class UnexpectedResponseError(APIError):
    pass