from morpheus_api.dataclasses.base_object import BaseObject


class BasicParameters(BaseObject):
    comp_ratio: str
    validate: str
    dedup_ratio: str
    dedup_unit: str


class StorageDefinitions(BaseObject):
    storage_definition: str


class WorkloadDefinitions(BaseObject):
    workload_definition: str


class RunDefinitions(BaseObject):
    run_definition: str
