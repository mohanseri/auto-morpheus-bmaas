from typing import Optional
from datetime import datetime

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import IDName


class Snapshot(BaseObject):
    id: int
    name: str
    status: str
    snapshot_type: str
    zone: IDName
    currently_active: bool
    date_created: datetime
    external_id: Optional[str] = None
    snapshot_created: Optional[datetime] = None
    description: Optional[str] = None
    parent_snapshot: Optional[IDName] = None
    state: Optional[str] = None
    datastore: Optional[str] = None


class SnapshotsList(BaseObject):
    snapshots: list[Snapshot]


class SnapshotData(BaseObject):
    name: str
    description: str


class CreateSnapshotData(BaseObject):
    snapshot: SnapshotData
