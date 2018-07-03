from api.builders import JSONRequestBuilder,GenericRequestBuilder
from api.handlers import UniqueResourceHandler
from api.generators import APIC_EMTokenGenerator
from api.decorators import APIC_EMDecorator
from api.entities import HTTPSServer,Credentials,HTTPMethod
from api.errors import APIAuthenticationError,APIError,InvalidRequestError
from api.errors import UnexpectedResponseError,UnknownResourceError
from api.cert_refresh.handlers import DeviceResponseHandler
from api.cert_refresh.constants import *
from ipaddress import ip_address,IPv4Address,IPv6Address
import getpass

Messages.log_message(Messages.WELCOME_MESSAGE)

ip = ""
while not (isinstance(ip,IPv4Address)):
    try:
        ip = input(Prompts.COMMON_PROMPT_TEMPLATE.format(message=Prompts.IP_ADDRESS_PROMPT))
        ip = ip.strip()
        ip = ip_address(ip)
    except ValueError as err:
        Messages.log_error(Messages.INVALID_IP_ADDRESS_MESSAGE)
server = HTTPSServer(str(ip))

token = None
while not token:
    try:
        username = input(Prompts.create_prompt(Prompts.USERNAME_PROMPT))
        password = getpass.getpass(Prompts.create_prompt(Prompts.PASSWORD_PROMPT))
        credentials = Credentials(username,password)
        Messages.log_message(Messages.APIC_EM_AUTHENTICATION_ATTEMPT)
        token = APIC_EMTokenGenerator(server,credentials).generate(certificate_check=Settings.VERIFY_SERVER_CERTIFICATE)
    except (APIAuthenticationError,InvalidRequestError):
        Messages.log_error(Messages.INVALID_CREDENTIALS)
    else:
        Messages.log_message(Messages.SUCCESSFUL_AUTHENTICATION_MESSAGE.format(token=token))

builder = JSONRequestBuilder(server)
builder = APIC_EMDecorator(builder,credentials)
builder.token = token

device = None
while not device:
    serial_number = input(Prompts.create_prompt(Prompts.SN_PROMPT))
    serial_number = serial_number.strip()
    builder.reset()
    builder.resource = '/api/v1/network-device/serial-number/{serial_number}'.format(serial_number=serial_number)
    builder.method = HTTPMethod.GET.value
    builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = builder.build()
    Messages.log_message(Messages.SEARCHING_DEVICE_SN_MESSAGE.format(serial_number=serial_number))
    response = request.send()
    try:
        device = DeviceResponseHandler.handler_chain().handle_response(response)
    except UnknownResourceError:
        Messages.log_error(Messages.UNKNOWN_DEVICE.format(serial_number=serial_number))
    except InvalidRequestError:
        Messages.log_error(Messages.INVALID_SERIAL_NUMBER)
    else:
        Messages.log_message(Messages.DEVICE_FOUND_MESSAGE.format(device=device))

builder.reset()
builder.resource = '/api/v1/trust-point/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = HTTPMethod.GET.value
builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
request = builder.build()
Messages.log_message(Messages.SEARCHING_TRUST_POINT_MESSAGE.format(device=device))
response = request.send()
trustpoint = UniqueResourceHandler().handle_response(response,"")

if trustpoint:
    Messages.log_message(Messages.TRUST_POINT_FOUND_MESSAGE.format(trustpoint_id=trustpoint))
    builder.reset()
    builder.resource= '/api/v1/trust-point/{trustpoint_id}'.format(trustpoint_id=trustpoint)
    builder.method = HTTPMethod.DELETE.value
    builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = builder.build()
    Messages.log_message(Messages.DELETING_TRUSTPOINT_MESSAGE.format(trustpoint_id=trustpoint))
    response = request.send()
else:
    Messages.log_message(Messages.NO_TRUST_POINT_FOUND_MESSAGE.format(device=device))

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
Messages.log_message(Messages.CREATING_TRUSTPOINT_MESSAGE.format(device=device))
response = request.send()

builder.reset()
builder.resource = '/api/v1/trust-point/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = HTTPMethod.GET.value
builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
request = builder.build()
Messages.log_message(Messages.SEARCHING_TRUST_POINT_MESSAGE.format(device=device))
response = request.send()
trustpoint = UniqueResourceHandler().handle_response(response,"")

if trustpoint:
    Messages.log_message(Messages.TRUST_POINT_FOUND_MESSAGE.format(trustpoint_id=trustpoint))
    builder.reset()
    builder.resource = '/api/v1/trust-point/{trustpoint_id}/config'.format(trustpoint_id=trustpoint)
    builder.method = HTTPMethod.GET.value
    builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = builder.build()
    Messages.log_message(Messages.TRUSTPOINT_CONFIGURATION_MESSAGE.format(trustpoint_id=trustpoint))
    response = request.send()
    config = response.document['response']
    pkcs12_url = config['pkcs12Url']
    pkcs12_password = config['pkcs12Password']

    file_builder = GenericRequestBuilder(server)
    file_builder.method = HTTPMethod.GET.value
    file_builder.resource = pkcs12_url
    file_builder.certificate_check = Settings.VERIFY_SERVER_CERTIFICATE
    request = file_builder.build()
    Messages.log_message(Messages.DOWNLOADING_PKCS12_MESSAGE.format(device=device))
    response = request.send()

    filename = '{serial_number}.pfx'.format(serial_number=serial_number)
    with open(filename,'wb') as pkcs12:
        pkcs12.write(response.data)
        Messages.log_message(Messages.STORED_PKCS12_MESSAGE.format(file=filename,password=pkcs12_password))