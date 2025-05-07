class NetworkConfiguration:
    TIME_ZONE: str = "America/Denver"
    NTP_SERVER: str = "16.110.135.123"
    DNS_SERVERS: list[str] = ["10.157.16.91", "10.157.16.92", "10.157.16.93"]
    DNS_SERVERS_VALIDATION: str = "10.157.16.91, 10.157.16.92, 10.157.16.93"
    SEARCH_DOMAIN: str = "cxo.storage.hpecorp.net"
    NETMASK: str = "255.255.252.0"
    GATEWAY: str = "10.157.232.1"
    PROXY: str = "http://web-proxy.corp.hpecorp.net:8080"
    HPE_VME_VM_SIZE: str = "Large"
    HPE_VME_MANAGEMENT_INTERFACE: str = "eth0"
