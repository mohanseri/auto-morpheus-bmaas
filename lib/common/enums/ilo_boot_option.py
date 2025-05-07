from enum import Enum


class ILOBootOption(Enum):
    BOOT_ONCE = "boot_once"
    BOOT_ALWAYS = "boot_always"
    NO_BOOT = "no_boot"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
