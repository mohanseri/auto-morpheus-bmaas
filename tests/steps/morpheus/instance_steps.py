import logging
import time
import random
from typing import Any
from lib.common.enums.backup_status import BackupStatus
from lib.common.enums.environment_code import EnvironmentCode
from lib.common.enums.instance_status import InstanceStatus
from lib.common.enums.instance_type_code import InstanceTypeCode
from lib.common.enums.ip_mode import IPMode
from lib.common.enums.process_status import ProcessStatus
from lib.common.enums.process_type import ProcessType
from lib.common.enums.snapshot_status import SnapshotStatus
from lib.common.enums.virtual_image_status import VirtualImageStatus
from morpheus_api.dataclasses.common_objects import ID, Code, IDCode, IDName, NameValue, CommonRequiredData
from morpheus_api.dataclasses.instance import (
    Instance,
    InstanceDetails,
    InstanceCreateData,
    InstanceData,
    InstanceList,
    InstanceResize,
    InstanceResizeData,
    InstanceUpdatePayload,
    ConfigUpdateData,
    InstanceUpdateData,
    InstanceSnapshotImport,
    InstanceNetworkInterface,
)
from morpheus_api.dataclasses.server import ServerNetworkInterface
from morpheus_api.dataclasses.backup import BackupData
from morpheus_api.dataclasses.network import Interface, InterfaceNetwork, NetworkID, NetworkInterface
from morpheus_api.dataclasses.processes import ProcessList
from morpheus_api.dataclasses.snapshot import SnapshotsList
from morpheus_api.dataclasses.volume import Volume
from morpheus_api.dataclasses.virtual_image import VirtualImage
from morpheus_api.settings import MorpheusAPIService, MorpheusSettings
from tests.steps.morpheus.common_steps import get_required_data, build_network_interface
from tests.steps.container_steps import wait_for_container_deletion, wait_for_container_status_update
from tests.steps.morpheus.virtual_image_steps import wait_for_virtual_image_creation, wait_for_virtual_image_status


settings = MorpheusSettings()

logger = logging.getLogger()

"""This module contains steps for ALL instance-related operations."""


def get_instance_status_by_id(morpheus_api_service: MorpheusAPIService, instance_id: int) -> str:
    """
    Helper function to get the instance status by ID.

    Args:
        morpheus_api_service (MorpheusAPIService): The service to interact with the Morpheus API.
        instance_id (int): The ID of the instance whose status is to be retrieved.
    Returns:
        str: The status of the instance.
    """
    vm: Instance = morpheus_api_service.instance_service.get_instance(instance_id)
    return vm.instance.status


def get_instance_locked_state_by_id(morpheus_api_service: MorpheusAPIService, instance_id: int) -> bool:
    """
    Helper function to get the instance locked state by ID.

    Args:
        morpheus_api_service (MorpheusAPIService): The service to interact with the Morpheus API.
        instance_id (int): The ID of the instance whose status is to be retrieved.
    Returns:
        bool: The locked state of the instance.
    """
    vm: Instance = morpheus_api_service.instance_service.get_instance(instance_id)
    return vm.instance.locked


def get_instance_id_by_name(morpheus_api_service: MorpheusAPIService, instance_name: str) -> str:
    """
    Helper function to get the instance ID by instance name.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service object used to interact \
            with the Morpheus API.
        instance_name (str): The name of the instance for which the ID is to be retrieved.
    Returns:
        int: The ID of the instance with the specified name.
    Raises:
        IndexError: If no instance with the specified name is found.
    """
    instance_list: InstanceList = morpheus_api_service.instance_service.list_instances(filter=f"name={instance_name}")
    return instance_list.instances[0].id


def get_volumes_count(morpheus_api_service: MorpheusAPIService, instance_id: int) -> int:
    """
    Helper function to get the count of volumes for an instance, excluding CD ROMs.

    Args:
        morpheus_api_service (MorpheusAPIService): The service used to interact with the Morpheus API.
        instance_id (int): The ID of the instance for which to count the volumes.
    Returns:
        int: The count of volumes excluding CD ROMs.
    """
    vm: Instance = morpheus_api_service.instance_service.get_instance(instance_id)
    volumes = vm.instance.volumes
    non_cd_rom_volumes = [volume for volume in volumes if volume.name != "CD Drive"]
    return len(non_cd_rom_volumes)


def instance_resize_payload(
    plan_id: int,
    volumes: list[Volume],
    network_interfaces: list[NetworkInterface],
    delete_original_volumes: bool = False,
) -> InstanceResizeData:
    """
    Fixture for instance resize payload.

    Args:
        plan_id (int): The identifier of the new plan to which the instance will be resized.
        volumes (list[Volume]): A list of Volume objects representing the volumes attached to the instance.
        network_interfaces (list[NetworkInterface]): A list of NetworkInterface objects representing the
        network interfaces attached to the instance.
        delete_original_volumes (bool, optional): A flag to indicate whether the original volumes should be deleted. (Amazon only)
    Returns:
        InstanceResizeData: An object containing the instance resize data, including:
            - instance: An InstanceResize object with the instance ID and plan ID.
            - volumes: A list of Volume objects for the instance.
            - network_interfaces: A list of NetworkInterface objects for the instance.
    """
    instance_data = InstanceResize(plan=ID(id=plan_id))

    network_interfaces = network_interfaces

    return InstanceResizeData(
        instance=instance_data,
        volumes=volumes,
        network_interfaces=network_interfaces,
        delete_original_volumes=delete_original_volumes,
    )


def reconfigure_instance(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    plan_id: int = None,
    volumes_to_add: list[Volume] = None,
    volumes_to_remove: list[int] = None,
    network_interfaces_to_add: list[NetworkInterface] = None,
    network_interfaces_to_remove: list[str] = None,
    delete_original_volumes: bool = False,
) -> tuple[bool, Instance]:
    """
    Helper function to reconfigure an instance by resizing it, adding or removing volumes, and network interfaces.

    Args:
        morpheus_api_service (MorpheusAPIService): The service used to interact with the Morpheus API.
        instance_id (int): The ID of the instance to be reconfigured.
        plan_id (int, optional): The ID of the new plan to which the instance will be resized. Defaults to None.
        volumes_to_add (list[Volume], optional): A list of Volume objects to be added or updated to the instance. \
            If a volume.id is not -1, then that volume will be updated if it is found in the instance. Defaults to None.
        volumes_to_remove (list[int], optional): A list of volume IDs to be removed from the instance. Defaults to None.
        network_interfaces_to_add (list[NetworkInterface], optional): A list of NetworkInterface objects to be added or updated to the instance. \
            Defaults to None.
        network_interfaces_to_remove (list[str], optional): A list of network interface IDs to be removed from the instance. \
            Defaults to None.
        delete_original_volumes (bool, optional): A flag to indicate whether the original volumes should be deleted. \
            Defaults to False. (Amazon only)

    Returns:
        Boolean: It will return true if successful else will return as False
        Instance: The updated instance object representing the reconfigured instance if successul else will return None
    """
    instance_result = False
    # build payload for instance resize
    instance_resize: InstanceResize = None
    if plan_id:
        instance_resize = InstanceResize(plan=ID(id=plan_id))

    # get the current list of Volumes for the Instance
    instance: Instance = morpheus_api_service.instance_service.get_instance(instance_id)
    volumes = instance.instance.volumes

    # if volumes_to_remove is present, remove matching Volumes from the list; don't remove root_volume
    if volumes_to_remove:
        volumes = [volume for volume in volumes if (volume.id not in volumes_to_remove or volume.root_volume is True)]

    # if volumes_to_add is present, add them to the list if their id is -1 (new volume)
    # otherwise, update the existing volume with the same id
    if volumes_to_add:
        for volume in volumes_to_add:
            if volume.id == -1:
                volumes.append(volume)
            else:
                for i, vol in enumerate(volumes):
                    if vol.id == volume.id:
                        volumes[i] = volume

    # get the current list of Network Interfaces for the Instance
    # 1) cannot delete the primary interface (row == 0)
    # 2) all Nodes of an Instance will have the same number of network interfaces as the Instance
    interfaces = instance.instance.interfaces

    # NOTE
    # We need to sanitize the "interfaces" returned from the Instance, it may likely be inaccurate/incomplete
    # The Morpheus UI is able to obtain this data, and it appears that they are using the data from the Server(s)
    # contained within the Instance. In my testing, one (1) of the contained Servers will coincide with the Instance
    # interface data. The interface lists between Instance and Server appears to always be sorted, which helps greatly.
    interfaces = sanitize_instance_interface_data(morpheus_api_service, interfaces, instance.instance.servers)

    # if network_interfaces_to_remove is present, remove matching Network Interfaces from the list.
    # Don't remove primary_interface (row == 0)
    if network_interfaces_to_remove:
        interfaces = [
            interface
            for interface in interfaces
            if (interface.id not in network_interfaces_to_remove or interface.row == 0)
        ]

    # we need to obtain the "network-1" name
    required_data = get_required_data(morpheus_api_service)

    # before adding new interfaces, we need to convert the list[InstanceNetworkInterface] to list[NetworkInterface]
    resize_interfaces: list[NetworkInterface] = []
    for interface in interfaces:
        resize_interfaces.append(
            NetworkInterface(
                primary_interface=interface.row == 0,
                network=NetworkID(id=required_data.network_id),
                ip_mode=interface.ip_mode,
                ip_address=interface.ip_address,
                id=interface.id,
            )
        )

    # if network_interfaces_to_add is present, add them to the list
    if network_interfaces_to_add:
        for interface in network_interfaces_to_add:
            if interface.id is None:
                resize_interfaces.append(interface)
            else:
                for i, intf in enumerate(resize_interfaces):
                    if intf.id == interface.id:
                        resize_interfaces[i] = interface

    instance_resize_data = InstanceResizeData(
        instance=instance_resize,
        volumes=volumes,
        network_interfaces=resize_interfaces,
        delete_original_volumes=delete_original_volumes,
    )
    logger.info(f"Payload built: {instance_resize_data}")

    # make the API call
    _, reconfiguring_instance = morpheus_api_service.instance_service.resize_instance(
        instance_id=instance_id, resize_payload=instance_resize_data
    )
    logger.info(f"Resize operation success. Status: {reconfiguring_instance.instance.status}")

    # wait for the instance to reach a RUNNING state again.
    instance_result = wait_for_instance_status_update(
        morpheus_api_service, instance_id, InstanceStatus.RUNNING, max_wait_time=3600  # 1 hour
    )

    # get the updated instance to return (for disk size changes, for example)
    return instance_result, morpheus_api_service.instance_service.get_instance(instance_id)


def sanitize_instance_interface_data(
    morpheus_api_service: MorpheusAPIService,
    instance_interfaces: list[InstanceNetworkInterface],
    instance_servers: list[int],
) -> list[InstanceNetworkInterface]:
    """
    Helper function to sanitize the instance interface data.

    Args:
        morpheus_api_service (MorpheusAPIService): The service used to interact with the Morpheus API.
        instance_interfaces (list[InstanceNetworkInterface]): The list of instance network interfaces to be sanitized.
        instance_servers (list[int]): The list of instance servers.

    Returns:
        list[InstanceNetworkInterface]: The sanitized list of instance network interfaces.
    """
    # NOTE: This is temporary code to sanitize the Instance interface data
    #
    # If the 1st Instance Interface has no "row" (None) we have a new Instance; grab the 1st Server interface data.
    # Otherwise, the Instance interface will have a valid "id". Use this value to return
    # the relevant Server interface data
    server_interfaces: list[ServerNetworkInterface] = []

    if instance_interfaces[0].row is None or instance_interfaces[0].row == 0:
        server_id = instance_servers[0]
        server_interfaces = morpheus_api_service.server_service.get_a_specific_server(server_id).server.interfaces
    else:
        server_interfaces = get_server_interfaces_matching_interface_id(
            morpheus_api_service, instance_servers, instance_interfaces[0].id
        )

    # check to ensure we have server interfaces
    assert len(server_interfaces) > 0, "No server interfaces found for the instance"

    # for each server interface, update the corresponding instance interface "id" and "row"; (row 0 is "primary_interface")
    # "ip_mode", "ip_address"
    for i, server_interface in enumerate(server_interfaces):
        instance_interfaces[i].id = str(server_interface.id)
        instance_interfaces[i].row = i
        instance_interfaces[i].ip_mode = IPMode.DHCP.value if server_interface.dhcp is True else IPMode.STATIC.value
        instance_interfaces[i].ip_address = server_interface.ip_address if server_interface.dhcp is False else None

    return instance_interfaces


def get_server_interfaces_matching_interface_id(
    morpheus_api_service: MorpheusAPIService, instance_servers: list[int], interface_id: str
) -> list[ServerNetworkInterface]:
    """
    Helper function to get the server interfaces matching the interface ID.

    Args:
        morpheus_api_service (MorpheusAPIService): The service used to interact with the Morpheus API.
        instance_servers (list[int]): The list of instance servers.
        interface_id (str): The ID of the interface to be matched.

    Returns:
        list[ServerNetworkInterface]: The list of server network interfaces matching the interface ID.
    """
    # NOTE: This is temporary code to sanitize the Instance interface data
    #
    # The interface "id" on the Instance is a "str", while the interface "id" on the Server(s) is an "int".
    interface_id_int = int(interface_id)

    for server_id in instance_servers:
        server_interfaces = morpheus_api_service.server_service.get_a_specific_server(server_id).server.interfaces
        for interface in server_interfaces:
            if interface.id == interface_id_int:
                return server_interfaces

    return []


def create_instance_payload(
    instance_name: str,
    layout_id: int,
    layout_code: str,
    layout_size: str,
    plan_id: int,
    plan_code: str,
    site_id: int,
    instance_context: str,
    instance_copies: int,
    config: dict[str, Any],
    zone_id: int,
    volumes: list[Volume],
    network_interfaces: list[NetworkInterface] = [],
    interfaces: list[Interface] = [],
    instance_type_code: InstanceTypeCode = InstanceTypeCode.MVM,
) -> InstanceCreateData:
    """
    Creates and returns the payload required for instance creation.

    Args:
        instance_name (str): The name of the instance to be created.
        layout_id (int): The identifier of the layout to be used for the instance.
        layout_code (str): The code of the layout to be used for the instance.
        layout_size (str): The size of the layout to be used for the instance.
        plan_id (int): The identifier of the plan to be used for the instance.
        plan_code (str): The code of the plan to be used for the instance.
        site_id (int): The identifier of the site where the instance will be created.
        instance_context (str): The context or description of the instance.
        instance_copies (int): The number of copies of the instance to be created.
        config (dict[str, Any]): A dictionary containing configuration settings for the instance.
        zone_id (int): The identifier of the zone where the instance will be created.
        volumes (list[Volume]): A list of Volume objects representing the volumes to be attached to the instance.
        network_interfaces (list[NetworkInterface]): A list of NetworkInterface objects representing the
        network interfaces to be attached to the instance.
        instance_type_code (InstanceTypeCode, optional): The code representing the type of instance to be created.
        Defaults to InstanceTypeCode.MVM.

    Returns:
        InstanceCreateData: An object containing all the necessary data for
        creating an instance, including instance details, copies, layout size,
        configuration, zone ID, volumes, and network interfaces.
    """
    layout = IDCode(id=layout_id, code=layout_code)
    plan = IDCode(id=plan_id, code=plan_code)

    instance_data = InstanceData(
        type=instance_type_code.value,
        site=ID(id=site_id),
        instanceType=Code(code=instance_type_code.value),
        layout=layout,
        plan=plan,
        name=instance_name,
        instance_context=instance_context,
    )

    instance_create_data = InstanceCreateData(
        instance=instance_data,
        copies=instance_copies,
        layout_size=layout_size,
        config=config,
        zone_id=zone_id,
        volumes=volumes,
    )

    if network_interfaces:
        instance_create_data.network_interfaces = network_interfaces
    else:
        instance_create_data.interfaces = interfaces

    return instance_create_data


def import_snapshot_for_instance(
    morpheus_api_service: MorpheusAPIService, instance_id: int, template_name: str, storage_bucket_id: int = 0
) -> VirtualImage:
    """
    Helper function to import a snapshot for an instance.

    Args:
        morpheus_api_service (MorpheusAPIService): The service used to interact with the Morpheus API.
        instance_id (int): The ID of the instance for which the snapshot is to be imported.
        template_name (str): The name of the snapshot to be imported.
        storage_bucket_id (int, optional): The ID of the storage bucket where the snapshot is stored. Defaults to 0.

    Returns:
        VirtualImage: The virtual image object representing the imported snapshot
    """
    logger.info(f"Importing snapshot for instance: {instance_id}")

    payload = InstanceSnapshotImport(template_name=template_name, storage_provider_id=storage_bucket_id)

    api_response = morpheus_api_service.snapshot_service.import_snapshot_of_instance(
        instance_id=instance_id,
        import_snapshot_payload=payload,
    )
    assert api_response.success is True, f"Failed to import snapshot for instance: {instance_id}"
    # Wait for snapshot to appear in the list
    wait_for_virtual_image_creation(morpheus_api_service, virtual_image_name=template_name)
    # Get virtual image id
    virtual_image: VirtualImage = morpheus_api_service.virtual_image_service.list_virtual_images(
        name=template_name
    ).virtual_images[0]

    logger.info(f"virtual image ID: {virtual_image.id}")
    # Wait for snapshot to be active
    wait_for_virtual_image_status(morpheus_api_service, virtual_image.id, VirtualImageStatus.ACTIVE)
    logger.info("Snapshot imported successfully")

    return virtual_image


def create_instance_from_template(
    morpheus_api_service: MorpheusAPIService,
    template_id: int,
    instance_name: str,
    storage_volume_type_id: int,
    datastore_id: int,
    network_id: str,
    layout_id: int,
    layout_code: str,
    plan_id: int,
    plan_code: str,
    zone_id: int,
    volume_size: int = 10,
    num_volumes: int = 1,
    layout_size: int = 1,
    instance_copies: int = 1,
    wait_for_creation: bool = True,
) -> tuple[bool, Instance]:
    """
    Create an instance from a given template.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance.
        template_id (int): The ID of the template to use for the instance.
        instance_name (str): The name of the instance to be created.
        storage_volume_type_id (int): The ID of the storage volume type.
        datastore_id (int): The ID of the datastore.
        network_id (str): The ID of the network.
        layout_id (int): The ID of the layout.
        layout_code (str): The code of the layout.
        plan_id (int): The ID of the plan.
        plan_code (str): The code of the plan.
        zone_id (int): The ID of the zone.
        volume_size (int, optional): The size of each volume. Defaults to 10.
        num_volumes (int, optional): The number of volumes. Defaults to 1.
        layout_size (int, optional): The size of the layout. Defaults to 1.
        instance_copies (int, optional): The number of instance copies. Defaults to 1.
        wait_for_creation (bool, optional): Whether to wait for the instance creation & any copies to complete. Defaults to True.

    Returns:
        tuple[bool, Instance]: A tuple containing a boolean indicating success and the created instance object.
    """
    # Volumes
    volumes: list[Volume] = []

    for i in range(num_volumes):
        volumes.append(
            Volume(
                id=-1,
                root_volume=True if i == 0 else False,
                name="root" if i == 0 else f"data-{i}",
                size=volume_size,
                storage_type=storage_volume_type_id,
                datastore_id=datastore_id,
            )
        )

    nic = settings.instance_settings.network_interfaces[0]
    network_interfaces = [
        NetworkInterface(
            primary_interface=nic["primary_interface"],
            network=NetworkID(id=network_id),
            ip_mode=nic["ip_mode"],
        )
    ]

    interfaces = [
        Interface(
            id=f"network-{network_id}",
            network=InterfaceNetwork(
                id=network_id,
                group=None,
                subnet=None,
                dhcp_server=False,
                name="ArubaCX-Mgmt-Demo",
                pool=IDName(
                    id=1,
                    name="IPPool120-125",
                ),
            ),
            ip_address=None,
            network_interface_type_id=16,
            ip_mode="",
        )
    ]


    instance_config = settings.instance_settings.config
    instance_config["imageId"] = template_id

    instance_payload = create_instance_payload(
        instance_name=instance_name,
        layout_id=layout_id,
        layout_code=layout_code,
        layout_size=layout_size,
        plan_id=plan_id,
        plan_code=plan_code,
        site_id=settings.instance_settings.site_id,
        instance_context=None,
        instance_copies=instance_copies,
        config=instance_config,
        zone_id=zone_id,
        volumes=volumes,
        interfaces=interfaces,
        instance_type_code=InstanceTypeCode.BM
    )

    # Create instance
    logger.info(f"Creating instance '{instance_name}'...")
    create_response: Instance = morpheus_api_service.instance_service.create_instance(instance_payload=instance_payload)
    logger.info(f"Instance created successfully: {create_response}")

    instance_copies: list[InstanceDetails] = []
    instance_result: bool = None
    instance_results: list[bool] = []
    instance_id: int = create_response.instance.id
    if wait_for_creation:
        instance_result: bool = wait_for_instance_status_update(
            morpheus_api_service, instance_id, InstanceStatus.RUNNING
        )
        instance_results.append(instance_result)

        if create_response.copies:
            for instance in create_response.copies:
                logger.info(f"Wait for Instance: {instance}")
                instance_copy_result: bool = wait_for_instance_status_update(
                    morpheus_api_service, instance.id, InstanceStatus.RUNNING
                )
                instance_results.append(instance_copy_result)
                instance_copy: Instance = morpheus_api_service.instance_service.get_instance(instance.id)
                instance_copies.append(instance_copy.instance)

        if False in instance_results:
            instance_result = False

    created_instance: Instance = morpheus_api_service.instance_service.get_instance(instance_id)
    created_instance.copies = instance_copies

    return instance_result, created_instance


def delete_instance(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    wait_for_deletion: bool = True,
    force: str = "off",
):
    """
    Helper function to delete an instance.

    Args:
        morpheus_api_service (MorpheusAPIService): The service used to interact with the Morpheus API.
        instance_id (int): The ID of the instance to be deleted.
        wait_for_deletion (bool, optional): A flag to indicate whether to wait for the instance to be deleted. Defaults to True.
        force (str, optional): A flag to indicate whether to force delete the instance. Defaults to off.
    """
    logger.info(f"Deleting instance: {instance_id}")
    morpheus_api_service.instance_service.delete_instance(instance_id=instance_id, force=force)
    if wait_for_deletion:
        wait_for_instance_deletion(morpheus_api_service, instance_id)
    logger.info(f"Instance '{instance_id}' deleted successfully")


def wait_for_instance_status_update(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    status: InstanceStatus,
    max_wait_time: int = 3600,
    sleep_time: int = 10,
):
    """
    Waits for a Morpheus instance to reach a specified status.

    This function polls the status of a Morpheus instance at regular intervals until \
        the instance reaches the desired status or the maximum wait time is exceeded.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service used to interact with the Morpheus platform.
        instance_id (int): The ID of the instance to check.
        status (InstanceStatus): The desired status to wait for.
        max_wait_time (int, optional): The maximum time to wait for the instance to reach the desired status, \
            in seconds. Defaults to 3600 seconds (60 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 10 seconds.

    Return:
        Boolean: It will return true if successful else will return as False
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        vm: Instance = morpheus_api_service.instance_service.get_instance(instance_id)
        if vm.instance.status == status.value:
            logger.info(f"Instance id {instance_id} status in the expected state now '{status.value}'")
            return True
        elif vm.instance.status == InstanceStatus.FAILED.value:
            logger.error(f"Instance id {instance_id} status has changed to failed.")
            return False
        else:
            logger.info(f"Waiting for instance status to be '{status.value}'...")
            time.sleep(sleep_time)

    else:
        logger.error(f"Max wait time exceeded for instance status '{status.value}' update.")

    return False


def wait_for_instance_deletion(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
):
    """
    Waits for an instance to be deleted.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance to wait for deletion.
        max_wait_time (int, optional): The maximum time to wait for the instance to be deleted, in seconds. \
            Defaults to 1800.
        sleep_time (int, optional): The time to sleep between status checks, in seconds. Defaults to 10.
    Raises:
        AssertionError: If the maximum wait time is exceeded before the instance is deleted.
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        try:
            morpheus_api_service.instance_service.get_instance(instance_id)
        except Exception as e:
            if "Not Found" in str(e):
                return
        logger.info(f"Waiting for instance {instance_id} to be deleted...")
        time.sleep(sleep_time)
    else:
        assert False, f"Max wait time exceeded for instance deletion: {instance_id}."


def wait_for_instance_snapshot_status_update(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    status: SnapshotStatus,
    max_wait_time: int = 120,
    sleep_time: int = 10,
):
    """
    Waits for the status of the latest snapshot of a given instance to update to the specified status.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance whose snapshot status is to be checked.
        status (SnapshotStatus): The desired status to wait for.
        max_wait_time (int, optional): The maximum time to wait for the status update, in seconds. Defaults to 120.
        sleep_time (int, optional): The time to sleep between status checks, in seconds. Defaults to 10.
    Raises:
        AssertionError: If the maximum wait time is exceeded without the snapshot status updating to the desired status.
    """
    # NOTE: This function has been updated to check the status of all Snapshots in the instance.

    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        snapshots: SnapshotsList = morpheus_api_service.snapshot_service.list_instance_snapshots(instance_id)
        logger.info(f"Checking {len(snapshots.snapshots)} snapshots for status '{status.value}'")
        for snapshot in snapshots.snapshots:
            if snapshot.status.lower() != status.value:
                logger.info(f"Snapshot id {snapshot.id} status is not in the expected state now '{status.value}'")
                break
            # if we make it here, we're good
            logger.info("were done checking - success")
            return
        # if we get here, we need to wait
        logger.info(f"Waiting for snapshot to (complete): {status.value}...")
        time.sleep(sleep_time)
    else:
        assert False, f"Max wait time exceeded for snapshot status '{status.value}' update."


def wait_for_instance_cloning(
    morpheus_api_service: MorpheusAPIService,
    cloned_instance_name: str,
    status: InstanceStatus = InstanceStatus.RUNNING,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
) -> tuple[bool, InstanceDetails]:
    """Waits for the clone VM instance to become available

    Args:
        morpheus_api_service (MorpheusAPIService): Base MorpheusAPIService initialized with base_url and api_token
        cloned_instance_name (str): Name given to the cloned instance
        status (str, optional): Expected status of the cloned VM. Defaults to InstanceStatus.RUNNING.
        max_wait_time (int, optional): Maximum time to wait for the VM to be available. Defaults to 1800 seconds.
        sleep_time (int, optional): Time to wait before trying to find the VM again. Defaults to 10 seconds.

    Returns:
        Boolean: It will return true if successful else will return as False
        InstanceDetails: Cloned InstanceDetails object if operation is successful else will return None
    """
    result = False
    cloned_instance: InstanceDetails = None
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        instance_list: InstanceList = morpheus_api_service.instance_service.list_instances(
            filter=f"name={cloned_instance_name}"
        )

        if len(instance_list.instances) == 1 and instance_list.instances[0].name == cloned_instance_name:
            cloned_instance = instance_list.instances[0]
            result = True
            break
        else:
            logger.info(f"Waiting for cloned instance {cloned_instance_name} to become available")
            time.sleep(sleep_time)
    else:
        logger.error(f"Max wait time exceeded for cloned instance {cloned_instance_name} to become available")

    if result:
        result = wait_for_instance_status_update(
            morpheus_api_service=morpheus_api_service,
            instance_id=cloned_instance.id,
            status=status,
            max_wait_time=max_wait_time,
            sleep_time=sleep_time,
        )

    return result, cloned_instance


def wait_for_instance_backup_status_update(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    status: BackupStatus,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
):
    """
    Waits for the backup status of a given instance to update to the desired status.
    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance whose backup status is being monitored.
        status (BackupStatus): The desired backup status to wait for.
        max_wait_time (int, optional): The maximum time to wait for the status update in seconds. \
            Defaults to 1800 seconds.
        sleep_time (int, optional): The time to sleep between status checks in seconds. Defaults to 10 seconds.
    Raises:
        AssertionError: If the maximum wait time is exceeded without the backup status updating to the desired status.
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        backups_list: BackupData = morpheus_api_service.backup_service.list_instance_backups(instance_id)
        if len(backups_list.backups) > 0 and backups_list.backups[0].backup_results[0].status.lower() == status.value:
            return
        else:
            logger.info(f"Waiting for backup to (be in succeeded state): '{status.value}'...")
            time.sleep(sleep_time)
    else:
        assert False, f"Max wait time exceeded for backup status '{status.value}' update."


def wait_for_instance_backup_count(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    expected_backup_count: int,
    max_wait_time: int = 1200,
    sleep_time: int = 30,
):
    """Wait for the expected backup count for an instance

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance whose backup status is being monitored.
        expected_backup_count (int): Number of backups expected for the provided instance
        max_wait_time (int, optional): The maximum time to wait for the status update in seconds. \
            Defaults to 1200 seconds.
        sleep_time (int, optional): The time to sleep between status checks in seconds. Defaults to 30 seconds.
    Raises:
        AssertionError: If the max wait time exceeds without the backup count equal to the expected backup count.
    """
    backup_list: BackupData = None
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        backup_list = morpheus_api_service.backup_service.list_instance_backups(instance_id)
        if len(backup_list.backups) == expected_backup_count:
            return
        else:
            logger.info(f"Waiting for backup count to reach {expected_backup_count}")
            time.sleep(sleep_time)
    else:
        assert False, f"Expected backup count {expected_backup_count} != {len(backup_list.backups)}"


def wait_for_instance_snapshot_count(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    expected_snapshot_count: int,
    max_wait_time: int = 1200,
    sleep_time: int = 30,
) -> bool:
    """Wait for the expected backup count for an instance

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance whose backup status is being monitored.
        expected_snapshot_count (int): Number of snapshots expected for the provided instance
        max_wait_time (int, optional): The maximum time to wait for the status update in seconds. \
            Defaults to 1200 seconds.
        sleep_time (int, optional): The time to sleep between status checks in seconds. Defaults to 30 seconds.
    Returns:
        Boolean: True if wait for snapshot count is successful, or False when time taken has exceeded maximum time.
    """
    snapshot_list: SnapshotsList = None
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        snapshot_list: SnapshotsList = morpheus_api_service.snapshot_service.list_instance_snapshots(instance_id)
        if len(snapshot_list.snapshots) == expected_snapshot_count:
            return True
        else:
            logger.info(f"Waiting for snapshot count to reach {expected_snapshot_count}")
            time.sleep(sleep_time)
    else:
        return False


def wait_for_instance_history_process_status_update(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    status: ProcessStatus = ProcessStatus.COMPLETE,
    process_type: ProcessType = ProcessType.STARTUP,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
):
    """Waits for the instance process type status to update to the specified status.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance whose process status is to be checked.
        status (ProcessStatus, optional): The desired status to wait for. Defaults to ProcessStatus.COMPLETE.
        process_type (ProcessType, optional): The type of process to check the status for. Defaults to ProcessType.STARTUP.
        max_wait_time (int, optional): The maximum time to wait for the status update, in seconds. Defaults to 1800.
        sleep_time (int, optional): The time to sleep between status checks, in seconds. Defaults to 10.
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        instance_history: ProcessList = morpheus_api_service.instance_service.get_instance_history(instance_id)
        process = instance_history.processes[0]
        if process.process_type.name == process_type.value and process.status == status.value:
            return
        else:
            logger.info(f"Waiting for instance status to be '{status.value}'...")
            time.sleep(sleep_time)
    else:
        assert False, f"Max wait time exceeded for instance status '{status.value}' update."


def create_instance_update_payload(
    name: str = None,
    display_name: str = None,
    owner_id: int = None,
    instance_context: EnvironmentCode = None,
    description: str = None,
    labels: list[str] = None,
    tags: list[NameValue] = None,
    add_tags: list[NameValue] = None,
    remove_tags: list[NameValue] = None,
    power_schedule_type: int = None,
    site_id: int = None,
    custom_options: dict[str, str] = None,
) -> InstanceUpdatePayload:
    """
    Creates and returns the payload required for updating an instance.

    Args:
        name (str, optional): The name of the instance. Defaults to None.
        display_name (str, optional): The display name of the instance. Defaults to None.
        owner_id (int, optional): The ID of the owner of the instance. Defaults to None.
        instance_context (EnvironmentCode, optional): The context or description of the instance. Defaults to None.
        description (str, optional): The description of the instance. Defaults to None.
        labels (list[str], optional): The labels associated with the instance. Defaults to None.
        tags (list[NameValue], optional): The tags associated with the instance. Defaults to None.
        add_tags (list[NameValue], optional): The tags to be added to the instance. Defaults to None.
        remove_tags (list[NameValue], optional): The tags to be removed from the instance. Defaults to None.
        power_schedule_type (int, optional): The power schedule type of the instance. Defaults to None.
        site_id (int, optional): The ID of the site where the instance is located. Defaults to None.
        custom_options (dict[str, str], optional): The custom options for the instance. Defaults to None.

    Returns:
        InstanceUpdatePayload: An object containing the instance update payload, including:
            - instance: An InstanceUpdateData object with the instance details to be updated.
            - config: A ConfigUpdateData object with the custom options to be updated.
    """
    instance_payload: InstanceUpdateData = InstanceUpdateData(
        name=name,
        display_name=display_name,
        owner_id=owner_id,
        instance_context=instance_context.value if instance_context else None,
        description=description,
        labels=labels,
        tags=tags,
        add_tags=add_tags,
        remove_tags=remove_tags,
        power_schedule_type=power_schedule_type,
        site=ID(id=site_id) if site_id else None,
    )
    config_payload: ConfigUpdateData = ConfigUpdateData(
        custom_options=custom_options,
    )

    payload: InstanceUpdatePayload = InstanceUpdatePayload(instance=instance_payload, config=config_payload)
    return payload


def start_instances(
    morpheus_api_service: MorpheusAPIService,
    instance_id_list: list[int],
    data=None,
    query_params=None,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
    wait_for_instance: bool = True,
) -> bool:
    """
    Start the specified instances and wait until instance has started if needed

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id_list (list): Instance id list
        data (dict, optional): The data to send in the request body. Defaults to None.
        query_params (dict, optional): The query parameters to include in the request URL. Defaults to None.
        wait_for_instance (bool, optional): Flag to wait until instances are started. Defaults to True.

    Returns:
        Returns True if all instances started successfully
        Return False if any one of the instance failed to start
    """
    result: bool = True
    for instance_id in instance_id_list:
        logger.info(f"Powering on instance id {instance_id}")
        response = morpheus_api_service.instance_service.start_instance(
            instance_id,
            data,
            query_params,
        )
        logger.info(f"Instance id {instance_id} start Instance Response: {response}")

    if wait_for_instance:
        for instance_id in instance_id_list:
            logger.info(f"Waiting for instance id {instance_id} to start")
            instance_status = wait_for_instance_status_update(
                morpheus_api_service,
                instance_id,
                InstanceStatus.RUNNING,
                max_wait_time,
                sleep_time,
            )
            if instance_status is False:
                result = instance_status
                logger.error(f"Failed to start the instance id {instance_id}")
            else:
                logger.info(f"Instance id {instance_id} is in Running state now")

    return result


def stop_instances(
    morpheus_api_service: MorpheusAPIService,
    instance_id_list: list[int],
    data=None,
    query_params=None,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
    wait_for_instance: bool = True,
) -> bool:
    """
    Stop the specified instances and wait until instance has been stopped if needed

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id_list (list): Instance id list
        data (dict, optional): The data to send in the request body. Defaults to None.
        query_params (dict, optional): The query parameters to include in the request URL. Defaults to None.
        max_wait_time (int, optional): The maximum time to wait for the instance to reach the desired status, \
            in seconds. Defaults to 1800 seconds (30 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 10 seconds.
        wait_for_instance (bool, optional): Flag to wait until instances are stopped. Defaults to True.

    Returns:
        Returns True if all instances stopped successfully
        Return False if any one of the instance failed to stop
    """
    result: bool = True
    for instance_id in instance_id_list:
        logger.info(f"Powering off instance id {instance_id}")
        response = morpheus_api_service.instance_service.stop_instance(
            instance_id,
            data,
            query_params,
        )
        logger.info(f"Instance id {instance_id} stop Instance Response: {response}")

    if wait_for_instance:
        for instance_id in instance_id_list:
            logger.info(f"Waiting for instance id {instance_id} to power off")
            instance_status = wait_for_instance_status_update(
                morpheus_api_service,
                instance_id,
                InstanceStatus.STOPPED,
                max_wait_time,
                sleep_time,
            )
            if instance_status is False:
                result = instance_status
                logger.error(f"Failed to stop the instance id {instance_id}")
            else:
                logger.info(f"Instance id {instance_id} is in stopped state now")

    return result


def suspend_instances(
    morpheus_api_service: MorpheusAPIService,
    instance_id_list: list[int],
    data=None,
    query_params=None,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
    wait_for_instance: bool = True,
) -> bool:
    """
    Suspend the specified instances and wait until instance has been suspended if needed

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id_list (list): Instance id list
        data (dict, optional): The data to send in the request body. Defaults to None.
        query_params (dict, optional): The query parameters to include in the URL. Defaults to None.
        max_wait_time (int, optional): The maximum time to wait for the instance to reach the desired status, \
            in seconds. Defaults to 1800 seconds (30 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 10 seconds.
        wait_for_instance (bool, optional): Flag to wait until instances are suspended. Defaults to True.

    Returns:
        Returns True if all instances suspended successfully
        Return False if any one of the instance failed to suspend
    """
    result: bool = True
    for instance_id in instance_id_list:
        logger.info(f"Suspending instance id {instance_id}")
        response = morpheus_api_service.instance_service.suspend_instance(
            instance_id,
            data,
            query_params,
        )
        logger.info(f"Instance id {instance_id} suspend Instance Response: {response}")

    if wait_for_instance:
        for instance_id in instance_id_list:
            logger.info(f"Waiting for instance id {instance_id} to suspend")
            instance_status = wait_for_instance_status_update(
                morpheus_api_service,
                instance_id,
                InstanceStatus.SUSPENDED,
                max_wait_time,
                sleep_time,
            )
            if instance_status is False:
                result = instance_status
                logger.error(f"Failed to suspend the instance id {instance_id}")
            else:
                logger.info(f"Instance id {instance_id} is in suspended state now")

    return result


def restart_instances(
    morpheus_api_service: MorpheusAPIService,
    instance_id_list: list[int],
    data=None,
    query_params=None,
    max_wait_time: int = 1800,
    sleep_time: int = 10,
    wait_for_instance: bool = True,
) -> bool:
    """
    Restart the specified instances and wait until instance has been restarted if needed

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id_list (list): Instance id list
        data (dict, optional): The data to send in the request body. Defaults to None.
        query_params (dict, optional): The query parameters to include in the request URL. Defaults to None.
        max_wait_time (int, optional): The maximum time to wait for the instance to reach the desired status, \
            in seconds. Defaults to 1800 seconds (30 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 10 seconds.
        wait_for_instance (bool, optional): Flag to wait until instances are restart. Defaults to True.

    Returns:
        Returns True if all instances restarted successfully
        Return False if any one of the instance failed to restart
    """
    result: bool = True
    for instance_id in instance_id_list:
        logger.info(f"Restarting instance id {instance_id}")
        response = morpheus_api_service.instance_service.restart_instance(
            instance_id,
            data,
            query_params,
        )
        logger.info(f"Instance id {instance_id} restart Instance Response: {response}")

    if wait_for_instance:
        for instance_id in instance_id_list:
            logger.info(f"Waiting for instance id {instance_id} to restart")
            instance_status = wait_for_instance_status_update(
                morpheus_api_service,
                instance_id,
                InstanceStatus.RUNNING,
                max_wait_time,
                sleep_time,
            )
            if instance_status is False:
                result = instance_status
                logger.error(f"Failed to restart the instance id {instance_id}")
            else:
                logger.info(f"Instance id {instance_id} is in running state now")

    return result


def add_nodes_to_instance(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    number_of_nodes: int = 1,
    wait_for_creation: bool = True,
) -> tuple[int, int]:
    """This function add single/multiple nodes to instance and wait for its status.
    It returns add node request status as true/false for success/failure.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance for which nodes to be added.
        number_of_nodes (int, optional): Number of nodes to be added to instance. Defaults to 1.
        wait_for_creation (bool, optional): Defaults to True.
        if True it waits for status update of container as running.

    Returns:
        tuple[int, int]: count of container which are added successfully and in running state,
        count of container for which a creation failed
    """
    container_list = []
    failed_container_creation_count = 0
    for _ in range(number_of_nodes):
        logger.info("Add /computing server to the instance")
        response = morpheus_api_service.instance_service.add_node_to_instance(instance_id=instance_id)
        message: str = ""
        if not response.results[str(instance_id)]["success"]:
            message = response.results[str(instance_id)]["msg"]
            failed_container_creation_count += 1
            logger.error(f"Adding nodes to Instance failed: {message}")
        container_list.append(response.results[str(instance_id)]["containers"][0]["id"])

    if wait_for_creation:
        running_container_count = 0
        for container_id in container_list:
            is_container_running = wait_for_container_status_update(
                morpheus_api_service=morpheus_api_service, container_id=container_id, status=InstanceStatus.RUNNING
            )
            if is_container_running:
                running_container_count += 1
            else:
                failed_container_creation_count += 1
        return running_container_count, failed_container_creation_count
    else:
        logger.info("Add node triggered and not waiting for nodes to come in running state")
        return number_of_nodes, failed_container_creation_count


def remove_nodes_from_instance(
    morpheus_api_service: MorpheusAPIService,
    container_ids_list: list[int],
    wait_for_removal: bool = True,
) -> tuple[int, int]:
    """Removes nodes from instance and waits for removal of nodes successfully

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.        container_ids_list (list[int]): _description_
        wait_for_removal (bool, optional): Defaults to True. If true then it waits untill node is removed

    Returns:
        tuple[int, int]: count of container which are removed successfully,
        count of container for which removal failed
    """
    failed_deletion_container_count = 0
    for container_id in container_ids_list:
        logger.info("Remove /computing server to the instance")
        response = morpheus_api_service.container_service.remove_container(container_id=container_id)
        if not response.success:
            failed_deletion_container_count += 1

    if wait_for_removal:
        successful_deletion_container_count = 0
        for container_id in container_ids_list:
            is_container_removed = wait_for_container_deletion(
                morpheus_api_service=morpheus_api_service,
                container_id=container_id,
            )
            if is_container_removed:
                successful_deletion_container_count += 1
            else:
                failed_deletion_container_count += 1
        return successful_deletion_container_count, failed_deletion_container_count
    else:
        logger.info("Remove node triggered and not waiting for node deletion")
        return len(container_ids_list), failed_deletion_container_count


def get_network_interface_payload(
    morpheus_api_service: MorpheusAPIService, instance: Instance = None, required_data: CommonRequiredData = None
) -> list[NetworkInterface]:
    """
    This function resizes the instance interfaces based on the required data.
    Args:
        morpheus_api_service: The Morpheus API service instance to interact with.
        instance:   The instance for which interfaces to be resized.
        required_data: The required data for resizing the instance interfaces.
    Returns:
        resize_interface: The list of resized interfaces.
    """
    interfaces = sanitize_instance_interface_data(
        morpheus_api_service, instance.instance.interfaces, instance.instance.servers
    )
    resize_interface: list[NetworkInterface] = []
    for interface in interfaces:
        resize_interface.append(
            NetworkInterface(
                primary_interface=interface.row == 0,
                network=NetworkID(id=required_data.network_id),
                ip_mode=interface.ip_mode,
                ip_address=interface.ip_address,
                id=interface.id,
            )
        )
    return resize_interface


def add_network_interfaces_to_instance(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    wait_for_resizing: bool = True,
    number_of_interfaces_to_add: int = 1,
) -> Instance:
    """This function adds and remove single/multiple n/w interfaces to instance and wait for its status.
    It returns add interface request status as true/false for success/failure.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance for which interfaces to be added.
        wait_for_resizing (bool, optional): Defaults to True.
        if True it waits for status update of interface as attached.
        number_of_interfaces_to_add (int): Number of interfaces to be added to instance. Defaults to 1.
    Returns:
        Instance: The instance object after adding the network interfaces.
    """

    # Get the instance details
    instance = morpheus_api_service.instance_service.get_instance(instance_id)
    required_data = get_required_data(morpheus_api_service)
    # before adding new interfaces, we need to convert the list[InstanceNetworkInterface] to list[NetworkInterface]
    resize_interface = get_network_interface_payload(morpheus_api_service, instance, required_data)

    for i in range(0, number_of_interfaces_to_add):
        interface_id = random.randint(1, 1000)
        new_interface = build_network_interface(
            network_id=required_data.network_id, primary_interface=False, interface_id=str(interface_id)
        )
        resize_interface.append(new_interface)

    instance_resize_data = InstanceResizeData(
        volumes=instance.instance.volumes,
        network_interfaces=resize_interface,
    )
    response, updated_instance = morpheus_api_service.instance_service.resize_instance(
        instance_id=instance_id, resize_payload=instance_resize_data
    )
    logger.info(f"Adding network interfaces Status: {updated_instance.instance.status}")
    assert response.success, f"Failed to add network interfaces to instance {instance_id}"

    if wait_for_resizing:
        wait_for_instance_status_update(morpheus_api_service, instance_id, InstanceStatus.RUNNING)
        # get the updated list of interfaces
        updated_instance = morpheus_api_service.instance_service.get_instance(instance_id)
    return updated_instance


def remove_network_interfaces_from_instance(
    morpheus_api_service: MorpheusAPIService,
    instance_id: int,
    wait_for_resizing: bool = True,
    number_of_interfaces_to_remove: int = 1,
) -> Instance:
    """This function adds and remove single/multiple n/w interfaces to instance and wait for its status.
    It returns add interface request status as true/false for success/failure.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        instance_id (int): The ID of the instance for which interfaces to be added.
        wait_for_resizing (bool, optional): Defaults to True.
        if True it waits for status update of interface as attached.
        number_of_interfaces_to_remove (int): Number of interfaces to be removed from instance. Defaults to 1.
    Returns:
        Instance: The instance object after removing the network interfaces.
    """

    # Get the instance details
    instance = morpheus_api_service.instance_service.get_instance(instance_id)
    required_data = get_required_data(morpheus_api_service)
    # before adding new interfaces, we need to convert the list[InstanceNetworkInterface] to list[NetworkInterface]
    resize_interface = get_network_interface_payload(morpheus_api_service, instance, required_data)

    for i in range(0, number_of_interfaces_to_remove):
        for interface in resize_interface:
            if interface.primary_interface is False:
                resize_interface.remove(interface)

    instance_resize_data = InstanceResizeData(
        volumes=instance.instance.volumes,
        network_interfaces=resize_interface,
    )
    response, updated_instance = morpheus_api_service.instance_service.resize_instance(
        instance_id=instance_id, resize_payload=instance_resize_data
    )
    logger.info(f"Removed network interfaces Status: {updated_instance.instance.status}")
    assert response.success, f"Failed to remove network interfaces from instance {instance_id}"

    if wait_for_resizing:
        wait_for_instance_status_update(morpheus_api_service, instance_id, InstanceStatus.RUNNING)
        # get the updated list of interfaces
        updated_instance = morpheus_api_service.instance_service.get_instance(instance_id)
    return updated_instance
