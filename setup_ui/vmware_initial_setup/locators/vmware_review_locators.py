class VMWareReviewLocators:
    # Network Details
    NTP_SERVERS = "span:right-of(:text('NTP Servers'))"  # present for HPE VME Essentials as well
    TIME_ZONE = "span:right-of(:text('Timezone'))"
    SEARCH_DOMAIN = "span:right-of(:text('Search Domain'))"
    DNS_SERVERS = "span:right-of(:text('DNS Servers'))"  # present for HPE VME Essentials as well

    # HPE VME Essentials Details
    APPLIANCE_URL = "span:right-of(:text('Appliance URL'))"
    IP_ADDRESS = "span:right-of(:text('IP Address'))"
    NETMASK = "span:right-of(:text('Netmask'))"
    GATEWAY = "span:right-of(:text('Gateway'))"
    HOST_NAME = "span:right-of(:text('Hostname'))"
    USERNAME = "span:right-of(:text('Username'))"
    PROXY = "span:right-of(:text('Proxy'))"
    VM_SIZE = "span:right-of(:text('VM Size'))"
    MANAGEMENT_INTERFACE = "span:right-of(:text('Management Interface'))"

    HPE_VME_INSTALLATION_PROGRESS_PERCENT = "svg[aria-label=*'Bar meter with value']"
    HPE_VME_INSTALLATION_SUCCESS_WINDOW = "Congratulations HPE VM Essentials Manager is Installed!"
