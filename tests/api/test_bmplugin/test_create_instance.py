import uuid
from pytest import fixture, mark
import logging

from lib.common.enums.virtual_image_name import VirtualImageName
from lib.common.enums.virtual_image_type import VirtualImageType
from lib.common.enums.service_plan_name import ServicePlanName
from morpheus_api.dataclasses.common_objects import CommonRequiredData
from morpheus_api.settings import MorpheusAPIService, MorpheusSettings
from tests.steps.morpheus.common_steps import get_required_data
from tests.steps.morpheus.instance_steps import (
    create_instance_from_template,
    delete_instance,
)
from morpheus_api.dataclasses.instance import Instance

CREATED_INSTANCE_NAME: str = f"HPE-BMaaS-Instance-{str(uuid.uuid4())[:5]}"
VIRTUAL_IMAGE_NAME: str = "RHEL-HPE-Min"
COMMON_REQUIRED_DATA: CommonRequiredData = None
CREATED_INSTANCE: Instance = None
VIRTUAL_IMAGE_ID: int = None

settings = MorpheusSettings()

logger = logging.getLogger()


@fixture(scope="module")
def morpheus_api_service():
    """
    Fixture to provide a MorpheusAPIService instance for testing.

    This fixture initializes a MorpheusAPIService instance using the provided API settings.
    After the test, it ensures that created Instance and virtual image is deleted and verifies its deletion.

    Yields:
        MorpheusAPIService: An instance of MorpheusAPIService for API interactions.
    Cleanup:
        - Deletes the created instances.
    """
    global COMMON_REQUIRED_DATA, VIRTUAL_IMAGE_ID

    logger.info(f"\n{'Setup Start'.center(40, '*')}")

    morpheus_api_service = MorpheusAPIService(api_settings=settings.api_settings)

    # Get required data for Instance creation
    logger.info("Getting required data for Instance creation")
    COMMON_REQUIRED_DATA = get_required_data(
        morpheus_api_service=morpheus_api_service,
        service_plan_name=ServicePlanName.CPU_1_MEMORY_1_GB,
    )

    logger.info("Fetching virtual images")
    virtual_image_list = morpheus_api_service.virtual_image_service.list_virtual_images()
    VIRTUAL_IMAGE_ID = [
        virtual_image
        for virtual_image in virtual_image_list.virtual_images
        if VIRTUAL_IMAGE_NAME == virtual_image.name and virtual_image.image_type == VirtualImageType.ISO.value
    ][0].id
    logger.info(f"Virtual Image ID = {VIRTUAL_IMAGE_ID}")

    logger.info(f"\n{'Setup Complete'.center(40, '*')}")

    yield morpheus_api_service

    logger.info(f"\n{'Teardown Start'.center(40, '*')}")

    if CREATED_INSTANCE:
        logger.info(f"Deleting instance {CREATED_INSTANCE.instance.name} . . .")
        delete_instance(morpheus_api_service, CREATED_INSTANCE.instance.id, force="on")
        logger.info(f"Instance {CREATED_INSTANCE.instance.name} deleted successfully")

    logger.info(f"\n{'Teardown Complete'.center(40, '*')}")



@mark.regression
@mark.filterwarnings("ignore::urllib3.exceptions.InsecureRequestWarning")
def test_create_instance(morpheus_api_service: MorpheusAPIService):
    """
    Test to add and remove network interfaces from an instance.
    Args:
        morpheus_api_service (MorpheusAPIService): An instance of MorpheusAPIService for API interactions.
    Raises:
        MorpheusAPIError: If there is an error during the API call for deleting the virtual image.

    This function performs the following steps:
    1. Create an instance.
    """
    global CREATED_INSTANCE

    # Create instance
    logger.info(f"Creating instance '{CREATED_INSTANCE_NAME}'...")
    create_status, CREATED_INSTANCE = create_instance_from_template(
        morpheus_api_service=morpheus_api_service,
        template_id=VIRTUAL_IMAGE_ID,
        instance_name=CREATED_INSTANCE_NAME,
        storage_volume_type_id=86,
        datastore_id=None,
        network_id="5",
        layout_id=277,
        layout_code="Single ILO Server",
        plan_id=243,
        plan_code="ilo-custom",
        zone_id=COMMON_REQUIRED_DATA.zone_id,
        volume_size=447,
        num_volumes=1,
        wait_for_creation=True,
    )
    assert create_status, f"Failed to create {VIRTUAL_IMAGE_NAME} instance"
    logger.info(f"Instance '{CREATED_INSTANCE_NAME}' created successfully")

    assert CREATED_INSTANCE.instance.status == "running", f"Instance {CREATED_INSTANCE_NAME} is not in 'running' state"
    logger.info(f"Instance '{CREATED_INSTANCE_NAME}' created with ID: {CREATED_INSTANCE.instance.id}")