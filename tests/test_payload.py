import sys
from pathlib import Path

# main.py puts backend/ on sys.path; mirror that so game_logic and config are
# the same module instances the app uses at runtime.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from backend.main import app
import game_logic

PLACEHOLDER_URL = "/static/images/placeholder.svg"


@pytest.fixture
def jpeg_images(tmp_path, monkeypatch):
    """Image dir with only .jpeg files, so every resolved URL must fall back."""
    for value in range(1, 301):
        (tmp_path / f"{value}.jpeg").touch()
    monkeypatch.setattr(game_logic, "IMAGES_DIR", str(tmp_path))
    return tmp_path


def test_normal_quiz_option_images_resolve_jpeg(jpeg_images):
    quiz = game_logic.generate_sum_quiz(streak=0)

    assert [entry["value"] for entry in quiz["option_images"]] == quiz["options"]
    assert all(entry["url"].endswith(".jpeg") for entry in quiz["option_images"])
    assert quiz["correct_image_url"].endswith(".jpeg")


def test_reto_quiz_option_images_resolve_jpeg(jpeg_images):
    quiz = game_logic.generate_repeated_sum_quiz()

    assert [entry["value"] for entry in quiz["option_images"]] == quiz["options"]
    assert all(entry["url"].endswith(".jpeg") for entry in quiz["option_images"])
    assert quiz["correct_image_url"].endswith(".jpeg")


def test_normal_quiz_payload_is_complete():
    quiz = game_logic.generate_sum_quiz(streak=0)

    assert quiz["placeholder_url"] == PLACEHOLDER_URL
    for image in quiz["images"]:
        assert set(image) == {"value", "filename", "url"}
    for entry in quiz["option_images"]:
        assert set(entry) == {"value", "filename", "url"}
        assert entry["url"] == f"/static/images/{entry['filename']}"


def test_reto_quiz_payload_is_complete():
    quiz = game_logic.generate_repeated_sum_quiz()

    assert quiz["placeholder_url"] == PLACEHOLDER_URL
    for entry in quiz["option_images"]:
        assert set(entry) == {"value", "filename", "url"}
        assert entry["url"] == f"/static/images/{entry['filename']}"


def test_gallery_payload_carries_placeholder_url():
    data = game_logic.generate_gallery_page()

    assert data["placeholder_url"] == PLACEHOLDER_URL


def test_placeholder_is_served():
    root = Path(__file__).resolve().parent.parent

    assert (root / "static" / "images" / "placeholder.svg").is_file()

    response = TestClient(app).get(PLACEHOLDER_URL)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg")


def test_quiz_http_payload_carries_resolved_urls(jpeg_images):
    client = TestClient(app)

    response = client.get("/api/quiz/sum", headers={"X-Session-Id": "payload-seam"})

    assert response.status_code == 200
    data = response.json()
    assert data["placeholder_url"] == PLACEHOLDER_URL
    assert [entry["value"] for entry in data["option_images"]] == data["options"]
    assert all(entry["url"].endswith(".jpeg") for entry in data["option_images"])


def test_frontend_renders_payload_urls_only():
    root = Path(__file__).resolve().parent.parent

    for name in ("sum.js", "count.js"):
        source = (root / "frontend" / "js" / name).read_text(encoding="utf-8")
        assert "data:image/svg" not in source
        assert "/static/images/" not in source
        assert "placeholder_url" in source

    assert "option_images" in (root / "frontend" / "js" / "sum.js").read_text(encoding="utf-8")
