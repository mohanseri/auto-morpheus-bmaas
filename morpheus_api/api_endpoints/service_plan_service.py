from requests import Response
from lib.common.enums.morpheus_api_endpoint_type import MorpheusAPIEndpoints
from lib.common.enums.service_plan_name import ServicePlanName
from morpheus_api.configuration.utils import MorpheusAPI
from morpheus_api.dataclasses.service_plan import ServicePlan, ServicePlanList

SERVICE_PLAN_ENDPOINT = MorpheusAPIEndpoints.SERVICE_PLANS.value


class ServicePlanService(MorpheusAPI):
    """ServicePlanService class provides methods to interact with the Morpheus API to manage service plans.

    This class provides methods strictly following /api/service-plans endpoint in Morpheus API.

    But all service-plan-related methods can be found in service_plan_steps.py file.
    """

    def list_service_plans(
        self,
        max: int = 25,
        offset: int = 0,
        sort: str = "name",
        direction: str = "asc",
        name: ServicePlanName = ServicePlanName.CPU_1_MEMORY_1_GB,
    ) -> ServicePlanList:
        """
        Retrieves a list of service plans with optional pagination and sorting.

        Args:
            max (int, optional): The maximum number of clusters to return. Defaults to 25.
            offset (int, optional): The offset from the start of the list. Defaults to 0.
            sort (str, optional): The field by which to sort the clusters. Defaults to "name".
            direction (str, optional): The direction of the sort, either "asc" for ascending or "desc" for descending.
            Defaults to "asc".
            name (ServicePlanName, optional): Name of the service plan to filter with. Defaults to ServicePlanName.CPU_1_MEMORY_1_GB.

        Returns:
            ServicePlanList: The ServicePlanList object containing the list of cluster layouts.
        """
        url = f"{SERVICE_PLAN_ENDPOINT}?max={max}&offset={offset}&sort={sort}&direction={direction}"

        if name:
            url = f"{url}&name={name.value}"

        response: Response = self._get(url)
        return ServicePlanList(**response.json())

    def get_service_plan_by_id(self, service_plan_id: int) -> ServicePlan:
        """
        Retrieve details of a specific service plan by its ID.

        Args:
            service_plan_id (int): The unique identifier of the service plan.

        Returns:
            ServicePlan: An object containing the details of the service plan.
        """
        response: Response = self._get(f"{SERVICE_PLAN_ENDPOINT}/{service_plan_id}")
        return ServicePlan(**response.json())
