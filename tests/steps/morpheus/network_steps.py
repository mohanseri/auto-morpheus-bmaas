import logging
from lib.common.enums.network_type_name import NetworkTypeName
from morpheus_api.dataclasses.common_objects import ID, IDName, IDNameCode
from morpheus_api.dataclasses.network import NetworkData, NetworkCreateData
from morpheus_api.settings import MorpheusAPIService

logger = logging.getLogger()

"""This module contains steps for ALL backup-related operations."""


def create_ovs_port_group_payload(
    morpheus_api: MorpheusAPIService,
    name: str,
    site_id: int,
    vlan_id: int,
    zone_id: int,
    zone_name: str,
    cluster_id: int,
    cluster_name: str,
    network_type_name: NetworkTypeName = NetworkTypeName.OVS_PORT_GROUP_NAME,
) -> NetworkCreateData:
    """
    Create the payload for an OVS port group network.

    Args:
        morpheus_api (MorpheusAPIService): The Morpheus API service instance.
        name (str): The name of the OVS port group.
        site_id (int): The ID of the site.
        vlan_id (int): The VLAN ID.
        zone_id (int): The ID of the zone.
        zone_name (str): The name of the zone.
        cluster_id (int): The ID of the cluster which is used for the Zone Pool ID.
        cluster_name (str): The name of the cluster which is used for the Zone Pool Name.
        network_type_name (NetworkTypeName, optional): The network type name. Defaults to NetworkTypeName.OVS_PORT_GROUP_NAME.

    Returns:
        NetworkCreateData: The payload data for creating the OVS port group network.

    Raises:
        AssertionError: If no network routers, groups, or network types are found.
    """

    logger.info(f"Creating OVS port group payload with name: {name}")

    # Obtain the SwitchID
    network_router_list = morpheus_api.network_service.list_network_routers()
    assert network_router_list.meta.total > 0, "No network routers found"

    # Obtain the Group ID & Name
    group_list = morpheus_api.group_service.list_groups()
    assert group_list.meta.total > 0, "No groups found"

    # Obtain the Network Type ID, Name, and Code
    network_type_list = morpheus_api.network_type_service.list_network_types(name=network_type_name.value)
    assert network_type_list.meta.total > 0, f"Network type {network_type_name.value} not found"

    network_data = NetworkData(
        name=name,
        vlan_id=vlan_id,
        switch_id=network_router_list.network_routers[0].name,
        site=ID(id=site_id),
        zone=IDName(id=zone_id, name=zone_name),
        type=IDNameCode(
            id=network_type_list.network_types[0].id,
            name=network_type_list.network_types[0].name,
            code=network_type_list.network_types[0].code,
        ),
        zone_pool=IDName(id=cluster_id, name=cluster_name),
        group=IDName(id=group_list.groups[0].id, name=group_list.groups[0].name),
        ipv4_enabled=True,
        ipv6_enabled=True,
    )
    network_create_data = NetworkCreateData(network=network_data)
    logger.info(f"OVS port group payload created: {network_create_data}")
    return network_create_data
