from typing import Optional
from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import Meta


class Group(BaseObject):
    id: int
    uuid: str
    name: str
    account_id: int
    location: Optional[str] = None
    code: Optional[str] = None


class GroupList(BaseObject):
    groups: list[Group]
    meta: Meta
