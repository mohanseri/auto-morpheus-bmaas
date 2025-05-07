import logging

from playwright.sync_api import expect, Page

from setup_ui.enums.installation_type import InstallationType
from setup_ui.page_object.base_page import BasePage
from setup_ui.vmware_initial_setup.locators.intallation_type_locators import InstallationTypeLocators

logger = logging.getLogger(__name__)


class InstallationTypePage(BasePage):
    """Installation Type Page Object"""

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def select_installation_type(self, installation_type: InstallationType):
        """Selects the installation type for VMWare Initial Setup.

        Args:
            installation_type (InstallationType): Type of installation to be selected. Valid values are:
                - "New Installation"
                - "Use Existing Installation"
        """
        logger.info(f"Selecting installation type: {installation_type.value}")

        if installation_type == InstallationType.USE_EXISTING_INSTALLATION:
            self.page.locator(InstallationTypeLocators.USE_EXISTING_INSTALLATION_DIV).click()
            expect(self.page.get_by_label(installation_type.value)).to_be_checked()
        else:
            self.page.locator(InstallationTypeLocators.NEW_INSTALLATION_DIV).click()
            expect(self.page.get_by_label(installation_type.value)).to_be_checked()
