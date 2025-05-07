from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import IDName, Meta


class OSType(BaseObject):
    id: int
    code: str
    name: str
    vendor: str
    category: str
    os_version: str
    bit_count: int
    platform: str
    owner: str
    os_family: Optional[str] = None
    description: Optional[str] = None


class VirtualImage(BaseObject):
    id: int
    name: str
    owner_id: int
    tenant: IDName
    image_type: str
    user_uploaded: bool
    user_defined: bool
    system_image: bool
    is_cloud_init: bool
    os_type: OSType
    accounts: list[IDName]
    status: str
    description: Optional[str] = None
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_password_hash: Optional[str] = None


class VirtualImageList(BaseObject):
    virtual_images: list[VirtualImage]
    meta: Meta


class VirtualImageObject(BaseObject):
    virtual_image: VirtualImage


class VirtualImagePayload(BaseObject):
    name: str
    image_type: str
    os_type: str
    is_cloud_init: bool
    install_agent: bool
    visibility: str
    is_auto_join_domain: bool
    virtio_supported: bool
    vm_tools_installed: bool
    is_force_customization: bool
    trial_version: bool
    is_sysprep: bool
    uefi: bool


class VirtualImageCreateData(BaseObject):
    virtual_image: VirtualImagePayload
