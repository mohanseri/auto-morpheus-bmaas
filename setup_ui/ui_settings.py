import os
import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class ConfigSettings(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra variables

        # Access and store the ENVIRONMENT variable within the class
        environment = os.getenv("ENVIRONMENT")
        logger.info(f"Environment = {environment}")

        # Set env_file conditionally based on the stored environment variable
        if environment == "development":
            env_file = ".env.dev"
        elif environment == "prod":
            env_file = ".env.prod"
        elif environment == "scint":
            env_file = ".env.scint"
        else:
            env_file = ".env.dev"


class HostConfiguration(ConfigSettings):
    """
    Host Configuration for initial setup
    These values will be overridden from .env file.
    """

    iso_file_path: str = "C:/Users/Administrator/Downloads/VMware-ESXi-8.0.2-23305546-HPE-802.0.0.11.6.0.5-May2024.iso"
    host_serial_number_1: str = "3M1D1Z15CD"
    host_serial_number_2: str = "3M1D1Z15CF"
    host_serial_number_3: str = "3M1D1Z15CG"
    host_management_ip_1: str = "10.157.232.44"
    host_management_ip_2: str = "10.157.232.45"
    host_management_ip_3: str = "10.157.232.46"
