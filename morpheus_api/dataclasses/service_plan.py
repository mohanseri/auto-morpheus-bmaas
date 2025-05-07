from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import Meta


class ServicePlan(BaseObject):
    id: int
    name: str
    active: bool
    sort_order: int
    description: str
    max_storage: int
    max_memory: int
    max_cores: int
    cores_per_socket: int
    custom_cpu: bool
    custom_cores: bool
    custom_max_storage: bool
    custom_max_data_storage: bool
    custom_max_memory: bool
    add_volumes: bool
    editable: bool
    max_cpu: Optional[int] = None
    max_disks: Optional[int] = None
    code: Optional[str] = None


class ServicePlanList(BaseObject):
    service_plans: list[ServicePlan]
    meta: Meta
