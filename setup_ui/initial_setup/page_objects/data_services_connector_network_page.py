import logging

from playwright.sync_api import Page

from setup_ui.initial_setup.locators.data_services_connector_network_locators import (
    DataServicesConnectorNetworkLocators,
)
from setup_ui.page_object.base_page import BasePage
from playwright.sync_api import expect

logger = logging.getLogger()


class DataServicesConnectorNetworkPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page=page)
        self.page = page

    def enter_network_interface_details_and_configure(
        self,
        address_type: str = "DHCP",
        host_name: str = "dsconnector-vm",
        subnet_mask: str = "255.255.252.0",
        default_gateway: str = "10.157.232.1",
        default_docker_bridge_network: str = "172.17.0.0/24",
        data_services_connector_bridge_network: str = "172.18.0.0/24",
    ):
        """Fills out the network interface details for the Data Services Connector.

        Args:
            address_type (str, optional): Type of address. Defaults to "DHCP". Valid values DHCP or Static.
            host_name (str, optional): Name of the DSC VM. Defaults to "dscconnector-vm".
            subnet_mask (str, optional): Subnet Mark for the DSC VM. Defaults to "255.255.252.0".
            default_gateway (str, optional): Default Gateway for the DSC VM. Defaults to "10.157.232.1".
            default_docker_bridge_network (str, optional): Default Docker Bridge for DSC VM. Defaults to "172.17.0.0/24"
            data_services_connector_bridge_network (str, optional): DSC Connect bridget network for DSC VM. Defaults to "172.18.0.0/24". # noqa E501
        """
        if address_type == "DHCP":
            logger.info("Selecting DHCP radio button...")
            dhcp_radio_button = self.page.get_by_role(
                role="radio",
                name=DataServicesConnectorNetworkLocators.RADIO_DHCP,
            )

            # The radio button control is hidden and cannot be clicked
            # Clicking on DHCP text instead
            if not dhcp_radio_button.is_checked():
                self.page.get_by_text(DataServicesConnectorNetworkLocators.RADIO_DHCP).click(force=True)

            logger.info("Validating DHCP information for DCS VM")
            expect(self.page.get_by_test_id(DataServicesConnectorNetworkLocators.HOST_NAME)).to_have_value(host_name)
            expect(self.page.get_by_test_id(DataServicesConnectorNetworkLocators.IP_ADDRESS)).not_to_have_value("")
            expect(self.page.get_by_test_id(DataServicesConnectorNetworkLocators.SUBNET_MASK)).to_have_value(
                subnet_mask
            )
            expect(
                self.page.get_by_test_id(
                    DataServicesConnectorNetworkLocators.DEFAULT_GATEWAY,
                )
            ).to_have_value(
                default_gateway,
            )
            expect(
                self.page.get_by_test_id(
                    DataServicesConnectorNetworkLocators.DEFAULT_DOCKER_BRIDGE_NETWORK,
                )
            ).to_have_value(default_docker_bridge_network)
            expect(
                self.page.get_by_test_id(
                    DataServicesConnectorNetworkLocators.DSC_DOCKER_BRIDGE_NETWORK,
                )
            ).to_have_value(data_services_connector_bridge_network)
        elif address_type == "Static":
            logger.info("Selecting Static radio button...")
            static_radio_button = self.page.get_by_role(
                role="radio",
                name=DataServicesConnectorNetworkLocators.RADIO_STATIC,
            )

            # The radio button control is hidden and cannot be clicked
            # Clicking on Static text instead
            if not static_radio_button.is_checked():
                self.page.get_by_text(DataServicesConnectorNetworkLocators.RADIO_STATIC).click(force=True)

            # NOTE: Add steps if needed

        self.click_next_button()
