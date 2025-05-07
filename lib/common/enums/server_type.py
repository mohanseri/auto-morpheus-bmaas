from enum import Enum


class ServerTypePlacementStrategy(Enum):
    AUTO = "auto"
    FAILOVER = "failover"
    PINNED = "pinned"
