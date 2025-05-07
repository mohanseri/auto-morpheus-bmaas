from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import ID, IDNameCode, Meta


class ClusterLayout(BaseObject):
    id: int
    name: str
    server_count: int
    sync_source: str
    storage_runtime: str
    has_auto_scale: bool
    memory_requirement: int
    cluster_version: str
    compute_version: str
    provision_type: ID
    has_settings: bool
    group_type: ID
    type: ID
    creatable: bool
    enabled: bool
    group_type: IDNameCode
    code: Optional[str] = None


class ClusterLayoutList(BaseObject):
    layouts: list[ClusterLayout]
    meta: Meta
