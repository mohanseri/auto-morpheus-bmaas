from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.volume import StorageVolumeList

STORAGE_VOLUME_ENDPOINT = MorpheusAPIEndpoints.STORAGE_VOLUMES.value


class StorageVolumeService(MorpheusAPI):
    """StorageVolumeService class provides methods to interact with the Morpheus API to manage storage volumes.

    This class provides methods strictly following /api/storage-volumes endpoint in Morpheus API.

    But all storage-volume-related methods can be found in storage_volume_steps.py file.
    """

    def list_volumes(self) -> StorageVolumeList:
        """
        Retrieve a list of storage volumes.

        This method sends a GET request to the "/api/storage-volumes" endpoint
        to fetch and return a list of storage volumes.

        Returns:
            StorageVolumeList: The response object containing the list of storage volumes.
        """
        response: Response = self._get(STORAGE_VOLUME_ENDPOINT)
        return StorageVolumeList(**response.json())
