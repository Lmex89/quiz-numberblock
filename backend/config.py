import json
import os

_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.json")

DEFAULTS = {
    "COUNT_MIN": 1,
    "COUNT_MAX": 5,
    "SUM_MIN_ITEMS": 2,
    "SUM_MAX_ITEMS": 3,
    "SUM_MIN_VALUE": 1,
    "SUM_MAX_VALUE": 20,
    "SUM_TOTAL_MAX": 32,
    "SUM_BIG_THRESHOLD": 30,
    "SUM_SMALL_MIN": 1,
    "SUM_SMALL_MAX": 10,
    "TOTAL_IMAGES": 20,
}

_config = None


def _load():
    global _config
    if _config is not None:
        return
    if os.path.exists(_CONFIG_FILE):
        with open(_CONFIG_FILE) as f:
            data = json.load(f)
        _config = {**DEFAULTS, **data}
    else:
        _config = dict(DEFAULTS)


def get(key: str):
    _load()
    return _config[key]


def get_all() -> dict:
    _load()
    return dict(_config)
