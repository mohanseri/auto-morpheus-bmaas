import requests
import warnings

from requests import Response
from lib.common.utils import handle_response

warnings.filterwarnings("ignore")

# NOTE; If proxies below are not working, attempt to use "http://hpeproxy.its.hpecorp.net:443"
proxies = {
    "http": "http://web-proxy.corp.hpecorp.net:8080",
    "https": "http://web-proxy.corp.hpecorp.net:8080",
}


class MorpheusAPI:
    def __init__(self, base_url, api_token, proxies=proxies):
        """Initializes the MorpheusAPI class.

        Args:
            base_url (_type_): The base URL of the Morpheus API.
            api_token (_type_): The API token for the Morpheus API.
            proxies (_type_, optional): The proxies to use for the Morpheus API. Defaults to proxies.
        """
        self.base_url = base_url
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.proxies = proxies

    def _get(self, endpoint, verify=False, expecting_error: bool = False) -> Response:
        """GET request to the Morpheus API.

        Args:
            endpoint (str): The endpoint to send the GET request to.
            verify (bool, optional): The verification of the GET request. Defaults to False.
            expecting_error (bool, optional): If the GET request is expected to return an error. Defaults to False.

        Returns:
            Response: The response from the GET request.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, verify=verify)
        if expecting_error:
            return response
        else:
            handle_response(response)
        return response

    def _post(self, endpoint, data, verify=False, expecting_error: bool = False) -> Response:
        """The POST request to the Morpheus API.

        Args:
            endpoint (str): The endpoint to send the POST request to.
            data (_type_): The data to send with the POST request.
            verify (bool, optional): The verification of the POST request. Defaults to False.
            expecting_error (bool, optional): If the POST request is expected to return an error. Defaults to False.

        Returns:
            Response: The response from the POST request.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data, verify=verify)
        if expecting_error:
            return response
        else:
            handle_response(response)
        return response

    def _post_upload(self, endpoint, data, verify=False, expecting_error: bool = False) -> Response:
        """The POST request to the Morpheus API for uploading files.

        Args:
            endpoint (str): The endpoint to send the POST request to.
            data (_type_): The data to send with the POST request.
            verify (bool, optional): The verification of the POST request. Defaults to False.
            expecting_error (bool, optional): If the POST request is expected to return an error. Defaults to False.

        Returns:
            Response: The response from the POST request.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, data=data, verify=verify)
        if expecting_error:
            return response
        else:
            handle_response(response)
        return response

    def _put(self, endpoint, data=None, verify=False, expecting_error: bool = False) -> Response:
        """The PUT request to the Morpheus API.

        Args:
            endpoint (str): The endpoint to send the PUT request to.
            data (_type_, optional): The data to send with the PUT request. Defaults to None.
            verify (bool, optional): The verification of the PUT request. Defaults to False.
            expecting_error (bool, optional): If the PUT request is expected to return an error. Defaults to False.

        Returns:
            Response: The response from the PUT request.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.put(url, headers=self.headers, json=data, verify=verify)
        if expecting_error:
            return response
        else:
            handle_response(response)
        return response

    def _delete(self, endpoint, verify=False, expecting_error: bool = False) -> Response:
        """The DELETE request to the Morpheus API.

        Args:
            endpoint (str): The endpoint to send the DELETE request to.
            verify (bool, optional): The verification of the DELETE request. Defaults to False.
            expecting_error (bool, optional): If the DELETE request is expected to return an error. Defaults to False.
        Returns:
            Response: The response from the DELETE request.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.delete(url, headers=self.headers, verify=verify)
        if expecting_error:
            return response
        else:
            handle_response(response)
        return response
