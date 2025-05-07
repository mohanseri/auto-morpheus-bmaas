from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.provision_type import ProvisionType, ProvisionTypeList

PROVISION_TYPE_ENDPOINT = MorpheusAPIEndpoints.PROVISION_TYPES.value


class ProvisionTypeService(MorpheusAPI):
    """ProvisionTypeService class provides methods to interact with the Morpheus API to manage provision types.

    This class provides methods strictly following /api/provision-types endpoint in Morpheus API.

    But all provision-type-related methods can be found in provision_type_steps.py file.
    """

    def list_provision_types(
        self,
        max: int = 25,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
        name: str = "KVM",
    ) -> ProvisionTypeList:
        """
        Retrieves a list of provision types with optional pagination and sorting.

        Args:
            max (int, optional): The maximum number of provision types to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field to sort the provision types by. Defaults to "name".
            direction (str, optional): The direction to sort the provision types. Defaults to "asc".
            name (str, optional): The name of the provision type for filtering. Defaults to "KVM".

        Returns:
            ProvisionTypeList: A list of provision types.

        Raises:
            AssertionError: If the response status code is not 200 (OK), an assertion error is raised.
        """
        url = f"{PROVISION_TYPE_ENDPOINT}?max={max}&offset={offset}&sort={sort}&direction={direction}"

        if name:
            url = f"{url}&name={name}"

        response: Response = self._get(url)
        return ProvisionTypeList(**response.json())

    def get_provision_type(self, provision_type_id: int) -> ProvisionType:
        """
        Retrieve a provision type by its ID.

        Args:
            provision_type_id (int): The ID of the provision type to retrieve.

        Returns:
            ProvisionType: An instance of ProvisionType containing the details of the retrieved provision type.

        Raises:
            AssertionError: If the response status code is not 200 (OK), an assertion error is raised.
        """
        response: Response = self._get(f"{PROVISION_TYPE_ENDPOINT}/{provision_type_id}")
        return ProvisionType(**response.json())
