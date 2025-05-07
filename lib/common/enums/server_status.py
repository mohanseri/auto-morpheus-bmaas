from enum import Enum


class ServerStatus(Enum):
    PROVISIONED = "provisioned"
    MAINTENANCING = "maintenancing"
    MAINTENANCE = "maintenance"
