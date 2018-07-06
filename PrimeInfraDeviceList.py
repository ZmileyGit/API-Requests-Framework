import getpass
from api.entities import HTTPSServer,Credentials,CertificateCheck
from api.builders import JSONRequestBuilder
from api.decorators import BasicAuthDecorator

ip_address = input("IP Address: ")
server = HTTPSServer(ip_address)

username = input("Username: ")
password = getpass.getpass()
credentials = Credentials(username,password)

builder = JSONRequestBuilder(server)
builder = BasicAuthDecorator(builder,credentials)
builder.resource = "/webacs/api/v1/data/Devices"
builder.certificate_check = CertificateCheck.IGNORE
builder.queries.add_query(".full","true")
request = builder.build()
response = request.send()

body = response.document if response.document else response.text
print("""
URL : {url},
HTTP Code: {code},
Reason : {reason}
Body :
{body}\
""".format(url=request.url,code=response.code,reason=response.reason,body=body))