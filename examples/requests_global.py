from python_proxychains import RoutingProxyAdapter
from python_proxychains.requests import enable_proxy, disable_proxy

import requests

adapter = RoutingProxyAdapter.from_json("config.json")

enable_proxy(adapter)


def make_request():
    return requests.get("https://2ip.ru", headers={"User-Agent": "curl/7.5.4"}).text


print(make_request())

disable_proxy()

print(make_request())
