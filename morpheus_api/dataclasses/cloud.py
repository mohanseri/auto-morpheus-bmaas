from typing import Optional, Dict
from pydantic.dataclasses import dataclass
from dataclasses import field


@dataclass
class CloudCreateData:
    name: str
    code: str
    zoneType: str
    config: Optional[Dict] = field(default_factory=dict)
