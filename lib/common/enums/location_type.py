from enum import Enum


class LocationType(Enum):
    SERVER = "server"  # also termed as HOST
    PROVIDER = "provider"
    INSTANCE = "instance"
