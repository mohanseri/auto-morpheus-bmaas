from typing import Optional

from pydantic import field_validator
from morpheus_api.dataclasses.base_object import BaseObject


class Volume(BaseObject):
    id: int
    root_volume: bool
    name: str
    size: int
    storage_type: int
    datastore_id: Optional[str] = None
    uuid: Optional[str] = None

    @field_validator("datastore_id", mode="before")
    def convert_datastore_id_to_str(cls, v):
        """
        Convert datastore_id to string if it is an integer.
        This is added because, in some objects, the datastore_id is an int
        """
        if isinstance(v, int):
            return str(v)
        return v


class StorageVolumeList(BaseObject):
    storage_volumes: list[Volume]
