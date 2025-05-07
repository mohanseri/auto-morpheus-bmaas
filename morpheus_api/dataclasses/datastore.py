from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import ID, Meta


class Datastore(BaseObject):
    id: int
    name: str
    type: str
    visibility: str
    active: bool
    allow_write: bool
    default_store: bool
    online: bool
    allow_read: bool
    allow_provision: bool
    external_id: str
    zone: ID
    owner: ID
    storage_size: Optional[int] = None
    free_space: Optional[int] = None
    code: Optional[str] = None


class DatastoreList(BaseObject):
    datastores: list[Datastore]
    meta: Meta
