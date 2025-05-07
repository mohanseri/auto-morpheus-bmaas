import logging

from playwright.sync_api import Page
from playwright.sync_api import expect

from setup_ui.page_object.base_page import BasePage
from setup_ui.vmware_initial_setup.locators.welcome_locators import WelcomeLocators

logger = logging.getLogger(__name__)


class WelcomePage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def validate_welcome_page(self):
        """Validate the Welcome page"""
        logger.info("Validating Welcome page")
        expect(self.page.get_by_role("heading", name=WelcomeLocators.WELCOME_TITLE)).to_be_visible()
