from urllib.parse import urlsplit

from .config_models import Config, Proxy, ProxyProtoEnum


class BlackholeError(ConnectionError):
    pass


class Router:
    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def _extract_host(url: str) -> str:
        parsed = urlsplit(url)
        host = parsed.hostname

        if host is None:
            parsed = urlsplit(f"//{url}")
            host = parsed.hostname

        if not host:
            raise ValueError(f"Cannot extract hostname from URL: {url}")

        return host.lower()

    def get_proxy(self, url: str) -> Proxy:
        host = self._extract_host(url)
        outbound = "direct"

        for rule in self.config.get_rules():
            if rule.match(host):
                outbound = rule.outbound
                break

        if outbound in {"direct", "freedom"}:
            return Proxy(
                tag=outbound,
                protocol=ProxyProtoEnum.freedom,
                url=None,
            )

        if outbound == "blackhole":
            return Proxy(
                tag=outbound,
                protocol=ProxyProtoEnum.blackhole,
                url=None,
            )

        return self.config.get_outbound_proxy(outbound)
        