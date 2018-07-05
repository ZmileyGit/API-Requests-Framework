class Messages:
    WELCOME_MESSAGE = "Manual Certificate Renewal Script"
    APIC_EM_DATA_COLLECTION_MESSAGE = "Collecting APIC-EM's Basic Data"
    INVALID_IP_ADDRESS_MESSAGE = "Please type in a valid IPv4 address"
    INVALID_CREDENTIALS = "Plase provide valid credentials for your APIC-EM server"
    UNKNOWN_DEVICE = "Unable to retrieve device with serial number: {serial_number}"
    INVALID_SERIAL_NUMBER = 'Please type in a valid serial number'
    APIC_EM_AUTHENTICATION_ATTEMPT = 'Authenticating with your APIC-EM server...'
    SUCCESSFUL_AUTHENTICATION_MESSAGE = 'Assigned token -> {token}'
    SEARCHING_DEVICE_SN_MESSAGE = 'Searching device with Serial Number -> {serial_number}'
    DEVICE_FOUND_MESSAGE = 'Found {device}'
    TRUST_POINT_FOUND_MESSAGE = 'Found trust point -> {trustpoint_id}'
    DELETING_TRUSTPOINT_MESSAGE = 'Deleting trust point -> {trustpoint_id}'
    CREATING_TRUSTPOINT_MESSAGE = 'Creating new trust point for {device}'
    NO_TRUST_POINT_FOUND_MESSAGE = 'No trust point found for {device}'
    TRUSTPOINT_CONFIGURATION_MESSAGE = 'Retrieving configuration for trust point -> {trustpoint_id}'
    DOWNLOADING_PKCS12_MESSAGE = 'Downloading PKCS12 file for {device}'
    STORED_PKCS12_MESSAGE = 'Stored successfully {file} with password {password}'
    SEARCHING_TRUST_POINT_MESSAGE = 'Searching trust point related to {device}'

class Prompts:
    IP_ADDRESS_PROMPT = "IP Address"
    USERNAME_PROMPT = "Username"
    SN_PROMPT = "Serial Number"

class Settings:
    VERIFY_SERVER_CERTIFICATE = False