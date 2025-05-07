import logging
from lib.common.enums.instance_status import InstanceStatus
from lib.common.enums.process_status import ProcessStatus
from lib.common.enums.process_type import ProcessType
from lib.common.enums.snapshot_status import SnapshotStatus
from morpheus_api.settings import MorpheusAPIService
from morpheus_api.dataclasses.snapshot import CreateSnapshotData, Snapshot, SnapshotData, SnapshotsList
from tests.steps.morpheus.instance_steps import (
    wait_for_instance_status_update,
    wait_for_instance_history_process_status_update,
    wait_for_instance_snapshot_count,
    wait_for_instance_snapshot_status_update,
)

logger = logging.getLogger()

"""This module contains steps for ALL snapshot-related operations."""


def delete_multiple_snapshots_of_an_instance(
    morpheus_api_service: MorpheusAPIService, instance_id: int, snapshot_ids: list[int], wait_for_deletion: bool = True
) -> bool:
    """Delete selective snapshots of an instance.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service object.
        instance_id (int): The ID of the instance to delete the snapshot from.
        snapshot_ids (list[int]): The IDs of the snapshots to delete.
        wait_for_deletion (bool, optional): Whether to wait for the snapshot to be deleted. Defaults to True.
    Returns:
        Boolean: True if wait for snapshot count is successful, or False when time taken has exceeded maximum time.
    """
    expected_snapshot_count: int = None
    if wait_for_deletion:
        snapshot_list = morpheus_api_service.snapshot_service.list_instance_snapshots(instance_id=instance_id)
        expected_snapshot_count = len(snapshot_list.snapshots) - len(snapshot_ids)

    for snapshot_id in snapshot_ids:
        response = morpheus_api_service.snapshot_service.delete_snapshot_of_an_instance(snapshot_id=snapshot_id)
        assert response.success, f"Failed to initiate delete snapshot {snapshot_id}. Response: {response}"

    if wait_for_deletion:
        # Wait for all of the snapshot deletions at the end rather than in-between snapshots to reduce the total wait time
        status = wait_for_instance_snapshot_count(
            morpheus_api_service=morpheus_api_service,
            instance_id=instance_id,
            expected_snapshot_count=expected_snapshot_count,
            max_wait_time=120,
            sleep_time=10,
        )
        return status


def delete_all_snapshots_of_multiple_instances(
    morpheus_api_service: MorpheusAPIService, instance_id_list: list[int], wait_for_deletion: bool = True
) -> bool:
    """Delete all snapshots of multiple instances.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service object.
        instance_id_list (list[int]): List containing IDs of instances to delete all snapshots of.
        wait_for_deletion (bool, optional): Whether to wait for the snapshots to be deleted. Defaults to True.

    Returns:
        result (bool): The status received from the wait operation. Defaults to True.
    """
    result = True
    for instance_id in instance_id_list:
        response = morpheus_api_service.snapshot_service.delete_all_snapshots_of_an_instance(instance_id=instance_id)
        assert (
            response.success
        ), f"Failed to initialize delete all snapshots of instance {instance_id}. Response: {response}"

        if wait_for_deletion:
            status = wait_for_instance_snapshot_count(
                morpheus_api_service=morpheus_api_service,
                instance_id=instance_id,
                expected_snapshot_count=0,
                max_wait_time=120,
                sleep_time=10,
            )
            if status is False:
                result = False
    return result


def create_multiple_snapshots_of_an_instance(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    number_of_snapshots: int = 1,
    wait_for_completion: bool = True,
) -> list[Snapshot]:
    """Create snapshots of an instance.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service object.
        instance_id (int): The ID of the instance to create snapshots for.
        number_of_snapshots (int, optional): The number of snapshots to create. Defaults to 1.
        wait_for_completion (bool, optional): Whether to wait for the snapshots to be created. Defaults to True.
    Returns:
        list[Snapshot]: The list of created snapshots in incremental order.
    """
    original_snapshot_list: SnapshotsList = morpheus_api_service.snapshot_service.list_instance_snapshots(
        instance_id=instance_id
    )
    original_snapshot_count: int = len(original_snapshot_list.snapshots)
    expected_snapshot_count: int = original_snapshot_count + number_of_snapshots

    for i in range(number_of_snapshots):
        name = f"{instance_id}-Snapshot-{i+original_snapshot_count+1}"
        description = f"Snapshot {i+original_snapshot_count+1} of instance {instance_id}"
        snapshot_data = SnapshotData(name=name, description=description)
        create_snapshot_data = CreateSnapshotData(snapshot=snapshot_data)
        response = morpheus_api_service.snapshot_service.create_snapshot_of_an_instance(
            instance_id=instance_id, snapshot_payload=create_snapshot_data
        )
        assert response.success, f"Failed to initiate create snapshot for instance {instance_id}. Response: {response}"

    if wait_for_completion:
        # wait for expected snapshot count to be reached
        wait_for_instance_snapshot_count(
            morpheus_api_service=morpheus_api_service,
            instance_id=instance_id,
            expected_snapshot_count=expected_snapshot_count,
            max_wait_time=120,
            sleep_time=10,
        )
        # wait until all instance snapshots are in a COMPLETE state
        wait_for_instance_snapshot_status_update(
            morpheus_api_service=morpheus_api_service,
            instance_id=instance_id,
            status=SnapshotStatus.COMPLETE,
            max_wait_time=600,
            sleep_time=10,
        )

    # Return the list of created snapshots in incremental order
    latest_snapshot_list = morpheus_api_service.snapshot_service.list_instance_snapshots(instance_id=instance_id)
    created_snapshots_list: list[Snapshot] = [
        snapshot for snapshot in latest_snapshot_list.snapshots if snapshot not in original_snapshot_list.snapshots
    ]

    return created_snapshots_list


def create_snapshots_of_multiple_instances(
    morpheus_api_service: MorpheusAPIService,
    instance_ids: list[int],
    number_of_snapshots: list[int],
    wait_for_completion: bool = True,
) -> list[Snapshot]:
    """Create snapshots of multiple instances.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service object.
        instance_ids (list[int]): The IDs of the instances to create snapshots for.
        number_of_snapshots (list[int]): The number of snapshots to create for each instance.
        wait_for_completion (bool, optional): Whether to wait for the snapshots to be created. Defaults to True.

    Returns:
        list[Snapshot]: The list of created snapshots in incremental order.
    """
    created_snapshots_list: list[Snapshot] = []
    old_instances_snapshot_count: list[int] = []

    if wait_for_completion:
        for instance_id in instance_ids:
            snapshots_list = morpheus_api_service.snapshot_service.list_instance_snapshots(instance_id=instance_id)
            old_instances_snapshot_count.append(len(snapshots_list.snapshots))

    for instance_id, number_of_snapshot in zip(instance_ids, number_of_snapshots):
        created_snapshots_list.extend(
            create_multiple_snapshots_of_an_instance(
                morpheus_api_service=morpheus_api_service,
                instance_id=instance_id,
                number_of_snapshots=number_of_snapshot,
                wait_for_completion=False,
            )
        )
    if wait_for_completion:
        # Wait for all of the snapshot creations at the end rather than in-between snapshots to reduce the total wait time
        for instance_id, snapshot_count in zip(instance_ids, old_instances_snapshot_count):
            wait_for_instance_snapshot_count(
                morpheus_api_service=morpheus_api_service,
                instance_id=instance_id,
                expected_snapshot_count=snapshot_count + number_of_snapshot,
                max_wait_time=120,
                sleep_time=10,
            )

    return created_snapshots_list


def revert_instance_to_snapshot(
    morpheus_api_service: MorpheusAPIService, instance_id: int, snapshot_id: int, wait_for_completion: bool = True
):
    """Revert an instance to a snapshot.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service object.
        instance_id (int): The ID of the instance to revert.
        snapshot_id (int): The ID of the snapshot to revert to.
        wait_for_completion (bool, optional): Whether to wait for the instance to complete the revert process. Defaults to True.
    """

    result = True
    response = morpheus_api_service.snapshot_service.revert_instance_to_snapshot(
        instance_id=instance_id, snapshot_id=snapshot_id
    )
    if response.success != True:
        result = False
        logger.error(
            f"Failed to initiate revert instance {instance_id} to snapshot {snapshot_id}. Response: {response}"
        )

    if wait_for_completion and result:
        # Wait for the instance status to update
        instance_result = wait_for_instance_status_update(
            morpheus_api_service=morpheus_api_service,
            instance_id=instance_id,
            status=InstanceStatus.RUNNING,
            max_wait_time=360,
            sleep_time=20,
        )
        # Wait for the instance to complete startup process
        if instance_result:
            instance_history_result = wait_for_instance_history_process_status_update(
                morpheus_api_service=morpheus_api_service,
                instance_id=instance_id,
                process_type=ProcessType.STARTUP,
                status=ProcessStatus.COMPLETE,
                max_wait_time=360,
                sleep_time=20,
            )
        else:
            logger.error(f"Instance id {instance_id} failed to start after snapshot revert")
            result = instance_result

        if instance_history_result is False:
            result = False

    return result
