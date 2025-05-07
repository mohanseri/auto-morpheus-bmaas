class StorageLocators:
    SERIAL_NUMBER = "select-storage"
    # page.get_by_role("button", name="Discover Storage System").click()
    DISCOVER_STORAGE_SYSTEM = "Discover Storage System"
    # Next button identifier comes from common_locators.py
    STORAGE_SERVER_DISCOVERY_MESSAGE = "Successfully discovered Storage System with Serial Number"

    IP_ADDRESS = "ipAddress"
    NETMASK = "netmask"
    GATEWAY = "gateway"
    # Next button identifier comes from common_locators.py
    # confirm-modal-confirm-check is present in common_locators.py
    # confirm-modal-primary-button is present in common_locators.py

    # Discover API call: https://initial-setup-3.local/seed/v1/discover-storage/4UW0004835
    # Storage Setup API call: https://initial-setup-3.local/seed/v1/storage-select
