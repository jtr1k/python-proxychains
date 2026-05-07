import pytest

from python_proxychains.config_models import PoolStrategyEnum, Proxy, ProxyProtoEnum
from python_proxychains.proxy import ProxyPool, Random, RoundRobin


def p(tag, port):
    return Proxy(tag=tag, protocol=ProxyProtoEnum.http, url=f"http://127.0.0.1:{port}")


def test_round_robin_strategy():
    s = RoundRobin([p("p1", 8081), p("p2", 8082)])

    assert [s.get_proxy().tag for _ in range(3)] == ["p1", "p2", "p1"]


def test_random_strategy(monkeypatch):
    proxies = [p("p1", 8081), p("p2", 8082)]
    monkeypatch.setattr("python_proxychains.proxy.random.choice", lambda items: items[1])

    assert Random(proxies).get_proxy().tag == "p2"


def test_proxy_pool_round_robin_and_stores_proxy_objects():
    proxies = [p("p1", 8081), p("p2", 8082)]
    pool = ProxyPool("pool", proxies, PoolStrategyEnum.round_robin)

    assert pool.proxies == proxies
    assert [pool.get_proxy().tag for _ in range(3)] == ["p1", "p2", "p1"]


def test_empty_proxy_list_is_invalid():
    with pytest.raises(ValueError, match="empty"):
        ProxyPool("pool", [], PoolStrategyEnum.random)