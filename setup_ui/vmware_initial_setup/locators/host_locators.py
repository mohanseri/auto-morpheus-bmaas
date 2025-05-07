class HostLocators:

    # ----- Discovery Tab Locators -----
    # Discovered Hosts table
    ADD_BUTTON = "svg[aria-description='Add {host_serial_number} to selected hosts']"

    # Selected Hosts table
    MANAGEMENT_IP = "input[name='management-ip']"

    # ----- Network Tab Locators -----
    # Common
    ADD_SERVER_BUTTON = "svg[aria-label='Add']"  # index 0 for NTP Servers, 1 for DNS Servers

    # Time Services
    NTP_SERVERS = "input[type='TextInput']"
    TIME_ZONE = "input[id='timezone__input']"
    TIME_ZONE_SEARCH = "input[type='search']"
    TIME_ZONE_OPTION = "//button[text()='{time_zone}']"  # get_by_role

    # Network Services
    DNS_SERVERS = "input[type='IPv4Input']"  # multiple -> use index
    SEARCH_DOMAIN = "input[id='search-domain']"
    NETMASK = "input[id='netmask']"
    GATEWAY = "input[id='gateway']"
