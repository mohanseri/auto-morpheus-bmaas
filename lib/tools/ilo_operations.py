import logging
import sys
import requests

from lib.common.enums.ilo_device import ILODevice
from lib.common.enums.ilo_boot_option import ILOBootOption

from hpilo import Ilo

from hpe_pc_automation_lib.commons.hardware_interfaces.ilo.ilo_utilities import ILOOperations as ILORedfishOperations

from lib.common.enums.ilo_workload_profile import ILOWorkloadProfile
from lib.common.utils import handle_response

REDFISH_BIOS_SETTINGS_URL = "https://{host}/redfish/v1/Systems/1/Bios/Settings"


class ILOOperations:
    """
    This class is used to set Virtual Media to boot and install HV Base OS.
    """

    def __init__(self, host: str, username: str, password: str, stdout: bool = False):
        """
        This method is used to initialize the ILOOperations class.

        Args:
            host (str): The IP address of the host.
            username (str): The username to connect to the host.
            password (str): The password to connect to the host.
            stdout (bool): If True, the logs will be printed to stdout. Default is False.

        Returns:
            None
        """
        self.host = host
        self.username = username
        self.password = password

        # Create non-root logger, to allow stdout stream addition for manual execution
        self.logger = logging.getLogger(f"ILOOperations-{host}")
        self.logger.setLevel(logging.INFO)
        if stdout:
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.hpilo: Ilo = Ilo(self.host, self.username, self.password)
        assert self.hpilo, f"Failed to connect to Host iLO: {self.host}"

        self.logger.info(f"[{self.host}] Connected to Host iLO: {self.host}")

        self.logger.info("Initializing iLO Redfish")
        self.ilo_redfish_operations = ILORedfishOperations(
            ilo_ip=self.host,
            username=self.username,
            password=self.password,
        )
        self.ilo_redfish_operations.create_redfish_session()
        self.logger.info(f"[{self.host}] Connected to Redfish Host iLO: {self.host}")

    def insert_virtual_media(self, media_url: str, device: ILODevice = ILODevice.CDROM):
        """
        This method is used to insert the virtual media file to the host.

        Args:
            media_url (str): The URL of the virtual media file to insert.
            device (ILODevice): The device to insert the virtual media file. Default is ILODevice.CDROM.
                Valid devices: ILODevice.FLOPPY and ILODevice.CDROM.
        Returns:
            None
        """
        self.logger.info(f"[{self.host}] Mounting: {media_url} to {device.value}")
        try:
            insert_status = self.hpilo.insert_virtual_media(device=device.value, image_url=media_url)
            if insert_status:
                self.logger.info(f"[{self.host}] Insert status: {insert_status}")

            vm_status = self.hpilo.get_vm_status()
            self.logger.info(f"[{self.host}] Mounted successfully: {vm_status}")
        except Exception as e:
            self.logger.error(f"[{self.host}] Error mounting: {e}")
            raise e

    def eject_virtual_media(self, device: ILODevice = ILODevice.CDROM):
        """
        This method is used to eject the virtual media file from the host.

        Args:
            device (ILODevice): The device to eject the virtual media file. Default is ILODevice.CDROM.
                Valid devices: ILODevice.FLOPPY and ILODevice.CDROM.

        Returns:
            None
        """
        self.logger.info(f"[{self.host}] Ejecting: {device.value}")
        try:
            eject_status = self.hpilo.eject_virtual_media(device=device.value)
            if eject_status:
                self.logger.info(f"[{self.host}] Eject status: {eject_status}")

            vm_status = self.hpilo.get_vm_status()
            self.logger.info(f"[{self.host}] Ejected successfully: {vm_status}")
        except Exception as e:
            self.logger.error(f"[{self.host}] Error ejecting: {e}")
            raise e

    def set_vm_status(self, device: ILODevice = ILODevice.CDROM, boot_option: ILOBootOption = ILOBootOption.NO_BOOT):
        """
        This method is used to set the virtual media status of the host.

        Args:
            device (ILODevice): The device to set the virtual media status. Default is ILODevice.CDROM.
                Valid devices: ILODevice.FLOPPY and ILODevice.CDROM.
            boot_option (ILOBootOption): The boot option to set. Default is ILOBootOption.NO_BOOT.
                Valid options: ILOBootOption.BOOT_ONCE, ILOBootOption.BOOT_ALWAYS, ILOBootOption.NO_BOOT,
                ILOBootOption.CONNECT, and ILOBootOption.DISCONNECT.

        Returns:
            None
        """
        self.logger.info(f"[{self.host}] Setting VM boot option: {boot_option.value} for {device.value}")
        try:
            set_status = self.hpilo.set_vm_status(device=device.value, boot_option=boot_option.value)
            if set_status:
                self.logger.info(f"[{self.host}] VM set status: {set_status}")

            vm_status = self.hpilo.get_vm_status()
            self.logger.info(f"[{self.host}] Status set successfully: {vm_status}")
        except Exception as e:
            self.logger.error(f"[{self.host}] Error setting VM status: {e}")
            raise e

    def reset_server(self):
        """
        This method is used to reset the server.

        Returns:
            None
        """
        self.logger.info(f"[{self.host}] Resetting server...")
        try:
            reset_status = self.hpilo.reset_server()
            if reset_status:
                self.logger.info(f"[{self.host}] Reset status: {reset_status}")
            self.logger.info(f"[{self.host}] Server reset successfully.")
        except Exception as e:
            self.logger.error(f"[{self.host}] Error resetting server: {e}")
            raise e

    def get_server_name(self):
        """
        This method is used to get the server name.

        Returns:
            str: The server name.
        """
        try:
            server_name = self.hpilo.get_server_name()
            self.logger.info(f"[{self.host}] Server name: {server_name}")
            return server_name
        except Exception as e:
            self.logger.error(f"[{self.host}] Error getting server name: {e}")
            raise e

    def set_server_name(self, name: str):
        """
        This method is used to set the server name.

        Args:
            name (str): The server name to set.

        Returns:
            None
        """
        try:
            result = self.hpilo.set_server_name(name=name)
            if result:
                self.logger.info(f"[{self.host}] Set server name status: {result}")
            self.logger.info(f"[{self.host}] Server name set to: {name}")
            return result
        except Exception as e:
            self.logger.error(f"[{self.host}] Error setting server name: {e}")
            raise e

    def get_system_settings(self) -> requests.Response:
        """Retrieves the system settings of the iLO

        Returns:
            requests.Response: Response with iLO settings
        """
        url = REDFISH_BIOS_SETTINGS_URL.format(host=self.host)
        self.logger.info(f"GET URL = {url}")

        response = requests.get(url, headers=self.ilo_redfish_operations.headers, json={}, verify=False)
        response = handle_response(response)
        self.logger.info(f"Response for GET /bios/settings: {response}")

        return response

    def set_workload_profile(
        self,
        workload_profile: ILOWorkloadProfile = ILOWorkloadProfile.VIRTUALIZATION_MAX_PERFORMANCE,
    ) -> requests.Response:
        """Set the iLO Workload Profile to `Virtualization-MaxPerformance`

        Args:
            workload_profile (ILOWorkloadProfile, optional): Name of the workload profile.
            Defaults to ILOWorkloadProfile.VIRTUALIZATION_MAX_PERFORMANCE.

        Returns:
            dict: Response of the PATCH operation

            #NOTE: Even on successful operation, I see the following error in the response:
            {"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"iLO.2.30.SystemResetRequired"}]}} # noqa E501

            The value is set as expected but this seems common as the system needs a reset
        """
        patch_payload = {"Attributes": {"WorkloadProfile": workload_profile.value}}
        self.logger.info(f"Workload Profile Payload: {patch_payload}")

        url = REDFISH_BIOS_SETTINGS_URL.format(host=self.host)
        self.logger.info(f"PATCH URL = {url}")

        response = requests.patch(url, headers=self.ilo_redfish_operations.headers, json=patch_payload, verify=False)
        response = handle_response(response)
        self.logger.info(f"Response for PATCH /bios/settings: {response}")

        return response
