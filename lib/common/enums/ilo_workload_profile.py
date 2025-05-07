from enum import Enum


class ILOWorkloadProfile(Enum):
    VIRTUALIZATION_MAX_PERFORMANCE = "Virtualization-MaxPerformance"
    GENERAL_PEAK_FREQUENCY_COMPUTE = "GeneralPeakFrequencyCompute"
    GENERAL_THROUGHPUT_COMPUTE = "GeneralThroughputCompute"
    VIRTUALIZATION_POWER_EFFICIENT = "Virtualization-PowerEfficient"
