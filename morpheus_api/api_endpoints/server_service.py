from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.server import (
    Server,
    ServerList,
    ServerData,
)
from morpheus_api.dataclasses.common_objects import APIResponse

import logging

SERVER_ENDPOINT = MorpheusAPIEndpoints.SERVERS.value

logger = logging.getLogger()


class ServerService(MorpheusAPI):
    """ServerService class provides methods to interact with the Morpheus API to manage servers.

    This class provides methods strictly following /api/servers endpoint in Morpheus API.

    But all server-related methods can be found in server_steps.py file.

    NOTE: The usage of terms 'server' and 'hosts' are relatively the same.
    Please refer to the API endpoint & can verify functionality usage in server_steps.py
    """

    def list_servers(self, query_params: str = None) -> ServerList:
        """Retrieves a list of all servers.

        Args:
            query_params (str, optional): _description_. Defaults to None.

        Returns:
            ServerList: The list of all servers.
        """
        endpoint = SERVER_ENDPOINT
        if query_params:
            endpoint += f"?{query_params}"
        response: Response = self._get(endpoint)
        logger.info(f"Response: {response.json()}")
        return ServerList(**response.json())

    def get_a_specific_server(self, instance_server_id: int) -> Server:
        """
        Retrieves a specific server by its ID.

        Args:
            instance_server_id (str): The ID of the server to retrieve.

        Returns:
            Server: The server object representing the server.
        """
        endpoint = f"{SERVER_ENDPOINT}/{instance_server_id}"
        response: Response = self._get(endpoint)
        logger.info(f"Response: {response.json()}")
        return Server(**response.json())

    def manage_server_placement_for_vm(self, instance_server_id: int, server_placement_data: ServerData) -> APIResponse:
        """
        Manages the server placement for a VM.

        Args:
            instance_server_id (str): The ID of the VM for which to manage the server placement. Only supported for MVM virtual machines.
            server_placement_data (ServerData): The data to manage the server placement for the VM.

        Returns:
            APIResponse: Success status of the operation.
        """
        endpoint = f"{SERVER_ENDPOINT}/{instance_server_id}/placement"
        server_placement_payload = server_placement_data.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        logger.info(f"Creating server placement payload: {server_placement_payload}")

        response: Response = self._put(
            endpoint,
            server_placement_payload,
        )
        return APIResponse(**response.json())

    def start_a_server(self, instance_server_id: str) -> APIResponse:
        """
        Starts a server.

        Args:
            instance_server_id (str): The ID of the server to start.

        Returns:
            APIResponse: Success status of the operation.
        """
        endpoint = f"{SERVER_ENDPOINT}/{instance_server_id}/start"
        response: Response = self._post(endpoint)
        return APIResponse(**response.json())

    def stop_a_server(self, instance_server_id: str) -> APIResponse:
        """
        Stops a server.

        Args:
            instance_server_id (str): The ID of the server to stop.

        Returns:
            APIResponse: Success status of the operation.
        """
        endpoint = f"{SERVER_ENDPOINT}/{instance_server_id}/stop"
        response: Response = self._post(endpoint)
        return APIResponse(**response.json())

    def enable_maintenance_mode(self, server_id: int) -> APIResponse:
        """This will enable maintenance mode on the HPE VME host.

        Args:
            server_id (int): server or host id.

        Returns:
            APIResponse: Success status of the operation.
        """
        response: Response = self._put(endpoint=f"{SERVER_ENDPOINT}/{server_id}/maintenance")
        return APIResponse(**response.json())

    def leave_maintenance_mode(self, server_id: int) -> APIResponse:
        """This will leave maintenance mode on the HPE VME host.

        Args:
            server_id (int): server or host id.

        Returns:
            APIResponse: Success status of the operation.
        """
        response: Response = self._put(endpoint=f"{SERVER_ENDPOINT}/{server_id}/leave-maintenance")
        return APIResponse(**response.json())
