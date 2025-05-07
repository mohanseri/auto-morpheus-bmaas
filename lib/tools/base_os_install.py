import threading
import time

from lib.common.enums.ilo_device import ILODevice
from lib.common.enums.ilo_boot_option import ILOBootOption

from lib.common.enums.ilo_workload_profile import ILOWorkloadProfile
from lib.tools.ilo_operations import ILOOperations


def install_base_os_on_cluster(cluster_node_ilos: list, iso_url: str, stdout: bool = False):
    """
    This function is used to install a BASE OS on a cluster of iLO hosts.

    Args:
        cluster_node_ilos (list): The list of iLO host iLO IP address, username and password.
            [["ilo_ip", "ilo_username", "ilo_password"], ...]
        iso_url (str): The URL of the ISO file to install.
        stdout (bool): If True, the logs will be printed to stdout. Default is False.
    """
    # create the threads for the ilo nodes
    threads: list[threading.Thread] = []
    for ilo_ip, ilo_username, ilo_password in cluster_node_ilos:
        base_os_install: BASEOSInstall = BASEOSInstall()
        thread = threading.Thread(
            target=base_os_install.install_base_os_on_node,
            args=(ilo_ip, ilo_username, ilo_password, iso_url, stdout),
        )
        threads.append(thread)

    # start the threads
    for thread in threads:
        thread.start()

    # wait for all threads to complete
    for thread in threads:
        thread.join()


class BASEOSInstall:
    """
    This class is used to install a BASE OS on the iLO host.
    """

    def install_base_os_on_node(
        self, ilo_ip: str, ilo_username: str, ilo_password: str, iso_url: str, stdout: bool = False
    ):
        """
        This function is used to install a BASE OS on the iLO host.

        Args:
            ilo_ip (str): The IP address of the iLO host.
            ilo_username (str): The username to connect to the iLO host.
            ilo_password (str): The password to connect to the iLO host.
            iso_url (str): The URL of the ISO file to install.
            stdout (bool): If True, the logs will be printed to stdout. Default is False.
        """
        self.ilo_ip = ilo_ip
        self.ilo_username = ilo_username
        self.ilo_password = ilo_password
        self.iso_url = iso_url
        self.stdout = stdout

        self.host_ilo: ILOOperations = ILOOperations(
            host=self.ilo_ip, username=self.ilo_username, password=self.ilo_password, stdout=self.stdout
        )

        # the OS Install will set the Server Name to "hv-ubuntu"
        self.target_host_name = "hv-ubuntu"
        self.source_host_name = "iso-install"

        self.host_ilo.logger.info(f"[{self.ilo_ip}] START {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}")

        # set hostname to "iso-install" and wait for it to be set to "hv-ubuntu"
        self.host_ilo.logger.info(f"[{self.ilo_ip}] Set Server Name to {self.source_host_name}")
        self.host_ilo.set_server_name(name=self.source_host_name)

        # insert virtual media
        self.host_ilo.logger.info(f"[{self.ilo_ip}] Mounting: {self.iso_url} to cdrom")
        self.host_ilo.insert_virtual_media(media_url=self.iso_url, device=ILODevice.CDROM)

        # set cdrom to boot_once
        self.host_ilo.logger.info(f"[{self.ilo_ip}] Set cdrom to boot_once")
        self.host_ilo.set_vm_status(device=ILODevice.CDROM, boot_option=ILOBootOption.BOOT_ONCE)

        # reset the server to start the install
        self.host_ilo.logger.info(f"[{self.ilo_ip}] Reset the server to start the install")
        self.host_ilo.reset_server()

        # check every 5 minutes to see of the server name has been updated
        self.host_name = self.host_ilo.get_server_name()
        while self.host_name != self.target_host_name:
            self.host_ilo.logger.info(
                f"[{self.ilo_ip}] Sleep for 5 mins. Waiting for server name to be set to {self.target_host_name}..."
            )
            time.sleep(300)
            self.host_name = self.host_ilo.get_server_name()

        self.host_ilo.logger.info(f"[{self.ilo_ip}] Server name is set: {self.host_name}")

        # when the server name is set to "hv-ubuntu", eject the virtual media
        self.host_ilo.logger.info(f"[{self.ilo_ip}] Set cdrom to no_boot")
        self.host_ilo.set_vm_status(device=ILODevice.CDROM, boot_option=ILOBootOption.NO_BOOT)

        self.host_ilo.logger.info(f"[{self.ilo_ip}] Ejecting virtual media")
        self.host_ilo.eject_virtual_media(device=ILODevice.CDROM)

        self.host_ilo.logger.info(f"[{self.ilo_ip}] END {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}")

        self.host_ilo.set_workload_profile()
        self.host_ilo.reset_server()
        time.sleep(300)
        ilo_system_settings = self.host_ilo.get_system_settings()
        assert ILOWorkloadProfile.VIRTUALIZATION_MAX_PERFORMANCE.value == ilo_system_settings.json().get(
            "Attributes"
        ).get("WorkloadProfile")
