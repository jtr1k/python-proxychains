from .. import RoutingProxyAdapter
from ._machinery import (
    _pollute_namespace,
    _restore_namespace,
    _requests_override_request,
)

import requests
from functools import wraps


def enable_proxy(adapter: RoutingProxyAdapter):
    _pollute_namespace(_requests_override_request(adapter))


def disable_proxy():
    _restore_namespace()
