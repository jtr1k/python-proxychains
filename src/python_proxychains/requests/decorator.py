from .. import RoutingProxyAdapter
from ._machinery import (
    _pollute_namespace,
    _restore_namespace,
    _requests_override_request,
)

import requests
from functools import wraps


def proxied(adapter: RoutingProxyAdapter):
    def _inner_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _pollute_namespace(_requests_override_request(adapter))
            ret = func(*args, **kwargs)
            _restore_namespace()
            return ret

        return wrapper

    return _inner_decorator
