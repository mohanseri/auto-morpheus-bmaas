import logging
import time

from waiting import wait, TimeoutExpired

from playwright.sync_api import expect, Page

from setup_ui.constants import NetworkConfiguration
from setup_ui.vmware_initial_setup.dataclasses.host_ip_info import HostSerialNumberIPInfo

from hpe_glcp_automation_lib.libs.commons.utils.pwright.pwright_utils import TableUtils

from setup_ui.vmware_initial_setup.locators.vmware_review_locators import VMWareReviewLocators
from setup_ui.vmware_initial_setup.page_objects.review_validation_page import ReviewValidationPage

logger = logging.getLogger()


class VMWareReviewPage(ReviewValidationPage):
    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page
        self.table_utils = TableUtils(page=self.page)

    def validate_hpe_vme_details(
        self,
        hosts_info: list[HostSerialNumberIPInfo],
        hpe_vme_ip_address: str,
        hpe_vme_appliance_url: str,
        hpe_vme_hostname: str,
        hpe_vme_username: str,
        hpe_vme_ntp_server: str = NetworkConfiguration.NTP_SERVER,
        hpe_vme_vm_size: str = NetworkConfiguration.HPE_VME_VM_SIZE,
        hpe_vme_management_interface: str = NetworkConfiguration.HPE_VME_MANAGEMENT_INTERFACE,
        hpe_vme_dns_servers: str = NetworkConfiguration.DNS_SERVERS_VALIDATION,
        network_details_ntp_server: str = NetworkConfiguration.NTP_SERVER,
        time_zone: str = NetworkConfiguration.TIME_ZONE,
        network_details_dns_servers: str = NetworkConfiguration.DNS_SERVERS_VALIDATION,
        search_domain: str = NetworkConfiguration.SEARCH_DOMAIN,
        netmask: str = NetworkConfiguration.NETMASK,
        gateway: str = NetworkConfiguration.GATEWAY,
        proxy: str = NetworkConfiguration.PROXY,
        no_proxy_list: str = None,
    ):
        """Validates the HPE VME and Host Details entered in the previous steps on the final review screen

        Args:
            hosts_info (list[HostSerialNumberIPInfo]): A list of Host Serial Number and Management IP information
            hpe_vme_ip_address (str): HPE VME IP Address
            hpe_vme_appliance_url (str): HPE VME Appliance URL
            hpe_vme_hostname (str): HPE VME Hostname
            hpe_vme_username (str): HPE VME Username
            hpe_vme_ntp_server (str, optional): HPE VME NTP Server to be validated under the 'HPE VM Essential Details' section on the review screen. Defaults to NetworkConfiguration.NTP_SERVER. # noqa E501
            hpe_vme_vm_size (str, optional): HPE VME VM Size. Defaults to NetworkConfiguration.HPE_VME_VM_SIZE.
            hpe_vme_management_interface (str, optional): HPE VME Management Interface. Defaults to NetworkConfiguration.HPE_VME_MANAGEMENT_INTERFACE. # noqa E501
            hpe_vme_dns_servers (str, optional): Comma separated list of HPE VME DNS Servers to be validated under the 'HPE VM Essential Details' section on the review screen. Defaults to NetworkConfiguration.DNS_SERVERS_VALIDATION. # noqa E501
            network_details_ntp_server (str, optional): NTP Server details to be validated under 'Network Details' section on the review screen. Defaults to NetworkConfiguration.NTP_SERVER. # noqa E501
            time_zone (str, optional): Time Zone value. Defaults to NetworkConfiguration.TIME_ZONE.
            network_details_dns_servers (str, optional): Comma separated list of DNS servers to be validated under the 'Network Details' section on the review screen. Defaults to NetworkConfiguration.DNS_SERVERS_VALIDATION. # noqa E501
            search_domain (str, optional): Search domain value. Defaults to NetworkConfiguration.SEARCH_DOMAIN.
            netmask (str, optional): Netmask value. Defaults to NetworkConfiguration.NETMASK.
            gateway (str, optional): Gateway value. Defaults to NetworkConfiguration.GATEWAY..
            proxy (_type_, optional): Proxy value. Defaults to NetworkConfiguration.PROXY.
            no_proxy_list (str, optional): Comma separated list of no proxy. Defaults to None.
        """
        self.validate_review_page(
            hosts_info=hosts_info,
            ntp_server=network_details_ntp_server,
            time_zone=time_zone,
            dns_servers=network_details_dns_servers,
            search_domain=search_domain,
            netmask=netmask,
            gateway=gateway,
        )

        hpe_vme_appliance_url_value = self.page.locator(VMWareReviewLocators.APPLIANCE_URL).first.text_content()
        assert (
            hpe_vme_appliance_url_value == hpe_vme_appliance_url
        ), f"Appliance URL: {hpe_vme_appliance_url} != {hpe_vme_appliance_url_value}"

        # Index 0 is for network details and index 1 is for HPE VME
        hpe_vme_ntp_server_value = self.page.locator(VMWareReviewLocators.NTP_SERVERS).nth(1).text_content()
        assert (
            hpe_vme_ntp_server_value == hpe_vme_ntp_server
        ), f"NTP Server: {hpe_vme_ntp_server} != {hpe_vme_ntp_server_value}"

        hpe_vme_ip_address_value = self.page.locator(VMWareReviewLocators.IP_ADDRESS).first.text_content()
        assert (
            hpe_vme_ip_address_value == hpe_vme_ip_address
        ), f"IP Address: {hpe_vme_ip_address} != {hpe_vme_ip_address_value}"

        netmask_value = self.page.locator(VMWareReviewLocators.NETMASK).first.text_content()
        assert netmask_value == netmask, f"Netmask: {netmask} != {netmask_value}"

        # Index 0 is for network details and index 1 is for HPE VME
        hpe_vme_dns_servers_value = self.page.locator(VMWareReviewLocators.DNS_SERVERS).nth(1).text_content()
        assert (
            hpe_vme_dns_servers_value == hpe_vme_dns_servers
        ), f"DNS Servers: {hpe_vme_dns_servers} != {hpe_vme_dns_servers_value}"

        gateway_value = self.page.locator(VMWareReviewLocators.GATEWAY).first.text_content()
        assert gateway_value == gateway, f"Gateway: {gateway} != {gateway_value}"

        hpe_vme_hostname_value = self.page.locator(VMWareReviewLocators.HOST_NAME).first.text_content()
        assert hpe_vme_hostname_value == hpe_vme_hostname, f"Hostname: {hpe_vme_hostname} != {hpe_vme_hostname_value}"

        hpe_vme_username_value = self.page.locator(VMWareReviewLocators.USERNAME).first.text_content()
        assert hpe_vme_username_value == hpe_vme_username, f"Username: {hpe_vme_username} != {hpe_vme_username_value}"

        proxy_value = self.page.locator(VMWareReviewLocators.PROXY).first.text_content()
        assert proxy_value == proxy, f"Proxy: {proxy} != {proxy_value}"

        if no_proxy_list:
            no_proxy_list_value = self.page.locator(VMWareReviewLocators.NO_PROXY_LIST).first.text_content()
            assert no_proxy_list_value == no_proxy_list, f"No Proxy List: {no_proxy_list} != {no_proxy_list_value}"

        vm_size_value = self.page.locator(VMWareReviewLocators.VM_SIZE).first.text_content()
        assert vm_size_value == hpe_vme_vm_size, f"VM Size: {hpe_vme_vm_size} != {vm_size_value}"

        management_interface_value = self.page.locator(VMWareReviewLocators.MANAGEMENT_INTERFACE).first.text_content()
        assert (
            management_interface_value == hpe_vme_management_interface
        ), f"Management Interface: {hpe_vme_management_interface} != {management_interface_value}"

    def __get_installation_progress_percent(self) -> int:
        """Retrieves the installation progress percentage from the progress bar.

        Returns:
            int: Progress percentage of the installation.
        """
        # progress % is in the format "Bar meter with value 43 out of 100"
        # DOM contains 2 elements with the same identifier with the same text. One of them is hidden
        # Fetching the first one to get the progress percentage
        progress_percent_text = self.page.locator(
            VMWareReviewLocators.HPE_VME_INSTALLATION_PROGRESS_PERCENT
        ).first.get_attribute(
            name="aria-label",
            timeout=30000,
        )
        progress_percent = int(progress_percent_text.split("value")[1].split("out")[0].strip())
        logger.info(f"Installation progress: {progress_percent}")
        return progress_percent

    def wait_for_hpe_vme_installation(self):
        """
        Waits for the HPE VME installation to complete.

        Raises:
            TimeoutExpired: If the installation does not complete within the specified timeout of 2.5 hours.

        NOTE: The API call happening behind the scenes does not provide the overall progress percentage.
        It provides progress percent of each individual step that is being performed
        """

        timeout = 2.5 * 60 * 60  # 2.5 hours
        try:
            wait(
                lambda: self.__get_installation_progress_percent() >= 95,
                timeout_seconds=timeout,
                sleep_seconds=(0.1, 10),
            )
        except TimeoutError:
            logger.error(
                f"Timeout waiting for installation to complete (2.5 hours). Installation progress percent: {self.__get_installation_progress_percent()}"  # noqa E501
            )
            raise

        # timeout is 10 minutes
        # NOTE:
        # After 95% progress, it may take around a minute to a few minutes for the installation to complete
        # As soon as the upload is complete, the progress bar is removed from the DOM
        # and no longer available to retrieve the text and our call to get the text will fail
        # That's why after 95%, we wait for the upload complete text to appear
        # The timeout is currently high because I haven't tried it multiple times to see how long it takes
        logger.info("Waiting for installation to complete...")
        expect(
            self.page.get_by_role(role="button", name=VMWareReviewLocators.HPE_VME_INSTALLATION_SUCCESS_WINDOW)
        ).to_be_visible(timeout=600000)
