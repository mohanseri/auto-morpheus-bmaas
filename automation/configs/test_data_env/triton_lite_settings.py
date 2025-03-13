def triton_lite_test_data(current_env, secrets, passwords):
    """
    Usage: Test bed data will be initialized in conftest.py
    define username, acct_name, app_name, device serials, subscriptions in this file
    Password and api_secret need to be in user_creds.json file
    """
    tb_data = {}
    tb_data["test_or_workflow_name1"] = {}
    tb_data["test_or_workflow_name2"] = {}
    if "triton-lite" in current_env:
        tb_data["test_or_workflow_name1"]["username"] = "username"
        tb_data["test_or_workflow_name1"]["password"] = passwords[tb_data["test_or_workflow_name1"]["username"]]
        tb_data["test_or_workflow_name1"]["account_name"] = "account_name1"
        return tb_data