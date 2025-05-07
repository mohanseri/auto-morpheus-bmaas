from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.cluster import Cluster, ClusterList
from morpheus_api.dataclasses.datastore import Datastore, DatastoreList
from morpheus_api.dataclasses.cluster_layout import ClusterLayout

CLUSTER_ENDPOINT = MorpheusAPIEndpoints.CLUSTERS.value


class ClusterService(MorpheusAPI):
    """ClusterService class provides methods to interact with the Morpheus API to manage clusters.

    This class provides methods strictly following /api/clusters endpoint in Morpheus API.

    But all cluster-related methods can be found in cluster_steps.py file.
    """

    def list_clusters(
        self,
        max: int = 25,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
    ) -> ClusterList:
        """
        Retrieves a list of clusters with optional pagination and sorting.

        Args:
            max (int, optional): The maximum number of clusters to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field by which to sort the clusters. Defaults to "name".
            direction (str, optional): The direction of the sort, either "asc" for ascending or "desc" for descending.
            Defaults to "asc".

        Returns:
            ClusterList: The ClusterList object containing the list of clusters.
        """
        response: Response = self._get(
            f"{CLUSTER_ENDPOINT}?max={max}&offset={offset}&sort={sort}&direction={direction}"
        )
        return ClusterList(**response.json())

    def get_cluster_by_id(self, cluster_id: int) -> Cluster:
        """
        Retrieve details of a specific cluster by its ID.

        Args:
            cluster_id (int): The unique identifier of the cluster.

        Returns:
            Cluster: An object containing the details of the cluster.
        """
        response: Response = self._get(f"{CLUSTER_ENDPOINT}/{cluster_id}")
        return Cluster(**response.json())

    def create_cluster(self, data) -> dict:
        """
        Create a new cluster.

        This method sends a POST request to the /api/clusters endpoint with the provided data to create a new cluster.

        Args:
            data (dict): A dictionary containing the data required to create the cluster.

        Returns:
            Response: The response object from the POST request.
        """
        response: Response = self._post(CLUSTER_ENDPOINT, data)
        return response.json()

    def delete_cluster(self, cluster_id: int) -> dict:
        """
        Deletes a cluster with the specified cluster ID.

        Args:
            cluster_id (int): The ID of the cluster to be deleted.

        Returns:
            Response: The response from the API after attempting to delete the cluster.
        """
        response: Response = self._delete(f"{CLUSTER_ENDPOINT}/{cluster_id}")
        return response.json()

    def list_datastores(
        self,
        cluster_id: int,
        max: int = 25,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
        phrase: str = "",
        name: str = "",
        code: str = "",
        hide_inactive: bool = False,
    ) -> DatastoreList:
        """
        Retrieves a list of datastores for a specific cluster with optional pagination and sorting.

        Args:
            cluster_id (int): The unique identifier of the cluster.
            max (int, optional): The maximum number of datastores to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field by which to sort the datastores. Defaults to "name".
            direction (str, optional): The direction of the sort, either "asc" for ascending or "desc" for descending.
            Defaults to "asc".
            phrase (str, optional): The phrase to search for in the datastores. Defaults to "".
            name (str, optional): The name of the datastore to search for. Defaults to "".
            code (str, optional): The code of the datastore to search for. Defaults to "".
            hide_inactive (bool, optional): Whether to hide inactive datastores. Defaults to False.

        Returns:
            DatastoreList: A DatastoreList containing the list of datastores.
        """
        url: str = f"{CLUSTER_ENDPOINT}/{cluster_id}/datastores"
        params: str = (
            f"max={max}&offset={offset}&sort={sort}&direction={direction}&phrase={phrase}&name={name}&code={code}&hideInactive={hide_inactive}"
        )

        response: Response = self._get(f"{url}?{params}")
        return DatastoreList(**response.json())

    def get_datastore_by_id(self, cluster_id: int, datastore_id: int) -> Datastore:
        """
        Retrieve details of a specific datastore by its ID within a cluster.

        Args:
            cluster_id (int): The unique identifier of the cluster.
            datastore_id (int): The unique identifier of the datastore.

        Returns:
            Datastore: A Datastore containing the details of the datastore.
        """
        response: Response = self._get(f"{CLUSTER_ENDPOINT}/{cluster_id}/datastores/{datastore_id}")
        return Datastore(**response.json())

    def get_cluster_layout_by_id(self, cluster_layout_id: int) -> ClusterLayout:
        """
        Retrieve details of a specific cluster by its ID.

        Args:
            cluster_layout_id (int): The unique identifier of the cluster layout.

        Returns:
            ClusterLayout: An object containing the details of the cluster layout.
        """
        response: Response = self._get(f"{CLUSTER_ENDPOINT}/{cluster_layout_id}")
        return ClusterLayout(**response.json())
