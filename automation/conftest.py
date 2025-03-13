import json
import logging
import os
import shutil
import sys

import pytest
from hpe_glcp_automation_lib.libs.commons.common_testbed_data.settings import (
    Settings,
    all_envs
)
from hpe_glcp_automation_lib.libs.commons.utils.s3.s3_download import download_file
from hpe_glcp_automation_lib.libs.ui_doorway.user_api.ui_doorway import UIDoorway
from automation.local_libs.login.web_ui_login import LoginHelper

from automation.constants import AUTOMATION_DIRECTORY

log = logging.getLogger(__name__)

settings = Settings()

# set default_env to polaris if none is provided from pytest command line or clusterinfo
default_env = "mira"
os.environ["CURRENT_ENV"] = default_env
os.environ["AUTOMATION_DIRECTORY"] = AUTOMATION_DIRECTORY


# Argument processing need to be executed before test data imports.
def pytest_addoption(parser):
    parser.addoption(
        "--env", action="store", choices=all_envs.keys(), default=default_env
    )


# command line argument parser to find env under test
for index, arg in enumerate(sys.argv):
    if arg.startswith("--env"):
        if "=" in arg:
            if arg.split("=")[1] in all_envs.keys():
                os.environ["CURRENT_ENV"] = arg.split("=")[1]
                break
            else:
                raise Exception(f"Unsupported environment: {arg.split('=')[1]}")
        elif sys.argv[index + 1] in all_envs.keys():
            os.environ["CURRENT_ENV"] = sys.argv[index + 1]
            break
        else:
            raise ValueError(f"Unsupported environment: {sys.argv[index + 1]}")

# default env or command line env will override if settings.current_env() found env from clusterinfo
current_env = settings.current_env()

# import test data environment based on current env under test in local environment or on k8s environment
exec(f'from automation.configs.test_data_env.{current_env}_settings import {current_env}_test_data')

class Creds:

    @staticmethod
    def downloaded_creds():
        """
        downloading creds from remote s3 locations if available or use from local directory
        """
        s3_file_location = "akuc/auto-cafe-template/creds/"
        get_cwd = os.getcwd()
        try:
            download_file(s3_file_location)
            shutil.copy(
                f"{get_cwd}/{s3_file_location}user_creds.json",
                AUTOMATION_DIRECTORY,
            )
            with open(os.path.join(AUTOMATION_DIRECTORY, "user_creds.json")) as fd:
                s3_login_data = json.load(fd)
                log.info("downloading creds from remote locations")
        except Exception as ex:
            with open(os.path.join(AUTOMATION_DIRECTORY, "user_creds.json")) as fd:
                s3_login_data = json.load(fd)
                log.info(f"Error on downloading creds. {ex}")
                log.info("using creds from local locations")
        return s3_login_data

    @staticmethod
    def resolve_creds(cluster):
        """
        downloading creds from remote s3 locations if available
        """
        log.info("getting creds from remote or local location")
        try:
            getcreds = Creds.downloaded_creds()
            client_ids_secrets = getcreds[cluster]["app_api_secrets"]
            users_passwords = getcreds[cluster]["users"]
            log.info(users_passwords)
            return client_ids_secrets, users_passwords
        except Exception as e:
            log.error(f"not able to download credentials, check logs:\n{e}")


class CreateLogFile:
    """
    Usage: Create log and result file location if not exists
    From this location Job will upload all logs and results
    """

    @staticmethod
    def log_file_location():
        return "/tmp/results/"

    @staticmethod
    def create_log_file():
        try:
            if not os.path.exists("/tmp/results/"):
                os.mkdir("/tmp/results/")
            if not os.path.exists("/tmp/results/log1.log"):
                with open("/tmp/results/log1.log", "w"):
                    pass
            return True
        except Exception as ex:
            log.info(f"not able to create log file and directory. Error: {ex}")


class NewUserAcctDevices:
    new_session = "None"
    new_acct_info = "None"
    new_iap_device_list = "None"
    new_sw_device_list = "None"
    new_gw_device_list = "None"
    new_storage_device_list = "None"
    new_compute_device_list = "None"
    app_prov_done = "None"
    verification_hash = "None"
    time_for_id = "None"
    email_with_timestamp = "None"
    cookies = ["None", "None", "None", "None"]


class ExistingUserAcctDevices:
    """
    ExistingUserAcctDevices test env variables available for usage in test cases,
    inner tests' conftest.py, and in test helper methods, local_libs
    """
    current_env = settings.current_env()
    login_page_url = settings.login_page_url()
    app_api_hostname = settings.get_app_api_hostname()
    sso_hostname = settings.get_sso_host()
    hpe_device_url = settings.get_hpe_device_url()
    aruba_device_url = settings.get_aruba_device_url()
    aruba_switch_device_url = settings.get_aruba_switch_device_url()
    ccs_device_url = settings.get_ccs_device_url()
    ccs_activate_v1_device_url = settings.get_ccs_activate_v1_device_url()
    ccs_activate_v2_device_url = settings.get_ccs_activate_v2_device_url()
    auth_url = settings.get_auth_url()
    s3_login_data = Creds.downloaded_creds()
    login_data = s3_login_data[current_env]
    # aruba_legacy_device_url = settings.get_aruba_legacy_device_url()
    create_log_file = CreateLogFile.create_log_file()
    log_files = CreateLogFile.log_file_location()
    secrets, passwords = Creds.resolve_creds(current_env)
    test_data = dict()
    exec('test_data = {}_test_data(current_env, secrets, passwords)'.format(current_env))
    humio_url = settings.get_humio_url()


def browser_type(playwright, browser_name: str):
    """
    instantiate browser types based on local or k8s env with headless true or false
    """
    if browser_name == "chromium":
        browser = playwright.chromium
        if os.getenv("DEBIAN_FRONTEND") == "noninteractive":
            return browser.launch(headless=True, slow_mo=100)
        elif os.getenv("POD_NAMESPACE") is None:
            return browser.launch(headless=False, slow_mo=100)
        else:
            return browser.launch(headless=True, slow_mo=100)
    if browser_name == "firefox":
        browser = playwright.firefox
        if os.getenv("DEBIAN_FRONTEND") == "noninteractive":
            return browser.launch(headless=True, slow_mo=100)
        elif os.getenv("POD_NAMESPACE") is None:
            return browser.launch(headless=False, slow_mo=100)
        else:
            return browser.launch(headless=True, slow_mo=100)
    if browser_name == "webkit":
        browser = playwright.webkit
        if os.getenv("DEBIAN_FRONTEND") == "noninteractive":
            return browser.launch(headless=True, slow_mo=100)
        elif os.getenv("POD_NAMESPACE") is None:
            return browser.launch(headless=False, slow_mo=100)
        else:
            return browser.launch(headless=True, slow_mo=100)


@pytest.fixture(scope="session")
def browser_instance(playwright):
    """
    instantiate browser instance for test cases
    """
    browser = browser_type(playwright, "chromium")
    yield browser
    browser.close()


@pytest.fixture
def skip_if_triton():
    if "triton" in ExistingUserAcctDevices.login_page_url:
        log.info("skipping env {}".format(ExistingUserAcctDevices.login_page_url))
        pytest.skip("triton env is SKIPPED")


@pytest.fixture
def skip_if_polaris():
    if "polaris" in ExistingUserAcctDevices.login_page_url:
        log.info("skipping env {}".format(ExistingUserAcctDevices.login_page_url))
        pytest.skip("polaris env is SKIPPED")


@pytest.fixture
def skip_if_mira():
    if "mira" in ExistingUserAcctDevices.login_page_url:
        log.info("skipping env {}".format(ExistingUserAcctDevices.login_page_url))
        pytest.skip("mira env is SKIPPED")


@pytest.fixture
def skip_if_triton_lite():
    if "triton-lite" in ExistingUserAcctDevices.login_page_url:
        log.info("skipping env {}".format(ExistingUserAcctDevices.login_page_url))
        pytest.skip("triton-lite env is SKIPPED")


@pytest.fixture
def skip_if_pavo():
    if "pavo" in ExistingUserAcctDevices.login_page_url:
        log.info("skipping env {}".format(ExistingUserAcctDevices.login_page_url))
        pytest.skip("pavo env is SKIPPED")


@pytest.fixture(scope="session")
def brownfield_standalone_user_login_load_account():
    """
    Login, Load account and create session for user api
    :return session: object with inerited methods to make user api calls
    """
    hostname = ExistingUserAcctDevices.login_page_url
    username = ExistingUserAcctDevices.test_data["brownfield_existing_user"]["username"]
    password = ExistingUserAcctDevices.login_data["users"][username]
    pcid = ExistingUserAcctDevices.test_data["brownfield_existing_user"]["pcid"]
    url = hostname.split("//")[1]
    return UIDoorway(url, username, password, pcid)

@pytest.fixture(scope="session")
def brownfield_standalone_logged_in_ui_storage_state(brownfield_standalone_user_login_load_account,
                                                     browser_instance):
    """
    Create playwright login state and reuse for subsequent playwright tests
    """
    pcid_name = ExistingUserAcctDevices.test_data['brownfield_existing_user']['acct1']
    yield LoginHelper.wf_webui_login(brownfield_standalone_user_login_load_account,
                                     browser_instance,
                                     "brnf_logged_in_state_2.json",
                                     pcid_name)
