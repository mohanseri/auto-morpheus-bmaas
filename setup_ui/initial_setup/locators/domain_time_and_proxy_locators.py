class DomainTimeAndProxyLocators:
    DNS_0 = "dns-input-0"
    DNS_1 = "dns-input-1"
    DNS_2 = "dns-input-2"
    SEARCH_DOMAIN_0 = "search-domain-input-0"
    REGION = "region-input-field"
    REGION_DROPDOWN_VALUE = "span:has-text('{region}')"
    TIME_ZONE = "time-zone-input-field"  # dropdown arrow button
    TIME_ZONE_DROPDOWN = (
        "div[role='listbox']"  # dropdown list container which appears after clicking on the arrow button
    )
    TIME_ZONE_DROPDOWN_VALUE = "span:has-text('{time_zone}')"  # dropdown value
    NTP = "ntp-input"
    INCLUDE_PROXY_SERVER = "include-proxy-server-checkbox"  # this is a hidden control and cannot be clicked
    INCLUDE_PROXY_SERVER_CHECKBOX_TEXT = "Include"
    # We will use the above identifier for clicking on the checkbox
    # The below mentioned XPATH is an alternative in case the we see failures with the above identifier
    # //div[@data-testid="include-proxy-server-checkbox-container"]//span[text()='Include']
    PROXY_SERVER_ADDRESS = "proxy-server-address-input"
    PROXY_PORT = "proxy-port-input"
