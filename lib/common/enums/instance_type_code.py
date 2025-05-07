from enum import Enum


class InstanceTypeCode(Enum):
    MVM = "mvm"
    KVM = "kvm"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    VMWARE = "vmware"
    BM = "hpe-baremetal-plugin.provision"
