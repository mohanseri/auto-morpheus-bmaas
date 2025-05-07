import logging

from playwright.sync_api import Page

from setup_ui.initial_setup.locators.activation_locators import ActivationLocators
from setup_ui.page_object.base_page import BasePage

logger = logging.getLogger()


class ActivationPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def get_activation_code(self) -> str:
        """Returns the activation code from the activation page.

        Returns:
            str: Generated activation code
        """
        logger.info("Retrieving activation code")
        activation_code: str = self.page.get_by_test_id(ActivationLocators.ACTIVATION_CODE).text_content()
        logger.info(f"Activation code: {activation_code}")
        return activation_code
