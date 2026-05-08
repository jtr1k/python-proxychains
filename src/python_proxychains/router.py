from .config import RoutingRule, Config, Proxy

import urllib
import ipaddress
import re
import socket

class Router:
    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def match_rule(domain: str, rule: RoutingRule) -> bool:
        for domain_re in rule.domain:
            if re.search(domain_re, domain):
                return True

        ip = ipaddress.ip_address(socket.gethostbyname(domain))

        for ip_rule in rule.ip:
            if ip in ip_rule:
                return True

        # TODO geoip

        return False


    def get_proxy(self, url: str) -> Proxy:
        
