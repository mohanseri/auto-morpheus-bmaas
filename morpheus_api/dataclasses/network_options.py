from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject


class NetworkOptionsNetworkDetails(BaseObject):
    id: str
    name: str
    allow_static_override: bool
    dhcp_server: bool = None
    pool: Optional[str] = None


class NetworkTypes(BaseObject):
    id: int
    name: str
    display_order: int
    enabled: bool
    default_type: bool
    external_id: str
    code: Optional[str] = None


class NetworkOptionsData(BaseObject):
    networks: list[NetworkOptionsNetworkDetails]
    network_types: list[NetworkTypes]


class NetworkOptions(BaseObject):
    success: bool
    data: NetworkOptionsData
    has_networks: Optional[bool] = None
    enable_network_type_selection: Optional[bool] = None
    supports_network_selection: Optional[bool] = None
