
class Headers:
    ACCEPT_ENCODING_HEADER = 'Accept-Charset'
    ACCEPT_HEADER = 'Accept'
    CONTENT_TYPE_HEADER = "Content-Type"
    AUTH_HEADER = "Authorization"
    TOKEN_HEADER = "X-Auth-Token"
    
class ContentTypes:
    PLAINTEXT_CONTENT_TYPE = "text/plain"
    JSON_CONTENT_TYPE = "application/json"

class StringTemplates:
    CONTENT_TYPE_TEMPLATE = "{0};charset={1}"
    BASIC_AUTH_TEMPLATE = "Basic {0}"
    BASIC_AUTH_USRPASSWD = "{0}:{1}"

class Settings:
    DEFAULT_ENCODING = 'UTF-8'
    DEFAULT_HEADER_ENCODING = 'ISO-8859-1'
    DEFAULT_RESOURCE_PATH = '/'