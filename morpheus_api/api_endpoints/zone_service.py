from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.zone import Zone, ZoneList

ZONE_ENDPOINT = MorpheusAPIEndpoints.ZONES.value


class ZoneService(MorpheusAPI):
    """ZoneService class provides methods to interact with the Morpheus API to manage zones.

    This class provides methods strictly following /api/zones endpoint in Morpheus API.

    But all zone-related methods can be found in zone_steps.py file.
    """

    def list_zones(self) -> ZoneList:
        """
        Retrieves a list of zones from the API.

        Returns:
            ZoneList: An object containing the list of zones.

        Raises:
            AssertionError: If the response status code is not 200 (OK), an assertion error is raised.
        """
        response: Response = self._get(ZONE_ENDPOINT)
        return ZoneList(**response.json())

    def get_zone(self, zone_id: int) -> Zone:
        """
        Retrieve a zone by its ID.

        Args:
            zone_id (int): The ID of the zone to retrieve.

        Returns:
            Zone: An instance of the Zone class populated with the retrieved zone data.

        Raises:
            AssertionError: If the response status code is not 200 (OK).

        """
        response: Response = self._get(f"{ZONE_ENDPOINT}/{zone_id}")
        return Zone(**response.json())
