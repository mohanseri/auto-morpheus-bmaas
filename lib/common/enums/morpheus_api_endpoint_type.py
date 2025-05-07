from enum import Enum


class MorpheusAPIEndpoints(Enum):
    BACKUPS = "/api/backups"
    CLUSTERS = "/api/clusters"
    GROUPS = "/api/groups"
    IMAGE_BUILDS = "/api/image-builds"
    INSTANCE_TYPES = "/api/instance-types"
    INSTANCES = "/api/instances"
    LIBRARY = "/api/library"
    NETWORKS = "/api/networks"
    NETWORK_TYPES = "/api/network-types"
    OPTIONS = "/api/options"
    PROVISION_TYPES = "/api/provision-types"
    SERVERS = "/api/servers"
    SERVICE_PLANS = "/api/service-plans"
    SNAPSHOTS = "/api/snapshots"
    STORAGE_BUCKETS = "/api/storage-buckets"
    STORAGE_VOLUME_TYPES = "/api/storage-volume-types"
    STORAGE_VOLUMES = "/api/storage-volumes"
    VIRTUAL_IMAGES = "/api/virtual-images"
    ZONES = "/api/zones"
    CONTAINERS = "/api/containers"
