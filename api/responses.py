class Response:
    def __init__(self,code,reason,headers,data=None):
        self.code = code
        self.reason = reason
        self.headers = headers
        self.data = data

class TextResponse(Response):
    def __init__(self,code,reason,headers,data=None,text=None):
        super().__init__(code,reason,headers,data)
        self.text = text

class JSONResponse(TextResponse):
    def __init__(self,code,reason,headers,data=None,text=None,document=None):
        super().__init__(code,reason,headers,data,text)
        self.document = document