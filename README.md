# pyproxychains

... потому что иногда нужно, чтобы запросы просто начали проходить.

## Интерфейс

```py
from python_proxychains import RoutingProxyAdapter

adapter = RoutingProxyAdapter.from_json("config.json")

# Decorator API
from python_proxychains.requests import proxied

import requests

@proxied(adapter)
def make_request():
    return requests.get("https://example.com")

make_request()
```

Больше примеров в [examples](./examples).

## Конфигурация

```json
{
    "log": {
        "loglevel": "info"
    },
    "routing": [
        {
            "domain": [
                ".*\\.ru"
            ],
            "outbound": "direct"
        }
    ],
    "proxies": [
        {
            "tag": "proxy1",
            "protocol": "socks5",
            "url": "socks5://localhost:10808"
        },
        {
            "tag": "direct",
            "protocol": "freedom"
        }
    ],
    "pools": [
        {
            "tag": "pool1",
            "proxies": [
                "proxy1",
            ],
            "strategy": "RoundRobin"
        }
    ]
}
```

## Разработка и тестирование

```bash
# Сборка библиотеки
uv build

# Запуск форматтеров
uv run black
uv run isort

# Тестирование
uv run pytest

# Проверка покрытия
uv run coverage run -m pytest
uv run coverage report
```


## Участники

Проект выполняется Лагутиным Георгием и Заборовым Егором.
