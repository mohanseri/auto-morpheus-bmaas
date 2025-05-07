from enum import Enum


class ServicePlanName(Enum):
    CPU_1_MEMORY_512_MB = "1 CPU, 512MB Memory"
    CPU_1_MEMORY_1_GB = "1 CPU, 1GB Memory"
    CPU_1_MEMORY_2_GB = "1 CPU, 2GB Memory"
    CPU_1_MEMORY_4_GB = "1 CPU, 4GB Memory"
    CPU_2_MEMORY_8_GB = "2 CPU, 8GB Memory"
    CPU_2_MEMORY_16_GB = "2 CPU, 16GB Memory"
    CPU_4_MEMORY_24_GB = "4 CPU, 24GB Memory"
    CPU_4_MEMORY_32_GB = "4 CPU, 32GB Memory"
