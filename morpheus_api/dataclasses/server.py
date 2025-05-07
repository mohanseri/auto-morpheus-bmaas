from typing import Optional
from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import (
    IDName,
    ID,
)


class ServerStats(BaseObject):
    running: Optional[bool] = None  # Windows
    ts: Optional[str] = None  # Linux
    free_swap: Optional[int] = None  # Linux
    used_swap: Optional[int] = None  # Linux
    cpu_idle_time: Optional[int] = None  # Linux
    cpu_system_time: Optional[int] = None  # Linux
    cpu_user_time: Optional[int] = None  # Linux
    cpu_total_time: Optional[int] = None  # Linux
    max_memory: Optional[int] = None  # Windows & Linux
    used_memory: Optional[int] = None  # Windows & Linux
    max_storage: Optional[int] = None  # Windows & Linux
    used_storage: Optional[int] = None  # Windows & Linux
    reserved_storage: Optional[int] = None
    cpu_usage: Optional[float] = None  # Windows & Linux
    free_memory: Optional[int] = None  # Windows & Linux
    net_tx_usage: Optional[int] = None  # Windows & Linux
    net_rx_usage: Optional[int] = None  # Windows & Linux
    network_bandwidth: Optional[int] = None  # Windows


class ServerNetworkInterface(BaseObject):
    id: int
    primary_interface: bool
    dhcp: bool
    ip_address: Optional[str] = None


class ServerDetails(BaseObject):
    id: int
    name: str
    hostname: str
    status: str  # Field required to validate the maintenance status of the host.
    parent_server: Optional[IDName] = None
    preferred_parent_server: Optional[IDName] = None
    power_state: str
    agent_installed: bool
    agent_version: Optional[str] = None
    last_agent_update: Optional[str] = None
    stats: ServerStats
    interfaces: list[ServerNetworkInterface]


class Server(BaseObject):
    server: ServerDetails


class ServerList(BaseObject):
    servers: list[ServerDetails]


class ServerPlacementServerData(BaseObject):
    preferred_parent_server: ID
    placement_strategy: str


class ServerData(BaseObject):
    server: ServerPlacementServerData
