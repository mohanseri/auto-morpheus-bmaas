import logging
import time

from playwright.sync_api import Page

from setup_ui.initial_setup.locators.domain_time_and_proxy_locators import DomainTimeAndProxyLocators
from setup_ui.page_object.base_page import BasePage

logger = logging.getLogger()


class DomainTimeAndProxyPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def enter_dns_server_details(self, dns_server_1: str, dns_server_2: str, dns_server_3: str):
        """Fills the DNS Server 1, 2, and 3 fields with the provided values.

        Args:
            dns_server_1 (str): DNS Server 1 value
            dns_server_2 (str): DNS Server 2 value
            dns_server_3 (str): DNS Server 3 value
        """
        logger.info(f"Entering data: {dns_server_1} in DSN 1 field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.DNS_0).fill(dns_server_1)

        logger.info(f"Entering data: {dns_server_2} in DSN 2 field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.DNS_1).fill(dns_server_2)

        logger.info(f"Entering data: {dns_server_3} in DSN 3 field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.DNS_2).fill(dns_server_3)

    def enter_search_domain_details(self, search_domain: str):
        """Fills the Search Domain field with the provided value.

        Args:
            search_domain (str): Search Domain value
        """
        logger.info(f"Entering data: {search_domain} in Search Domain field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.SEARCH_DOMAIN_0).fill(search_domain)

    def select_region_and_time_zone(self, region: str = "America", time_zone: str = "America/Denver"):
        """Selects the Region and Time Zone from the dropdowns.

        Args:
            region (str): Region value. Default is "America"
            time_zone (str): Time Zone value. Default is "America/Denver"
        """
        logger.info(f"Selecting {region} from Region field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.REGION).click()
        self.page.locator(DomainTimeAndProxyLocators.REGION_DROPDOWN_VALUE.format(region=region)).click()

        # waiting for time zone dropdown to load
        time.sleep(3)

        logger.info(f"Selecting {time_zone} from Time Zone field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.TIME_ZONE).click()
        time_zone_dropdown_container = self.page.locator(DomainTimeAndProxyLocators.TIME_ZONE_DROPDOWN)
        target_time_zone_element = self.page.locator(
            DomainTimeAndProxyLocators.TIME_ZONE_DROPDOWN_VALUE.format(
                time_zone=time_zone,
            )
        )

        while not target_time_zone_element.is_visible():
            # tried it in browser and 1400 get to Denver. We can later adjust it to increment by 500 px
            # Code to try out in the browser console:
            # ```
            # const dropdown = document.querySelector("div[role='listbox']");
            # dropdown.scrollBy(0, 1400);
            # ```
            #
            logger.info(f"Scrolling within Time Zone dropdown to find {time_zone} element")
            time_zone_dropdown_container.evaluate("(dropdown) => dropdown.scrollBy(0, 1400)")  # Scroll down by 1400px
            time.sleep(0.2)  # small delay for DOM to update

        target_time_zone_element.scroll_into_view_if_needed()
        target_time_zone_element.click()

    def enter_ntp_server_details(self, ntp_server: str):
        """Fills the NTP Server field with the provided value.

        Args:
            ntp_server (str): NTP Server value
        """
        logger.info(f"Entering data: {ntp_server} in NTP Server field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.NTP).fill(ntp_server)

    def enter_proxy_details(self, proxy_address: str = "http://web-proxy.corp.hpecorp.net", proxy_port: str = 8080):
        """Fills the Proxy Server Address and Proxy Port fields with the provided values.

        Args:
            proxy_address (str): Proxy Server Address value. Defaults to "http://web-proxy.corp.hpecorp.net"
            proxy_port (str): Proxy Port value. Defaults to 8080
        """
        logger.info("Validating if 'Proxy' checkbox is checked")
        include_proxy = self.page.get_by_test_id(DomainTimeAndProxyLocators.INCLUDE_PROXY_SERVER)
        is_include_proxy_checked = include_proxy.is_checked()
        logger.info(f"Proxy checkbox checked = {is_include_proxy_checked}")

        if not is_include_proxy_checked:
            logger.info("Checking 'Proxy' checkbox")
            include_proxy_checkbox = self.page.get_by_text(
                DomainTimeAndProxyLocators.INCLUDE_PROXY_SERVER_CHECKBOX_TEXT,
            )
            include_proxy_checkbox.scroll_into_view_if_needed()
            include_proxy_checkbox_visible: bool = include_proxy_checkbox.is_visible()
            logger.info(f"Include Proxy Checkbox visible = {include_proxy_checkbox_visible}")
            include_proxy_checkbox.click(force=True)

        logger.info(f"Entering data: {proxy_address} in Proxy Server field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.PROXY_SERVER_ADDRESS).fill(proxy_address)

        logger.info(f"Entering data: {proxy_port} in Proxy Port field")
        self.page.get_by_test_id(DomainTimeAndProxyLocators.PROXY_PORT).fill(proxy_port)
