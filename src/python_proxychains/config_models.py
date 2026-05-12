from enum import Enum
from typing import Annotated, Optional, Pattern

import ipaddress
import json
import random
import re
import socket

from pydantic import AnyUrl, BaseModel, BeforeValidator, Field, model_validator
from pydantic.networks import IPvAnyNetwork
from pydantic_extra_types.country import CountryAlpha2


class LogLevelEnum(str, Enum):
    none = "none"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"


class LoggingSettings(BaseModel):
    log_level: LogLevelEnum = Field(
        default=LogLevelEnum.info,
        alias="loglevel",
    )


def compile_regex(value: str | Pattern[str]) -> Pattern[str]:
    if isinstance(value, re.Pattern):
        return value

    try:
        return re.compile(value)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}") from e


def wrap_country_code(value) -> str:
    return str(CountryAlpha2(value))


def wrap_ip_network(value):
    return ipaddress.ip_network(str(IPvAnyNetwork(value)))


CompiledRegex = Annotated[Pattern[str], BeforeValidator(compile_regex)]
CountryCode = Annotated[str, BeforeValidator(wrap_country_code)]
IpNetwork = Annotated[ipaddress.IPv4Network, BeforeValidator(wrap_ip_network)]


class RoutingRule(BaseModel):
    domain: Optional[list[CompiledRegex]] = None
    geoip: Optional[list[CountryCode]] = None
    ip: Optional[list[IpNetwork]] = None
    outbound: str

    @staticmethod
    def from_args(
        domain: list[str] | None = None,
        ip: list[str] | None = None,
        geoip: list[str] | None = None,
        outbound: str = "direct",
    ) -> "RoutingRule":
        return RoutingRule(
            domain=[compile_regex(domain_re) for domain_re in domain or []],
            ip=[wrap_ip_network(ip_rule) for ip_rule in ip or []],
            geoip=[wrap_country_code(country) for country in geoip or []],
            outbound=outbound,
        )

    @staticmethod
    def from_dict(rule: dict) -> "RoutingRule":
        return RoutingRule.from_args(
            domain=rule.get("domain", []),
            ip=rule.get("ip", []),
            geoip=rule.get("geoip", []),
            outbound=rule.get("outbound", "direct"),
        )

    def match(self, domain: str) -> bool:
        for domain_re in self.domain or []:
            if re.search(domain_re, domain):
                return True

        try:
            ip = ipaddress.ip_address(socket.gethostbyname(domain))
        except socket.gaierror:
            return False

        for ip_rule in self.ip or []:
            if ip in ip_rule:
                return True

        return False


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

    @staticmethod
    def from_dict(proxy: dict) -> "Proxy":
        return Proxy(
            tag=proxy["tag"],
            protocol=proxy["protocol"],
            url=proxy.get("url"),
        )


class PoolStrategyEnum(str, Enum):
    round_robin = "RoundRobin"
    random = "Random"
    custom = "Custom"


class ProxyPoolModel(BaseModel):
    tag: str
    proxies: list[str]
    strategy: PoolStrategyEnum


class ConfigModel(BaseModel):
    log: LoggingSettings
    routing: list[RoutingRule]
    proxies: list[Proxy]
    pools: list[ProxyPoolModel]

    @model_validator(mode="after")
    def finalize_config(self) -> "ConfigModel":
        proxy_tags = {proxy.tag for proxy in self.proxies}

        for pool in self.pools:
            for tag in pool.proxies:
                if tag not in proxy_tags:
                    raise ValueError(
                        f"ProxyPool {pool.tag} references a non-existent proxy {tag}"
                    )

        pool_tags = {pool.tag for pool in self.pools}

        for proxy in self.proxies:
            if proxy.tag in pool_tags:
                raise ValueError(f"Name collision of proxy and pool {proxy.tag}")

            self.pools.append(
                ProxyPoolModel(
                    tag=proxy.tag,
                    proxies=[proxy.tag],
                    strategy=PoolStrategyEnum.round_robin,
                )
            )

        return self


class ProxyManager:
    def __init__(self, proxies: list[Proxy] | None = None):
        self._proxies: dict[str, Proxy] = {}

        for proxy in proxies or []:
            self.add(proxy)

    def add(self, proxy: Proxy) -> None:
        if proxy.tag in self._proxies:
            raise ValueError(f"Proxy with tag '{proxy.tag}' already exists")

        self._proxies[proxy.tag] = proxy

    def get(self, tag: str) -> Proxy:
        if tag not in self._proxies:
            raise KeyError(f"Proxy with tag '{tag}' not found")

        return self._proxies[tag]

    def find(self, tag: str) -> Proxy | None:
        return self._proxies.get(tag)

    def has(self, tag: str) -> bool:
        return tag in self._proxies

    def remove(self, tag: str) -> Proxy:
        if tag not in self._proxies:
            raise KeyError(f"Proxy with tag '{tag}' not found")

        return self._proxies.pop(tag)

    def list(self) -> list[Proxy]:
        return list(self._proxies.values())

    def tags(self) -> list[str]:
        return list(self._proxies.keys())

    def __contains__(self, tag: str) -> bool:
        return self.has(tag)

    def __getitem__(self, tag: str) -> Proxy:
        return self.get(tag)

    def __len__(self) -> int:
        return len(self._proxies)


class ProxyStrategy:
    def __init__(self, proxies: list[Proxy]):
        if not proxies:
            raise ValueError("Proxy list is empty")

        self.proxies = proxies

    def get_proxy(self) -> Proxy:
        raise NotImplementedError


class Random(ProxyStrategy):
    def get_proxy(self) -> Proxy:
        return random.choice(self.proxies)


class RoundRobin(ProxyStrategy):
    def __init__(self, proxies: list[Proxy]):
        super().__init__(proxies)
        self.index = 0

    def get_proxy(self) -> Proxy:
        proxy = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        return proxy


class ProxyPool:
    def __init__(
        self,
        tag: str,
        proxies: list[Proxy],
        strategy: PoolStrategyEnum,
    ):
        self.tag = tag
        self.proxies = proxies
        self.strategy_name = strategy

        match strategy:
            case PoolStrategyEnum.round_robin:
                self.strategy = RoundRobin(proxies)
            case PoolStrategyEnum.random:
                self.strategy = Random(proxies)
            case PoolStrategyEnum.custom:
                raise NotImplementedError("Custom strategy is not implemented yet")
            case _:
                raise ValueError(f"Unknown proxy pool strategy: {strategy}")

    def get_proxy(self) -> Proxy:
        return self.strategy.get_proxy()


class Config:
    def __init__(
        self,
        log: LoggingSettings,
        routing_rules: list[RoutingRule],
        proxies: ProxyManager,
        pools: list[ProxyPool],
    ):
        self.log = log
        self.routing_rules = routing_rules
        self.proxies = proxies
        self.pools: dict[str, ProxyPool] = {}

        for pool in pools:
            if pool.tag in self.pools:
                raise ValueError(f"Duplicate proxy pool tag: {pool.tag}")

            self.pools[pool.tag] = pool

    def get_rules(self) -> list[RoutingRule]:
        return self.routing_rules

    def get_proxy(self, tag: str) -> Proxy:
        return self.proxies.get(tag)

    def get_proxy_pool(self, tag: str) -> ProxyPool:
        if tag not in self.pools:
            raise KeyError(f"Proxy pool with tag '{tag}' not found")

        return self.pools[tag]

    def get_outbound_proxy(self, tag: str) -> Proxy:
        return self.get_proxy_pool(tag).get_proxy()

    @staticmethod
    def from_json(path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as file:
            raw_json = file.read()

        model = ConfigModel.model_validate_json(raw_json)
        raw_config = json.loads(raw_json)

        routing_rules = [
            RoutingRule.from_dict(rule)
            for rule in raw_config.get("routing", [])
        ]

        proxies = [
            Proxy.from_dict(proxy)
            for proxy in raw_config.get("proxies", [])
        ]

        proxy_manager = ProxyManager(proxies)

        pools: list[ProxyPool] = []

        for pool_model in model.pools:
            pool_proxies = [
                proxy_manager.get(proxy_tag)
                for proxy_tag in pool_model.proxies
            ]

            pools.append(
                ProxyPool(
                    tag=pool_model.tag,
                    proxies=pool_proxies,
                    strategy=pool_model.strategy,
                )
            )

        return Config(
            log=model.log,
            routing_rules=routing_rules,
            proxies=proxy_manager,
            pools=pools,
        )