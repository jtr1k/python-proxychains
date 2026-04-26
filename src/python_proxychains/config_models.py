import re
from enum import Enum
from typing import Annotated, List, Optional, Pattern

from pydantic import (
    AnyUrl,
    BaseModel,
    BeforeValidator,
    ValidationError,
    model_validator,
)
from pydantic_extra_types.country import CountryAlpha2


class LogLevelEnum(str, Enum):
    none = "none"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"


class LoggingSettings(BaseModel):
    log_level: LogLevelEnum = LogLevelEnum.info


def compile_regex(value: str | Pattern[str]) -> Pattern[str]:
    if isinstance(value, re.Pattern):
        return value

    try:
        return re.compile(value)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}") from e


CompiledRegex = Annotated[Pattern[str], BeforeValidator(compile_regex)]


class RoutingRule(BaseModel):
    domain: Optional[List[CompiledRegex]] = None
    geoip: Optional[List[CountryAlpha2]] = None
    outbound: str


class ProxyProtoEnum(str, Enum):
    socks5 = "socks5"
    socks5h = "socks5h"
    http = "http"
    freedom = "freedom"
    blackhole = "blackhole"


class Proxy(BaseModel):
    tag: str
    protocol: ProxyProtoEnum
    url: Optional[AnyUrl] = None


class PoolStrategyEnum(str, Enum):
    round_robin = "RoundRobin"
    random = "Random"


class ProxyPoolModel(BaseModel):
    tag: str
    proxies: List[str]
    strategy: PoolStrategyEnum


class ConfigModel(BaseModel):
    log: LoggingSettings
    routing: List[RoutingRule]
    proxies: List[Proxy]
    pools: List[ProxyPoolModel]

    @model_validator(mode="after")
    def finalize_config(value: ConfigModel) -> ConfigModel:
        proxy_tags = {i.tag for i in value.proxies}

        for pool in value.pools:
            for tag in pool.proxies:
                if tag not in proxy_tags:
                    raise ValueError(
                        f"ProxyPool {pool.tag} references a non-existent proxy {tag}"
                    )

        pool_tags = {i.tag for i in value.pools}

        for proxy in value.proxies:
            if proxy.tag in pool_tags:
                raise ValueError(f"Name collision of proxy and pool {proxy.tag}")

            value.pools.append(
                ProxyPoolModel(
                    tag=proxy.tag,
                    proxies=[proxy.tag],
                    strategy=PoolStrategyEnum.round_robin,
                )
            )

        return value
