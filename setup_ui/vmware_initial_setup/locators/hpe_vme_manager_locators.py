class HPEVMEManagerLocators:
    IP_ADDRESS = "input[id='ip-addr']"
    NETMASK = "input[id='netmask']"
    GATEWAY = "input[id='gateway']"
    DNS_SERVERS = "input[type='MaskedInput']"  # multiple -> use index
    APPLIANCE_URL = "input[id='applianceURL']"
    HOST_NAME = "input[id='hostname']"
    USERNAME = "input[id='username']"
    PASSWORD = "input[type='password']"
    PROXY = "input[name='proxy']"
    NO_PROXY_LIST = "input[type='TextInput']"
