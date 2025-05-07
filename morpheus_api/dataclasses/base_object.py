from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# All dataclasses must extend from this object for conversion from snake_case to camelCase
class BaseObject(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
