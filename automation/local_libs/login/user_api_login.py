from automation_svc_ui.conftest import ExistingUserAcctDevices
from hpe_glcp_automation_lib.libs.ui_doorway.user_api.ui_doorway import UIDoorway

class UserApiLogin():
    @staticmethod
    def user_api_login_load_account(username, password, pcid):
        hostname = ExistingUserAcctDevices.login_page_url
        url = hostname.split('//')[1]
        return UIDoorway(url, username, password, pcid)