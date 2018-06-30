from api.builders import JSONRequestBuilder,GenericRequestBuilder
from api.generators import APIC_EMTokenGenerator
from api.decorators import APIC_EMDecorator
from api.entities import HTTPSServer,Credentials,HTTPMethod
from api.errors import APIAuthenticationError,APIError,InvalidRequestError,UnexpectedResponseError
from api.handlers import ResponseHandler,InvalidRequestHandler
from ipaddress import ip_address,IPv4Address,IPv6Address
from ssl import create_default_context,Purpose
import getpass
import re
from time import sleep

class Messages:
    ERROR_MESSAGE_TEMPLATE = "\n|{message}|\n"
    WELCOME_MESSAGE = "Manual Certificate Renewal Script"
    APIC_EM_DATA_COLLECTION_MESSAGE = "Collecting APIC-EM's Basic Data"
    INVALID_IP_ADDRESS_MESSAGE = "Please type in a valid IPv4 address"
    INVALID_CREDENTIALS = "Plase provide valid credentials for your APIC-EM server"
    UNKNOWN_DEVICE = "Unable to retrieve device with serial number: {serial_number}"
    INVALID_SERIAL_NUMBER = 'Please type in a valid serial number'


class Prompts: 
    COMMON_PROMP_TEMPLATE = "{message}: "
    IP_ADDRESS_PROMPT = "IP Address"
    USERNAME_PROMPT = "Username"
    PASSWORD_PROMPT = "Password"
    SN_PROMPT = "Serial Number"

class Settings:
    VERIFY_SERVER_CERTIFICATE = False

class Device:
    def __init__(self,serial_number,hostname,platform_id,mgmt_ip):
        self.serial_number = serial_number
        self.hostname = hostname
        self.platform_id = platform_id
        self.mgmt_ip = mgmt_ip

class Trustpoint:
    def __init__(self,tid,profile_name,controller):
        self.tid = tid 
        self.profile_name = profile_name

class UnknownResourceError(APIError):
    pass

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
        document = response.document
        return response.code == 200 and document and 'response' in document and 'serialNumber' in document['response']

class UnknownDeviceHandler(DeviceResponseHandler):
    def process(self,response):
        raise UnknownResourceError()
    def is_processable(self,response):
        document = response.document
        return response.code == 404 and document and 'response' in document and 'errorCode' in document['response'] and document['response']['errorCode'] == 'Not found'

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
        document = response.document
        return response.code == 200 and document and 'response' in document and 'id' in document['response']      

class UnknownTrustpointHandler(TrustpointResponseHandler):
    def process(self,response):
        raise UnknownResourceError()
    def is_processable(self,response):
        document = response.document
        return response.code == 404 and document and 'response' in document and 'errorCode' in document['response'] and document['response']['errorCode'] == 'Not found'

ip = ""
while not (isinstance(ip,IPv4Address)):
    try:
        ip = input(Prompts.COMMON_PROMP_TEMPLATE.format(message=Prompts.IP_ADDRESS_PROMPT))
        ip = ip.strip()
        ip = ip_address(ip)
    except ValueError as err:
        print(Messages.ERROR_MESSAGE_TEMPLATE.format(message=Messages.INVALID_IP_ADDRESS_MESSAGE))
server = HTTPSServer(str(ip))

token = None
while not token:
    try:
        username = input(Prompts.COMMON_PROMP_TEMPLATE.format(message=Prompts.USERNAME_PROMPT))
        password = getpass.getpass(Prompts.COMMON_PROMP_TEMPLATE.format(message=Prompts.PASSWORD_PROMPT))
        credentials = Credentials(username,password)
        token = APIC_EMTokenGenerator(server,credentials).generate(certificate_check=Settings.VERIFY_SERVER_CERTIFICATE)
    except APIAuthenticationError as err:
        print(Messages.ERROR_MESSAGE_TEMPLATE.format(message=Messages.INVALID_CREDENTIALS))

builder = JSONRequestBuilder(server)
builder = APIC_EMDecorator(builder,credentials)

device = None
while not device:
    serial_number = input(Prompts.COMMON_PROMP_TEMPLATE.format(message=Prompts.SN_PROMPT))
    builder.reset()
    builder.resource = '/api/v1/network-device/serial-number/{serial_number}'.format(serial_number=serial_number)
    builder.method = HTTPMethod.GET.value
    builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = builder.build()
    response = request.send()
    try:
        device = DeviceResponseHandler.handler_chain().handle_response(response)
    except UnknownResourceError:
        print(Messages.ERROR_MESSAGE_TEMPLATE.format(message=Messages.UNKNOWN_DEVICE.format(serial_number=serial_number)))
    except InvalidRequestError:
        print(Messages.ERROR_MESSAGE_TEMPLATE.format(message=Messages.INVALID_SERIAL_NUMBER))

builder.reset()
builder.resource = '/api/v1/trust-point/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = HTTPMethod.GET.value
builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
request = builder.build()
response = request.send()
trustpoint = ExistentTrustpointHandler().handle_response(response,"")


if trustpoint:
    builder.reset()
    builder.resource= '/api/v1/trust-point/{trustpoint_id}'.format(trustpoint_id=trustpoint)
    builder.method = HTTPMethod.DELETE.value
    builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = builder.build()
    response = request.send()

builder.reset()
builder.resource = '/api/v1/trust-point'
builder.method = HTTPMethod.POST.value
builder.data = {
    "entityName": device.hostname,
    "serialNumber": device.serial_number,
    "platformId": device.platform_id,
    "trustProfileName": "sdn-network-infra-iwan",
    "controllerIpAddress": server.ip
}
builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
request = builder.build()
response = request.send()

builder.reset()
builder.resource = '/api/v1/trust-point/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = HTTPMethod.GET.value
builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
request = builder.build()
response = request.send()
trustpoint = ExistentTrustpointHandler().handle_response(response,"")

if trustpoint:
    builder.reset()
    builder.resource = '/api/v1/trust-point/{trustpoint_id}/config'.format(trustpoint_id=trustpoint)
    builder.method = HTTPMethod.GET.value
    builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = builder.build()
    response = request.send()

    config = response.document['response']
    pkcs12_url = config['pkcs12Url']
    pkcs12_password = config['pkcs12Password']

    file_builder = GenericRequestBuilder(server)
    file_builder.method = HTTPMethod.GET.value
    file_builder.resource = pkcs12_url
    file_builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = file_builder.build()
    response = request.send()

    filename = '{serial_number}.pfx'.format(serial_number=serial_number)
    with open(filename,'wb') as pkcs12:
        pkcs12.write(response.data)
        print("\nPKCS12's Password: {pkcs12_password}".format(pkcs12_password=pkcs12_password))