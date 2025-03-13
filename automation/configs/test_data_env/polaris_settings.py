def polaris_test_data(current_env, secrets, passwords):
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
    if "polaris" in current_env:
        tb_data["gmail_username"] = "name@gmail.com"
        tb_data["test_or_workflow_name1"]["username"] = "username"
        tb_data["test_or_workflow_name1"]["account_name1"] = "Some_account_name1"
        tb_data["test_or_workflow_name1"]["app_api_user"] = "some_api_id"

        tb_data['greenfield_new_user_acct']['api_auth_client_id'] = "af4a9915-f274-44bc-b665-b75e8e131bc0_api"
        tb_data['greenfield_new_user_acct']['api_auth_client_secret'] = tb_data['greenfield_new_user_acct'][
            'api_auth_client_id']
        tb_data['greenfield_new_user_acct']["gf_app_id"] = "17c23735-f960-4b85-9cc2-610a4fae617d"
        tb_data['greenfield_new_user_acct']["gf_region"] = "us-west"

        # TODO: replace by service-centric UI user
        tb_data['brownfield_existing_user']['username'] = "hcloud203+ncaqnmd@gmail.com"
        tb_data['brownfield_existing_user']['password'] = tb_data['brownfield_existing_user']['username']
        tb_data['brownfield_existing_user']['acct1'] = "ncaqnmd Company"
        tb_data['brownfield_existing_user']['pcid'] = "cbbf8e64ba5511edb2cf966718796261"
        tb_data['brownfield_existing_user']['appid'] = "17c23735-f960-4b85-9cc2-610a4fae617d"
        tb_data["brownfield_existing_user"]['app_instance_id'] = "af4a9915-f274-44bc-b665-b75e8e131bc0"
        tb_data["brownfield_existing_user"]['acid'] = "d1f8a48cba5511ed86d72a9370e310e1"
        tb_data["brownfield_existing_user"]['iap_sn'] = "STIAPP0IW4"
        tb_data["brownfield_existing_user"]['gw_sn'] = "STGWAL4VBD"
        tb_data["brownfield_existing_user"]['sw_sn'] = "STSWILETGH"
        tb_data["brownfield_existing_user"]['iap_lic_key'] = "E9405A72604314D029"
        tb_data["brownfield_existing_user"]['gw_lic_key'] = "E56E67BF8FD4F4428B"
        tb_data["brownfield_existing_user"]['sw_lic_key'] = "EB9D047D2F6E94D35B"

        return tb_data
