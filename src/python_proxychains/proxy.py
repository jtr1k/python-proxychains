import random
from typing import List

from .config_models import PoolStrategyEnum, Proxy


class ProxyStrategy:
    def __init__(self, proxies: List[Proxy]):
        if not proxies:
            raise ValueError("Proxy list is empty")
        self.proxies = proxies

    def get_proxy(self) -> Proxy:
        raise NotImplementedError


class Random(ProxyStrategy):
    def get_proxy(self) -> Proxy:
        return random.choice(self.proxies)


class RoundRobin(ProxyStrategy):
    def __init__(self, proxies: List[Proxy]):
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
        proxies: List[Proxy],
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