from python_proxychains import RoutingProxyAdapter
from python_proxychains.requests import proxied

adapter = RoutingProxyAdapter.from_json("config.json")


@proxied(adapter)
def make_request():
    import requests

    return requests.get("https://2ip.ru", headers={"User-Agent": "curl/7.5.4"}).text


print(make_request())
