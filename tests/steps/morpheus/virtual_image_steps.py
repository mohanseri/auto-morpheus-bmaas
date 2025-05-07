import logging
import time
from lib.common.enums.os_type import OSType
from lib.common.enums.virtual_image_status import VirtualImageStatus
from lib.common.enums.virtual_image_type import VirtualImageType
from lib.common.enums.visibility import Visibility
from morpheus_api.dataclasses.virtual_image import (
    VirtualImage,
    VirtualImagePayload,
    VirtualImageCreateData,
)
from morpheus_api.settings import MorpheusAPIService


logger = logging.getLogger()

"""This module contains steps for ALL virtual-image-related operations."""


def create_virtual_image_payload(
    name: str,
    image_type: VirtualImageType,
    os_type: OSType,
    is_cloud_init: bool = False,
    install_agent: bool = False,
    visibility: Visibility = Visibility.PRIVATE,
    is_auto_join_domain: bool = False,
    virtio_supported: bool = True,
    vm_tools_installed: bool = True,
    is_force_customization: bool = False,
    trial_version: bool = False,
    is_sysprep: bool = False,
    uefi: bool = False,
) -> VirtualImageCreateData:
    """
    Helper function to create a virtual image payload.

    Args:
        name (str): The name of the virtual image.
        image_type (VirtualImageType): The type of the image.
        os_type (OSType): The type of the operating system.
        is_cloud_init (bool): Whether cloud-init is enabled. Defaults to False.
        install_agent (bool): Whether the agent is installed. Defaults to False.
        visibility (Visibility): The visibility of the image. Defaults to Visibility.PRIVATE.
        is_auto_join_domain (bool): Whether the image is auto-joined to a domain. Defaults to False.
        virtio_supported (bool): Whether virtio is supported. Defaults to True.
        vm_tools_installed (bool): Whether VM tools are installed. Defaults to True.
        is_force_customization (bool): Whether customization is forced. Defaults to False.
        trial_version (bool): Whether the image is a trial version. Defaults to False.
        is_sysprep (bool): Whether sysprep is enabled. Defaults to False.
        uefi (bool): Whether UEFI is enabled. Defaults to False.

    Returns:
        VirtualImageCreateData: The virtual image payload.
    """
    virtual_image_payload: VirtualImagePayload = VirtualImagePayload(
        name=name,
        image_type=image_type.value,
        os_type=os_type.value,
        is_cloud_init=is_cloud_init,
        install_agent=install_agent,
        visibility=visibility,
        is_auto_join_domain=is_auto_join_domain,
        virtio_supported=virtio_supported,
        vm_tools_installed=vm_tools_installed,
        is_force_customization=is_force_customization,
        trial_version=trial_version,
        is_sysprep=is_sysprep,
        uefi=uefi,
    )

    virtual_image_create_data: VirtualImageCreateData = VirtualImageCreateData(virtual_image=virtual_image_payload)

    return virtual_image_create_data


def delete_virtual_image(
    morpheus_api_service: MorpheusAPIService,
    virtual_image_id: int,
    wait_for_deletion: bool = True,
):
    """
    Helper function to delete an instance.

    Args:
        morpheus_api_service (MorpheusAPIService): The service used to interact with the Morpheus API.
        virtual_image_id (int): The ID of the virtual image to be deleted.
        wait_for_deletion (bool, optional): A flag to indicate whether to wait for the virtual image to be deleted. Defaults to True.
    """
    logger.info(f"Deleting virtual image: {virtual_image_id}")
    morpheus_api_service.virtual_image_service.delete_virtual_image(virtual_image_id=virtual_image_id)
    if wait_for_deletion:
        wait_for_virtual_image_deletion(morpheus_api_service, virtual_image_id)
    logger.info(f"Virtual Image '{virtual_image_id}' deleted successfully")


def wait_for_virtual_image_creation(
    morpheus_api_service: MorpheusAPIService,
    virtual_image_name: str,
    max_wait_time: int = 1800,
    sleep_time: int = 30,
):
    """
    Wait for the virtual image to be created

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        virtual_image_name (str): The name of the virtual image to be created.
        max_wait_time (int, optional): The maximum time to wait for the virtual image to be created. \
            Defaults to 1800 seconds.
        sleep_time (int, optional): The time to sleep between status checks in seconds. Defaults to 30 seconds.

    Raises:
        AssertionError: If the max wait time exceeds without the virtual image being created.
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        virtual_image_list = morpheus_api_service.virtual_image_service.list_virtual_images(name=virtual_image_name)
        if len(virtual_image_list.virtual_images) == 1:
            return
        else:
            logger.info(f"Waiting for virtual image {virtual_image_name} to be created")
            time.sleep(sleep_time)
    else:
        assert False, f"Max wait time exceeded for virtual image {virtual_image_name} creation"


def wait_for_virtual_image_deletion(
    morpheus_api_service: MorpheusAPIService,
    virtual_image_id: int,
    max_wait_time: int = 1800,
    sleep_time: int = 30,
):
    """
    Waits for a virtual image to be deleted.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service used to interact with the Morpheus platform.
        virtual_image_id (int): The ID of the virtual image to wait for deletion.
        max_wait_time (int, optional): The maximum time to wait for the virtual image to be deleted, in seconds. \
            Defaults to 1800.
        sleep_time (int, optional): The time to sleep between status checks, in seconds. Defaults to 30.
    Raises:
        AssertionError: If the maximum wait time is exceeded before the virtual image is deleted.
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        try:
            morpheus_api_service.virtual_image_service.get_virtual_image_by_id(virtual_image_id)
        except Exception as e:
            if "Not Found" in str(e):
                return
        logger.info(f"Waiting for virtual image {virtual_image_id} to be deleted...")
        time.sleep(sleep_time)
    else:
        assert False, f"Max wait time exceeded for virtual image deletion: {virtual_image_id}."


def wait_for_virtual_image_status(
    morpheus_api_service: MorpheusAPIService,
    virtual_image_id: int,
    status: VirtualImageStatus,
    max_wait_time: int = 1800,
    sleep_time: int = 30,
):
    """
    Waits for a virtual image to reach a specified status.

    This function polls the status of a virtual image at regular intervals until \
        the virtual image reaches the desired status or the maximum wait time is exceeded.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service used to interact with the Morpheus platform.
        virtual_image_id (int): The ID of the virtual image to check.
        status (VirtualImageStatus): The desired status to wait for.
        max_wait_time (int, optional): The maximum time to wait for the virtual image to reach the desired status, \
            in seconds. Defaults to 1800 seconds (30 minutes).
        sleep_time (int, optional): The time to wait between status checks, in seconds. Defaults to 30 seconds.

    Raises:
        AssertionError: If the maximum wait time is exceeded before the virtual image reaches the desired status.
    """
    start_time = time.time()
    while time.time() - start_time <= max_wait_time:
        virtual_image = morpheus_api_service.virtual_image_service.get_virtual_image_by_id(
            virtual_image_id=virtual_image_id
        )
        if virtual_image.status == status.value:
            return
        else:
            logger.info(f"Waiting for virtual image status to be '{status.value}'")
            time.sleep(sleep_time)
    else:
        assert False, f"Max wait time exceeded for virtual image status '{status.value}' update."


def create_and_upload_virtual_image(
    morpheus_api_service: MorpheusAPIService,
    image_name: str,
    image_path: str,
    image_filename: str,
    image_type: VirtualImageType,
    os_type: OSType,
    wait_for_creation: bool = True,
) -> int:
    """
    Creates a virtual image and uploads the image file.

    Args:
        morpheus_api_service (MorpheusAPIService): The Morpheus API service instance to interact with.
        image_name (str): The name of the virtual image to be created.
        image_path (str): The path to the image file.
        image_filename (str): The name of the image file.
        image_type (VirtualImageType): The type of the image.
        os_type (OSType): The type of the operating system.
        wait_for_creation (bool, optional): A flag to indicate whether to wait for the virtual image to be created. Defaults to True.

    Returns:
        int: The ID of the virtual image created.
    """
    virtual_image_payload: VirtualImageCreateData = create_virtual_image_payload(
        name=image_name,
        image_type=image_type,
        os_type=os_type,
        is_cloud_init=False,
        install_agent=True if os_type is OSType.UBUNTU_2204_64BIT else False,
        vm_tools_installed=False if os_type is OSType.UBUNTU_2204_64BIT else True,
        uefi=False,
    )

    virtual_image: VirtualImage = None
    virtual_image_id: int = None

    logger.info(f"Creating Virtual Image '{image_name}'...")
    try:
        virtual_image = morpheus_api_service.virtual_image_service.create_virtual_image(
            virtual_image_payload=virtual_image_payload
        )
        virtual_image_id = virtual_image.id
        logger.info(f"Virtual Image '{image_name}' created successfully. ID = '{virtual_image_id}'")
    except Exception as e:
        logger.info(f"Virtual Image '{image_name}' creation failed.  Exception: {e}")

    # add '/' to end of image_path if not present
    if image_path[-1] != "/":
        image_path += "/"

    # Upload image file if the Virtual Image was created successfully
    if virtual_image:
        # Upload Image
        logger.info(f"Uploading image file '{image_filename}' for Virtual Image '{image_name}'...")
        api_response = morpheus_api_service.virtual_image_service.upload_virtual_image_file(
            virtual_image_id=virtual_image.id,
            file_path=image_path,
            file_name=image_filename,
        )
        assert api_response.success is True, f"Upload virtual image file '{image_path}{image_filename}' failed"
        logger.info(f"Upload of image file '{image_filename}' succeeded")
    else:
        logger.info("Skipping upload - Virtual Image creation failed")

    # wait for virtual image creation if required
    if wait_for_creation and virtual_image:
        logger.info(f"Waiting for Virtual Image '{image_name}' to be active...")
        wait_for_virtual_image_status(morpheus_api_service, virtual_image_id, VirtualImageStatus.ACTIVE)

    return virtual_image_id
