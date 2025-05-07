from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.common_objects import APIResponse
from morpheus_api.dataclasses.network import Network, NetworkList, NetworkCreateData, NetworkResponse, NetworkRouterList

NETWORK_ENDPOINT = MorpheusAPIEndpoints.NETWORKS.value


class NetworkService(MorpheusAPI):
    """NetworkService class provides methods to interact with the Morpheus API to manage networks.

    This class provides methods strictly following /api/networks endpoint in Morpheus API.

    But all network-related methods can be found in network_steps.py file.
    """

    def list_networks(self, name: str = "") -> NetworkList:
        """
        Retrieve a list of networks from the network service.

        Args:
            name (str, optional): The name of the network to filter by. Defaults to an empty string.

        Returns:
            NetworkList: An object containing the list of networks.

        Raises:
            requests.exceptions.RequestException: If the request to the network service fails.
        """
        endpoint: str = NETWORK_ENDPOINT
        if name:
            endpoint += f"?name={name}"
        response: Response = self._get(endpoint)
        return NetworkList(**response.json())

    def get_network(self, network_id: int) -> Network:
        """
        Retrieve network details by network ID.

        Args:
            network_id (int): The ID of the network to retrieve.

        Returns:
            Network: An instance of the Network class containing the network details.

        Raises:
            HTTPError: If the request to the network endpoint fails.
        """
        response: Response = self._get(f"{NETWORK_ENDPOINT}/{network_id}")
        return NetworkResponse(**response.json()).network

    def create_network(self, network_payload: NetworkCreateData) -> Network:
        """
        Creates a new network using the provided network payload.

        Args:
            network_payload (NetworkCreateData): The data required to create a new network.

        Returns:
            Network: The created network object.

        Raises:
            HTTPError: If the network creation request fails.
        """
        network_create_data = network_payload.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        response: Response = self._post(NETWORK_ENDPOINT, network_create_data)
        return NetworkResponse(**response.json()).network

    def delete_network(self, network_id: int) -> APIResponse:
        """
        Deletes a network with the specified network ID.

        Args:
            network_id (int): The ID of the network to be deleted.

        Returns:
            APIResponse: The APIResponse object containing the result of the delete operation.
        """
        response: Response = self._delete(f"{NETWORK_ENDPOINT}/{network_id}")
        return APIResponse(**response.json())

    def list_network_routers(self, name: str = "") -> NetworkRouterList:
        """
        Retrieve a list of network routers from the network service.

        Args:
            name (str, optional): The name of the network to filter by. Defaults to an empty string.

        Returns:
            NetworkRouterList: An object containing the list of network routers.

        Raises:
            requests.exceptions.RequestException: If the request to the network service fails.
        """
        endpoint: str = f"{NETWORK_ENDPOINT}/routers"
        if name:
            endpoint += f"?name={name}"
        response: Response = self._get(endpoint)
        return NetworkRouterList(**response.json())
