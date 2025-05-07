from typing import Optional
from datetime import datetime

from lib.common.enums.location_type import LocationType
from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import IDName
from lib.common.enums.backup_type import BackupType as BackupTypeEnum


class BackupType(BaseObject):
    id: int
    code: str
    name: str
    copy_to_store: bool


class BackupJob(BaseObject):
    id: int
    name: str
    last_execution: Optional[datetime]


class BackupResult(BaseObject):
    id: int
    duration_millis: int
    container_id: int
    server_id: int
    date_created: datetime
    last_updated: datetime
    start_date: datetime
    end_date: datetime
    backup_name: str
    status: str
    error: bool
    size_in_bytes: int
    size_in_mb: int
    status_message: Optional[str] = None
    error_message: Optional[str] = None
    volume_path: Optional[str] = None
    result_archive: Optional[str] = None
    result_path: Optional[str] = None
    snapshot_id: Optional[int] = None
    snapshot_external_id: Optional[str] = None


class BackupsList(BaseObject):
    id: int
    name: str
    backup_type: BackupType
    target_all: bool
    backup_job: BackupJob
    date_created: datetime
    last_updated: datetime
    backup_results: list[BackupResult]
    storage_provider: Optional[IDName] = None
    target_path: Optional[str] = None
    cron_expression: Optional[str] = None
    cron_description: Optional[str] = None
    target_username: Optional[str] = None
    target_name: Optional[str] = None
    ssh_host: Optional[str] = None
    ssh_port: Optional[int] = None
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None
    retention_count: Optional[int] = None


class Instance(BaseObject):
    id: int


class BackupData(BaseObject):
    instance: Instance
    backups: list[BackupsList]


class CreateBackupPayload(BaseObject):
    name: str
    container_id: int
    instance_id: Optional[int] = None
    server_id: Optional[int] = None
    location_type: LocationType = LocationType.INSTANCE
    backup_type: BackupTypeEnum = BackupTypeEnum.KVM
    job_action: str = "new"
    job_name: Optional[str] = None
    retention_count: Optional[str] = None
    job_schedule: Optional[str] = None

    class Config:
        use_enum_values = True


class CreateBackup(BaseObject):
    backup: CreateBackupPayload
