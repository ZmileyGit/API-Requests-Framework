from api.dao.base import DAO
from api.entities import HTTPMethod
from api.handlers import ResponseHandler

class DeviceDAO(DAO):
    BY_SERIAL_NUMBER = '/api/v1/network-device/serial-number/{serial_number}'
    def by_serial_number(self,serial_number:str):
        self.builder.reset()
        self.builder.resource = DeviceDAO.BY_SERIAL_NUMBER.format(serial_number=serial_number)
        self.builder.method = HTTPMethod.GET
        request = self.builder.build()
        response = request.send()
        return response