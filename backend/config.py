import json
import os
from loguru import logger

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
    "GALLERY_CONTINUOUS_MAX": 20,
    "GALLERY_EXTRAS": [],
}

_config = None


def _load():
    global _config
    if _config is not None:
        logger.debug("Config already loaded, skipping")
        return
    if os.path.exists(_CONFIG_FILE):
        logger.debug(f"Loading config from {_CONFIG_FILE}")
        with open(_CONFIG_FILE) as f:
            data = json.load(f)
        _config = {**DEFAULTS, **data}
        logger.info(f"Config loaded from {_CONFIG_FILE}: {len(data)} overrides applied")
    else:
        logger.warning(f"Config file {_CONFIG_FILE} not found, using defaults")
        _config = dict(DEFAULTS)
    logger.debug(f"Effective config: {_config}")


def get(key: str):
    _load()
    if key not in _config:
        logger.error(f"Config key '{key}' not found, available keys: {list(_config.keys())}")
        raise KeyError(key)
    val = _config[key]
    logger.debug(f"Config get {key}={val}")
    return val


def get_all() -> dict:
    _load()
    logger.debug(f"Config get_all returning {len(_config)} keys")
    return dict(_config)
