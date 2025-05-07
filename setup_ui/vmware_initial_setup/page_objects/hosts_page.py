import logging

from playwright.sync_api import Page


from hpe_glcp_automation_lib.libs.commons.utils.pwright.pwright_utils import TableUtils

from setup_ui.constants import NetworkConfiguration
from setup_ui.vmware_initial_setup.dataclasses.host_ip_info import HostSerialNumberIPInfo
from setup_ui.vmware_initial_setup.locators.host_locators import HostLocators
from setup_ui.vmware_initial_setup.page_objects.review_validation_page import ReviewValidationPage

logger = logging.getLogger()


class HostsPage(ReviewValidationPage):
    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page
        # There are 2 tables on the Hosts > Discovery screen: Discovered Hosts and Selected Hosts
        # We only need to interact with the Selected Hosts table that's why we are passing index=2
        # We were able to click on the '+' button in the Discovered Hosts table using the locator
        # We have another table on Hosts > Details screen which has index 1 because there is only 1 table on the screen
        # That's why we are initializing the table_utils within the functions

    def select_hosts(self, hosts_serial_number: list[str]):
        """Selects the hosts in the Discovered Hosts table by clicking on the '+' button

        Args:
            hosts_serial_number (list[str]): List of host serial numbers to be selected
        """
        for host_serial_number in hosts_serial_number:
            logger.info(f"Clicking on + button for {host_serial_number}")
            self.page.locator(HostLocators.ADD_BUTTON.format(host_serial_number=host_serial_number)).click()

    def enter_management_ip_for_hosts(self, hosts_info: list[HostSerialNumberIPInfo]):
        """Enters the management IP for each host in the Selected Hosts table

        Args:
            hosts_info (list[HostSerialNumberIPInfo]): List of host serial number and their respective management IP
        """
        logger.info("Retrieving column index of Serial Number")
        table_utils = TableUtils(page=self.page, index=2)
        serial_number_column_index = table_utils.get_column_index_by_name(column_name="Serial Number")
        logger.info(serial_number_column_index)

        for host_info in hosts_info:
            row_indices = table_utils.get_rows_indices_by_text(row_text=host_info.host_serial_number)
            logger.info(f"{host_info.host_serial_number} is present in {row_indices[0]}")

            # Each row has a 'Management IP' text box with the same locator.
            # That's why we need to use nth() - 1 to select the correct one
            logger.info(f"Entering management IP for {host_info.host_serial_number}")
            self.page.locator(HostLocators.MANAGEMENT_IP).nth(row_indices[0] - 1).fill(host_info.management_ip)

    def enter_host_network_configuration_details(
        self,
        ntp_server: str = NetworkConfiguration.NTP_SERVER,
        time_zone: str = NetworkConfiguration.TIME_ZONE,
        dns_servers: list[str] = NetworkConfiguration.DNS_SERVERS,
        search_domain: str = NetworkConfiguration.SEARCH_DOMAIN,
        netmask: str = NetworkConfiguration.NETMASK,
        gateway: str = NetworkConfiguration.GATEWAY,
    ):
        """Enters the host network configuration details in the UI

        Args:
            ntp_server (str): NTP server details for the host. Default to NetworkConfiguration.NTP_SERVER.
            time_zone (str, optional): Time Zone for the host. Defaults to NetworkConfiguration.TIME_ZONE.
            dns_servers (list[str]): List of DNS Servers for the host. Defaults to NetworkConfiguration.DNS_SERVERS.
            search_domain (str): Search Domain details for the host. Defaults to NetworkConfiguration.SEARCH_DOMAIN.
            netmask (str): Netmask details for the host. Defaults to NetworkConfiguration.NETMASK.
            gateway (str): Gateway details for the host. Defaults to NetworkConfiguration.GATEWAY.

        Raises:
            Exception: If the requested Time Zone option is not found in the UI
        """
        logger.info(f"Entering NTP Sever details: {ntp_server}")
        self.page.locator(HostLocators.NTP_SERVERS).fill(ntp_server)

        logger.info(f"Selecting time zone: {time_zone}")
        self.page.locator(HostLocators.TIME_ZONE).click(force=True)
        self.page.wait_for_selector(HostLocators.TIME_ZONE_SEARCH)
        self.page.locator(HostLocators.TIME_ZONE_SEARCH).fill(time_zone)
        time_zone_option = self.page.query_selector(f"text={time_zone}")

        if time_zone_option is not None:
            time_zone_option.click()
        else:
            logger.error(f"Time zone option '{time_zone}' not found")
            raise Exception(f"Time zone option '{time_zone}' not found")

        logger.info(f"Entering DNS Servers: {dns_servers}")
        for i, dns_server in enumerate(dns_servers):
            # First text box is already present in the UI.
            # We need to click on the '+' button to add more DNS servers
            # nth(0) is for NTP Servers
            if i != 0:
                self.page.locator(HostLocators.ADD_SERVER_BUTTON).nth(1).click()

            logger.info(f"Filling DNS Server {i + 1}: {dns_server}")
            self.page.locator(HostLocators.DNS_SERVERS).nth(i).fill(dns_server)

        logger.info(f"Filling Search Domain: {search_domain}")
        self.page.locator(HostLocators.SEARCH_DOMAIN).fill(search_domain)

        logger.info(f"Filling Netmask: {netmask}")
        self.page.locator(HostLocators.NETMASK).fill(netmask)

        logger.info(f"Filling Gateway: {gateway}")
        self.page.locator(HostLocators.GATEWAY).fill(gateway)
