from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import IDNameCode, Meta


class InstanceTypeLayout(BaseObject):
    id: int
    name: str
    instance_type: IDNameCode
    description: Optional[str] = None
    code: Optional[str] = None
    account: Optional[int] = None


class InstanceTypeLayoutList(BaseObject):
    instance_type_layouts: list[InstanceTypeLayout]
    meta: Meta


class InstanceType(BaseObject):
    instance_type_layouts: list[InstanceTypeLayout]
