import os

import requests

from lib.common.exceptions import APIError


def ping_ip_address(ip_address: str) -> bool:
    """
    Check if the IP address is reachable.

    Args:
        ip_address (str): IP address to check.

    Returns:
        bool: True if the IP address is reachable, False otherwise.
    """
    response = os.system(f"ping -c 1 {ip_address}")
    return response == 0


def handle_response(response: requests.Response):
    """Handles the response from APIs.

    Args:
        response (requests.Response): The response from the API.

    Raises:
        APIError: The error from the API.

    Returns:
        Response: The response from the API.
    """
    if response.status_code == 400:
        raise APIError(f"Bad Request: {response.text}")
    elif response.status_code == 401:
        raise APIError("Unauthorized: Check your API token.")
    elif response.status_code == 403:
        raise APIError("Forbidden: You do not have access to this resource.")
    elif response.status_code == 404:
        raise APIError("Not Found: The requested resource could not be found.")
    elif response.status_code == 500:
        raise APIError("Internal Server Error: Something went wrong on the server.")
    elif not response.ok:  # NOTE: response.ok is True if status_code is less than 400 (not in [400, 500))
        raise APIError(f"Error: {response.text}, Error Code: {response.status_code}")
    return response
