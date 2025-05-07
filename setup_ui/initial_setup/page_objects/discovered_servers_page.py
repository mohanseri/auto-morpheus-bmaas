"""
This is the first (Welcome) page that opens up when we navigate to initial-setup.local URL

All we need here is to navigate to the next page by clicking on the "Next" button
"""

import logging

from playwright.sync_api import Page

from setup_ui.page_object.base_page import BasePage
from hpe_glcp_automation_lib.libs.commons.utils.pwright.pwright_utils import TableUtils

logger = logging.getLogger()


class DiscoveredServersPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page
        self.table_utils = TableUtils(page=self.page)

    def validate_server_discovery(self, servers_serial_numbers: list[str] = ["3M1D1Z1182"]):
        """Iterates through servers_serial_numbers and checks for their 'Used for Setup' state in the table

        Args:
            servers_serial_numbers (list[str], optional): List of servers used for setup. Defaults to ["3M1D1Z1182"].
        """
        logger.info("Retrieving column index of Serial Number")
        serial_number_column_index = self.table_utils.get_column_index_by_name(column_name="Serial Number")
        logger.info(serial_number_column_index)

        logger.info("Checking for 'Yes' in 'Used for Setup' column for each server serial number")
        for server_serial_number in servers_serial_numbers:
            row_indices = self.table_utils.get_rows_indices_by_text(row_text=server_serial_number)
            logger.info(row_indices)

            used_for_setup = " ".join(
                self.page.locator(self.table_utils.row_columns_template.format(row_index=row_indices[0]))
                .nth(serial_number_column_index)
                .text_content()
                .split()
            )
            logger.info(f"Server Serial Number {server_serial_number} used for setup = {used_for_setup}")
            assert (
                used_for_setup == "Yes"
            ), f"Server Serial Number {server_serial_number} used for setup = {used_for_setup}"
