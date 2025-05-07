from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.group import Group, GroupList

GROUP_ENDPOINT = MorpheusAPIEndpoints.GROUPS.value


class GroupService(MorpheusAPI):
    """GroupService class provides methods to interact with the Morpheus API to manage groups.

    This class provides methods strictly following /api/groups endpoint in Morpheus API.

    But all group-related methods can be found in group_steps.py file.
    """

    def list_groups(self) -> GroupList:
        """
        Retrieves a list of groups from the API.

        Returns:
            GroupList: A GroupList containing the list of groups.

        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        response: Response = self._get(GROUP_ENDPOINT)
        return GroupList(**response.json())

    def get_group(self, group_id: int) -> Group:
        """
        Retrieve a group by its ID.

        Args:
            group_id (int): The ID of the group to retrieve.

        Returns:
            Group: An instance of the Group class populated with the data from the response.

        Raises:
            AssertionError: If the response status code is not 200 (OK), an assertion error is raised.
        """
        response: Response = self._get(f"{GROUP_ENDPOINT}/{group_id}")
        return Group(**response.json())
