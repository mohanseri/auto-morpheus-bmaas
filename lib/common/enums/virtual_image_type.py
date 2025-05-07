from enum import Enum


class VirtualImageType(Enum):
    ALIBABA = "alibaba"
    AMAZON_AMI = "ami"
    AZURE_MARKETPLACE = "azure"
    ISO = "iso"
    OCI = "oci"
    PXE_BOOT = "pxe"
    QCOW2 = "qcow2"
    RAW = "raw"
    VHD = "vhd"
    VMWARE = "vmware"
