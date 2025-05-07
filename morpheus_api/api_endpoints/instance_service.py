from requests import Response
from urllib.parse import urlencode
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.common_objects import APIResponse
from morpheus_api.dataclasses.container import ContainerList
from morpheus_api.dataclasses.instance import (
    Instance,
    InstanceCreateData,
    InstanceList,
    InstanceResizeData,
    InstanceUpdatePayload,
)
from morpheus_api.dataclasses.processes import ProcessList
import logging

INSTANCE_ENDPOINT = MorpheusAPIEndpoints.INSTANCES.value

logger = logging.getLogger()


class InstanceService(MorpheusAPI):
    """InstanceService class provides methods to interact with the Morpheus API to manage instances.

    This class provides methods strictly following /api/instances endpoint in Morpheus API.

    But all instance-related methods can be found in instance_steps.py file.

    NOTE: The only exception is that Backup & Snapshot specific APIs that use /api/instances endpoint will be found in their respective services.

    Methods:
        list_instances(max_results=100, filter: str = "") -> InstanceList:
            Lists all instances with optional filtering and maximum results limit.
        get_instance(instance_id) -> Instance:
            Retrieves a specific instance by its ID.
        create_instance(data):
            Creates a new instance with the provided data.
        delete_instance(instance_id, removeVolumes="on"):
            Deletes an instance by its ID, with an option to remove associated volumes.
        stop_instance(instance_id, data=None, query_params=None):
            Stops an instance by its ID with optional data and query parameters.
        start_instance(instance_id, data=None, query_params=None):
            Starts an instance by its ID with optional data and query parameters.
        restart_instance(instance_id, data=None, query_params=None):
            Restarts an instance by its ID with optional data and query parameters.
        suspend_instance(instance_id, data=None, query_params=None):
            Suspends an instance by its ID with optional data and query parameters.
        resize_instance(instance_id, data):
            Resizes an instance by its ID with the provided data.
        clone_instance(instance_id: int, clone_instance_name: str) -> dict:
            Clones a specific instance by its ID and assigns a new name to the cloned instance.
        add_node_to_instance(self, instance_id: int) -> APIResponse:
            Add nodes /computing servers to instance
        get_containers_for_instance(self, instance_id: int):
            This function provides details of the compute server(s) running on an instance
    """

    def list_instances(self, max_results=100, filter: str = "") -> InstanceList:
        """
        Retrieves a list of instances from the API.

        Args:
            max_results (int, optional): The maximum number of results to return. Defaults to 100.
            filter (str, optional): A filter string to apply to the instance list. Defaults to "".
        Returns:
            InstanceList: An object containing the list of instances.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        endpoint = f"{INSTANCE_ENDPOINT}?max={max_results}"

        if filter:
            endpoint = f"{endpoint}&{filter}"

        response: Response = self._get(endpoint)
        return InstanceList(**response.json())

    def get_instance(self, instance_id: int) -> Instance:
        """
        Retrieve an instance by its ID.

        Args:
            instance_id (int): The unique identifier of the instance to retrieve.
        Returns:
            Instance: An Instance object populated with the data from the response.
        Raises:
            AssertionError: If the response status code is not 200 (OK), \
                an assertion error is raised with the response details.
        """
        response: Response = self._get(f"{INSTANCE_ENDPOINT}/{instance_id}")
        return Instance(**response.json())

    def create_instance(self, instance_payload: InstanceCreateData) -> Instance:
        """
        Creates a new instance using the provided data.

        Args:
            instance_payload (InstanceCreateData): The data required to create a new instance.
        Returns:
            Instance: The instance object created from the API response.
        Raises:
            AssertionError: If the response status code is not 200 (OK), \
                an assertion error is raised with the response code and text.
        """
        instance_create_data = instance_payload.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        logger.info(f"Creating instance with data: {instance_create_data}")

        response: Response = self._post(INSTANCE_ENDPOINT, instance_create_data)
        return Instance(**response.json())

    def delete_instance(
        self,
        instance_id: int,
        force: str = "off",
        remove_volumes: str = "on",
        expecting_error: bool = False,
    ) -> APIResponse:
        """
        Deletes an instance with the given instance ID.

        Args:
            instance_id (int): The ID of the instance to be deleted.
            force (str, optional): Flag to indicate whether to force delete the instance. Defaults to "off".
            remove_volumes (str, optional): Flag to indicate whether to remove volumes associated with the instance.
                           Defaults to "on".
            expecting_error (bool, optional): Flag to indicate if the API is expected to return an error. Defaults to False.
        Returns:
            APIResponse: The APIResponse from the API containing the delete instance success / failure result.
        """
        response: Response = self._delete(
            endpoint=f"{INSTANCE_ENDPOINT}/{instance_id}?force={force}&removeVolumes={remove_volumes}",
            expecting_error=expecting_error,
        )
        return APIResponse(**response.json())

    def stop_instance(self, instance_id: int, data=None, query_params=None) -> APIResponse:
        """
        Stops an instance with the given instance ID.

        Args:
            instance_id (int): The ID of the instance to stop.
            data (dict, optional): The data to send in the request body. Defaults to None.
            query_params (dict, optional): The query parameters to include in the request URL. Defaults to None.
        Returns:
            APIResponse: The APIResponse from the API containing the stop instance success / failure result.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        endpoint = f"{INSTANCE_ENDPOINT}/{instance_id}/stop"
        if query_params:
            endpoint = f"{endpoint}?{query_params}"
        response: Response = self._put(endpoint, data)
        return APIResponse(**response.json())

    def start_instance(self, instance_id: int, data=None, query_params=None) -> APIResponse:
        """
        Start an instance with the given instance ID.

        Args:
            instance_id (int): The ID of the instance to start.
            data (dict, optional): The data to send in the request body. Defaults to None.
            query_params (dict, optional): The query parameters to include in the request URL. Defaults to None.
        Returns:
            APIResponse: The APIResponse from the API containing the start instance success / failure result.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        endpoint = f"{INSTANCE_ENDPOINT}/{instance_id}/start"
        if query_params:
            endpoint = f"{endpoint}?{query_params}"
        response: Response = self._put(endpoint, data)
        return APIResponse(**response.json())

    def restart_instance(self, instance_id: int, data=None, query_params=None) -> APIResponse:
        """
        Restart an instance with the given instance ID.

        Args:
            instance_id (int): The ID of the instance to restart.
            data (dict, optional): The data to send in the request body. Defaults to None.
            query_params (dict, optional): The query parameters to include in the request URL. Defaults to None.
        Returns:
            APIResponse: The APIResponse from the API containing the restart instance success / failure result.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        endpoint = f"{INSTANCE_ENDPOINT}/{instance_id}/restart"
        if query_params:
            endpoint = f"{endpoint}?{query_params}"
        response: Response = self._put(endpoint, data)
        return APIResponse(**response.json())

    def suspend_instance(self, instance_id: int, data=None, query_params=None) -> APIResponse:
        """
        Suspend an instance by its ID.

        Args:
            instance_id (int): The ID of the instance to suspend.
            data (dict, optional): The data to send in the request body. Defaults to None.
            query_params (dict, optional): The query parameters to include in the URL. Defaults to None.
        Returns:
            APIResponse: The APIResponse from the API containing the suspend instance success / failure result.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        endpoint = f"{INSTANCE_ENDPOINT}/{instance_id}/suspend"
        if query_params:
            endpoint = f"{endpoint}?{query_params}"
        response: Response = self._put(endpoint, data)
        return APIResponse(**response.json())

    def resize_instance(self, instance_id: int, resize_payload: InstanceResizeData) -> tuple[APIResponse, Instance]:
        """
        Resize an instance with the given instance ID using the provided data.

        Args:
            instance_id (int): The ID of the instance to be resized.
            resize_payload (InstanceResizeData): The data containing the resize parameters.

        Returns:
            APIResponse: The APIResponse from the API containing the resize instance success / failure result.
            Instance: The resized instance object.

        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        instance_resize_payload = resize_payload.model_dump(by_alias=True, exclude_none=True)

        logger.info(f"Resizing instance with data: {instance_resize_payload}")

        response: Response = self._put(f"{INSTANCE_ENDPOINT}/{instance_id}/resize", instance_resize_payload)
        response_json = response.json()

        api_response = APIResponse(**response_json)
        resized_instance = Instance(**response_json)

        return api_response, resized_instance

    def clone_instance(self, instance_id: int, clone_instance_name: str) -> APIResponse:
        """
        Clone an existing instance with a new name.

        Args:
            instance_id (int): The ID of the instance to be cloned.
            clone_instance_name (str): The name for the cloned instance.
        Returns:
            APIResponse: The APIResponse from the API containing the clone instance success / failure result.
        Raises:
            AssertionError: If the API response status code is not 200 OK.
        """
        response: Response = self._put(
            f"{INSTANCE_ENDPOINT}/{instance_id}/clone",
            data={"name": clone_instance_name},
        )
        return APIResponse(**response.json())

    def eject_instance(self, instance_id: int) -> APIResponse:
        """
        This will eject any ISO media on all containers in the instance.

        Args:
            instance_id (int): The ID of the instance to eject.

        Returns:
            APIResponse: The APIResponse from the API containing the instance ejection success / failure result.

        Raises:
            AssertionError: If the API response status code is not 200 (OK)
        """
        url = f"{INSTANCE_ENDPOINT}/{instance_id}/eject"

        response: Response = self._put(url)
        return APIResponse(**response.json())

    def update_instance(
        self, instance_id: int, instance_update_payload: InstanceUpdatePayload
    ) -> tuple[APIResponse, Instance]:
        """
        Updates an instance with the given data.

        Args:
            instance_id (int): The ID of the instance to update.
            instance_update_payload (InstanceUpdatePayload): The data to update the instance with.

        Returns:
            APIResponse: The APIResponse from the API containing the instance update success / failure result.
            Instance: The updated instance object.

        Raises:
            AssertionError: If the API response status code is not 200 (OK)
        """
        url = f"{INSTANCE_ENDPOINT}/{instance_id}"

        instance_update_data = instance_update_payload.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        logger.info(f"Updating instance with data: {instance_update_data}")

        response: Response = self._put(url, instance_update_data)
        response_json = response.json()

        api_response = APIResponse(**response_json)
        updated_instance = Instance(**response_json)

        return api_response, updated_instance

    def lock_instance(self, instance_id: int) -> APIResponse:
        """
        Lock an instance by its ID.

        Args:
            instance_id (int): The ID of the instance to lock.
        Returns:
            APIResponse: The APIResponse from the API.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        response: Response = self._put(f"{INSTANCE_ENDPOINT}/{instance_id}/lock")
        return APIResponse(**response.json())

    def unlock_instance(self, instance_id: int) -> APIResponse:
        """
        Unlock an instance by its ID.

        Args:
            instance_id (int): The ID of the instance to unlock.
        Returns:
            APIResponse: The APIResponse from the API.
        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        response: Response = self._put(f"{INSTANCE_ENDPOINT}/{instance_id}/unlock")
        return APIResponse(**response.json())

    def get_instance_history(
        self,
        instance_id: int,
        container_id: int = None,
        server_id: int = None,
        zone_id: int = None,
    ) -> ProcessList:
        """
        Retrieves a list of an instance processes history.

        Args:
            instance_id (int): The ID of the instance.
            container_id (int): The ID of the container.
            server_id (int): The ID of the server.
            zone_id (int): The ID of the zone.

        Returns:
            ProcessList: An object containing the list of process retrieved from the API.
        """
        query_params = {}
        if container_id:
            query_params["containerId"] = container_id
        if server_id:
            query_params["serverId"] = server_id
        if zone_id:
            query_params["zoneId"] = zone_id

        query_string = f"?{urlencode(query_params)}" if query_params else ""
        response: Response = self._get(f"{INSTANCE_ENDPOINT}/{instance_id}/history{query_string}")
        return ProcessList(**response.json())

    def add_node_to_instance(self, instance_id: int) -> APIResponse:
        """Add nodes /computing servers to instance

        Args:
            instance_id (int): ID of instance

        Returns:
                APIResponse: The APIResponse from the API.
        """
        response: Response = self._put(f"{INSTANCE_ENDPOINT}/action?ids={instance_id}&code=generic-add-node")
        return APIResponse(**response.json())

    def get_containers_for_instance(self, instance_id: int) -> ContainerList:
        """This function provides details of the compute server(s) running on an instance

        Args:
            instance_id (int): ID of instance
        Returns:
            ContainerList: list of containers
        """
        response: Response = self._get(f"{INSTANCE_ENDPOINT}/{instance_id}/containers")
        return ContainerList(**response.json())
