from enum import Enum


class VirtualImageStatus(Enum):
    ACTIVE = "Active"
    SAVING = "Saving"
    FAILED = "Failed"
