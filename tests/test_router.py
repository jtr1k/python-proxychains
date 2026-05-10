import pytest
from pydantic import AnyUrl

from python_proxychains.config_models import (
    Config,
    LoggingSettings,
    PoolStrategyEnum,
    Proxy,
    ProxyManager,
    ProxyPool,
    ProxyProtoEnum,
    RoutingRule,
)
from python_proxychains.router import Router


def make_proxy(tag="proxy", url="http://127.0.0.1:10808"):
    return Proxy(tag=tag, protocol=ProxyProtoEnum.socks5, url=AnyUrl(url))


def make_config(rules=None, proxies=None, pools=None):
    return Config(
        log=LoggingSettings(),
        routing_rules=rules or [],
        proxies=ProxyManager(proxies or []),
        pools=pools or [],
    )


def test_no_match_returns_direct_freedom():
    router = Router(make_config())

    proxy = router.get_proxy("https://example.com")

    assert proxy.tag == "direct"
    assert proxy.protocol == ProxyProtoEnum.freedom
    assert proxy.url is None


def test_domain_rule_returns_proxy_from_pool():
    proxy = make_proxy("main")
    pool = ProxyPool("out", [proxy], PoolStrategyEnum.round_robin)
    rule = RoutingRule.from_args(domain=[r".*\.com$"], outbound="out")

    router = Router(make_config([rule], [proxy], [pool]))

    assert router.get_proxy("https://example.com").tag == "main"


def test_blackhole_outbound():
    rule = RoutingRule.from_args(domain=[r".*blocked\.com$"], outbound="blackhole")
    router = Router(make_config([rule]))

    proxy = router.get_proxy("https://blocked.com")

    assert proxy.tag == "blackhole"
    assert proxy.protocol == ProxyProtoEnum.blackhole
    assert proxy.url is None


def test_direct_and_freedom_outbound_are_freedom():
    direct_rule = RoutingRule.from_args(domain=[r"direct\.com"], outbound="direct")
    freedom_rule = RoutingRule.from_args(domain=[r"free\.com"], outbound="freedom")

    router = Router(make_config([direct_rule, freedom_rule]))

    assert router.get_proxy("https://direct.com").protocol == ProxyProtoEnum.freedom
    assert router.get_proxy("https://free.com").protocol == ProxyProtoEnum.freedom


def test_missing_outbound_pool_raises_key_error():
    rule = RoutingRule.from_args(domain=[r".*example\.com$"], outbound="missing")
    router = Router(make_config([rule]))

    with pytest.raises(KeyError, match="missing"):
        router.get_proxy("https://example.com")