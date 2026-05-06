from .config_models import Proxy, ProxyStrategyModel

class ProxyStrategy:
    def __init__(self, proxies: List[Proxy]):
        self.proxies = proxies

class Random(ProxyStrategy):
    def get_proxy():
        return random.choice(self.proxies)

class RoundRobin(ProxyStrategyModel):
    def __init__(self, proxies):
        self.index = 0
        super().__init__(proxies)

    def get_proxy():
        self.index = (self.index + 1) % len(self.proxies)
        return self.proxies[self.index]

class ProxyPool(ProxyPoolModel):
    def __init__(self, tag: str, proxies: List[Proxy], strategy: PoolStrategyEnum, custom_strategy=None):
        super().__init__(tag, proxies, strategy)
        match strategy:
            case PoolStrategyEnum.round_robin:
                self.strategy = RoundRobin(proxies)
            case PoolStrategyEnum.random:
                self.strategy = Random(proxies)
            case PoolStrategyEnum.custom:
                self.strategy = custom_strategy(proxies)

    def get_proxy(self, tag: str) -> Proxy:
        return self.strategy.get_proxy()

