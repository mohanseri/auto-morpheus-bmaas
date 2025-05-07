from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import Meta


class StorageVolumeType(BaseObject):
    id: int
    name: str
    description: str
    display_order: int
    default_type: bool
    enabled: bool
    has_datastore: bool
    code: Optional[str] = None


class StorageVolumeTypeList(BaseObject):
    storage_volume_types: list[StorageVolumeType]
    meta: Meta
