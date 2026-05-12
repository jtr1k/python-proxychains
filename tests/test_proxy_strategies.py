import pytest

from python_proxychains.config_models import (
    PoolStrategyEnum,
    Proxy,
    ProxyPool,
    ProxyProtoEnum,
    Random,
    RoundRobin,
)


def make_proxy(tag: str, port: int) -> Proxy:
    return Proxy(
        tag=tag,
        protocol=ProxyProtoEnum.http,
        url=f"http://127.0.0.1:{port}",
    )


def test_round_robin_returns_proxies_in_order():
    strategy = RoundRobin([
        make_proxy("proxy1", 8081),
        make_proxy("proxy2", 8082),
    ])

    assert strategy.get_proxy().tag == "proxy1"
    assert strategy.get_proxy().tag == "proxy2"
    assert strategy.get_proxy().tag == "proxy1"


def test_random_returns_selected_proxy(monkeypatch):
    proxies = [
        make_proxy("proxy1", 8081),
        make_proxy("proxy2", 8082),
    ]

    monkeypatch.setattr(
        "python_proxychains.config_models.random.choice",
        lambda items: items[1],
    )

    assert Random(proxies).get_proxy().tag == "proxy2"


def test_proxy_pool_uses_round_robin_strategy():
    proxies = [
        make_proxy("proxy1", 8081),
        make_proxy("proxy2", 8082),
    ]

    pool = ProxyPool(
        tag="pool1",
        proxies=proxies,
        strategy=PoolStrategyEnum.round_robin,
    )

    assert pool.tag == "pool1"
    assert pool.proxies == proxies
    assert pool.strategy_name == PoolStrategyEnum.round_robin
    assert pool.get_proxy().tag == "proxy1"
    assert pool.get_proxy().tag == "proxy2"
    assert pool.get_proxy().tag == "proxy1"


def test_proxy_pool_rejects_empty_proxy_list():
    with pytest.raises(ValueError, match="empty"):
        ProxyPool(
            tag="pool1",
            proxies=[],
            strategy=PoolStrategyEnum.random,
        )