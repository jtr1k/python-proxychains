from python_proxychains import RoutingProxyAdapter

from requests import Session

s = Session()
adapter = RoutingProxyAdapter.from_json("config.json")

s.mount("https://", adapter)

s.get("https://2ip.ru")
s.get("https://ip.ipapi.is")
