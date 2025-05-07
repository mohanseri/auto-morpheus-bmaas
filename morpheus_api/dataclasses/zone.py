from typing import Optional
from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import IDName, IDNameCode, Meta


class Zone(BaseObject):
    id: int
    uuid: str
    name: str
    owner: IDName
    account_id: int
    account: IDName
    visibility: str
    enabled: bool
    status: str
    zone_type: IDNameCode
    status_message: Optional[str] = None
    location: Optional[str] = None
    code: Optional[str] = None


class ZoneList(BaseObject):
    zones: list[Zone]
    meta: Meta
