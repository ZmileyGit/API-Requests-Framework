from api.builders import RequestBuilder

class DAO:
    def __init__(self,builder:RequestBuilder):
        self.builder = builder