from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.common_objects import APIResponse
from morpheus_api.dataclasses.instance import InstanceSnapshotImport
from morpheus_api.dataclasses.snapshot import (
    CreateSnapshotData,
    Snapshot,
    SnapshotsList,
)

import logging

INSTANCE_ENDPOINT = MorpheusAPIEndpoints.INSTANCES.value
SNAPSHOT_ENDPOINT = MorpheusAPIEndpoints.SNAPSHOTS.value

logger = logging.getLogger()


class SnapshotService(MorpheusAPI):
    """SnapshotService class provides methods to interact with the Morpheus API to manage snapshots.

    This class provides methods strictly following /api/snapshots endpoint in Morpheus API.

    But all snapshot-related methods can be found in snapshot_steps.py file.

    NOTE: The only exception is that Snapshot APIs that use /api/instances endpoint will be housed here as well.

    """

    def delete_snapshot_of_an_instance(self, snapshot_id: int) -> APIResponse:
        """Delete a snapshot by its ID.

        Args:
            snapshot_id (int): The ID of the snapshot to delete.

        Returns:
            APIResponse: The APIResponse from the API containing the snapshot deletion success / failure result.
        """
        response: Response = self._delete(f"{SNAPSHOT_ENDPOINT}/{snapshot_id}")
        return APIResponse(**response.json())

    def get_snapshot_by_id(self, snapshot_id: int) -> Snapshot:
        """Get a snapshot by its ID.

        Args:
            snapshot_id (int): The ID of the snapshot to retrieve.

        Returns:
            Snapshot: The Snapshot object containing the snapshot.
        """
        response: Response = self._get(f"{SNAPSHOT_ENDPOINT}/{snapshot_id}")
        return Snapshot(**response.json())

    def list_instance_snapshots(self, instance_id: int) -> SnapshotsList:
        """
        Retrieve a list of snapshots for a given instance.

        Args:
            instance_id (int): The unique identifier of the instance.
        Returns:
            SnapshotsList: An object containing the list of snapshots.
        Raises:
            AssertionError: If the response status code is not 200 (OK), \
                an assertion error is raised with the response status code and text.
        """
        response: Response = self._get(f"{INSTANCE_ENDPOINT}/{instance_id}/snapshots")
        return SnapshotsList(**response.json())

    def create_snapshot_of_an_instance(
        self, instance_id: int, snapshot_payload: CreateSnapshotData = None
    ) -> APIResponse:
        """
        Create a snapshot for a given instance.

        Args:
            instance_id (int): The ID of the instance for which the snapshot is to be created.
            snapshot_payload (CreateSnapshotData, optional): The data containing the snapshot creation parameters.
        Returns:
            APIResponse: The APIResponse from the API containing the snapshot creation success / failure result.
        Raises:
            AssertionError: If the API response status code is not 200 (OK), \
                an assertion error is raised with the response status code and text.
        """
        if snapshot_payload is None:
            response: Response = self._put(f"{INSTANCE_ENDPOINT}/{instance_id}/snapshot")
        else:
            create_snapshot_payload = snapshot_payload.model_dump(by_alias=True, exclude_none=True)
            response: Response = self._put(f"{INSTANCE_ENDPOINT}/{instance_id}/snapshot", data=create_snapshot_payload)
        return APIResponse(**response.json())

    def delete_all_snapshots_of_an_instance(self, instance_id: int) -> APIResponse:
        """
        Delete all snapshot of an Instance by its ID.
        Args:
            instance_id (int): The ID of the instance to have all its snapshots deleted.
        Returns:
            APIResponse: The APIResponse from the API containing the snapshot deletion success / failure result.
        Raises:
            AssertionError: If the API response status code is not 200 (OK), \
                an assertion error is raised with the response status code and text.
        """
        response: Response = self._delete(f"{INSTANCE_ENDPOINT}/{instance_id}/delete-all-snapshots")
        return APIResponse(**response.json())

    def import_snapshot_of_instance(
        self,
        instance_id: int,
        import_snapshot_payload: InstanceSnapshotImport,
    ) -> APIResponse:
        """
        Import snapshot of an instance, creating a Virtual Image.

        Args:
            instance_id (int): The ID of the instance to import the snapshot from.
            import_snapshot_payload (InstanceSnapshotImport): The data containing the snapshot import parameters.

        Returns:
            APIResponse: The APIResponse from the API containing the snapshot import success / failure result.

        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        url: str = f"{INSTANCE_ENDPOINT}/{instance_id}/import-snapshot"
        payload = import_snapshot_payload.model_dump(by_alias=True, exclude_none=True)
        logger.info(f"Import snapshot payload: {payload}")

        response: Response = self._put(url, data=payload)
        return APIResponse(**response.json())

    def revert_instance_to_snapshot(self, instance_id: int, snapshot_id: int) -> APIResponse:
        """Revert an instance to a snapshot by its ID.

        Args:
            instance_id (int): The ID of the instance to revert.
            snapshot_id (int): The ID of the snapshot to revert to.

        Returns:
            APIResponse: The APIResponse from the API containing the instance revert to snapshot success / failure result.
        """
        response: Response = self._put(f"{INSTANCE_ENDPOINT}/{instance_id}/revert-snapshot/{snapshot_id}")
        return APIResponse(**response.json())
