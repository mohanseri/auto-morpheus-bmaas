from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.storage_bucket import (
    StorageBucketList,
    StorageBucket,
)

STORAGE_BUCKET_ENDPOINT = MorpheusAPIEndpoints.STORAGE_BUCKETS.value


class StorageBucketService(MorpheusAPI):
    """StorageBucketService class provides methods to interact with the Morpheus API to manage storage buckets.

    This class provides methods strictly following /api/storage-buckets endpoint in Morpheus API.

    But all storage-bucket-related methods can be found in storage_bucket_steps.py file.
    """

    def list_storage_buckets(
        self,
        max: int = 25,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
        phrase: str = "",
        name: str = "",
    ) -> StorageBucketList:
        """
        Retrieves a list of storage buckets with optional pagination and sorting.

        Args:
            max (int, optional): The maximum number of storage buckets to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field by which to sort the storage buckets. Defaults to "name".
            direction (str, optional): The direction in which to sort the storage buckets. Defaults to "asc".
            phrase (str, optional): The phrase to search for in the storage buckets. Defaults to "".
            name (str, optional): The name of the storage bucket to search for. Defaults to "".

        Returns:
            StorageBucketList: The StorageBucketList object containing the list of storage buckets.
        """
        params: str = f"max={max}&offset={offset}&sort={sort}&direction={direction}&phrase={phrase}&name={name}"

        response: Response = self._get(f"{STORAGE_BUCKET_ENDPOINT}?{params}")
        return StorageBucketList(**response.json())

    def get_storage_bucket_by_id(self, storage_bucket_id: int) -> StorageBucket:
        """
        Retrieves a storage bucket by its ID.

        Args:
            storage_bucket_id (int): The ID of the storage bucket to retrieve.

        Returns:
            StorageBucket: The StorageBucket object containing the storage bucket.
        """
        url: str = f"{STORAGE_BUCKET_ENDPOINT}/{storage_bucket_id}"

        response: Response = self._get(url)
        return StorageBucket(**response.json())
