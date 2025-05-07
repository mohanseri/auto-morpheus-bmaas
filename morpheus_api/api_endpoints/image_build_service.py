from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.image_build import ImageBuild, ImageBuildList

IMAGE_BUILD_ENDPOINT = MorpheusAPIEndpoints.IMAGE_BUILDS.value


class ImageBuildService(MorpheusAPI):
    """ImageBuildService class provides methods to interact with the Morpheus API to manage image builds.

    This class provides methods strictly following /api/image-builds endpoint in Morpheus API.

    But all image-build-related methods can be found in image_build_steps.py file.
    """

    def list_image_builds(self) -> ImageBuildList:
        """
        Retrieves a list of image builds with optional pagination and sorting.

        Returns:
            ImageBuildList: The VirtualImageList object containing the list of virtual images.
        """
        response: Response = self._get(IMAGE_BUILD_ENDPOINT)
        return ImageBuildList(**response.json())

    def get_image_build_by_id(self, image_build_id: int) -> ImageBuild:
        """
        Retrieve details of a specific virtual image by its ID.

        Args:
            image_build_id (int): The unique identifier of the image build.

        Returns:
            ImageBuild: An object containing the details of the virtual image.
        """
        response: Response = self._get(f"{IMAGE_BUILD_ENDPOINT}/{image_build_id}")
        return ImageBuild(**response.json())
