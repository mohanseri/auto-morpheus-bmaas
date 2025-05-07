import logging
import time

from playwright.sync_api import expect, Page

from setup_ui.page_object.base_page import BasePage
from setup_ui.vmware_initial_setup.locators.upload_images_locators import UploadImagesLocators

logger = logging.getLogger(__name__)


class UploadImagesPage(BasePage):
    """Upload Images Page Object"""

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def __get_upload_progress_percent(self) -> int:
        """Retrieves the upload progress percentage from the progress bar.

        Returns:
            int: Progress percentage of the upload.
        """
        # progress % is in the format "Bar meter with value 43 out of 100"
        # DOM contains 2 elements with the same identifier with the same text. One of them is hidden
        # Fetching the first one to get the progress percentage
        progress_percent_text = self.page.locator(UploadImagesLocators.UPLOAD_PROGRESS_PERCENTAGE).first.get_attribute(
            name="aria-label",
            timeout=30000,
        )
        progress_percent = int(progress_percent_text.split("value")[1].split("out")[0].strip())
        logger.info(f"Upload progress: {progress_percent}")
        return progress_percent

    def upload_image(self, image_path: str):
        """Uploads an image to the Upload Images page.

        Args:
            image_path (str): Path to the image file to be uploaded.
        """
        logger.info("Waiting for page to load completely...")
        upload_button = self.page.get_by_role(role="button", name=UploadImagesLocators.UPLOAD_BUTTON)
        expect(upload_button).to_be_enabled()

        logger.info(f"Uploading image: {image_path}")
        self.page.locator(UploadImagesLocators.FILE_INPUT).set_input_files(image_path)
        upload_button.click()

        # This button appears when trying to upload an image with the same name as an existing image
        # While developing, this button appears as we have tried this step a few times already
        override_existing_file_button = self.page.query_selector(f"text={UploadImagesLocators.OVERRIDE_EXISTING_FILE}")
        logger.info(override_existing_file_button)

        if override_existing_file_button is not None:
            logger.info("Override existing file button is present. Clicking it.")
            override_existing_file_button.click()

        # timeout is 30 seconds
        logger.info("Waiting for upload progress bar to appear...")
        self.page.wait_for_selector(UploadImagesLocators.UPLOADING_PROGRESS_BAR, timeout=30000)
        self.page.wait_for_selector(UploadImagesLocators.UPLOAD_PROGRESS_PERCENTAGE, timeout=30000)

        progress_percent = self.__get_upload_progress_percent()
        logger.info(f"Upload progress: {progress_percent}")

        while progress_percent < 95:
            progress_percent = self.__get_upload_progress_percent()
            logger.info(f"Upload progress: {progress_percent}")
            time.sleep(10)

        # timeout is 5 minutes
        # NOTE:
        # After 95% progress, it may take around 30 seconds to a minute for the upload to complete
        # As soon as the upload is complete, the progress bar is removed from the DOM
        # and no longer available to retrieve the text and our call to get the text will fail
        # That's why after 95%, we wait for the upload complete text to appear
        logger.info("Waiting for uploads to complete...")
        self.page.wait_for_selector(UploadImagesLocators.UPLOADS_COMPLETE, timeout=300000)
