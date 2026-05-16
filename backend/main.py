import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os

from session_manager import sessions
from game_logic import generate_count_quiz, generate_sum_quiz

app = FastAPI(title="Contador Dinámico de Objetos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_home():
    logger.debug("Serving home page")
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/count.html")
def serve_count():
    logger.debug("Serving count.html")
    return FileResponse(os.path.join(FRONTEND_DIR, "count.html"))


@app.get("/sum.html")
def serve_sum():
    logger.debug("Serving sum.html")
    return FileResponse(os.path.join(FRONTEND_DIR, "sum.html"))


@app.get("/css/{filepath:path}")
def serve_css(filepath: str):
    logger.debug(f"Serving CSS: {filepath}")
    return FileResponse(os.path.join(FRONTEND_DIR, "css", filepath))


@app.get("/js/{filepath:path}")
def serve_js(filepath: str):
    logger.debug(f"Serving JS: {filepath}")
    return FileResponse(os.path.join(FRONTEND_DIR, "js", filepath))


def _resolve_session(request: Request, response: Response) -> str:
    sid = request.headers.get("x-session-id") or request.cookies.get("session_id")
    new_sid = sessions.get_session_id(sid)
    if sid != new_sid:
        logger.info(f"New session: {new_sid[:8]}... (was: {sid})")
    elif sid:
        logger.debug(f"Session resolved: {sid[:8]}...")
    return new_sid


@app.get("/api/quiz/count")
def api_quiz_count(request: Request, response: Response):
    sid = _resolve_session(request, response)
    logger.info(f"Generating count quiz for session {sid[:8]}...")
    quiz = generate_count_quiz()
    sessions[sid]["last_quiz"] = quiz
    logger.info(f"Count quiz served: quantity={quiz['quantity']}, correct={quiz['correct_answer']}")
    return {"session_id": sid, **quiz}


@app.get("/api/quiz/sum")
def api_quiz_sum(request: Request, response: Response):
    sid = _resolve_session(request, response)
    logger.info(f"Generating sum quiz for session {sid[:8]}...")
    quiz = generate_sum_quiz()
    sessions[sid]["last_quiz"] = quiz
    logger.info(f"Sum quiz served: total={quiz['total_sum']}, correct={quiz['correct_answer']}")
    return {"session_id": sid, **quiz}


class VerifyRequest(BaseModel):
    game_type: str
    answer: int


@app.post("/api/verify")
def api_verify(body: VerifyRequest, request: Request, response: Response):
    sid = _resolve_session(request, response)
    session = sessions[sid]

    last = session.get("last_quiz")
    if not last or last["game_type"] != body.game_type:
        logger.warning(f"Verify mismatch: no quiz for game_type={body.game_type}, session={sid[:8]}...")
        return JSONResponse(status_code=400, content={"error": "no quiz for this game type"})

    correct = body.answer == last["correct_answer"]
    streak_key = f"streak_{body.game_type}"
    if correct:
        session[streak_key] += 1
    else:
        session[streak_key] = 0

    msg = "¡Correcto!" if correct else f"Incorrecto. La respuesta era {last['correct_answer']}"
    if correct and session[streak_key] > 1:
        msg += f" Racha: {session[streak_key]}"

    logger.info(
        f"Verify {body.game_type}: answer={body.answer}, correct={correct}, "
        f"streak={session[streak_key]}, session={sid[:8]}..."
    )

    return {
        "correct": correct,
        "correct_answer": last["correct_answer"],
        "streak": session[streak_key],
        "message": msg,
    }
