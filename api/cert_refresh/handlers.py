from api.handlers import ResponseHandler,InvalidRequestHandler
from api.errors import UnexpectedResponseError,InvalidRequestError,UnknownResourceError
from api.cert_refresh.conditioners import DeviceSNConditioner
from api.conditioners import HTTPCodeConditioner,UnknownResourceConditioner,UniqueResourceConditioner
from api.cert_refresh.models import Device


class DeviceResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        return ValidDeviceHandler(
            UnknownDeviceHandler(
                InvalidSerialNumberHandler()
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

class UnknownDeviceHandler(DeviceResponseHandler):
    def process(self,response):
        raise UnknownResourceError()
    def is_processable(self,response):
        return HTTPCodeConditioner(
            404,
            next_conditioner=UnknownResourceConditioner()
        ).process(response)

class InvalidSerialNumberHandler(InvalidRequestHandler):
    def process(self,response):
        raise InvalidRequestError()

class TrustpointResponseHandler(ResponseHandler):
    @staticmethod
    def handler_chain():
        ExistentTrustpointHandler(
            UnknownTrustpointHandler()
        )

class ExistentTrustpointHandler(TrustpointResponseHandler):
    def process(self,response):
        raw_trustpoint = response.document['response']
        return raw_trustpoint['id']
    def is_processable(self,response):
        return HTTPCodeConditioner(
            200,
            next_conditioner=UniqueResourceConditioner()
        ).process(response) 

class UnknownTrustpointHandler(TrustpointResponseHandler):
    def process(self,response):
        raise UnknownResourceError()
    def is_processable(self,response):
        return HTTPCodeConditioner(
            404,
            next_conditioner=UnknownResourceConditioner()
        ).process(response)