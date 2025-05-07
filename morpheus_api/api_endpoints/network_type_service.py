from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.network import NetworkTypeList

NETWORK_TYPES_ENDPOINT = MorpheusAPIEndpoints.NETWORK_TYPES.value


class NetworkTypeService(MorpheusAPI):
    """NetworkTypesService class provides methods to interact with the Morpheus API to manage networks.

    This class provides methods strictly following /api/network-types endpoint in Morpheus API.

    But all network-type-related methods can be found in network_steps.py file.
    """

    def list_network_types(self, name: str = "") -> NetworkTypeList:
        """
        Retrieve a list of network types from the API.

        Args:
            name (str, optional): The name of the network type to filter by. Defaults to an empty string.

        Returns:
            NetworkTypeList: An object containing the list of network types.
        """
        endpoint: str = NETWORK_TYPES_ENDPOINT
        if name:
            endpoint += f"?name={name}"
        response: Response = self._get(endpoint)
        return NetworkTypeList(**response.json())
