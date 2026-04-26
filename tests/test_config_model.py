import pytest

from python_proxychains.config_models import ConfigModel

SAMPLE_CONFIG = "tests/sample_config.json"


def test_whole_config():
    json_data = open(SAMPLE_CONFIG).read()

    ConfigModel.model_validate_json(json_data)
