from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.storage_volume_type import StorageVolumeType, StorageVolumeTypeList

STORAGE_VOLUME_TYPE_ENDPOINT = MorpheusAPIEndpoints.STORAGE_VOLUME_TYPES.value


class StorageVolumeTypeService(MorpheusAPI):
    """StorageVolumeTypeService class provides methods to interact with the Morpheus API to manage storage volume types.

    This class provides methods strictly following /api/storage-volume-types endpoint in Morpheus API.

    But all storage-volume-type-related methods can be found in storage_volume_type_steps.py file.
    """

    def list_storage_volumes(
        self,
        max: int = 100,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
        name: str = "",
        code: str = "",
        phrase: str = "",
    ) -> StorageVolumeTypeList:
        """
        Retrieves a list of storage volume types with optional pagination and sorting.

        Args:
            max (int, optional): The maximum number of clusters to return. Defaults to 100.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field by which to sort the clusters. Defaults to "name".
            direction (str, optional): The direction of the sort, either "asc" for ascending or "desc" for descending.
            Defaults to "asc".
            name (str, optional): The name of the service plan to search for. Defaults to "".
            code (str, optional): The code of the service plan to search for. Defaults to "".
            phrase (str, optional): The phrase to search for in the service plans. Defaults to "".

        Returns:
            StorageVolumeTypeList: The StorageVolumeTypeList object containing the list of storage volume types.
        """
        params: str = (
            f"max={max}&offset={offset}&sort={sort}&direction={direction}&name={name}&code={code}&phrase={phrase}"
        )

        response: Response = self._get(f"{STORAGE_VOLUME_TYPE_ENDPOINT}?{params}")
        return StorageVolumeTypeList(**response.json())

    def get_storage_volume_by_id(self, storage_volume_id: int) -> StorageVolumeType:
        """
        Retrieve details of a specific service plan by its ID.

        Args:
            storage_volume_id (int): The unique identifier of the storage volume.

        Returns:
            StorageVolumeType: An object containing the details of the storage volume type.
        """
        response: Response = self._get(f"{STORAGE_VOLUME_TYPE_ENDPOINT}/{storage_volume_id}")
        return StorageVolumeType(**response.json())
