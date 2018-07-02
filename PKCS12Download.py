from api.builders import JSONRequestBuilder,GenericRequestBuilder
from api.generators import APIC_EMTokenGenerator
from api.decorators import APIC_EMDecorator
from api.entities import HTTPSServer,Credentials,HTTPMethod
from api.errors import APIAuthenticationError,APIError,InvalidRequestError
from api.errors import UnexpectedResponseError,UnknownResourceError
from api.cert_refresh.handlers import DeviceResponseHandler,ExistentTrustpointHandler
from api.cert_refresh.constants import *
from ipaddress import ip_address,IPv4Address,IPv6Address
from ssl import create_default_context,Purpose
import getpass
import re
from time import sleep

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