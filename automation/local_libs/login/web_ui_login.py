import logging
import os

from hpe_glcp_automation_lib.libs.authn.ui.login_page import Login
from hpe_glcp_automation_lib.libs.commons.utils.pwright.pwright_utils import browser_page, browser_stop
from hpe_glcp_automation_lib.libs.ui_doorway.user_api.ui_doorway import UIDoorway

log = logging.getLogger(__name__)
RECORD_DIR = os.path.join("tmp", "results")


class LoginHelper:
    """
    UI Login helper class.
    """

    @staticmethod
    def wf_webui_login(login_info: UIDoorway, browser, storage_filename, pcid_name=None):
        """Store browser state with logged-in user and return path to the file with saved storage state.

        :param login_info: UIDoorway instance of logged-in user.
        :param browser: playwright browser instance.
        :param storage_filename: name of the file with saved storage state of browser.
        :param pcid_name: account name, which should be chosen after user logged in.
        :return: path to the file with saved storage state.
        """
        context, page = browser_page(browser)
        login_page = Login(page, login_info.host).open()
        if pcid_name:
            login_page \
                .login_acct(login_info.user, login_info.password, pcid_name) \
                .go_to_account_by_name(pcid_name) \
                .wait_for_loaded_state()
        else:
            login_page \
                .login_acct(login_info.user, login_info.password) \
                .wait_for_loaded_state()
        storage_state_path = os.path.join(RECORD_DIR, storage_filename)
        context.storage_state(path=storage_state_path)
        browser_stop(context, page, storage_filename)
        return storage_state_path
