from morpheus_api.dataclasses.base_object import BaseObject


class ContainerDetails(BaseObject):
    id: int
    name: str
    uuid: str
    account_id: int
    status: str


# Single container
class Container(BaseObject):
    container: ContainerDetails


# List of containers
class ContainerList(BaseObject):
    containers: list[ContainerDetails]
