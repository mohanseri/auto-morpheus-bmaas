from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI

from morpheus_api.dataclasses.common_objects import APIResponse
from morpheus_api.dataclasses.container import Container
import logging

CONTAINERS_ENDPOINT = MorpheusAPIEndpoints.CONTAINERS.value

logger = logging.getLogger()


class ContainerService(MorpheusAPI):
    """ContainerService class provides methods to interact with the Morpheus API to manage containers.

    This class provides methods strictly following /api/containers endpoint in Morpheus API.

    But all containers-related methods can be found in caontainers_steps.py file.

    Methods:
        get_container_by_id(self, container_id: int) -> Container:
            Retrieve a container by its ID.
        remove_container(self, container_id: int) -> APIResponse:
            Remove node /computing server/container
    """

    def get_container_by_id(self, container_id: int) -> Container:
        """Retrieve a container by its ID.

        Args:
            container_id (int): The unique identifier of the container to retrieve

        Returns:
            Container: A Container object populated with the data from the response
        """
        response: Response = self._get(f"{CONTAINERS_ENDPOINT}/{container_id}")
        return Container(**response.json())

    def remove_container(self, container_id: int) -> APIResponse:
        """Remove node /computing server/container
        Args:
            container_id (int): ID of The unique identifier of the container

        Returns:
                APIResponse: The APIResponse from the API.
        """
        response: Response = self._put(f"{CONTAINERS_ENDPOINT}/action?ids={container_id}&code=generic-remove-node")
        return APIResponse(**response.json())
