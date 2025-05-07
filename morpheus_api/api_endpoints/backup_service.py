from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.backup import (
    CreateBackup,
    CreateBackupPayload,
    BackupData,
)
from morpheus_api.dataclasses.common_objects import APIResponse

import logging

logger = logging.getLogger()

BACKUP_ENDPOINT = MorpheusAPIEndpoints.BACKUPS.value
INSTANCE_ENDPOINT = MorpheusAPIEndpoints.INSTANCES.value


class BackupService(MorpheusAPI):
    """BackupService class provides methods to interact with the Morpheus API to manage backups.

    This class provides methods strictly following /api/backups endpoint in Morpheus API.

    But all backup-related methods can be found in backup_steps.py file.

    NOTE: The only exception is that Backup APIs that use /api/instances endpoint will be housed here as well.

    """

    def create_backup(self, create_backup_job_payload: CreateBackupPayload) -> APIResponse:
        """Creates a backup job.

        Args:
            create_backup_job_payload (CreateBackupPayload): The payload for creating a backup job.

        Returns:
            APIResponse: The response from the create backup job request.
        """

        create_backup_job_payload = CreateBackup(backup=create_backup_job_payload)
        json_data = create_backup_job_payload.model_dump(by_alias=True, exclude_none=True)
        logger.info(f"Creating backup job with data: {json_data}")

        response: Response = self._post(BACKUP_ENDPOINT, data=json_data)
        return APIResponse(**response.json())

    def delete_backup(self, backup_id: int) -> APIResponse:
        """
        Delete a backup by its ID.

        Args:
            backup_id (int): The ID of the backup to be deleted.
        Returns:
            APIResponse: The APIResponse from the API containing the backup deletion success / failure result.
        Raises:
            AssertionError: If the API response status code is not 200 (OK), \
                an assertion error is raised with the response status code and text.
        """
        response: Response = self._delete(f"{BACKUP_ENDPOINT}/{backup_id}")
        return APIResponse(**response.json())

    def list_instance_backups(self, instance_id: int) -> BackupData:
        """
        Retrieve the list of backups for a given instance.

        Args:
            instance_id (int): The unique identifier of the instance.
        Returns:
            BackupData: An object containing the backup data.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        response: Response = self._get(f"{INSTANCE_ENDPOINT}/{instance_id}/backups")
        return BackupData(**response.json())

    def create_instance_backup(self, instance_id: int) -> APIResponse:
        """
        Initiates a backup for the specified instance.
        Args:
            instance_id (int): The unique identifier of the instance to back up.
        Returns:
            APIResponse: The APIResponse from the API containing the backup creation success / failure result.
        Raises:
            AssertionError: If the response status code is not 200 (OK), \
                an assertion error is raised with the response details.
        """
        response: Response = self._put(f"{INSTANCE_ENDPOINT}/{instance_id}/backup")
        return APIResponse(**response.json())
