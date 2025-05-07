import json
import logging
import time
import re
from lib.common.enums.linux_filesystem_types import LinuxFilesystemTypes
from lib.common.enums.windows_filesystem_types import WindowsFilesystemTypes
from lib.common.enums.service_plan_name import ServicePlanName
from lib.common.enums.storage_volume_type import StorageVolumeType
from lib.platform.io_manager import IOManager
from lib.platform.remote_ssh_manager import RemoteConnect
from morpheus_api.dataclasses.common_objects import CommonRequiredData
from morpheus_api.dataclasses.network import NetworkID, NetworkInterface
from morpheus_api.dataclasses.volume import Volume
from morpheus_api.settings import ProxySettings, VDBenchSettings, MorpheusAPIService, MorpheusSettings
from lib.common.enums.ip_mode import IPMode

settings = MorpheusSettings()
logger = logging.getLogger()

"""This module contains common steps that can be reused across different test cases."""


def write_and_validate_data_dm_core(
    host_ip: str,
    username: str,
    password: str,
    export_filename: str = None,
    validation: bool = False,
    percentage_to_fill: int = 5,
    copy_dm_core: bool = False,
    super_user: bool = True,
) -> str:
    """
    Write and validate data using DMCore on the remote server.

    Args:
        host_ip (str): Remote server IP address.
        username (str): Remote server username.
        password (str): Remote server password.
        export_filename (str, optional): Export filename. Defaults to None.
        validation (bool, optional): Run DMCore validation. Defaults to False.
        percentage_to_fill (int, optional): Percentage to fill. Defaults to 5.
        copy_dm_core (bool, optional): Copy DMCore binary to the remote server. Defaults to False.
        super_user (bool, optional): Run commands as super user. Defaults to True.

    Returns:
        str: DMCore execution status
    """
    remote_client: RemoteConnect = None
    io_manager: IOManager = None

    return_status: str = "not run"

    # Connect to the remote server
    logger.info(f"Connecting to the remote server {host_ip}")
    try:
        remote_client = RemoteConnect(
            host_ip=host_ip,
            username=username,
            password=password,
        )
        logger.info("Connected to the remote server")
    except Exception as e:
        logger.info(f"Connection failed: {e}")
        raise e

    # instantiate IOManager
    io_manager = IOManager(client=remote_client, super_user=super_user)
    logger.info("IOManager created")

    if not validation or copy_dm_core:
        # Copy DMCore to the remote server
        try:
            if io_manager.copy_dmcore_binary_to_remote_host():
                logger.info("DM CORE binary copied")
            else:
                logger.info("DM CORE binary already present on the remote server")
        except Exception as e:
            logger.info(f"DM CORE binary copy failed: {e}")
            # Close connection
            remote_client.close_connection()
            logger.info("Remote connection closed")
            raise e

    # Run DMCore
    try:
        logger.info("DM CORE started")
        return_status = io_manager.run_dmcore(
            export_filename=export_filename,
            validation=validation,
            percentage_to_fill=percentage_to_fill,
        )
        logger.info("DM CORE completed")
    except Exception as e:
        logger.info(f"DM CORE failed: {e}")
        raise e
    finally:
        # Close connection
        remote_client.close_connection()
        logger.info("Remote connection closed")

    # Return the status of DMCore execution
    return return_status


def write_and_validate_data_vdbench(
    host_ip: str,
    username: str,
    password: str,
    proxy_settings: ProxySettings,
    vdbench_settings: VDBenchSettings,
    validate: bool = False,
    custom_config_file_name: str = "config",
) -> bool:
    """
    Establishes a connection to a remote server, configures the environment, and runs VDBench.

    Args:
        host_ip (str): The IP address of the remote server.
        username (str): The username for the remote server.
        password (str): The password for the remote server.
        proxy_settings (ProxySettings): The proxy settings to be applied on the remote server.
        vdbench_settings (VDBenchSettings): The settings for VDBench.
        validate (bool, optional): Whether to validate the VDBench run. Defaults to False.
        custom_config_file_name (str, optional): The name of the custom VDBench configuration file. Defaults to "config"

    Returns:
        bool: True if VDBench runs successfully, False otherwise.
    """

    logger.info(f"Establishing connection to the remote server {host_ip}")
    remote_client = RemoteConnect(
        host_ip=host_ip,
        username=username,
        password=password,
        sock=True,
        window_size=52428800,
        packet_size=327680,
    )
    io_manager = IOManager(client=remote_client, super_user=True)

    if not validate:
        logger.info(f"Adding proxy to the remote server {host_ip}")
        io_manager.add_proxy_to_instance(proxy_settings=proxy_settings)

        logger.info(f"Copying VDBench executable to the remote server {host_ip}")
        io_manager.copy_vdbench_executable_to_remote_host(vdbench_settings=vdbench_settings)

        logger.info(f"Installing Java on the remote server {host_ip}")
        io_manager.install_java_on_remote_host(vdbench_settings=vdbench_settings)

        logger.info("Creating VDBench config file for generating files and directories")
        io_manager.create_vdbench_config_file_for_generating_files_and_dirs(vdbench_settings=vdbench_settings)

    logger.info("Running VDBench")
    return io_manager.run_vdbench(validate=validate, custom_config_file_name=custom_config_file_name)


def get_required_data(
    morpheus_api_service: MorpheusAPIService,
    storage_volume_type: StorageVolumeType = StorageVolumeType.STANDARD,
    service_plan_name: ServicePlanName = ServicePlanName.CPU_1_MEMORY_1_GB,
) -> CommonRequiredData:
    """
    Fetch required data for instance and virtual images creation

    Args:
        morpheus_api_service (MorpheusAPIService): An instance of MorpheusAPIService for API interactions.
        storage_volume_type (StorageVolumeType): The type of storage volume to fetch for STORAGE_VOLUME_TYPE_ID. Defaults to StorageVolumeType.STANDARD.
        service_plan_name (ServicePlanName): The name of the service plan to fetch for PLAN_ID and PLAN_CODE. Defaults to ServicePlanName.CPU_1_MEMORY_1_GB.

    This function obtains the required data for creating instances and virtual images:
        - used when creating virtual image (import as image)
        STORAGE_BUCKET_ID

        - used in instance creation
        STORAGE_VOLUME_TYPE_ID
        DATASTORE_ID
        ZONE_ID
        NETWORK_ID
        LAYOUT_ID
        LAYOUT_CODE
        PLAN_ID
        PLAN_CODE

        - used in fetching datastore ID
        CLUSTER_ID

        - used in fetching network ID
        PROVISION_TYPE_ID

        - used in fetching layouts
        INSTANCE_TYPE_ID

    Returns:
        CommonRequiredData: An object containing the required data for instance and virtual images creation
    """
    required_data = CommonRequiredData()

    logger.info(f"Fetching storage bucket: {settings.instance_settings.storage_bucket_name}")
    storage_bucket_list = morpheus_api_service.storage_bucket_service.list_storage_buckets(
        name=settings.instance_settings.storage_bucket_name
    )
    if storage_bucket_list.meta.total:
        required_data.storage_bucket_id = storage_bucket_list.storage_buckets[0].id
        logger.info(f"Storage bucket ID: {required_data.storage_bucket_id}")
    else:
        logger.info(f"Storage bucket {settings.instance_settings.storage_bucket_name} not found")

    logger.info(f"Fetching storage volume type: {storage_volume_type.value}")
    storage_volume_type_list = morpheus_api_service.storage_volume_type_service.list_storage_volumes(
        code=storage_volume_type.value
    )
    if storage_volume_type_list.meta.total:
        required_data.storage_volume_type_id = storage_volume_type_list.storage_volume_types[0].id
        logger.info(f"Storage volume type ID: {required_data.storage_volume_type_id}")
    else:
        logger.info(f"Storage volume type {storage_volume_type.value} not found")

    logger.info("Fetching cluster ID")
    cluster_list = morpheus_api_service.cluster_service.list_clusters()
    if cluster_list.meta.total:
        required_data.cluster_id = cluster_list.clusters[0].id
        required_data.cluster_name = cluster_list.clusters[0].name
        logger.info(f"Cluster ID: {required_data.cluster_id}, Cluster Name: {required_data.cluster_name}")
    else:
        logger.info("Cluster not found")

    # logger.info(f"Fetching datastore ID for cluster: {required_data.cluster_id}")
    # datastore_list = morpheus_api_service.cluster_service.list_datastores(
    #     cluster_id=required_data.cluster_id, name=settings.instance_settings.datastore_name
    # )
    # if datastore_list.meta.total:
    #     required_data.datastore_id = datastore_list.datastores[0].id
    #     logger.info(f"Datastore ID: {required_data.datastore_id}")
    # else:
    #     logger.info(f"Datastore {settings.instance_settings.datastore_name} not found")

    logger.info("Fetching provision type ID")
    provision_type_list = morpheus_api_service.provision_type_service.list_provision_types()
    if provision_type_list.meta.total:
        required_data.provision_type_id = provision_type_list.provision_types[0].id
        logger.info(f"Provision type ID: {required_data.provision_type_id}")
    else:
        logger.info("Provision type not found")

    logger.info("Fetching zone ID")
    zone_list = morpheus_api_service.zone_service.list_zones()
    if zone_list.meta.total:
        required_data.zone_id = zone_list.zones[0].id
        required_data.zone_name = zone_list.zones[0].name
        logger.info(f"Zone ID: {required_data.zone_id}, Zone Name: {required_data.zone_name}")
    else:
        logger.info("Zone not found")

    logger.info("Fetching network ID")
    option_types = morpheus_api_service.option_service.get_network_options_for_cloud(
        zone_id=required_data.zone_id,
        provision_type_id=required_data.provision_type_id,
    )
    if option_types.data.networks:
        required_data.network_id = option_types.data.networks[0].id
        logger.info(f"Network ID: {required_data.network_id}")
    else:
        logger.info("Network not found")

    logger.info("Fetching instance type ID")
    instance_type_list = morpheus_api_service.instance_type_service.get_all_instance_types()
    if instance_type_list.meta.total:
        required_data.instance_type_id = instance_type_list.instance_types[0].id
        logger.info(f"Instance Type ID: {required_data.instance_type_id}")
    else:
        logger.info("Instance Type not found")

    logger.info(f"Fetching instance type layout ID and CODE for instance type: {required_data.instance_type_id}")
    layout_list = morpheus_api_service.instance_type_service.get_instance_type_layouts(
        instance_type_id=required_data.instance_type_id
    )
    if len(layout_list):
        layout = layout_list[0]
        required_data.layout_id = layout.id
        required_data.layout_code = layout.code
        logger.info(f"Layout ID: {required_data.layout_id}, Layout Code: {required_data.layout_code}")
    else:
        logger.info("Layout not found")

    logger.info(f"Fetching service plan: {service_plan_name.value}")
    service_plans = morpheus_api_service.service_plan_service.list_service_plans(name=service_plan_name)
    service_plan_filtered = [service_plan for service_plan in service_plans.service_plans if "kvm" in service_plan.code]
    if service_plan_filtered:
        service_plan = service_plan_filtered[0]
        required_data.plan_id = service_plan.id
        required_data.plan_code = service_plan.code
        logger.info(f"Service Plan ID: {required_data.plan_id}, Service Plan Code: {required_data.plan_code}")
    else:
        logger.info(f"Service Plan {service_plan_name.value} not found")

    return required_data


def build_volume(
    name: str, storage_type: int, size: int = None, id: int = -1, root_volume: bool = False, datastore_id: str = None
) -> Volume:
    """
    Build a Volume object with the given parameters.

    Args:
        name (str): The name of the volume.
        storage_type (int): The storage type of the volume.
        size (int): The size of the volume in GB. Defaults to None; will use Plan default.
        id (int): The ID of the volume. Defaults to -1.
        root_volume (bool): Whether the volume is a root volume. Defaults to False.
        datastore_id (str): The datastore ID of the volume. Defaults to None.

    Returns:
        Volume: The built Volume object.
    """
    volume = Volume(
        id=id,
        root_volume=root_volume,
        name=name,
        size=size,
        storage_type=storage_type,
        datastore_id=datastore_id,
    )

    return volume


def build_network_interface(
    network_id: str,
    primary_interface: bool = False,
    ip_mode: IPMode = IPMode.DHCP,
    ip_address: str = None,
    interface_id: str = None,
) -> NetworkInterface:
    """
    Build a NetworkInterface object with the given parameters.

    Args:
        network_id (str): The ID of the NetworkID.
        primary_interface (bool, optional): Whether the network interface is the primary interface. Defaults to False.
        ip_mode (IPMode, optional): The IP mode of the network interface. Defaults to IPMode.DHCP.
        ip_address (str, optional): The IP address of the network interface. Defaults to None.
        interface_id (str, optional): The ID of the network interface. Defaults to None.

    Returns:
        NetworkInterface: The built NetworkInterface object.
    """
    network_interface = NetworkInterface(
        primary_interface=primary_interface,
        network=NetworkID(id=network_id),
        ip_mode=ip_mode.value,
        ip_address=ip_address,
        id=interface_id,
    )

    return network_interface


def execute_commands_from_remote_server(
    host_ip: str,
    username: str,
    password: str,
    cmds: list[str],
) -> list[list[str]]:
    """
    Connects to Remote Server and executes a series of commands.

    Args:
        host_ip (str): Remote server IP address.
        username (str): Remote server username.
        password (str): Remote server password.
        cmds (list[str]): A list of commands to be executed.

    Returns:
        list[str]: A list of outputs for each executed command, including any error messages.
    """

    results = []
    remote_client = RemoteConnect(
        host_ip=host_ip,
        username=username,
        password=password,
    )

    for cmd in cmds:
        try:
            result = remote_client.execute_command_sudo_passwd(cmd)
            results.append(result)
        except Exception as cmd_error:
            results.append(f"Error executing command '{cmd}': {str(cmd_error)}")

    remote_client.close_connection()
    return results


def get_checksum_from_remote_server(
    host_ip: str,
    username: str,
    password: str,
    file_path: str,
) -> str:
    """
    Returns checksum of a file by connecting to remote server.

    Args:
        host_ip (str): Remote server IP address.
        username (str): Remote server username.
        password (str): Remote server password.
        file_path (str): Path of the file to get checksum.

    Returns:
        str: Checksum value of the file.
    """

    checksum_cmd = f'test -f {file_path} && md5sum {file_path} || echo "File does not exist"'
    result = execute_commands_from_remote_server(host_ip, username, password, [checksum_cmd])[0]

    if result and not result[-1].endswith("File does not exist"):
        return result[len(result) - 1].split()[0]
    else:
        return "File not found"


def format_linux_volume_and_mount(
    instance_ip: str,
    file_system_device: str,
    file_system_type: LinuxFilesystemTypes,
    mount_point: str,
    partition_number: int = 1,
) -> list[str]:
    """
    Format a volume and mount it on the remote server.
    - fdisk to create primary partition
    - mkfs to create filesystem
    - mkdir to create mount point
    - mount to mount the device partition

    Args:
        instance_ip (str): The IP address of the remote server.
        file_system_device (str): The device to format (/dev/vdb).
        file_system_type (LinuxFilesystemTypes): The type of filesystem to format the device with.
        mount_point (str): The mount point for the device.
        partition_number (int, optional): The partition number to format. Defaults to 1.
    """
    df_output: list[str] = None

    try:
        # Connect to the instance IP
        remote_client = RemoteConnect(
            host_ip=instance_ip,
            username=settings.instance_settings.user_name,
            password=settings.instance_settings.password,
        )

        # create partition
        logger.info("Creating Partition")
        # NOTE: The password is asked for the "sudo echo" portion. We need to add "sudo" here for
        # the fdisk command, but the credentials are not asked for a 2nd time
        # n=new partition, p=primary, partition_number=partition number, default, default, w=write
        command = f"echo -e 'n\np\n{partition_number}\n\n\nw\n' | sudo fdisk {file_system_device}"
        logger.info(f"Command: {command}")
        output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {output}")

        # make file system on partition
        logger.info("Creating File System")
        file_system_partition: str = f"{file_system_device}{partition_number}"
        command = f"mkfs -t {file_system_type.value} {file_system_partition}"
        logger.info(f"Command: {command}")
        output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {output}")

        # create mount point
        logger.info("Creating Mount Point")
        command = f"mkdir -p {mount_point}"
        logger.info(f"Command: {command}")
        output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {output}")

        # mount the device partition
        logger.info("Mounting Device Partition")
        command = f"mount {file_system_partition} {mount_point}"
        logger.info(f"Command: {command}")
        output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {output}")

        # execute "df /{file_system_partition}" command to get the partition details to return
        logger.info("Executing df Command")
        command = f"df {file_system_partition}"
        logger.info(f"Command: {command}")
        df_output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {df_output}")

    except Exception as e:
        logger.info(f"Exception: {e}")
        raise e

    finally:
        if remote_client:
            # Close connection
            remote_client.close_connection()
            logger.info("Remote connection closed")

    return df_output


def extend_linux_volume_filesystem(
    instance_ip: str,
    file_system_device: str,
    mount_point: str,
    file_system_type: LinuxFilesystemTypes = LinuxFilesystemTypes.XFS,
    partition_number: int = 1,
) -> list[str]:
    """
    Extend the filesystem on the disk.

    Args:
        instance_ip (str): The IP address of the remote server.
        file_system_device (str): The device to extend (/dev/vdb).
        mount_point (str): The mount point for the device.
        file_system_type (LinuxFilesystemTypes): The type of filesystem to extend the device with. Defaults to LinuxFilesystemTypes.XFS.
        partition_number (int): The partition number to extend. Defaults to 1.

    Returns:
        list[str]: The output of the df command.
    """
    # SKIP - unmount the partition  "umount /mnt/data-1"
    # - fdisk to extend the partition  "d\nn\np\n{partition_number}\n\n\nN\nw\n"
    # SKIP - re-mount the partition  "mount /dev/vdb1 /mnt/data-1"
    # - xfs_growfs to extend the filesystem at the mount point "sudo xfs_growfs -d /mnt/data-1"
    #
    # Currently only XFS is tested:  xfs_growfs
    if file_system_type != LinuxFilesystemTypes.XFS:
        raise NotImplementedError(f"File system type {file_system_type.value} is not supported")

    df_output: list[str] = None

    try:
        # Connect to the instance IP
        remote_client = RemoteConnect(
            host_ip=instance_ip,
            username=settings.instance_settings.user_name,
            password=settings.instance_settings.password,
        )

        logger.info(f"Extending partition {partition_number} on {file_system_device}")
        # NOTE: The password is asked for the "sudo echo" portion. We need to add "sudo" here for
        # the fdisk command, but the credentials are not asked for a 2nd time
        # d=delete partition, n=new partition, p=primary, partition_number=partition number, default, default, w=write
        command = f"echo -e 'd\nn\np\n{partition_number}\n\n\nw\n' | sudo fdisk {file_system_device}"
        logger.info(f"Command: {command}")
        output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {output}")

        # grow the xfs filesystem
        logger.info(f"Extending XFS File System at mountpoint {mount_point}")
        command = f"xfs_growfs -d {mount_point}"
        logger.info(f"Command: {command}")
        output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {output}")

        file_system_partition: str = f"{file_system_device}{partition_number}"
        # execute "df /{file_system_partition}" command to get the partition details to return
        logger.info("Executing df Command")
        command = f"df {file_system_partition}"
        logger.info(f"Command: {command}")
        df_output = remote_client.execute_command_sudo_passwd(command=command)
        logger.info(f"Output: {df_output}")

    except Exception as e:
        logger.info(f"Exception: {e}")
        raise e

    finally:
        if remote_client:
            # Close connection
            remote_client.close_connection()
            logger.info("Remote connection closed")

    return df_output


def format_windows_volume(
    instance_ip: str, windows_username: str, drive_letter: str, filesystem_type: WindowsFilesystemTypes
) -> list[str]:
    """
    Format a volume on the remote server.

    Args:
        instance_ip (str): The IP address of the remote server.
        windows_username (str): The username for the remote server.
        drive_letter (str): The drive letter of the disk to format.
        filesystem_type (WindowsFilesystemTypes): The type of filesystem to format the disk with.

    Returns:
        list[str]: The output of the Format-Volume command.
    """
    format_output: list[str] = None

    try:
        # Connect to the instance IP
        remote_client = RemoteConnect(
            host_ip=instance_ip,
            username=windows_username,
            password=settings.instance_settings.password,
        )

        # bring disk online
        logger.info("Bringing offline disks online")
        command = 'Powershell -Command "Get-Disk | Where-Object IsOffline -Eq $True | Set-Disk -IsOffline $False"'
        logger.info(f"Command: {command}")
        output = remote_client.execute_command(command=command, super_user=False)
        logger.info(f"Output: {output}")

        # get raw disk number
        logger.info("Getting raw disk number")
        command = 'Powershell -Command "Get-Disk | Where-Object PartitionStyle -Eq RAW | ConvertTo-Json"'
        logger.info(f"Command: {command}")
        output = remote_client.execute_command(command=command, super_user=False)
        json_response = json.loads("".join(output))
        disk_number = int(json_response["DiskNumber"])
        logger.info(f"Raw disk number = {disk_number}")

        # initialize disk
        logger.info("Initializing disk")
        command = f'Powershell -Command "Initialize-Disk {disk_number}"'
        logger.info(f"Command: {command}")
        output = remote_client.execute_command(command=command, super_user=False)
        logger.info(f"Output: {output}")

        time.sleep(5)  # Adding some sleep for disk to be initialized and ready

        # create disk partition
        logger.info("Creating disk partition")
        command = (
            f'Powershell -Command "New-Partition -DiskNumber {disk_number} -DriveLetter {drive_letter} -UseMaximumSize"'
        )
        logger.info(f"Command: {command}")
        output = remote_client.execute_command(command=command, super_user=False)
        logger.info(f"Output: {output}")

        # format disk
        logger.info("Formatting disk")
        command = f'Powershell -Command "Format-Volume -DriveLetter {drive_letter} -FileSystem {filesystem_type.value}"'
        logger.info(f"Command: {command}")
        format_output = remote_client.execute_command(command=command, super_user=False)
        logger.info(f"Output: {format_output}")

    except Exception as e:
        logger.info(f"Exception: {e}")
        raise e

    finally:
        if remote_client:
            # Close connection
            remote_client.close_connection()
            logger.info("Remote connection closed")

    return format_output


def extend_windows_volume_filesystem(
    instance_ip: str,
    windows_username: str,
    drive_letter: str,
) -> list[str]:
    """
    Extend the filesystem on the disk.

    Args:
        instance_ip (str): The IP address of the remote server.
        windows_username (str): The username for the remote server.
        drive_letter (str): The drive letter of the disk to extend.

    Returns:
        list[str]: The output of the Get-Volume command.
    """
    extend_output: list[str] = None

    try:
        # Connect to the instance IP
        remote_client = RemoteConnect(
            host_ip=instance_ip,
            username=windows_username,
            password=settings.instance_settings.password,
        )

        # Get the maximum supported size for the partition
        logger.info(f"Getting maximum supported size for the partition on drive {drive_letter}")
        command = f'Powershell -Command "(Get-PartitionSupportedSize -DriveLetter {drive_letter}).SizeMax"'
        logger.info(f"Command: {command}")
        output = remote_client.execute_command(command=command, super_user=False)
        logger.info(f"Output: {output}")

        # Output: ['64407715328\r']
        max_size = int(output[0].strip())

        # extend disk partition
        logger.info("Extending disk partition")
        command = f'Powershell -Command "Resize-Partition -DriveLetter {drive_letter} -Size {max_size}"'
        logger.info(f"Command: {command}")
        output = remote_client.execute_command(command=command, super_user=False)
        logger.info(f"Output: {output}")

        # get volume details
        logger.info("Getting volume details")
        command = f'Powershell -Command "Get-Volume -DriveLetter {drive_letter}"'
        logger.info(f"Command: {command}")
        extend_output = remote_client.execute_command(command=command, super_user=False)
        logger.info(f"Output: {extend_output}")

    except Exception as e:
        logger.info(f"Exception: {e}")
        raise e

    finally:
        if remote_client:
            # Close connection
            remote_client.close_connection()
            logger.info("Remote connection closed")

    return extend_output


def install_qemu_guest_agent_linux(
    host_ip: str,
    username: str,
    password: str,
) -> bool:
    """
    Installs the QEMU Guest Agent on Linux ISO instance.

    Args:
        host_ip (str): Remote server IP address.
        username (str): Remote server username.
        password (str): Remote server password.

    Returns:
        bool: True if the QEMU Guest Agent is installed successfully, False otherwise.
    """

    remote_client = RemoteConnect(
        host_ip=host_ip,
        username=username,
        password=password,
    )

    io_manager = IOManager(client=remote_client, super_user=True)
    io_manager.add_proxy_to_instance(proxy_settings=settings.proxy_settings)

    qemu_guest_agent_installation_cmds = [
        "sudo apt update",
        "sudo apt install -y qemu-guest-agent",
        "sudo systemctl start qemu-guest-agent",
        "sudo systemctl enable qemu-guest-agent",
        "sudo systemctl status qemu-guest-agent",
    ]

    results = [], status = False
    for cmd in qemu_guest_agent_installation_cmds:
        result = remote_client.execute_command_sudo_passwd(cmd)
        results.append(result)

    result = results[4][11]
    if re.search(r"Started QEMU Guest Agent", result).group(0) == "Started QEMU Guest Agent":
        status = True
    return status


def mount_and_partition_disk(
    host_ip: str,
    username: str,
    password: str,
    disk_name: str,
) -> bool:
    """
    Creates a partition, formats the disk, and mounts it.

    Args:
        host_ip (str): Remote server IP address.
        username (str): Remote server username.
        password (str): Remote server password.
        disk_name (str): The name of the disk to partition and mount (e.g., "vdb").

    Returns:
        bool: True if the disk was successfully mounted, False if an error occurred.
    """

    status = False
    create_partition = f"echo -e 'n\np\n\n\n\nw' | sudo fdisk /dev/{disk_name}"
    format_partition = f"sudo mkfs.ext4 /dev/{disk_name}1"
    create_dir = f"sudo mkdir /mnt/{disk_name}"
    mount_partition = f"sudo mount /dev/{disk_name}1 /mnt/{disk_name}"
    check_mount = f"mount | grep /dev/{disk_name}"

    commands = [create_partition, format_partition, create_dir, mount_partition, check_mount]
    result = execute_commands_from_remote_server(host_ip, username, password, commands)

    expected_result = f"/dev/{disk_name}1 on /mnt/{disk_name}"
    if expected_result in result[-1][-1]:
        status = True
    return status


def write_data_to_disk(
    host_ip: str,
    username: str,
    password: str,
    file_path: str,
    data_size_in_gb: int = 5,
):
    """
    Writes data to the specified disk by creating a file and filling it with dummy data.

    Args:
        host_ip (str): Remote server IP address.
        username (str): Remote server username.
        password (str): Remote server password.
        file_path (str): Full path, including the directory and file name.
        data_size_in_gb (int): The size of the data to write to the file in GB. Defaults to 5.
    """

    write_cmd = f"sudo dd if=/dev/zero of={file_path} bs=1M count={data_size_in_gb * 1000}"
    execute_commands_from_remote_server(host_ip, username, password, write_cmd)
