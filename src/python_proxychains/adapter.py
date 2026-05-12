from requests import PreparedRequest, Response
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError

from .config_models import ProxyProtoEnum
from .router import Router


class RoutingProxyAdapter(HTTPAdapter):
    def __init__(self, router: Router, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router = router

    def send(self, request: PreparedRequest, **kwargs) -> Response:
        proxy = self.router.get_proxy(request.url)

        if proxy.protocol == ProxyProtoEnum.blackhole:
            raise ConnectionError(f"Request blocked by blackhole route: {request.url}")

        if proxy.protocol == ProxyProtoEnum.freedom:
            kwargs.pop("proxies", None)
            return super().send(request, **kwargs)

        if proxy.url is None:
            raise ValueError(f"Proxy {proxy.tag} has no URL")

        proxy_url = str(proxy.url)

        kwargs["proxies"] = {
            "http": proxy_url,
            "https": proxy_url,
        }

        return super().send(request, **kwargs)

    @staticmethod
    def from_json(path: str) -> "RoutingProxyAdapter":
        return RoutingProxyAdapter(Router.from_json(path))
