from .config import RoutingRule, Config, Proxy

import urllib
import ipaddress
import re
import socket

class Router:
    def __init__(self, config: Config):
        self.config = config

    def get_proxy(self, url: str) -> Proxy:
        pass
        
