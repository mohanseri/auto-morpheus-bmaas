from playwright.sync_api import Page

from setup_ui.page_object.base_page import BasePage


class ReviewPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    # NOTE: Placeholder for future implementation
    # The click submit button method is in BasePage class
