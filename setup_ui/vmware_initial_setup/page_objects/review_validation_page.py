import logging

from playwright.sync_api import Page

from setup_ui.constants import NetworkConfiguration
from setup_ui.page_object.base_page import BasePage
from setup_ui.vmware_initial_setup.dataclasses.host_ip_info import HostSerialNumberIPInfo
from setup_ui.vmware_initial_setup.locators.vmware_review_locators import VMWareReviewLocators

from hpe_glcp_automation_lib.libs.commons.utils.pwright.pwright_utils import TableUtils

logger = logging.getLogger()


class ReviewValidationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page
        self.table_utils = TableUtils(page=self.page)

    def validate_review_page(
        self,
        hosts_info: list[HostSerialNumberIPInfo],
        ntp_server: str = NetworkConfiguration.NTP_SERVER,
        time_zone: str = NetworkConfiguration.TIME_ZONE,
        dns_servers: str = NetworkConfiguration.DNS_SERVERS_VALIDATION,
        search_domain: str = NetworkConfiguration.SEARCH_DOMAIN,
        netmask: str = NetworkConfiguration.NETMASK,
        gateway: str = NetworkConfiguration.GATEWAY,
    ):
        """Validates the Review page details for the hosts and network configuration

        Args:
            hosts_info (list[HostSerialNumberIPInfo]): A list of Host Serial Number and Management IP information
            ntp_server (str, optional): NTP Server value. Defaults to NetworkConfiguration.NTP_SERVER.
            time_zone (str, optional): Time zone value. Defaults to NetworkConfiguration.TIME_ZONE.
            dns_servers (str, optional): Comma separated list of DNS Servers. Defaults to NetworkConfiguration.DNS_SERVERS_VALIDATION. # noqa E501
            search_domain (str, optional): Search domain value. Defaults to NetworkConfiguration.SEARCH_DOMAIN.
            netmask (str, optional): Netmask value. Defaults to NetworkConfiguration.NETMASK.
            gateway (str, optional): Gateway value. Defaults to NetworkConfiguration.GATEWAY.
        """
        serial_number_column_index = self.table_utils.get_column_index_by_name(column_name="Serial Number")
        logger.info(serial_number_column_index)

        management_ip_column_index = self.table_utils.get_column_index_by_name(column_name="Management IP")
        logger.info(management_ip_column_index)

        for host_info in hosts_info:
            logger.info(f"Validating {host_info.host_serial_number} has {host_info.management_ip} as management IP")

            # As we are getting the row index using the host serial number, we don't have to explicitly validate the text in that field # noqa E501
            row_indices = self.table_utils.get_rows_indices_by_text(row_text=host_info.host_serial_number)
            logger.info(f"{host_info.host_serial_number} is present in {row_indices[0]}")

            # Each host will have a management IP which we assigned in the previous step
            # That's why we need to use nth() - 1 to select the correct one
            row_identifier = self.table_utils.row_columns_template.format(row_index=row_indices[0])

            # Split the row identifier to get the first part
            # As there is a comma in the row identifier, we need to split it into 2 parts
            # :nth-match(table, 1)>tbody>tr:nth-child({row_index})>td,:nth-match(table, 1)>tbody>tr:nth-child({row_index})>th # noqa E501
            parts = row_identifier.split(",", 2)
            row_td_locator = ",".join(parts[:2])

            # row_td_locator = :nth-match(table, 1)>tbody>tr:nth-child({row_index})>td
            # appending nth-child to get the management IP value
            # Playwright has the .nth() method but for some reason it is not working -\(-_-)/-
            row_td_locator = f"{row_td_locator}:nth-child({management_ip_column_index})"
            management_ip = " ".join(self.page.locator(row_td_locator).text_content().split())
            logger.info(f"Server Serial Number {host_info.host_serial_number}, Management IP = {management_ip}")
            assert (
                management_ip == host_info.management_ip
            ), f"Server Serial Number {host_info.host_serial_number}, Management IP = {management_ip}"

        # We have to use '.first' because the 'right-of' identifier finds all the elements to the current element's right # noqa E501
        network_details_ntp_server_value = self.page.locator(VMWareReviewLocators.NTP_SERVERS).first.text_content()
        assert (
            network_details_ntp_server_value == ntp_server
        ), f"DNS Servers: {ntp_server} != {network_details_ntp_server_value}"

        time_zone_value = self.page.locator(VMWareReviewLocators.TIME_ZONE).first.text_content()
        assert time_zone_value == time_zone, f"Time Zone: {time_zone} != {time_zone_value}"

        network_details_dns_servers_value = self.page.locator(VMWareReviewLocators.DNS_SERVERS).first.text_content()
        assert (
            network_details_dns_servers_value == dns_servers
        ), f"DNS Servers: {dns_servers} != {network_details_dns_servers_value}"

        search_domain_value = self.page.locator(VMWareReviewLocators.SEARCH_DOMAIN).first.text_content()
        assert search_domain_value == search_domain, f"Search Domain: {search_domain} != {search_domain_value}"

        netmask_value = self.page.locator(VMWareReviewLocators.NETMASK).first.text_content()
        assert netmask_value == netmask, f"Netmask: {netmask} != {netmask_value}"

        gateway_value = self.page.locator(VMWareReviewLocators.GATEWAY).first.text_content()
        assert gateway_value == gateway, f"Gateway: {gateway} != {gateway_value}"
