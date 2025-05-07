from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import Meta


class Config(BaseObject):
    host: str
    export_folder: str


class StorageBucket(BaseObject):
    id: int
    name: str
    active: bool
    account_id: int
    provider_type: str
    config: Config
    bucket_name: str
    read_only: bool
    default_backup_target: bool
    default_deployment_target: bool
    default_virtual_image_target: bool
    copy_to_store: bool
    retention_policy_type: Optional[str] = None
    retention_policy_days: Optional[str] = None
    retention_provider: Optional[str] = None


class StorageBucketList(BaseObject):
    storage_buckets: list[StorageBucket]
    meta: Meta
