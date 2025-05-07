from typing import Optional
from morpheus_api.dataclasses.base_object import BaseObject


class Name(BaseObject):
    name: str


class Value(BaseObject):
    value: Optional[str] = None


class ID(BaseObject):
    id: int


class IDName(ID, Name):
    pass


class NameValue(Name, Value):
    pass


class Code(BaseObject):
    code: str


class IDCode(ID, Code):
    pass


class IDNameCode(IDCode, Name):
    pass


class APIResponse(BaseObject):
    success: bool
    results: Optional[dict] = None
    msg: Optional[str] = None


class Meta(BaseObject):
    offset: int
    max: int
    size: int
    total: int


class CommonRequiredData(BaseObject):
    layout_id: int = None
    layout_code: str = None
    plan_id: int = None
    plan_code: str = None
    zone_id: int = None
    zone_name: str = None
    network_id: str = None
    datastore_id: int = None
    storage_volume_type_id: int = None
    storage_bucket_id: int = None
    cluster_id: int = None
    cluster_name: str = None
    provision_type_id: int = None
    instance_type_id: int = None
