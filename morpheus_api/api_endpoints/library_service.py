from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.cluster_layout import ClusterLayoutList
from morpheus_api.dataclasses.instance_type_layout import InstanceTypeLayout, InstanceTypeLayoutList

LIBRARY_ENDPOINT = MorpheusAPIEndpoints.LIBRARY.value


class LibraryService(MorpheusAPI):
    """LibraryService class provides methods to interact with the Morpheus API to manage the library.

    This class provides methods strictly following /api/library endpoint in Morpheus API.

    But all library related methods can be found in library_steps.py file.
    """

    def list_cluster_layouts(
        self,
        max: int = 25,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
    ) -> ClusterLayoutList:
        """
        Retrieves a list of cluster layouts with optional pagination and sorting.

        Args:
            max (int, optional): The maximum number of clusters to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field by which to sort the clusters. Defaults to "name".
            direction (str, optional): The direction of the sort, either "asc" for ascending or "desc" for descending.
            Defaults to "asc".

        Returns:
            ClusterLayoutList: The ClusterLayoutList object containing the list of cluster layouts.
        """
        response: Response = self._get(
            f"{LIBRARY_ENDPOINT}/cluster-layouts?max={max}&offset={offset}&sort={sort}&direction={direction}"
        )
        return ClusterLayoutList(**response.json())

    def get_instance_type_layouts(self, instance_type_id: int) -> InstanceTypeLayoutList:
        """
        Retrieve layouts for a specific instance type by its ID.

        Args:
            instance_type_id (int): The unique identifier of the instance type.

        Returns:
            InstanceTypeLayoutList: An object containing the list of layouts for the instance type.
        """
        response: Response = self._get(f"{LIBRARY_ENDPOINT}/instance-types/{instance_type_id}/layouts")
        return InstanceTypeLayoutList(**response.json())

    def get_instance_type_layout_by_id(self, instance_type_id: int, instance_type_layout_id: int) -> InstanceTypeLayout:
        """
        Retrieve the layout of a specific instance type by its ID.

        Args:
            instance_type_id (int): The ID of the instance type.
            instance_type_layout_id (int): The ID of the instance type layout.

        Returns:
            InstanceTypeLayout: An object representing the instance type layout.

        Raises:
            AssertionError: If the response status code is not 200 (OK).
        """
        response: Response = self._get(
            f"{LIBRARY_ENDPOINT}/instance-types/{instance_type_id}/layouts{instance_type_layout_id}"
        )
        return InstanceTypeLayout(**response.json())
