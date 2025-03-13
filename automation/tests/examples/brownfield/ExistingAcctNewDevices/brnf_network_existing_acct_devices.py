import logging
import os

from hpe_glcp_automation_lib.libs.acct_mgmt.ui.choose_account_page import ChooseAccount

from hpe_glcp_automation_lib.libs.commons.ui.manage_account_page import ManageAccount
from hpe_glcp_automation_lib.libs.commons.utils.pwright.pwright_utils import (
    browser_page,
    browser_stop,
)

from automation.conftest import ExistingUserAcctDevices

log = logging.getLogger(__name__)

class WfScExistingAcctDevices:
    def __init__(self):
        log.info("Initialize Existing Acct new Devices class")
        """
        Create Test variables
        """
        self.cluster = ExistingUserAcctDevices.login_page_url
        self.pcid_name = ExistingUserAcctDevices.test_data['brownfield_existing_user']['acct1']

    def wf_audit_log_info(self,
                          browser_instance,
                          storage_state_path,
                          username,
                          expected_description
                          ) -> bool:
        """
        Step #3: Check user login audit logs on audit logs page.
        :params initiated browser_instance:
        :params logged in playwright login stored object:
        :params username:
        :return boolean:
        """

        test_name = (
            os.environ.get("PYTEST_CURRENT_TEST", "").split(":")[-1].split(" ")[0]
        )
        context, page = browser_page(browser_instance, storage_state_path)

        try:
            ChooseAccount(page, self.cluster) \
                .open() \
                .go_to_account_by_name(self.pcid_name) \
                .wait_for_loaded_state() \
                .nav_bar.navigate_to_manage()
            audit_logs = ManageAccount(page, self.cluster).open_audit_logs()
            audit_logs \
                .wait_for_loaded_table() \
                .search_for_text(username) \
                .should_have_row_with_values_in_columns({"Description": expected_description}) \
                .open_row_details("Description", expected_description) \
                .should_audit_log_item_have_details(expected_description)

            return True

        except Exception as ex:
            log.error(f"Error:\n{ex}")
            return False

        finally:
            browser_stop(context, page, test_name)

    def wf_roles_page(self,
                      browser_instance,
                      storage_state_path) -> bool:
        """Step #19: Check role at Roles page."""
        log.info(f"Playwright: verifying existing role at Roles page.")

        test_name = (
            os.environ.get("PYTEST_CURRENT_TEST", "").split(":")[-1].split(" ")[0]
        )
        context, page = browser_page(browser_instance, storage_state_path)

        try:
            ChooseAccount(page, self.cluster).open() \
                .go_to_account_by_name(self.pcid_name) \
                .wait_for_loaded_state().nav_bar.navigate_to_manage()
            roles_page = ManageAccount(page, self.cluster).open_identity_and_access().open_roles_and_permissions()

            roles_page \
                .wait_for_loaded_table() \
                .should_contain_text_in_title("Roles & Permissions") \
                .should_have_search_field() \
                .search_for_text("Workspace Administrator") \
                .should_have_rows_count(1) \
                .should_contain_text_in_table("Workspace Administrator Role") \
                .should_have_row_with_text_in_column("Description", "Workspace Administrator Role")

            return True

        except Exception as ex:
            log.error(f"Error:\n{ex}")
            return False

        finally:
            browser_stop(context, page, test_name)
