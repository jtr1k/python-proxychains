from requests import PreparedRequest, Response
from requests.adapters import HTTPAdapter

from .router import Router


class RoutingProxyAdapter(HTTPAdapter):

    def __init__(self, router: Router):
        self.router = router

    def send(self, request: PreparedRequest, **kwargs) -> Response:

        proxy = router.get_proxy(request.url).url

        kwargs["proxies"] = {"https://": proxy, "http://": proxy}
        return super().send(request, **kwargs)
