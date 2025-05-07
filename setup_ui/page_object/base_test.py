import logging

from playwright.sync_api import Page, Browser, BrowserContext
from playwright.sync_api import sync_playwright


logger = logging.getLogger()


class BaseTest:

    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    def get_page(self, headless: bool = True) -> Page:
        """
        Initializes the browser and returns the page object.
        This method is responsible for launching the browser and creating a new page.
        It ensures that the browser is only launched once per instance of BaseTest.
        If the browser is already launched, it reuses the existing instance.

        Args:
            headless (bool): If True, runs the browser in headless mode. Defaults to True.

        Returns:
            Page: Initialized page object for interaction with the browser.
        """
        if not self.browser:
            # Launch the browser only once per instance of BaseTest
            # This will help in ensuring only one browser per test run
            # multiple tests can run in parallel with their own browser instances
            logger.info("Launching browser for the first time...")
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(headless=headless, args=["--start-maximized"])
            self.context = self.browser.new_context(ignore_https_errors=True, no_viewport=True)
            self.page = self.context.new_page()
            self.page.set_default_timeout(60000)  # Set default timeout for all actions to 60 seconds
        else:
            logger.info("Reusing existing browser instance...")

        return self.page

    def close_browser(self):
        """Close the browser and clean up resources."""
        if self.browser:
            logger.info("Closing the browser...")
            self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
