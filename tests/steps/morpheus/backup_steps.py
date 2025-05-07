from lib.common.enums.backup_type import BackupType
from lib.common.enums.location_type import LocationType
from morpheus_api.dataclasses.backup import CreateBackupPayload


"""This module contains steps for ALL backup-related operations."""


def create_backup_payload(
    instance_id: int,
    backup_name: str,
    container_id: int,
    server_id: int = None,
    location_type: LocationType = LocationType.INSTANCE,
    backup_type: BackupType = BackupType.KVM,
    job_action: str = "new",
    job_name: str = None,
    retention_count: str = None,
    job_schedule: str = None,
) -> CreateBackupPayload:
    """
    Creates a payload for a backup job.

    Args:
        instance_id (int): The ID of the instance to back up.
        backup_name (str): The name of the backup.
        container_id (int): The ID of the container where the backup will be stored.
        location_type (LocationType): Should be one of "instance", "provider", or "server".
        Defaults to "LocationType.INSTANCE".
        backup_type (BackupType, optional): The type of backup. Defaults to BackupType.KVM.
        job_action (str, optional): The action for the job (e.g., "new", "update"). Defaults to "new".
        job_name (str, optional): The name of the job. Defaults to None.
        retention_count (str, optional): The number of backups to retain. Defaults to None.
        job_schedule (str, optional): The schedule for the backup job. Defaults to None.

    Returns:
        CreateBackupJobPayload: The payload for the backup job.
    """
    create_backup_job_payload = CreateBackupPayload(
        instance_id=instance_id,
        server_id=server_id,
        name=backup_name,
        container_id=container_id,
        location_type=location_type,
        backup_type=backup_type,
        job_action=job_action,
        job_name=job_name,
        retention_count=retention_count,
        job_schedule=job_schedule,
    )
    return create_backup_job_payload
