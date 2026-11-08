import json
import sys
from pathlib import Path

# main.py puts backend/ on sys.path; mirror that so game_logic and config are
# the same module instances the app uses at runtime.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import pytest

import config
import game_logic


@pytest.fixture
def load_config(tmp_path, monkeypatch):
    def _load(overrides):
        path = tmp_path / "config.json"
        path.write_text(json.dumps(overrides), encoding="utf-8")
        monkeypatch.setattr(config, "_CONFIG_FILE", str(path))
        config.reload()

    yield _load
    config.reload()


def test_sum_quiz_honors_tuned_limits(load_config):
    load_config({
        "SUM_MAX_VALUE": 6,
        "SUM_TOTAL_MAX": 8,
        "SUM_BIG_THRESHOLD": 4,
        "SUM_SMALL_MIN": 1,
        "SUM_SMALL_MAX": 2,
    })

    for _ in range(100):
        quiz = game_logic.generate_sum_quiz(streak=0)
        values = [img["value"] for img in quiz["images"]]

        assert all(1 <= v <= 6 for v in values)
        assert quiz["total_sum"] == sum(values)
        assert quiz["total_sum"] <= 8
        if values[0] > 4:
            assert 1 <= values[1] <= 2
        if values[1] > 4:
            assert 1 <= values[0] <= 2


def test_gallery_honors_tuned_continuous_max(load_config):
    load_config({"GALLERY_CONTINUOUS_MAX": 5, "GALLERY_EXTRAS": []})

    data = game_logic.generate_gallery_page()

    assert data["total"] == 5
    assert [img["value"] for img in data["images"]] == [1, 2, 3, 4, 5]


def test_repeated_quiz_reads_tuned_total_max(load_config):
    load_config({"SUM_TOTAL_MAX": 75})

    for _ in range(100):
        quiz = game_logic.generate_repeated_sum_quiz()
        distractors = [o for o in quiz["options"] if o != quiz["correct_answer"]]

        assert quiz["total_sum"] == quiz["base_value"] * quiz["repeats"]
        assert all(o <= 75 for o in distractors)


def test_shipped_config_generation_unchanged():
    config.reload()  # discard any fixture tuning before reading config.json

    for _ in range(200):
        quiz = game_logic.generate_sum_quiz(streak=0)
        values = [img["value"] for img in quiz["images"]]

        assert set(quiz) == {
            "game_type",
            "images",
            "total_sum",
            "options",
            "correct_answer",
            "correct_image_url",
        }
        assert len(values) == 2
        assert all(1 <= v <= 300 for v in values)
        assert quiz["total_sum"] == sum(values) <= 300
        assert len(quiz["options"]) == 3
        assert quiz["correct_answer"] in quiz["options"]
        if values[0] > 15:
            assert 1 <= values[1] <= 10
        if values[1] > 15:
            assert 1 <= values[0] <= 10
