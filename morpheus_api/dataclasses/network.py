from typing import Any, Optional
from pydantic import Field
from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import ID, IDName, IDNameCode, Meta


class Network(BaseObject):
    id: int
    name: str
    display_name: Optional[str] = None
    zone: IDName
    type: IDNameCode
    owner: IDName
    ipv4_enabled: bool
    ipv6_enabled: bool
    category: Optional[str] = None
    external_id: Optional[str] = None
    internal_id: Optional[str] = None
    unique_id: Optional[str] = None
    external_type: str
    code: Optional[str] = None


class NetworkList(BaseObject):
    networks: list[Network]
    meta: Meta


class NetworkID(BaseObject):
    id: str


class InterfaceNetwork(BaseObject):
    id: int
    dhcp_server: bool
    name: str
    pool: IDName
    group: Optional[str] = None
    subnet: Optional[str] = None


class Interface(BaseObject):
    id: str
    network: InterfaceNetwork
    network_interface_type_id: int
    ip_address: Optional[str] = None
    ip_mode: Optional[str] = None


class NetworkInterface(BaseObject):
    primary_interface: bool
    network: NetworkID
    ip_mode: str
    ip_address: Optional[str] = None
    id: Optional[str] = None


class NetworkResourcePermissions(BaseObject):
    all: bool
    sites: list[int]


class NetworkData(BaseObject):
    name: str
    site: ID
    zone: IDName
    type: IDNameCode
    vlan_id: Optional[int] = None
    switch_id: Optional[str] = None
    zone_pool: Optional[IDName] = None
    group: Optional[IDName] = None
    display_name: Optional[str] = None
    labels: Optional[list[str]] = None
    description: Optional[str] = None
    ipv4_enabled: Optional[bool] = None
    ipv6_enabled: Optional[bool] = None
    cidr: Optional[str] = None
    gateway: Optional[str] = None
    dns_primary: Optional[str] = None
    dns_secondary: Optional[str] = None
    gateway_ipv6: Optional[str] = Field(default=None, alias="gatewayIPv6")
    netmask_ipv6: Optional[str] = Field(default=None, alias="netmaskIPv6")
    dns_primary_ipv6: Optional[str] = Field(default=None, alias="dnsPrimaryIPv6")
    dns_secondary_ipv6: Optional[str] = Field(default=None, alias="dnsSecondaryIPv6")
    cidr_ipv6: Optional[str] = Field(default=None, alias="cidrIPv6")
    pool: Optional[int] = None
    pool_ipv6: Optional[int] = Field(default=None, alias="poolIPv6")
    allow_static_override: Optional[bool] = None
    assign_public_ip: Optional[bool] = Field(default=None, alias="assignPublicIP")
    active: Optional[bool] = None
    dhcp_server: Optional[bool] = None
    dhcp_server_ipv6: Optional[bool] = Field(default=None, alias="dhcpServerIPv6")
    network_domain: Optional[ID] = None
    search_domains: Optional[str] = None
    network_proxy: Optional[ID] = None
    appliance_url_proxy_bypass: Optional[bool] = None
    no_proxy: Optional[str] = None
    visibility: Optional[str] = None
    config: Optional[Any] = None  # If needed, this NetworkTypeConfig can be updated to specific dataclasses
    tenants: Optional[list[IDName]] = None
    resource_permissions: Optional[NetworkResourcePermissions] = None


class NetworkCreateData(BaseObject):
    network: NetworkData


class NetworkResponse(BaseObject):
    success: Optional[bool] = None
    errors: Optional[Any] = None
    network: Optional[Network] = None
    msg: Optional[str] = None


class NetworkType(BaseObject):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class NetworkTypeList(BaseObject):
    network_types: list[NetworkType]
    meta: Meta


class NetworkRouter(BaseObject):
    id: int
    name: str


class NetworkRouterList(BaseObject):
    network_routers: list[NetworkRouter]
    meta: Meta
