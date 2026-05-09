from python_proxychains.config_models import LogLevelEnum, ProxyProtoEnum, Config

SAMPLE_CONFIG = "sample_config.json"


def test_config_from_json_loads_basic_fields():
    config = Config.from_json(SAMPLE_CONFIG)

    assert config.log.log_level == LogLevelEnum.info
    assert len(config.get_rules()) == 2


def test_config_from_json_loads_proxies():
    config = Config.from_json(SAMPLE_CONFIG)

    assert config.get_proxy("proxy1").protocol == ProxyProtoEnum.socks5
    assert config.get_proxy("direct").protocol == ProxyProtoEnum.freedom
    assert config.get_proxy("block").protocol == ProxyProtoEnum.blackhole


def test_config_from_json_loads_pool():
    config = Config.from_json(SAMPLE_CONFIG)

    pool = config.get_proxy_pool("pool1")

    assert pool.tag == "pool1"
    assert [proxy.tag for proxy in pool.proxies] == ["proxy1", "proxy2"]


def test_config_get_outbound_proxy_uses_pool_strategy():
    config = Config.from_json(SAMPLE_CONFIG)

    assert config.get_outbound_proxy("pool1").tag == "proxy1"
    assert config.get_outbound_proxy("pool1").tag == "proxy2"
    assert config.get_outbound_proxy("pool1").tag == "proxy1"