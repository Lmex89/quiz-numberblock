import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app
import sesion  # same top-level module main.py uses (shared state and monkeypatch target)


@pytest.fixture
def client():
    # Fresh cookie jar per test; module session storage is global.
    return TestClient(app)


def _quiz(client, sid):
    response = client.get("/api/quiz/sum", headers={"X-Session-Id": sid})
    assert response.status_code == 200
    return response.json()


def _verify(client, sid, game_type, answer):
    return client.post(
        "/api/verify",
        json={"game_type": game_type, "answer": answer},
        headers={"X-Session-Id": sid},
    )


def test_quiz_verify_round_trip(client):
    supplied = str(uuid.uuid4())

    quiz = _quiz(client, supplied)
    sid = quiz["session_id"]
    assert sid != supplied
    assert quiz["streak"] == 0
    assert "reto_active" not in quiz
    assert quiz["game_type"] == "sum"

    response = _verify(client, sid, "sum", quiz["correct_answer"])

    assert response.status_code == 200
    assert response.json() == {
        "session_id": sid,
        "correct": True,
        "correct_answer": quiz["correct_answer"],
        "streak": 1,
        "message": "¡Correcto!",
        "reto_active": False,
    }


def test_quiz_response_creates_session_and_sets_cookie(client):
    supplied = str(uuid.uuid4())

    response = client.get("/api/quiz/sum", headers={"X-Session-Id": supplied})

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] != supplied
    assert data["streak"] == 0
    assert response.cookies.get("session_id") == data["session_id"]


def test_quiz_response_creates_session_for_missing_id(client):
    response = client.get("/api/quiz/sum")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"]
    assert data["streak"] == 0
    assert response.cookies.get("session_id") == data["session_id"]


def test_reto_offered_at_hito_10_and_settled_by_correct_answer(client):
    sid = str(uuid.uuid4())

    for racha in range(10):
        quiz = _quiz(client, sid)
        sid = quiz["session_id"]
        assert quiz["streak"] == racha
        assert "reto_active" not in quiz
        verdict = _verify(client, sid, "sum", quiz["correct_answer"]).json()
        assert verdict["streak"] == racha + 1

    reto = _quiz(client, sid)
    assert reto["streak"] == 10
    assert reto["reto_active"] is True
    assert reto["base_value"] * reto["repeats"] == reto["correct_answer"]
    assert len(reto["images"]) == reto["repeats"]

    verdict = _verify(client, sid, "sum", reto["correct_answer"]).json()
    assert verdict["correct"] is True
    assert verdict["reto_active"] is True
    assert verdict["streak"] == 12
    assert verdict["message"] == "🎉 ¡Reto superado! +2 estrellas"

    siguiente = _quiz(client, sid)
    assert siguiente["streak"] == 12
    assert "reto_active" not in siguiente


def test_three_consecutive_wrong_answers_reset_streak(client):
    sid = str(uuid.uuid4())

    for racha in range(2):
        quiz = _quiz(client, sid)
        sid = quiz["session_id"]
        verdict = _verify(client, sid, "sum", quiz["correct_answer"]).json()
        assert verdict["streak"] == racha + 1

    for _ in range(3):
        quiz = _quiz(client, sid)
        sid = quiz["session_id"]
        verdict = _verify(client, sid, "sum", quiz["correct_answer"] + 1).json()
        assert verdict["correct"] is False

    assert verdict["streak"] == 0

    quiz = _quiz(client, sid)
    assert quiz["streak"] == 0
    verdict = _verify(client, sid, "sum", quiz["correct_answer"]).json()
    assert verdict["streak"] == 1


def test_verify_unknown_session_is_400_without_creating_one(client):
    antes = client.get("/api/debug").json()["active_sessions"]

    response = _verify(client, str(uuid.uuid4()), "sum", 1)

    assert response.status_code == 400
    assert response.json() == {"error": "session not found"}
    assert client.get("/api/debug").json()["active_sessions"] == antes


def test_verify_missing_session_is_400_without_creating_one(client):
    antes = client.get("/api/debug").json()["active_sessions"]

    response = client.post("/api/verify", json={"game_type": "sum", "answer": 1})

    assert response.status_code == 400
    assert response.json() == {"error": "session not found"}
    assert client.get("/api/debug").json()["active_sessions"] == antes


def test_verify_non_sum_game_type_is_400(client):
    quiz = _quiz(client, str(uuid.uuid4()))

    response = _verify(client, quiz["session_id"], "count", quiz["correct_answer"])

    assert response.status_code == 400
    assert "game type" in response.json()["error"]


def test_verify_without_quiz_is_400(client, monkeypatch):
    def explota(streak=0):
        raise RuntimeError("quiz generation failed")

    monkeypatch.setattr(sesion, "generate_sum_quiz", explota)
    failed = client.get("/api/quiz/sum")
    assert failed.status_code == 500
    sid = failed.cookies.get("session_id")
    assert sid

    response = _verify(client, sid, "sum", 1)

    assert response.status_code == 400
    assert response.json() == {"error": "no quiz loaded, generate a quiz first"}


def test_quiz_generation_failure_is_500(client, monkeypatch):
    def explota(streak=0):
        raise RuntimeError("quiz generation failed")

    monkeypatch.setattr(sesion, "generate_sum_quiz", explota)

    response = client.get("/api/quiz/sum")

    assert response.status_code == 500
    assert response.json() == {"error": "failed to generate sum quiz"}
