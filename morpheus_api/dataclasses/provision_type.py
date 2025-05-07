from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import Meta


class ProvisionType(BaseObject):
    id: int
    name: str
    acl_enabled: bool
    multi_tenant: bool
    host_network: bool
    code: Optional[str] = None
    description: Optional[str] = None
    dhcp_server: Optional[str] = None
    allow_static_override: Optional[bool] = None
    pool: Optional[str] = None


class ProvisionTypeList(BaseObject):
    provision_types: list[ProvisionType]
    meta: Meta
