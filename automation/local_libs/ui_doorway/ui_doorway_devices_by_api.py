import logging

from hpe_glcp_automation_lib.libs.ui_doorway.user_api.ui_doorway import UIDoorway

log = logging.getLogger(__name__)

ALLOWED_DEVICE_TYPES = "STORAGE", "DHCI_STORAGE", "COMPUTE", "IAP", "SWITCH", "CONTROLLER", "GATEWAY"


class UiDoorwayDevices:

    @staticmethod
    def get_subscription_key(device_type, serial_no, part_no, sa_user_login_load_account: UIDoorway):
        """

        :param device_type: device type.
        :param serial_no: device's serial number.
        :param part_no: device's part number.
        :param sa_user_login_load_account: UIDoorway instance for user API-calls.
        :return: subscription key assigned to device or None.
        """
        if device_type not in ALLOWED_DEVICE_TYPES:
            raise ValueError(f"Not supported device type: '{device_type}'")
        payload = {
            "device_type": device_type,
            "serial_number": serial_no,
            "part_number": part_no
        }
        try:
            resp = sa_user_login_load_account.filter_devices(payload)

            return resp["devices"][0].get("subscription_key")
        except Exception as e:
            log.warning(e)
        return None
