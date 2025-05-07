import os
import logging
from dotenv import dotenv_values
from pydantic_settings import BaseSettings
from typing import Any, ClassVar
from morpheus_api.api_endpoints.backup_service import BackupService
from morpheus_api.api_endpoints.container_service import ContainerService
from morpheus_api.api_endpoints.library_service import LibraryService
from morpheus_api.api_endpoints.cluster_service import ClusterService
from morpheus_api.api_endpoints.group_service import GroupService
from morpheus_api.api_endpoints.server_service import ServerService
from morpheus_api.api_endpoints.image_build_service import ImageBuildService
from morpheus_api.api_endpoints.instance_service import InstanceService
from morpheus_api.api_endpoints.instance_type_service import InstanceTypeService
from morpheus_api.api_endpoints.network_service import NetworkService
from morpheus_api.api_endpoints.network_type_service import NetworkTypeService
from morpheus_api.api_endpoints.option_service import OptionService
from morpheus_api.api_endpoints.provision_type_service import ProvisionTypeService
from morpheus_api.api_endpoints.storage_bucket_service import StorageBucketService
from morpheus_api.api_endpoints.service_plan_service import ServicePlanService
from morpheus_api.api_endpoints.snapshot_service import SnapshotService
from morpheus_api.api_endpoints.storage_volume_type_service import StorageVolumeTypeService
from morpheus_api.api_endpoints.virtual_image_service import VirtualImageService
from morpheus_api.api_endpoints.storage_volume_service import StorageVolumeService
from morpheus_api.api_endpoints.zone_service import ZoneService

logger = logging.getLogger(__name__)


# API Related Settings
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


class CommonSettings(ConfigSettings):
    """
    CommonSettings is a configuration class that loads settings from a .env.base file.

    Attributes:
        base_env (ClassVar): A dictionary containing environment variables loaded from .env.base.
        instances (str): The instances setting, default is "default-instances".
        dm_core (str): The DM core setting, default is "default-dm-core".
        http_proxy (str): The HTTP proxy setting, default is "http://hpeproxy.its.hpecorp.net:443".
        https_proxy (str): The HTTPS proxy setting, default is "http://hpeproxy.its.hpecorp.net:443".
        vdbench_directory (str): The Vdbench directory setting, default is "/home/".
        resource_directory (str): The resource directory setting, default is "lib/resources/vdbench".
        vdbench_folder (str): The Vdbench folder setting, default is "vdbench50407".
        vdbench_archive (str): The Vdbench archive setting, default is "vdbench50407.zip".
        vdbench_config_path (str): The Vdbench config path setting, default is "/home/".
        vdbench_custom_config_file (str): The Vdbench custom config file setting, default is "vdbench_config".
        vdbench_windows_custom_config_file (str): The Vdbench Windows custom config file setting, default is "vdbench_windows_config".
        vdbench_config_file (str): The Vdbench config file setting, default is "config".
        comp_ratio (str): The compression ratio setting, default is "2".
        validate_vdbench (str): The validate Vdbench setting, default is "no".
        journal (str): The journal setting, default is "no".
        dedup_ratio (str): The deduplication ratio setting, default is "2".
        dedup_unit (str): The deduplication unit setting, default is "4k".
        sd (str): The storage definition setting, default is "sd=sd%s,openflags=o_direct,lun=/dev/%s,range=(0,80),threads=5".
        wd (str): The workload definition setting, default is "wd=seq%s,sd=sd%s,rhpct=0,whpct=0,seekpct=0,xfersize=1M,rdpct=0".
        rd (str): The run definition setting, default is "rd=rd%s,wd=seq*,elapsed=30m,maxdata=8g,interval=1,iorate=max".
        fsd (str): The file system definition setting, default is "fsd=fsd%s,anchor=%s,depth=%s,width=%s,files=%s,size=%s".
        fwd (str): The file workload definition setting, default is "fwd=fwd%s,fsd=fsd%s,operation=%s,xfersize=1M,fileio=sequential,fileselect=random,threads=2".
        frd (str): The file run definition setting, default is "rd=rd%s,fwd=fwd1,fwdrate=100,format=%s,elapsed=10,interval=1".
    """

    base_env: ClassVar = dotenv_values(".env.base")
    instances: str = base_env.get("INSTANCES", "default-instances")
    dm_core: str = base_env.get("DM_CORE", "default-dm-core")
    http_proxy: str = base_env.get("HTTP_PROXY", "http://hpeproxy.its.hpecorp.net:443")
    https_proxy: str = base_env.get("HTTPS_PROXY", "http://hpeproxy.its.hpecorp.net:443")
    vdbench_directory: str = base_env.get("VDBENCH_DIRECTORY", "/home/")
    resource_directory: str = base_env.get("RESOURCE_DIRECTORY", "lib/resources/vdbench")
    vdbench_folder: str = base_env.get("VDBENCH_FOLDER", "vdbench50407")
    vdbench_archive: str = base_env.get("VDBENCH_ARCHIVE", "vdbench50407.zip")
    vdbench_config_path: str = base_env.get("VDBENCH_CONFIG_PATH", "/home/")
    vdbench_custom_config_file: str = base_env.get("VDBENCH_CUSTOM_CONFIG_FILE", "vdbench_config")
    vdbench_windows_custom_config_file: str = base_env.get(
        "VDBENCH_WINDOWS_CUSTOM_CONFIG_FILE", "vdbench_windows_config"
    )
    vdbench_config_file: str = base_env.get("VDBENCH_CONFIG_FILE", "config")
    comp_ratio: str = base_env.get("COMP_RATIO", "2")
    validate_vdbench: str = base_env.get("VALIDATE_VDBENCH", "no")
    journal: str = base_env.get("JOURNAL", "no")
    dedup_ratio: str = base_env.get("DEDUP_RATIO", "2")
    dedup_unit: str = base_env.get("DEDUP_UNIT", "4k")
    sd: str = base_env.get("SD", "sd=sd%s,openflags=o_direct,lun=/dev/%s,range=(0,80),threads=5")
    wd: str = base_env.get("WD", "wd=seq%s,sd=sd%s,rhpct=0,whpct=0,seekpct=0,xfersize=1M,rdpct=0")
    rd: str = base_env.get("RD", "rd=rd%s,wd=seq*,elapsed=30m,maxdata=8g,interval=1,iorate=max")
    fsd: str = base_env.get("FSD", "fsd=fsd%s,anchor=%s,depth=%s,width=%s,files=%s,size=%s")
    fwd: str = base_env.get(
        "FWD", "fwd=fwd%s,fsd=fsd%s,operation=%s,xfersize=1M,fileio=sequential,fileselect=random,threads=2"
    )
    frd: str = base_env.get("FRD", "rd=rd%s,fwd=fwd1,fwdrate=100,format=%s,elapsed=10,interval=1")


# API Related Settings
class APISettings(ConfigSettings):
    """
    Morpheus API settings.
    These values will be overridden from .env file.
    """

    base_url: str = "https://morpheus8"  # Default base URL
    api_token: str = "YOUR-API-TOKEN"  # Default API token


# Instance Related Settings
class InstanceSettings(ConfigSettings):
    """
    Morpheus instance settings.
    These values will be overridden from .env file.
    """

    site_id: int = 1
    type: str = "mvm"
    instance_type_code: str = "mvm"
    layout_id: int = 269
    layout_code: str = "Morpheus MVM 1.0 on Existing Ubuntu 22.04"
    plan_id: int = 152
    plan_code: str = "kvm-vm-1024"
    instance_name: str = "python-mvm14"
    copies: int = 1
    layout_size: int = 1
    user_name: str = ""
    password: str = ""
    storage_bucket_name: str = ""
    datastore_name: str = ""
    config: dict[str, Any] = {
        "createUser": False,
        "imageId": "402",
        "expose": 8080,
        "resourcePoolId": "pool-2",
        "poolProviderType": "mvm",
        "kvmHostId": 4,
        "noAgent": False,
    }
    zone_id: int = 1
    volumes: list[dict[str, Any]] = [
        {
            "id": -1,
            "root_volume": True,
            "name": "root",
            "size": 10,
            "storage_type": 1,
            "datastore_id": "6",
        }
    ]
    resize_volumes: list[dict[str, Any]] = [
        {
            "id": -1,
            "root_volume": False,
            "name": "data",
            "size": 40,
            "storage_type": 1,
            "datastore_id": "6",
        },
    ]
    network_interfaces: list[dict[str, Any]] = [
        {
            "primary_interface": True,
            "network": {"id": "network-4"},
            "ip_mode": "dhcp",
        }
    ]


class VirtualImageSettings(ConfigSettings):
    virtual_image_location: str = "lib/resources/virtual_images/"
    ubuntu_iso_filename: str = "morpheus_sanity.iso"
    ubuntu_qcow2_filename: str = "morpheus_sanity.qcow2"


class DMCoreSettings(ConfigSettings):
    dmcore_binary: str = "lib/resources/dmcore/dmcore"


class VDBenchSettings(ConfigSettings):
    vdbench_directory: str
    resource_directory: str
    vdbench_folder: str
    vdbench_archive: str
    vdbench_config_path: str
    vdbench_custom_config_file: str
    vdbench_windows_custom_config_file: str
    vdbench_config_file: str
    comp_ratio: str
    validate_vdbench: str
    journal: str
    dedup_ratio: str
    dedup_unit: str
    sd: str
    wd: str
    rd: str
    fsd: str
    fwd: str
    frd: str


class ProxySettings(ConfigSettings):
    http_proxy: str
    https_proxy: str


class MorpheusAPIService:
    """
    A service class to interact with the Morpheus API.

    This class initializes and configures the necessary services to interact with the Morpheus API using the provided
    API settings.

    Attributes:
        instance_service (InstanceService): An instance of the InstanceService class configured with the provided
            API settings.
    Methods:
        __init__(api_settings: APISettings):
            api_settings (APISettings): The settings required to configure the API service, including base URL and

    """

    # Add other services as we make progress
    def __init__(self, api_settings: APISettings):
        self.instance_service = InstanceService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.instance_type_service = InstanceTypeService(
            base_url=api_settings.base_url,
            api_token=api_settings.api_token,
        )
        self.backup_service = BackupService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.cluster_service = ClusterService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.library_service = LibraryService(
            base_url=api_settings.base_url,
            api_token=api_settings.api_token,
        )
        self.group_service = GroupService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.server_service = ServerService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.image_build_service = ImageBuildService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.network_service = NetworkService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.network_type_service = NetworkTypeService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.option_service = OptionService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.provision_type_service = ProvisionTypeService(
            base_url=api_settings.base_url,
            api_token=api_settings.api_token,
        )
        self.option_service = OptionService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.snapshot_service = SnapshotService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.storage_bucket_service = StorageBucketService(
            base_url=api_settings.base_url,
            api_token=api_settings.api_token,
        )
        self.service_plan_service = ServicePlanService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.storage_volume_type_service = StorageVolumeTypeService(
            base_url=api_settings.base_url,
            api_token=api_settings.api_token,
        )
        self.storage_volume_service = StorageVolumeService(
            base_url=api_settings.base_url, api_token=api_settings.api_token
        )
        self.virtual_image_service = VirtualImageService(
            base_url=api_settings.base_url,
            api_token=api_settings.api_token,
        )
        self.zone_service = ZoneService(base_url=api_settings.base_url, api_token=api_settings.api_token)
        self.container_service = ContainerService(base_url=api_settings.base_url, api_token=api_settings.api_token)


# Final combined settings
class MorpheusSettings(ConfigSettings):
    """
    MorpheusSettings is a configuration class that inherits from ConfigSettings.
    It encapsulates various settings required for the Morpheus QA Automation.

    Attributes:
        common_settings (CommonSettings): Common settings shared across different configurations.
        api_settings (APISettings): Settings specific to the API.
        instance_settings (InstanceSettings): Settings related to instances.
        virtual_image_settings (VirtualImageSettings): Settings for virtual images.
        dmcore_settings (DMCoreSettings): Settings for DMCore.
        proxy_settings (ProxySettings): Proxy settings initialized with HTTP and HTTPS proxies from common settings.
        vdbench_settings (VDBenchSettings): VDBench settings initialized with various parameters from common settings.
    """

    common_settings: CommonSettings = CommonSettings()
    api_settings: APISettings = APISettings()
    instance_settings: InstanceSettings = InstanceSettings()
    virtual_image_settings: VirtualImageSettings = VirtualImageSettings()
    dmcore_settings: DMCoreSettings = DMCoreSettings()
    proxy_settings: ProxySettings = ProxySettings(
        http_proxy=common_settings.http_proxy,
        https_proxy=common_settings.https_proxy,
    )
    vdbench_settings: VDBenchSettings = VDBenchSettings(
        vdbench_directory=common_settings.vdbench_directory,
        resource_directory=common_settings.resource_directory,
        vdbench_folder=common_settings.vdbench_folder,
        vdbench_archive=common_settings.vdbench_archive,
        vdbench_config_path=common_settings.vdbench_config_path,
        vdbench_custom_config_file=common_settings.vdbench_custom_config_file,
        vdbench_windows_custom_config_file=common_settings.vdbench_windows_custom_config_file,
        vdbench_config_file=common_settings.vdbench_config_file,
        comp_ratio=common_settings.comp_ratio,
        validate_vdbench=common_settings.validate_vdbench,
        journal=common_settings.journal,
        dedup_ratio=common_settings.dedup_ratio,
        dedup_unit=common_settings.dedup_unit,
        sd=common_settings.sd,
        wd=common_settings.wd,
        rd=common_settings.rd,
        fsd=common_settings.fsd,
        fwd=common_settings.fwd,
        frd=common_settings.frd,
    )
