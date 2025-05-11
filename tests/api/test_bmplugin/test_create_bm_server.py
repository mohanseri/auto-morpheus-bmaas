import json
import os
from dotenv import load_dotenv
from hpe_morpheus_automation_libs.api.external_api.server.servers_api import ServerAPI
from hpe_morpheus_automation_libs.api.external_api.server.servers_payload import CreateHost

# Explicitly load the .env.dev file
load_dotenv(dotenv_path=".env.dev")

def test_create_baremetal_host():
    """
    Test case to create a BareMetal Host using the ServerAPI class.
    """
    # Initialize the ServerAPI with credentials from environment variables
    server_api = ServerAPI(
        host=os.getenv("MORPHEUS_HOST"),
        username=os.getenv("MORPHEUS_USERNAME"),
        password=os.getenv("MORPHEUS_PASSWORD"),
        verify=False,  # Disable SSL verification for testing purposes
    )

    # Define the payload for creating a BareMetal Host
    payload = CreateHost(
        server={
            "cloud": {"id": 1},
            "computeServerType": {"code": "IloBareMetalUnmanaged"},
            "group": {"id": 1},
            "config": {
                "iloIpAddress": os.getenv("ILO_IP_ADDRESS"),
                "iloUsername": os.getenv("ILO_USERNAME"),
                "iloPassword": os.getenv("ILO_PASSWORD"),
                "macAddress": os.getenv("MAC_ADDRESS"),
            },
            "name": os.getenv("HOST_NAME"),
            "visibility": "private",
        }
    )

    # Send the request to create the BareMetal Host
    response = server_api.add_baremetal_host(qparams=payload)

    # Validate the response status code
    assert response.status_code == 200, f"Failed to create BareMetal Host. Status Code: {response.status_code}"

    # Parse and pretty-print the response JSON
    response_json = response.json()
    print("BareMetal Host Created:")
    print(json.dumps(response_json, indent=4))

    # Verify the creation status and other details
    assert response_json.get("success") == True, "BareMetal Host creation failed"
    assert response_json.get("server", {}).get("name") == os.getenv("HOST_NAME"), "BareMetal Host name mismatch"
    assert response_json.get("server", {}).get("status") == "provisioning", "BareMetal Host status mismatch"
    assert response_json.get("server", {}).get("computeServerType", {}).get("code") == "IloBareMetalUnmanaged", "BareMetal Host type mismatch"
    # assert response_json.get("server", {}).get("group", {}).get("id") == 1, "BareMetal Host group ID mismatch"
    # assert response_json.get("server", {}).get("cloud", {}).get("id") == 1, "BareMetal Host cloud ID mismatch"
    # assert response_json.get("server", {}).get("visibility") == "private", "BareMetal Host visibility mismatch"
