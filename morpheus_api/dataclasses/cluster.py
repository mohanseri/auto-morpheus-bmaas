from typing import Optional
from pydantic.dataclasses import dataclass
from dataclasses import field

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import Meta


class Cluster(BaseObject):
    id: int
    name: str
    enabled: bool
    visibility: str
    status: str
    managed: bool
    status_message: Optional[str] = None
    location: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None


class ClusterList(BaseObject):
    clusters: list[Cluster]
    meta: Meta


@dataclass
class ClusterCreateData:
    name: str
    cloud: int
    type: int
    config: Optional[dict] = field(default_factory=dict)
    labels: Optional[list[str]] = field(default_factory=list)
