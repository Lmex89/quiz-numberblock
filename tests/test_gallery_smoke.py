import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_gallery_payload_shape():
    response = client.get("/api/gallery")

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"images", "placeholder_url", "page", "per_page", "total", "total_pages"}
    assert data["page"] >= 1
    assert data["per_page"] >= 1
    assert data["total"] >= 1
    assert data["total_pages"] >= 1
    assert 0 < len(data["images"]) <= data["per_page"]

    for image in data["images"]:
        assert set(image) == {"value", "filename", "url"}
        assert isinstance(image["value"], int)
        assert image["filename"].endswith((".jpg", ".jpeg"))
        assert image["url"].startswith("/static/images/")
