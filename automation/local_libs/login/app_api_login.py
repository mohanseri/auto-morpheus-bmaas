from hpe_glcp_automation_lib.libs.adi.app_api.adi_app_api import ActivateInventory
from hpe_glcp_automation_lib.libs.adi.app_api.app_api_helper import AdiAppApiHelper

from automation_svc_ui.conftest import ExistingUserAcctDevices

class AppApiSession():
    @staticmethod
    def adi_app_session(app_api_key, app_api_secret):
        adi_app_api = ActivateInventory(
            host=ExistingUserAcctDevices.app_api_hostname,
            sso_host=ExistingUserAcctDevices.sso_hostname,
            client_id=app_api_key,
            client_secret=app_api_secret,
        )
        return adi_app_api

    @staticmethod
    def adi_app_helper_session(app_api_key, app_api_secret):
        adi_app_api = AdiAppApiHelper(
            host=ExistingUserAcctDevices.app_api_hostname,
            sso_host=ExistingUserAcctDevices.sso_hostname,
            client_id=app_api_key,
            client_secret=app_api_secret,
        )
        return adi_app_api