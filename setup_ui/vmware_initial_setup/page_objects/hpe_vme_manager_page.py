import logging

from playwright.sync_api import Page

from setup_ui.constants import NetworkConfiguration
from setup_ui.page_object.base_page import BasePage
from setup_ui.vmware_initial_setup.locators.hpe_vme_manager_locators import HPEVMEManagerLocators

logger = logging.getLogger()


class HPEVMEManagerPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def enter_and_validate_hpe_vme_manager_details(
        self,
        ip_address: str,
        appliance_url: str,
        hostname: str,
        username: str,
        password: str,
        netmask: str = NetworkConfiguration.NETMASK,
        gateway: str = NetworkConfiguration.GATEWAY,
        dns_servers: list[str] = NetworkConfiguration.DNS_SERVERS,
        proxy: str = NetworkConfiguration.PROXY,
        no_proxy_list: str = None,
    ):
        """Enters the HPE VME Manager details in the UI and validates the values carried over from the previous page

        Args:
            ip_address (str): IP Address to be assigned to the HPE VME Manager
            appliance_url (str): URL to be assigned to the HPE VME Manager
            hostname (str): Hostname to be assigned to the HPE VME Manager
            username (str): Username to be assigned to the HPE VME Manager
            password (str): Password to be assigned to the HPE VME Manager
            netmask (str, optional): Netmask for HPE VME Manager. Defaults to NetworkConfiguration.NETMASK
            gateway (str, optional): Gateway for HPE VME Manager. Defaults to NetworkConfiguration.GATEWAY
            dns_servers (list[str], optional): DNS Servers for HPE VME Manager. Defaults to NetworkConfiguration.GATEWAY # noqa E501
            proxy (_type_, optional): Proxy for HPE VME Manager. Defaults to NetworkConfiguration.PROXY.
            no_proxy_list (str, optional): Comma separated values for No Proxy List for HPE VME Manager. Defaults to None. # noqa E501
        """
        logger.info(f"Entering IP address {ip_address}")
        self.page.locator(HPEVMEManagerLocators.IP_ADDRESS).fill(ip_address)

        logger.info(f"Entering appliance URL {appliance_url}")
        self.page.locator(HPEVMEManagerLocators.APPLIANCE_URL).fill(appliance_url)

        logger.info(f"Entering hostname {hostname}")
        self.page.locator(HPEVMEManagerLocators.HOST_NAME).fill(hostname)

        logger.info(f"Entering username {username}")
        self.page.locator(HPEVMEManagerLocators.USERNAME).fill(username)

        logger.info(f"Entering password {password}")
        self.page.locator(HPEVMEManagerLocators.PASSWORD).fill(password)

        logger.info(f"Entering proxy {proxy}")
        self.page.locator(HPEVMEManagerLocators.PROXY).fill(proxy)

        if no_proxy_list:
            logger.info(f"Entering no proxy list {no_proxy_list}")
            self.page.locator(HPEVMEManagerLocators.NO_PROXY_LIST).fill(no_proxy_list)

        logger.info(f"Validating netmask value to be {netmask}")
        netmask_value = self.page.locator(HPEVMEManagerLocators.NETMASK).input_value()
        assert netmask_value == netmask, f"Netmask value is {netmask_value}, expected {netmask}"

        logger.info(f"Validating gateway value to be {gateway}")
        gateway_value = self.page.locator(HPEVMEManagerLocators.GATEWAY).input_value()
        assert gateway_value == gateway, f"Gateway value is {gateway_value}, expected {gateway}"

        logger.info(f"Validating DNS servers value to be {dns_servers}")
        for i, dns_server in enumerate(dns_servers):
            dns_server_value = self.page.locator(HPEVMEManagerLocators.DNS_SERVERS).nth(i).input_value()
            assert dns_server_value == dns_server, f"DNS server value is {dns_server_value}, expected {dns_server}"
