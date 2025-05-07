import logging

from playwright.sync_api import Page

from setup_ui.initial_setup.locators.storage_locators import StorageLocators
from setup_ui.page_object.base_page import BasePage
from playwright.sync_api import expect

logger = logging.getLogger()


class DiscoverStoragePage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def discover_storage(self, storage_serial_number: str):
        """Enters the storage serial number and clicks on the 'Discover Storage System' button and waits for discovery

        Args:
            storage_serial_number (str): Serial number of the storage system

        Raises:
            TimeoutError: When the storage discovery does not complete in 5 minutes
        """
        logger.info(f"Entering Storage Serial Number {storage_serial_number}")
        self.page.get_by_test_id(StorageLocators.SERIAL_NUMBER).fill(storage_serial_number)

        logger.info("Clicking on Discover Storage button")
        self.page.get_by_role(role="button", name=StorageLocators.DISCOVER_STORAGE_SYSTEM).click()

        logger.info("Waiting for storage configuration to complete")
        self.wait_for_configuration()

        logger.info("Validating configuration success message")
        expect(self.page.get_by_text(StorageLocators.STORAGE_SERVER_DISCOVERY_MESSAGE)).to_be_visible()

        self.click_next_button()

    def enter_storage_management_interface_details(self, ip_address: str, subnet_mask: str, gateway: str):
        """Fills out the Storage Server's IP Address, Subnet Mask, and Gateway fields.

        Args:
            ip_address (str): IP Address of the storage server
            subnet_mask (str): Subnet mask of the storage server
            gateway (str): Gateway of the storage server
        """
        # NOTE: The commented out code to `fill` the details will be uncommented once we are able to test

        logger.info(f"Entering {ip_address} in IP Address field")
        # self.page.get_by_test_id(StorageLocators.IP_ADDRESS).fill(ip_address)
        ip_address_text = self.page.get_by_test_id(StorageLocators.IP_ADDRESS).input_value()
        logger.info(f"IP Address = {ip_address_text}")

        logger.info(f"Entering {subnet_mask} in Subnet Mask field")
        # self.page.get_by_test_id(StorageLocators.NETMASK).fill(subnet_mask)
        netmask_text = self.page.get_by_test_id(StorageLocators.NETMASK).input_value()
        logger.info(f"Netmask = {netmask_text}")

        logger.info(f"Entering {gateway} in Gateway field")
        # self.page.get_by_test_id(StorageLocators.GATEWAY).fill(gateway)
        gateway_text = self.page.get_by_test_id(StorageLocators.GATEWAY).input_value()
        logger.info(f"Gateway = {gateway_text}")

    def confirm_storage_details(self):
        """Confirms storage server details and moves on to the next step"""
        self.click_next_button()

        # Not available in my current testing. Will enable once available
        # self.wait_for_configuration()
