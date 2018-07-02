class Messages:
    ERROR_MESSAGE_TEMPLATE = "\n|{message}|\n"
    WELCOME_MESSAGE = "Manual Certificate Renewal Script"
    APIC_EM_DATA_COLLECTION_MESSAGE = "Collecting APIC-EM's Basic Data"
    INVALID_IP_ADDRESS_MESSAGE = "Please type in a valid IPv4 address"
    INVALID_CREDENTIALS = "Plase provide valid credentials for your APIC-EM server"
    UNKNOWN_DEVICE = "Unable to retrieve device with serial number: {serial_number}"
    INVALID_SERIAL_NUMBER = 'Please type in a valid serial number'


class Prompts: 
    COMMON_PROMPT_TEMPLATE = "{message}: "
    IP_ADDRESS_PROMPT = "IP Address"
    USERNAME_PROMPT = "Username"
    PASSWORD_PROMPT = "Password"
    SN_PROMPT = "Serial Number"

class Settings:
    VERIFY_SERVER_CERTIFICATE = False