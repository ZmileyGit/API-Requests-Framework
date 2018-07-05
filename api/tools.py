from api.entities import Server,HTTPMethod,Operator,Comparator
from api.constants import Settings,Headers
import re


class RequestTools:
    @staticmethod
    def search_header(tuples:list,needle:str):
        result = []
        for tupl in tuples:
            if tupl[0] == needle:
                result.append(tupl[1])
        return result if len(result) > 0 else None
    @staticmethod
    def get_response_encoding(headers:list):
        content_type = RequestTools.search_header(headers,Headers.CONTENT_TYPE_HEADER)
        if content_type:
            for value in content_type:
                regex = re.search('charset=([A-Za-z0-9_-]+)',value)
                if regex:
                    return regex.group(1)
        return Settings.DEFAULT_ENCODING

from getpass import getpass

class Logger:
    ERROR_MESSAGE_TEMPLATE = "\n|{message}|\n"
    COMMON_MESSAGE_TEMPLATE = '+ {message}\n'
    _INSTANCE = None
    @staticmethod
    def instance():
        if(not Logger._INSTANCE):
            Logger._INSTANCE = Logger()
        return Logger._INSTANCE
    def _build_log(self,template:str,message:str,**kwargs):
        log = template.format(message=message,**kwargs)
        return log
    def log(self,log):
        print(log)
        return log
    def log_message(self,message,**kwargs):
        return self.log(self._build_log(Logger.COMMON_MESSAGE_TEMPLATE,message))
    def log_error(self,message,**kwargs):
        return self.log(self._build_log(Logger.ERROR_MESSAGE_TEMPLATE,message))

class Prompter:
    COMMON_PROMPT_TEMPLATE = "{message}: "
    PASSWORD_PROMPT = "Password"
    _INSTANCE = None
    @staticmethod
    def instance():
        if(not Prompter._INSTANCE):
            Prompter._INSTANCE = Prompter()
        return Prompter._INSTANCE
    def _build_prompt(self,template:str,message:str,**kwargs):
        prompt = template.format(message=message,**kwargs)
        return prompt
    def input(self,message,**kwargs):
        value = input(
            self._build_prompt(
                Prompter.COMMON_PROMPT_TEMPLATE,
                message,
                **kwargs
                )
            )
        return value
    def password(self,message=PASSWORD_PROMPT,**kwargs):
        password = getpass(
            self._build_prompt(
                Prompter.COMMON_PROMPT_TEMPLATE,
                message,
                **kwargs
            )
        )
        return password

class EnumBooleanOperations:
    @staticmethod
    def compare(value,against,op:Comparator):
        if op == Comparator.EQ:
            return value == against
        elif op == Comparator.NEQ:
            return value != against
        elif op == Comparator.GT:
            return value > against
        elif op == Comparator.LT:
            return value < against
        elif op == Comparator.GTE:
            return value >= against
        elif op == Comparator.LTE:
            return value <= against
        raise ValueError()
    @staticmethod
    def join(left,right,op:Operator):
        if op == Operator.AND:
            return left and right
        elif op == Operator.OR:
            return left or right
        raise ValueError()