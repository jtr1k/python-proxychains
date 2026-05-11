from .. import RoutingProxyAdapter
import requests


def _requests_override_request(adapter: RoutingProxyAdapter):
    def inner(method, url, **kwargs):
        with requests.Session() as session:
            session.mount("https://", adapter)
            return session.request(method=method, url=url, **kwargs)

    return inner


def _requests_override_method(method, request_func):
    def override(url, **kwargs):
        return request_func(method, url, **kwargs)

    return override


_methods = ("get", "options", "head", "post", "put", "patch", "delete")
_original = {k: getattr(requests, k) for k in _methods} | {"request": requests.request}


def _overrides(request_func):
    return {k: _requests_override_method(k, request_func) for k in _methods} | {
        "request": request_func
    }


def _apply_namespace(lib, namespace):
    for name, func in namespace.items():
        setattr(lib, name, func)


def _pollute_namespace(request_func):
    _apply_namespace(requests, _overrides(request_func))


def _restore_namespace():
    _apply_namespace(requests, _original)
