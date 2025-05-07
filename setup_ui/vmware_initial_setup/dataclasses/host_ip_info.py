from morpheus_api.dataclasses.base_object import BaseObject


class HostSerialNumberIPInfo(BaseObject):
    host_serial_number: str
    management_ip: str
