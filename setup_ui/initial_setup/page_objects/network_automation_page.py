import logging

from playwright.sync_api import Page

from setup_ui.initial_setup.locators.network_automation_locators import NetworkAutomationLocators
from setup_ui.page_object.base_page import BasePage


logger = logging.getLogger()


class NetworkAutomationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def acknowledge_warning(self):
        """Acknowledging the warning for Skipping Network Automation"""
        logger.info("Checking Acknowledge checkbox")
        acknowledgement_checkbox_text = self.page.get_by_text(
            NetworkAutomationLocators.ACKNOWLEDGEMENT_CHECKBOX_TEXT,
        )
        acknowledgement_checkbox_text_visible: bool = acknowledgement_checkbox_text.is_visible()
        logger.info(f"Acknowledgement Checkbox visible = {acknowledgement_checkbox_text_visible}")

        acknowledgement_checkbox_text.click(force=True)

        self.click_yes_button()

    # NOTE: We will add required functions once network automation is enabled
