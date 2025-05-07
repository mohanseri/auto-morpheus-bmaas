from enum import Enum


class InstanceStatus(Enum):
    PROVISIONING = "provisioning"
    REMOVING = "removing"
    RUNNING = "running"
    STOPPED = "stopped"
    STOPPING = "stopping"
    SUSPENDED = "suspended"
    FAILED = "failed"
    DEPLOYING = "deploying"
