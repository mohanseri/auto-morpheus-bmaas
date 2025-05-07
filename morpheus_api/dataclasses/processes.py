from typing import Optional

from morpheus_api.dataclasses.base_object import BaseObject
from morpheus_api.dataclasses.common_objects import Meta


class CreatedByAndUpdatedBy(BaseObject):
    username: str
    display_name: str


class ProcessType(BaseObject):
    code: str
    name: str


class Event(BaseObject):
    id: int
    process_id: int
    account_id: int
    unique_id: str
    process_type: ProcessType
    description: Optional[str] = None
    ref_type: str
    ref_id: int
    sub_type: Optional[str] = None
    sub_id: Optional[str] = None
    zone_id: Optional[int] = None
    integration_id: Optional[str] = None
    instance_id: int
    container_id: Optional[int] = None
    server_id: Optional[int] = None
    container_name: Optional[str] = None
    display_name: str
    status: str
    reason: Optional[str] = None
    percent: int
    status_eta: int
    message: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    duration: Optional[int] = None
    date_created: str
    last_updated: str
    created_by: CreatedByAndUpdatedBy
    updated_by: CreatedByAndUpdatedBy


class Process(BaseObject):
    id: int
    account_id: int
    unique_id: str
    process_type: ProcessType
    description: Optional[str] = None
    sub_type: Optional[str] = None
    sub_id: Optional[str] = None
    zone_id: Optional[int] = None
    integration_id: Optional[str] = None
    app_id: Optional[str] = None
    instance_id: int
    container_id: Optional[int] = None
    server_id: Optional[int] = None
    container_name: Optional[str] = None
    display_name: str
    status: str
    reason: Optional[str] = None
    percent: int
    status_eta: int
    message: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    duration: Optional[int] = None
    date_created: str
    last_updated: str
    created_by: CreatedByAndUpdatedBy
    updated_by: CreatedByAndUpdatedBy
    events: list[Event]


class ProcessList(BaseObject):
    processes: list[Process]
    meta: Meta
