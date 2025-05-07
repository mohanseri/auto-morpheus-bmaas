from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.network_options import NetworkOptions

OPTION_ENDPOINT = MorpheusAPIEndpoints.OPTIONS.value


class OptionService(MorpheusAPI):
    """OptionService class provides methods to interact with the Morpheus API to manage options.

    This class provides methods strictly following /api/options endpoint in Morpheus API.

    But all option-related methods can be found in option_steps.py file.
    """

    def get_network_options_for_cloud(self, zone_id: int, provision_type_id: int) -> NetworkOptions:
        """
        Retrieve network options for a specific cloud zone and provision type.

        Args:
            zone_id (int): The ID of the cloud zone.
            provision_type_id (int): The ID of the provision type.

        Returns:
            NetworkOptions: An instance containing the network options.

        Raises:
            AssertionError: If the response status code is not 200 (OK), with the response status code and text.
        """
        response: Response = self._get(
            f"{OPTION_ENDPOINT}/zoneNetworkOptions?zoneId={zone_id}&provisionTypeId={provision_type_id}"
        )
        return NetworkOptions(**response.json())
