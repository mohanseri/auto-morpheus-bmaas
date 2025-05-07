from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.instance import InstanceTypeList
from morpheus_api.dataclasses.instance_type_layout import InstanceTypeLayout, InstanceType

INSTANCE_TYPE_ENDPOINT = MorpheusAPIEndpoints.INSTANCE_TYPES.value


class InstanceTypeService(MorpheusAPI):
    """InstanceTypeService class provides methods to interact with the Morpheus API to manage instance types.

    This class provides methods strictly following /api/instance-types endpoint in Morpheus API.

    But all instance-type-related methods can be found in instance_type_steps.py file.
    """

    def get_all_instance_types(
        self,
        max: int = 25,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
        name: str = "HPE VM",
    ) -> InstanceTypeList:
        """
        Retrieves a list of all instance types with pagination and sorting options.

        Args:
            max (int, optional): The maximum number of instance types to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field by which to sort the instance types. Defaults to "name".
            direction (str, optional): The direction of sorting, either "asc" for ascending or "desc" for descending.
            Defaults to "asc".
            name (str, optional): Name of the instance-type to filter with. Defaults to "HPE Virtualization".

        Returns:
            InstanceTypeList: An object containing the instance types retrieved from the API.

        Raises:
            AssertionError: If the API response status code is not 200 (OK)
        """
        url = f"{INSTANCE_TYPE_ENDPOINT}?max={max}&offset={offset}&sort={sort}&direction={direction}"
        if name:
            url = f"{url}&name={name}"

        response: Response = self._get(url)
        return InstanceTypeList(**response.json())

    def get_instance_type_layouts(self, instance_type_id: int) -> list[InstanceTypeLayout]:
        """
        Retrieve layouts for a specific instance type by its ID.

        Args:
            instance_type_id (int): The unique identifier of the instance type.

        Returns:
            list[InstanceTypeLayout]: A list of layouts for the instance type.
        """
        response: Response = self._get(f"{INSTANCE_TYPE_ENDPOINT}/{instance_type_id}")

        instance_type: InstanceType = InstanceType(**response.json()["instanceType"])

        return instance_type.instance_type_layouts
