import APIClient
import getpass
from time import sleep

print("---Manual Certificate Renewal Script---\n")

print("Collecting APIC-EM's Basic Data\n")

valid_ip = False
ip_address = input("IP Address: ")
server = APIClient.Server("https",ip_address,443)

username = input("Username: ")
password = getpass.getpass()
credentials = APIClient.Credentials(username,password)

print("\nCollecting Affected Device's Data\n")
serial_number = input("Serial Number: ")

builder = APIClient.JSONRequestBuilder(server)
builder = APIClient.APIC_EMDecorator(builder,credentials)
builder.resource = '/api/v1/network-device/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = APIClient.HTTPMethod.GET.value
builder.certificate_check = False
request = builder.build()
response = request.send()
device = response.document['response']
hostname = device['hostname']
pid = device['platformId']
management_ip = device['managementIpAddress']
print("""
Device Found
Management IP Address: {management_ip}
Hostname: {hostname}
PID: {pid}\
""".format(management_ip=management_ip,hostname=hostname,pid=pid))

builder.reset()
builder.resource = '/api/v1/trust-point/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = APIClient.HTTPMethod.GET.value
builder.certificate_check = False
request = builder.build()
response = request.send()
trustpoint = response.document['response']
trust_profile_name = trustpoint['trustProfileName']
controller = trustpoint['controllerIpAddress']
print("""
Trustpoint Found
Trust Profile Name: {trust_profile_name}
Controller IP Address: {controller}\
""".format(trust_profile_name=trust_profile_name,controller=controller))

builder.reset()
builder.resource = '/api/v1/trust-point/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = APIClient.HTTPMethod.DELETE.value
builder.certificate_check = False
request = builder.build()
response = request.send()
task = response.document['response']

print("\nWaiting 5 seconds for deletion")
sleep(5)

builder.reset()
builder.resource = '/api/v1/trust-point'
builder.method = APIClient.HTTPMethod.POST.value
builder.data = {
  "entityName": hostname,
  "serialNumber": serial_number,
  "platformId": pid,
  "trustProfileName": "sdn-network-infra-iwan",
  "controllerIpAddress": controller
}
builder.certificate_check = False
request = builder.build()
response = request.send()
task = response.document['response']

print("\nWaiting 5 seconds for creation")
sleep(5)

builder.reset()
builder.resource = '/api/v1/trust-point/serial-number/{serial_number}'.format(serial_number=serial_number)
builder.method = APIClient.HTTPMethod.GET.value
builder.certificate_check = False
request = builder.build()
response = request.send()
trustpoint = response.document['response']
trustpoint_id = trustpoint['id']

builder.reset()
builder.resource = '/api/v1/trust-point/{trustpoint_id}/config'.format(trustpoint_id=trustpoint_id)
builder.method = APIClient.HTTPMethod.GET.value
builder.certificate_check = False
request = builder.build()
response = request.send()
config = response.document['response']
pkcs12_url = config['pkcs12Url']
pkcs12_password = config['pkcs12Password']

file_builder = APIClient.GenericRequestBuilder(server)
file_builder.method = APIClient.HTTPMethod.GET.value
file_builder.resource = pkcs12_url
file_builder.certificate_check = False
request = file_builder.build()
response = request.send()

filename = '{serial_number}.pfx'.format(serial_number=serial_number)
with open(filename,'wb') as pkcs12:
    pkcs12.write(response.data)
    print("\nPKCS12's Password: {pkcs12_password}".format(pkcs12_password=pkcs12_password))