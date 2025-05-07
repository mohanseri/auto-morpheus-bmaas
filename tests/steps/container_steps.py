import time
import logging
from lib.common.enums.instance_status import InstanceStatus
from morpheus_api.dataclasses.container import Container
from morpheus_api.settings import MorpheusAPIService

logger = logging.getLogger()


def wait_for_container_status_update(
    morpheus_api_service: MorpheusAPIService,
    container_id: int,
    status: InstanceStatus,
    max_wait_time: int = 3600,
    sleep_time: int = 10,
) -> bool:
    """
    Waits for a Morpheus container to reach a specified status.

    This function polls the status of a Morpheus container at regular intervals until \
        the container reaches the desired status or the maximum wait time is exceeded.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service used to interact with the Morpheus platform.
        container_id (int): The ID of the container to check.
        status (InstanceStatus): The desired status to wait for.
        max_wait_time (int, optional): The maximum time to wait for the container to reach the desired status, \
            in seconds. Defaults to 3600 seconds (60 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 10 seconds.
    Return:
        bool: True if container is running state, false if max time for status update is exceeded
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        container: Container = morpheus_api_service.container_service.get_container_by_id(container_id)
        if container.container.status == status.value:
            return True
        else:
            logger.info(f"Waiting for container status to be '{status.value}'...")
            time.sleep(sleep_time)

    else:
        logger.error(f"Max wait time exceeded for instance status '{status.value}' update.")
        return False


def wait_for_container_deletion(
    morpheus_api_service: MorpheusAPIService,
    container_id: int,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
) -> bool:
    """ Waits for an container to be deleted.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        container_id (int): The ID of the container to wait for deletion.
        max_wait_time (int, optional): The maximum time to wait for the container to be deleted, in seconds. \
            Defaults to 1800.
        sleep_time (int, optional): The time to sleep between status checks, in seconds. Defaults to 10.
    Returns:
        bool: True incase container is removed, false if max time for removal is exceeded
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        try:
            morpheus_api_service.container_service.get_container_by_id(container_id)
        except Exception as e:
            if "Not Found" in str(e):
                return True
        logger.info(f"Waiting for container {container_id} to be deleted...")
        time.sleep(sleep_time)
    else:
        logger.error(f"Max wait time exceeded for container deletion: {container_id}.")
        return False
