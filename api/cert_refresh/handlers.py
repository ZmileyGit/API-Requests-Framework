from api.handlers import ResponseHandler,InvalidRequestHandler,UnknownResourceHandler,UniqueResourceHandler
from api.errors import UnexpectedResponseError,InvalidRequestError,UnknownResourceError
from api.cert_refresh.conditioners import DeviceSNConditioner
from api.conditioners import HTTPCodeConditioner,UnknownResourceConditioner,UniqueResourceConditioner
from api.cert_refresh.models import Device


class DeviceResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return ValidDeviceHandler(
            InvalidRequestHandler(
                UnknownResourceHandler()
            )
        )

class ValidDeviceHandler(DeviceResponseHandler):
    def process(self,response):
        raw_device = response.document['response']
        if 'serialNumber' in raw_device and 'hostname' in raw_device and 'platformId' in raw_device and 'managementIpAddress' in raw_device:
            return Device(
                raw_device['serialNumber'],
                raw_device['hostname'],
                raw_device['platformId'],
                raw_device['managementIpAddress']
            )
        return UnexpectedResponseError()
    def is_processable(self,response):
        return HTTPCodeConditioner(200,DeviceSNConditioner()).process(response)

class TrustpointResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        UniqueResourceHandler(
            UnknownResourceHandler()
        )