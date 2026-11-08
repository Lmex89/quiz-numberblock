import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from backend import config

# Independent copy of today's shipped tuning (ticket #11 acceptance criteria).
SHIPPED_DEFAULTS = {
    "SUM_MIN_ITEMS": 2,
    "SUM_MAX_ITEMS": 2,
    "SUM_MIN_VALUE": 1,
    "SUM_MAX_VALUE": 300,
    "SUM_TOTAL_MAX": 300,
    "SUM_BIG_THRESHOLD": 15,
    "SUM_SMALL_MIN": 1,
    "SUM_SMALL_MAX": 10,
    "TOTAL_IMAGES": 300,
    "GALLERY_CONTINUOUS_MAX": 300,
    "GALLERY_EXTRAS": [],
}


def _point_config_at(tmp_path, monkeypatch, data=None):
    path = tmp_path / "config.json"
    if data is not None:
        path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(config, "_CONFIG_FILE", str(path))
    config.reload()


def test_missing_file_uses_shipped_defaults(tmp_path, monkeypatch):
    _point_config_at(tmp_path, monkeypatch)  # no config.json written

    assert config.get_all() == SHIPPED_DEFAULTS


def test_partial_file_overlays_defaults(tmp_path, monkeypatch):
    _point_config_at(tmp_path, monkeypatch, {"SUM_MAX_VALUE": 42})

    assert config.get("SUM_MAX_VALUE") == 42
    assert config.get("SUM_TOTAL_MAX") == 300


def test_unknown_key_raises_keyerror(tmp_path, monkeypatch):
    _point_config_at(tmp_path, monkeypatch, {"SUM_MAX_VALUE": 42})

    with pytest.raises(KeyError):
        config.get("NOT_A_CONFIG_KEY")


def test_reload_reflects_changed_fixture(tmp_path, monkeypatch):
    _point_config_at(tmp_path, monkeypatch, {"SUM_MAX_VALUE": 20})
    assert config.get("SUM_MAX_VALUE") == 20

    # Rewrite the same path, then drop the cache; the next read sees the new file.
    (tmp_path / "config.json").write_text(
        json.dumps({"SUM_MAX_VALUE": 40}), encoding="utf-8"
    )
    assert config.get("SUM_MAX_VALUE") == 20  # cached until reload

    config.reload()

    assert config.get("SUM_MAX_VALUE") == 40
