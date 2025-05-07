import logging
import time
from lib.common.enums.server_type import ServerTypePlacementStrategy
from lib.common.enums.server_status import ServerStatus
from morpheus_api.dataclasses.common_objects import ID
from morpheus_api.dataclasses.server import (
    ServerPlacementServerData,
    ServerData,
)
from morpheus_api.settings import MorpheusAPIService

logger = logging.getLogger()

"""This module contains steps for ALL server-related operations.

NOTE: The usage of terms 'server' and 'hosts' are relatively the same. 
Please refer to the API endpoint & can verify functionality in server_service.py
"""


def manage_server_placement_payload(
    preferred_server_id: int,
    placement_strategy: ServerTypePlacementStrategy = ServerTypePlacementStrategy.PINNED,
) -> ServerPlacementServerData:
    """Creates the payload for managing server placement for a VM.

    Args:
        preferred_server_id (int): The ID of the preferred server.
        placement_strategy (ServerTypePlacementStrategy, optional): The placement strategy. Defaults to ServerTypePlacementStrategy.PINNED.

    Returns:
        ServerPlacementServerData: The payload for managing server placement.
    """
    return ServerData(
        server=ServerPlacementServerData(
            preferred_parent_server=ID(id=preferred_server_id),
            placement_strategy=placement_strategy.value,
        )
    )


def get_new_available_server_id(
    morpheus_api_service: MorpheusAPIService, instance_cluster_id: int, original_server_id: int
) -> int:
    """Gets the new available server ID for the VM.

    Args:
        morpheus_api_service (MorpheusAPIService): The service to interact with the Morpheus API.
        instance_cluster_id (int): The ID of the instance cluster.
        original_server_id (int): The ID of the original server.

    Returns:
        int: The new available server ID for the VM.
    """
    query_params = f"clusterId={instance_cluster_id}"
    servers_list = morpheus_api_service.server_service.list_servers(query_params=query_params)
    new_server_id: int = None
    for server in servers_list.servers:
        if server.id != original_server_id:
            new_server_id = server.id
            break
    return new_server_id


def validate_agent_installation(morpheus_api_service: MorpheusAPIService, server_id: int) -> bool:
    """Validates the installation of the agent on the server.

    Args:
        morpheus_api_service (MorpheusAPIService): The service to interact with the Morpheus API.
        server_id (int): The ID of the server.

    Returns:
        bool: True if the agent is installed, False otherwise.
    """
    server = morpheus_api_service.server_service.get_a_specific_server(server_id)

    if server.server.agent_installed:
        logger.info(f"Agent is installed. Version = {server.server.agent_version}")
    else:
        logger.info("Agent is not installed")
        return False

    # check agent stat fields that are present for both Windows and Linux VMs
    required_stats = [
        "cpu_usage",
        "net_rx_usage",
        "net_tx_usage",
        "max_storage",
        "used_storage",
        "max_memory",
        "used_memory",
        "free_memory",
    ]

    for stat in required_stats:
        if getattr(server.server.stats, stat) is None:
            logger.info(f"{stat} stat is not available")
            return False

    logger.info("agent stats are available")
    return True


def wait_for_server_status_update(
    morpheus_api_service: MorpheusAPIService,
    server_id: int,
    status: ServerStatus,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
) -> bool:
    """
    Waits for a Morpheus server to reach a specified status.

    This function polls the status of a Morpheus server at regular intervals until \
        the server reaches the desired status or the maximum wait time is exceeded.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service used to interact with the Morpheus platform.
        server_id (str): The ID of the server to check.
        status (str): The desired status to wait for.
        max_wait_time (int, optional): The maximum time to wait for the server to reach the desired status, \
            in seconds. Defaults to 1800 seconds (30 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 10 seconds.
    Raises:
        AssertionError: If the maximum wait time is exceeded before the server reaches the desired status.
    
    Returns:
        bool: Indicates the success/failure in transition of the status
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        server = morpheus_api_service.server_service.get_a_specific_server(server_id)
        if server.server.status == status.value:
            return True
        else:
            logger.info(f"Waiting for server status to be '{status.value}'...")
            time.sleep(sleep_time)
    else:
        logger.info(f"Max wait time exceeded for server status '{status.value}' update.")
        return False


def wait_for_server_update(
    morpheus_api_service: MorpheusAPIService,
    server_id: int,
    new_server_id: int,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
):
    """
    Waits for a Morpheus server to update its Parent Server ID.

    This function polls the Morpheus server at regular intervals until \
        the server obtains the desired Parent Server ID or the maximum wait time is exceeded.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service used to interact with the Morpheus platform.
        server_id (str): The ID of the server to check.
        new_server_id (int): The ID of the server to check.
        max_wait_time (int, optional): The maximum time to wait for the server to reach the desired status, \
            in seconds. Defaults to 1800 seconds (30 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 10 seconds.
    Raises:
        AssertionError: If the maximum wait time is exceeded before the server reaches the desired status.
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        server = morpheus_api_service.server_service.get_a_specific_server(server_id)
        if (server.server.parent_server.id == new_server_id) and (
            server.server.preferred_parent_server.id == new_server_id
        ):
            return
        else:
            logger.info(f"Waiting for server to be '{new_server_id}'...")
            time.sleep(sleep_time)

    else:
        assert False, f"Max wait time exceeded for server '{new_server_id}' update."


def enable_maintenance_mode(
    morpheus_api_service: MorpheusAPIService, server_id: int, timeout_in_seconds: int = 300
) -> bool:
    """Fuction enable the maintenance mode and validate the server has successfully entered the mode.

    Args:
        server_id (int): host or server id
        timeout_in_seconds (int): Time out in seconds to enter the maintenence mode. Min 30 seconds

    Returns:
        result (bool): Status of the operation.
    """
    # Enable maintenance mode
    morpheus_api_service.server_service.enable_maintenance_mode(server_id=server_id)
    # Check host status is "maintenance"
    sleep_time: int = 30
    # Check the server status for every 30 seconds till the timeout.
    result = wait_for_server_status_update(
        morpheus_api_service=morpheus_api_service,
        server_id=server_id,
        status=ServerStatus.MAINTENANCE,
        max_wait_time=timeout_in_seconds,
        sleep_time=sleep_time,
    )
    return result


def leave_maintenance_mode(
    morpheus_api_service: MorpheusAPIService, server_id: int, timeout_in_seconds: int = 300
) -> bool:
    """Function leave the maintenance mode for the sever and validate the server has successfully exited the mode.

    Args:
        server_id (int): host or server id
        timeout_in_seconds (int): Time out in seconds to leave the maintenence mode. Min 30 seconds.

    Returns:
        bool: Status of the operation within the specified tiemout.
    """
    # Leave maintenance mode
    morpheus_api_service.server_service.leave_maintenance_mode(server_id=server_id)
    # Check host status is "provisioned"
    sleep_time: int = 30
    # Check the server status for every 30 seconds till the timeout.
    result = wait_for_server_status_update(
        morpheus_api_service=morpheus_api_service,
        server_id=server_id,
        status=ServerStatus.PROVISIONED,
        max_wait_time=timeout_in_seconds,
        sleep_time=sleep_time,
    )
    return result
