import logging
import time
from playwright.sync_api import Page

from setup_ui.locators.common_locators import CommonLocators

logger = logging.getLogger()


class BasePage:

    def __init__(self, page: Page):
        """Base Page for initializing the browser and launching the URL."""
        self.page = page

    def launch_url(self, launch_url: str):
        """Opens the provided URL in the browser.

        Args:
            launch_url (str): URL to be launched in the browser
        """
        logger.info(f"Launching the URL: {launch_url}")
        self.page.goto(launch_url)
        # waits for the page to load (HTML, CSS, JS, etc.)
        self.page.wait_for_load_state()

    # Common methods across multiple pages
    def click_next_button(self):
        """Clicks the Next button on the page."""
        logger.info("Clicking on 'Next' button")
        next_button = self.page.get_by_role("button", name=CommonLocators.BUTTON_NEXT)
        next_button.scroll_into_view_if_needed()
        next_button.click()
        logging.info("Clicked on the 'Next' button.")

    def click_submit_button(self):
        """Clicks on the 'Submit' button on the Review page."""
        logger.info("Clicking on 'Submit' button")
        submit_button = self.page.get_by_role("button", name=CommonLocators.BUTTON_SUBMIT)
        submit_button.scroll_into_view_if_needed()
        submit_button.click()
        logging.info("Clicked on the 'Submit' button.")

    def click_yes_button(self):
        """Clicks on the 'Yes, Proceed' button on confirmation windows."""
        logger.info("Clicking on 'Yes, Proceed' button")
        yes_proceed_button = self.page.get_by_test_id(CommonLocators.BUTTON_YES)
        yes_proceed_button.scroll_into_view_if_needed()
        yes_proceed_button.click()
        logging.info("Clicked on the 'Yes, Proceed' button.")

    def click_finish_button(self):
        """Clicks on the 'Finish' button."""
        logger.info("Clicking on 'Finish' button")
        finish_button = self.page.get_by_role("button", name=CommonLocators.BUTTON_FINISH)
        finish_button.scroll_into_view_if_needed()
        finish_button.click()
        logging.info("Clicked on the 'Finish' button.")

    def wait_for_configuration(self):
        """Checks the progress window's visibility and waits for the configuration to complete.

        Raises:
            TimeoutError: If the configuration isn't completed in 5 minutes
        """
        timeout = 5 * 60  # 5 minutes
        start_time = time.time()

        time.sleep(5)
        while True:
            configuration_window_visible: bool = self.page.get_by_test_id(
                CommonLocators.PROGRESS_WINDOW,
            ).is_visible()

            if not configuration_window_visible:
                logger.info("Configuration completed.")
                break

            if time.time() - start_time > timeout:
                logger.error("Server discovery timed out.")
                raise TimeoutError("Server discovery did not complete in 5 minutes.")

            logger.info("Waiting for server discovery to complete...")
            time.sleep(5)
