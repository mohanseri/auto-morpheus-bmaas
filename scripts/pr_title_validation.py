import argparse
import json
import re
import sys
import requests
from requests.auth import HTTPBasicAuth


JIRA_SERVER = 'https://hpe.atlassian.net'
validation_failed = False
ALLOWED_TYPE = ["Task", "Story", "Sub-task", "Bug"]


def get_all_jiras(pr_title_str):
    ccs_jiras_committed_lt = []
    ccs_jiras_committed_tmp = re.findall(r"CCS-[\d]+", str(pr_title_str))
    for ccs_jiras_committed in list(set(ccs_jiras_committed_tmp)):
        ccs_jiras_committed_lt.append(ccs_jiras_committed.replace("CCS-", "GLCP-"))
    glcp_jiras_committed_st = re.findall(r"GLCP-[\d]+", str(pr_title_str))
    glcp_jiras_committed_lt = list(set(glcp_jiras_committed_st))
    jiras_committed = ccs_jiras_committed_lt + glcp_jiras_committed_lt
    if not jiras_committed:
        jiras_committed_st = re.findall(r"PCCM-[\d]+", str(pr_title_str))
        jiras_committed = list(set(jiras_committed_st))
    return list(set(jiras_committed))  # Remove duplicates


def get_issue(jira_id, user, apikey):
    url = f"{JIRA_SERVER}/rest/api/2/issue/{jira_id}"
    auth = HTTPBasicAuth(user, apikey)
    headers = {
        "Accept": "application/json"
    }
    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )
    print(f"Response: {response}")
    response_data_json = None
    if response.status_code == 200:
        response_data_json = json.loads(response.text)
    return response.status_code, response_data_json


def process_input(pr_title_str, user, apikey):
    global validation_failed
    # Get all the jira ids from pr title and process for each jira id.
    jiras_list = get_all_jiras(pr_title_str=pr_title_str)
    print(f"List of Jiras: {jiras_list}")
    if not jiras_list or len(jiras_list) == 0:
        print("Error: No Jira ticket is provided in PR title. Please provide a valid Jira ticket", file=sys.stderr)
        validation_failed = True
        return
    for jira_id in jiras_list:
        status_code, resp_json = get_issue(jira_id=jira_id, user=user, apikey=apikey)
        ticket_type = resp_json.get("fields", {}).get("issuetype", {}).get("name", None)
        if ticket_type not in ALLOWED_TYPE:
            print(f"Error: {jira_id} is not of Allowed Jira type {ALLOWED_TYPE}. Current type: {ticket_type}")
            validation_failed = True
        if status_code != 200:
            print(f"Error: Invalid jira id: {jira_id}.")
            validation_failed = True


if __name__ == "__main__":
    # Fetch inputs
    my_parser = argparse.ArgumentParser()
    # ATATT3xFfGF0KbIGAnvNPHaz-Rtp1JrmGQJf_w9mIDtSZIA5-AZGUUrCAjhEf7eBDUeytlvqJPfx5HGPqnJ-Lxkqar6W0RQEHn-b3vBOetzheEBs4woFrgWswDrziMlKj6pn7o2X7uT6cw-JSHtim-pEC9Z0gNER9lwYpEDOjmOA3naewg9FoUg=21979ACA
    my_parser.add_argument('-p', '--pr_title', help="Pull Request Title", action='store', type=str, required=True)
    my_parser.add_argument('-u', '--user', help="Username to access Jira", action='store', type=str, required=True)
    my_parser.add_argument('-a', '--apikey', help="User's apikey to access Jira", action='store', type=str, required=True)
    args = my_parser.parse_args()
    user = None
    apikey = None
    pr_title = None
    pr_title = args.pr_title
    user = args.user
    apikey = args.apikey

    # Validate Input
    if pr_title is None:
        print("Error: PR Tile is not provided. Nothing to process.", file=sys.stderr)
        print("PR-Subject: ERROR: invalid or no ticket/bugid found. Check whether the ticket exists. Make sure PR subject is with right format. PR Subject Format - JiraProjectID-ticket1, JiraProjectID-ticketN: subject. Example - CCS-34704: Validation of the json files while pushing OR CCP-34536, CCS-34539: Analyze tools to monitor performance.")
        sys.exit(1)
    if user is None or apikey is None:
        print("Error: Access credentials not provided. Exit", file=sys.stderr)
        print("PR-Subject: ERROR: invalid or no ticket/bugid found. Check whether the ticket exists. Make sure PR subject is with right format. PR Subject Format - JiraProjectID-ticket1, JiraProjectID-ticketN: subject. Example - CCS-34704: Validation of the json files while pushing OR CCP-34536, CCS-34539: Analyze tools to monitor performance.")
        sys.exit(1)

    # Process PR title.
    process_input(pr_title_str=pr_title, user=user, apikey=apikey)
    print(validation_failed)
    if validation_failed:
        print(f"ERROR: `{pr_title}`contains invalid GLCP ticket. Please make sure PR title contains valid GLCP ticket.", file=sys.stderr)
        print("PR-Subject: ERROR: invalid or no ticket/bugid found. Check whether the ticket exists. Make sure PR subject is with right format. PR Subject Format - JiraProjectID-ticket1, JiraProjectID-ticketN: subject. Example - CCS-34704: Validation of the json files while pushing OR CCP-34536, CCS-34539: Analyze tools to monitor performance.")
        sys.exit(1)
    print("SUCCESS")
    sys.exit(0)
