from typing import Any, Optional
from pydantic import field_validator

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import ID, Code, IDCode, IDName, Meta, NameValue
from morpheus_api.dataclasses.volume import Volume
from morpheus_api.dataclasses.network import Interface, NetworkInterface


class InstanceData(BaseObject):
    site: ID
    type: str
    instanceType: Code
    layout: IDCode
    plan: IDCode
    name: str
    instance_context: Optional[str] = None


class InstanceCreateData(BaseObject):
    instance: InstanceData
    copies: int
    layout_size: int
    config: dict[str, Any]
    zone_id: int
    volumes: list[Volume]
    network_interfaces: Optional[list[NetworkInterface]] = None  # Added missing field
    interfaces: Optional[list[Interface]] = None  # Added missing field


class InstanceResize(BaseObject):
    plan: ID  # Changed to use Plan dataclass


class InstanceResizeData(BaseObject):
    instance: Optional[InstanceResize] = None
    volumes: Optional[list[Volume]] = None
    network_interfaces: Optional[list[NetworkInterface]] = None  # Added missing field
    delete_original_volumes: bool = False  # Amazon only


class InstanceDetailsInstanceType(BaseObject):
    id: int
    code: str
    category: str
    name: str
    image: str


class InstanceConnectionInfo(BaseObject):
    ip: str


class InstanceNetworkInterface(BaseObject):
    id: Optional[str] = None  # can be 'int' or 'str'
    row: Optional[int] = None
    ip_mode: str
    ip_address: Optional[str] = None

    @field_validator("id", mode="before")
    def convert_id_to_str(cls, v):
        """
        Convert id to string if it is an integer.
        This is added because, in some objects, the id is an int.
        """
        if isinstance(v, int):
            return str(v)
        return v


class InstanceDetails(BaseObject):
    id: int
    name: str
    uuid: str
    account_id: int
    tenant: IDName
    instance_type: InstanceDetailsInstanceType
    status: str
    volumes: list[Volume]
    containers: list[int]
    servers: list[int]
    connection_info: list[InstanceConnectionInfo]
    cluster: Optional[IDName] = None
    locked: bool
    interfaces: Optional[list[InstanceNetworkInterface]] = None
    plan: IDCode


class Instance(BaseObject):
    instance: InstanceDetails
    copies: Optional[list[InstanceDetails]] = None


class InstanceList(BaseObject):
    instances: list[InstanceDetails]


class InstanceType(BaseObject):
    id: int
    name: str
    description: str
    provision_type_code: str
    category: str
    active: bool
    environment_prefix: str
    visibility: str
    featured: bool
    account: Optional[int] = None


class InstanceTypeList(BaseObject):
    instance_types: list[InstanceType]
    meta: Meta


class InstanceSnapshotImport(BaseObject):
    template_name: str
    storage_provider_id: int


class InstanceUpdateData(BaseObject):
    name: Optional[str] = None
    description: Optional[str] = None
    instance_context: Optional[str] = None
    labels: Optional[list[str]] = None
    tags: Optional[list[NameValue]] = None
    add_tags: Optional[list[NameValue]] = None
    remove_tags: Optional[list[NameValue]] = None
    power_schedule_type: Optional[int] = None
    site: Optional[ID] = None
    owner_id: Optional[int] = None
    display_name: Optional[str] = None


class ConfigUpdateData(BaseObject):
    custom_options: Optional[dict[str, str]] = None


class InstanceUpdatePayload(BaseObject):
    instance: InstanceUpdateData
    config: ConfigUpdateData
