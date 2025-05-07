from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import IDName, IDNameCode, Meta


class ImageBuild(BaseObject):
    id: int
    account: IDName
    type: IDNameCode
    site: IDName
    zone: IDName
    description: Optional[str] = None


class ImageBuildList(BaseObject):
    image_builds: list[ImageBuild]
    meta: Meta
