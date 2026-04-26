

from enum import Enum
from typing import List

from pydantic import AnyUrl, BaseModel, ValidationError


class LogLevelEnum(str, Enum):
    none = "none"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"


class LoggingSettings(BaseModel):
    log_level: LogLevelEnum = LogLevelEnum.info


class RoutingItem(BaseModel):
    domain: List[AnyUrl]
    outbound: str
