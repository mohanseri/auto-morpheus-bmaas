def mira_test_data(current_env, secrets, passwords):
    """
    Usage: Test bed data will be initialized in conftest.py
    define username, acct_name, app_name, device serials, subscriptions in this file
    Password and api_secret need to be in user_creds.json file
    """
    tb_data = {}
    tb_data["test_or_workflow_name1"] = {}
    tb_data["test_or_workflow_name2"] = {}
    tb_data["greenfield_new_user_acct"] = {}
    tb_data["brownfield_existing_user"] = {}
    if "mira" in current_env:
        tb_data["test_or_workflow_name1"]["username"] = "hcloud203+lvkauji@gmail.com"
        tb_data["test_or_workflow_name1"]["password"] = passwords[tb_data["test_or_workflow_name1"]["username"]]
        tb_data["test_or_workflow_name1"]["account_name"] = "account_name1"

        tb_data['greenfield_new_user_acct']['api_auth_client_id'] = "swsc_client"
        tb_data['greenfield_new_user_acct']['api_auth_client_secret'] = tb_data['greenfield_new_user_acct'][
            'api_auth_client_id']

        # TODO: replace by service-centric UI user with application auto-assigning
        tb_data['brownfield_existing_user']['username'] = "hcloud203+lvkauji@gmail.com"
        tb_data['brownfield_existing_user']['password'] = tb_data['brownfield_existing_user']['username']
        tb_data['brownfield_existing_user']['acct1'] = "lvkauji"
        tb_data['brownfield_existing_user']['pcid'] = "9b2f834ab9e111ed88a65aac80df3fb3"
        tb_data['brownfield_existing_user']['appid'] = "6be1a454-48e1-40c7-a1f7-3d2c0417e24c"
        tb_data["brownfield_existing_user"]['app_instance_id'] = "9cb411ee-5bc8-43b7-be2d-863b21b19b57"
        tb_data["brownfield_existing_user"]['acid'] = "1b0ea49403fa11eeaf0b1678a169e9a4"

    return tb_data
