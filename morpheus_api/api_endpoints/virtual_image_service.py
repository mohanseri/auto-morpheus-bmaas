import logging
from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.common_objects import APIResponse
from morpheus_api.dataclasses.virtual_image import (
    VirtualImage,
    VirtualImageCreateData,
    VirtualImageList,
    VirtualImageObject,
)

VIRTUAL_IMAGE_ENDPOINT = MorpheusAPIEndpoints.VIRTUAL_IMAGES.value

logger = logging.getLogger()


class VirtualImageService(MorpheusAPI):
    """VirtualImageService class provides methods to interact with the Morpheus API to manage virtual images.

    This class provides methods strictly following /api/virtual-images endpoint in Morpheus API.

    But all virtual-image-related methods can be found in virtual_image_steps.py file.
    """

    def list_virtual_images(
        self,
        max: int = 25,
        offset: int = 0,
        name: str = "",
        filter_type: str = "User",
    ) -> VirtualImageList:
        """
        Retrieves a list of virtual images with optional pagination and sorting.

        Args:
            max (int, optional): The maximum number of virtual images to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            name (str, optional): The name of the virtual image to filter by. Defaults to "".
            filter_type (str, optional): The field by which to filters the virtual image by provided value. Defaults to "User".

        Returns:
            VirtualImageList: The VirtualImageList object containing the list of virtual images.
        """
        params: str = f"max={max}&offset={offset}&name={name}&filterType={filter_type}"
        response: Response = self._get(f"{VIRTUAL_IMAGE_ENDPOINT}?{params}")
        return VirtualImageList(**response.json())

    def get_virtual_image_by_id(self, virtual_image_id: int) -> VirtualImage:
        """
        Retrieve details of a specific virtual image by its ID.

        Args:
            virtual_image_id (int): The unique identifier of the virtual image.

        Returns:
            VirtualImage: An object containing the details of the virtual image.
        """
        response: Response = self._get(f"{VIRTUAL_IMAGE_ENDPOINT}/{virtual_image_id}")

        # A single Virtual Image is returned in an object with field named 'virtual_image'
        virtual_image_object = VirtualImageObject(**response.json())
        return virtual_image_object.virtual_image

    def create_virtual_image(self, virtual_image_payload: VirtualImageCreateData) -> VirtualImage:
        """
        Create a new Virtual Image.

        Args:
            virtual_image_payload (VirtualImageCreateData): The data to be used for creating the Virtual Image.

        Returns:
            VirtualImage: A Virtual Image object populated with the data from the response.

        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        virtual_image_payload_dict = virtual_image_payload.model_dump(by_alias=True, exclude_none=True)
        logger.info(f"Create Virtual Image Payload Dict: {virtual_image_payload_dict}")

        response: Response = self._post(VIRTUAL_IMAGE_ENDPOINT, data=virtual_image_payload_dict)

        # A single Virtual Image is returned in an object with field named 'virtual_image'
        virtual_image_object = VirtualImageObject(**response.json())
        return virtual_image_object.virtual_image

    def upload_virtual_image_file(self, virtual_image_id: int, file_path: str, file_name: str) -> APIResponse:
        """
        Upload a file to a virtual image.

        Args:
            virtual_image_id (int): The ID of the virtual image.
            file_path (str): The path to the file to be uploaded.
            file_name (str): The name of the file to be uploaded.

        Returns:
            APIResponse: The response object from the API.

        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        url: str = f"{VIRTUAL_IMAGE_ENDPOINT}/{virtual_image_id}/upload?filename={file_name}"
        with open(f"{file_path}{file_name}", "rb") as data:
            response: Response = self._post_upload(endpoint=url, data=data)
            return APIResponse(**response.json())

    def remove_virtual_image_file(self, virtual_image_id: int, filename: str) -> APIResponse:
        """
        Remove the file from a virtual image.

        Args:
            virtual_image_id (int): The ID of the virtual image.
            filename (str): The name of the file to be removed.

        Returns:
            APIResponse: The response object from the API.

        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        url: str = f"{VIRTUAL_IMAGE_ENDPOINT}/{virtual_image_id}/files?filename={filename}"
        response: Response = self._delete(url)
        return APIResponse(**response.json())

    def delete_virtual_image(self, virtual_image_id: int) -> APIResponse:
        """
        Delete a virtual image by its ID.

        Args:
            virtual_image_id (int): The ID of the virtual image to be deleted.

        Returns:
            APIResponse: The response from the API after attempting to delete the virtual image.

        Raises:
            AssertionError: If the response status code is not 200 (OK) \
            an assertion error is raised with the response status code and text.
        """
        response: Response = self._delete(f"{VIRTUAL_IMAGE_ENDPOINT}/{virtual_image_id}")
        return APIResponse(**response.json())
