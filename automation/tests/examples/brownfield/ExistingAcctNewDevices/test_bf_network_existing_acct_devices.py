import logging

import allure
import pytest

from automation.conftest import ExistingUserAcctDevices
from automation.tests.examples.brownfield.ExistingAcctNewDevices.brnf_network_existing_acct_devices import (
    WfScExistingAcctDevices,
)

log = logging.getLogger(__name__)


@allure.parent_suite("auto-cafe-template")
@allure.suite("Brownfield network devices service_centric_ui")
@allure.sub_suite("Brownfield existing account new network devices")
@pytest.mark.skipif("polaris" in ExistingUserAcctDevices.login_page_url, reason="Not supported on polaris.")
@pytest.mark.skipif("pavo" in ExistingUserAcctDevices.login_page_url, reason="Not supported on pavo.")
@pytest.mark.skipif("triton-lite" in ExistingUserAcctDevices.login_page_url, reason="Not supported on triton-lite.")
class TestExistingAccountNewDevicesSvc:
    @pytest.mark.seventeenth
    @pytest.mark.Regression
    def test_get_audit_log_for_user_login(
            self,
            browser_instance,
            brownfield_standalone_logged_in_ui_storage_state,
            ):
        """
        Test audit log message for IAP device
        Log type for user login is successful or not seen in the message.
        """
        create_test = WfScExistingAcctDevices()
        username = ExistingUserAcctDevices.test_data["brownfield_existing_user"][
            "username"]
        expected_description = (
            f'User {username} logged in via ping mode.'
        )
        assert create_test.wf_audit_log_info(browser_instance,
                                             brownfield_standalone_logged_in_ui_storage_state,
                                             username,
                                             expected_description
                                             )

    @pytest.mark.order(41)
    @pytest.mark.Regression
    def test_search_at_roles_page(self, browser_instance, brownfield_standalone_logged_in_ui_storage_state):
        create_test = WfScExistingAcctDevices()
        assert create_test.wf_roles_page(browser_instance, brownfield_standalone_logged_in_ui_storage_state)
