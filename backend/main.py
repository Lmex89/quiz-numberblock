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
import traceback

from session_manager import sessions
from game_logic import generate_count_quiz, generate_sum_quiz

logger.info("Starting quiz app backend")
logger.debug(f"Python version: {sys.version}")
logger.debug(f"Working directory: {os.getcwd()}")
logger.debug(f"Backend dir: {os.path.dirname(__file__)}")

app = FastAPI(title="Contador Dinámico de Objetos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("CORS middleware configured: allow all origins, methods, headers")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
logger.debug(f"Frontend dir: {FRONTEND_DIR}")
logger.debug(f"Static dir: {STATIC_DIR}")

if not os.path.isdir(FRONTEND_DIR):
    logger.error(f"Frontend directory not found at {FRONTEND_DIR}")
if not os.path.isdir(STATIC_DIR):
    logger.error(f"Static directory not found at {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
logger.info("Static files mounted at /static")


@app.get("/")
def serve_home():
    path = os.path.join(FRONTEND_DIR, "index.html")
    logger.debug(f"Serving home page: {path}")
    if not os.path.isfile(path):
        logger.error(f"Home page not found: {path}")
        return JSONResponse(status_code=404, content={"error": "home page not found"})
    return FileResponse(path)


@app.get("/count.html")
def serve_count():
    path = os.path.join(FRONTEND_DIR, "count.html")
    logger.debug(f"Serving count page: {path}")
    if not os.path.isfile(path):
        logger.error(f"Count page not found: {path}")
        return JSONResponse(status_code=404, content={"error": "count page not found"})
    return FileResponse(path)


@app.get("/sum.html")
def serve_sum():
    path = os.path.join(FRONTEND_DIR, "sum.html")
    logger.debug(f"Serving sum page: {path}")
    if not os.path.isfile(path):
        logger.error(f"Sum page not found: {path}")
        return JSONResponse(status_code=404, content={"error": "sum page not found"})
    return FileResponse(path)


@app.get("/css/{filepath:path}")
def serve_css(filepath: str):
    path = os.path.join(FRONTEND_DIR, "css", filepath)
    logger.debug(f"Serving CSS: {filepath} -> {path}")
    if not os.path.isfile(path):
        logger.warning(f"CSS file not found: {path}")
        return JSONResponse(status_code=404, content={"error": f"css not found: {filepath}"})
    return FileResponse(path)


@app.get("/js/{filepath:path}")
def serve_js(filepath: str):
    path = os.path.join(FRONTEND_DIR, "js", filepath)
    logger.debug(f"Serving JS: {filepath} -> {path}")
    if not os.path.isfile(path):
        logger.warning(f"JS file not found: {path}")
        return JSONResponse(status_code=404, content={"error": f"js not found: {filepath}"})
    return FileResponse(path)


def _resolve_session(request: Request, response: Response) -> str:
    sid = request.headers.get("x-session-id") or request.cookies.get("session_id")
    logger.debug(f"Resolving session: provided session_id={sid[:20] if sid else None}")
    new_sid = sessions.get_session_id(sid)
    if sid != new_sid:
        logger.info(f"New session created: {new_sid[:8]}... (was: {sid[:20] if sid else None})")
    elif sid:
        logger.debug(f"Session resolved: {sid[:8]}...")
    response.set_cookie(key="session_id", value=new_sid, httponly=False)
    logger.debug(f"Session cookie set: {new_sid[:8]}...")
    return new_sid


@app.get("/api/quiz/count")
def api_quiz_count(request: Request, response: Response):
    sid = _resolve_session(request, response)
    logger.info(f"Generating count quiz for session {sid[:8]}...")
    try:
        quiz = generate_count_quiz()
    except Exception as e:
        logger.error(f"Failed to generate count quiz: {e}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"error": "failed to generate count quiz"})
    sessions[sid]["last_quiz"] = quiz
    logger.info(f"Count quiz served: quantity={quiz['quantity']}, correct={quiz['correct_answer']}, options={quiz['options']}")
    return {"session_id": sid, **quiz}


@app.get("/api/quiz/sum")
def api_quiz_sum(request: Request, response: Response):
    sid = _resolve_session(request, response)
    logger.info(f"Generating sum quiz for session {sid[:8]}...")
    try:
        quiz = generate_sum_quiz()
    except Exception as e:
        logger.error(f"Failed to generate sum quiz: {e}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"error": "failed to generate sum quiz"})
    sessions[sid]["last_quiz"] = quiz
    logger.info(f"Sum quiz served: total={quiz['total_sum']}, correct={quiz['correct_answer']}, options={quiz['options']}, images={[img['value'] for img in quiz['images']]}")
    return {"session_id": sid, **quiz}


@app.get("/api/debug")
def api_debug():
    summary = sessions.get_summary()
    logger.debug(f"Debug endpoint: {summary}")
    return summary


class VerifyRequest(BaseModel):
    game_type: str
    answer: int


@app.post("/api/verify")
def api_verify(body: VerifyRequest, request: Request, response: Response):
    sid = _resolve_session(request, response)
    logger.debug(f"Verify request: session={sid[:8]}..., game_type={body.game_type}, answer={body.answer}")

    try:
        session = sessions[sid]
    except KeyError as e:
        logger.error(f"Session not found: {e}, session={sid[:8]}...")
        return JSONResponse(status_code=400, content={"error": "session not found"})

    last = session.get("last_quiz")
    if last is None:
        logger.error(f"Verify called with no last_quiz: session={sid[:8]}..., game_type={body.game_type}, answer={body.answer}")
        return JSONResponse(status_code=400, content={"error": "no quiz loaded, generate a quiz first"})

    if last["game_type"] != body.game_type:
        logger.error(f"Verify game_type mismatch: stored={last['game_type']}, received={body.game_type}, session={sid[:8]}...")
        return JSONResponse(status_code=400, content={"error": f"game type mismatch: stored '{last['game_type']}', received '{body.game_type}'"})

    stored_correct = last["correct_answer"]
    correct = body.answer == stored_correct
    logger.debug(f"Verify comparison: answer={body.answer}, stored_correct={stored_correct}, correct={correct}")

    streak_key = f"streak_{body.game_type}"
    fail_key = f"fail_count_{body.game_type}"
    session.setdefault(streak_key, 0)
    session.setdefault(fail_key, 0)
    if correct:
        session[streak_key] += 1
        session[fail_key] = 0
        logger.debug(f"Answer correct, streak={session[streak_key]}")
    else:
        session[fail_key] += 1
        logger.debug(f"Answer incorrect, fail_count={session[fail_key]}")
        if session[fail_key] >= 3:
            session[streak_key] = 0
            session[fail_key] = 0
            logger.info(f"3 consecutive failures, streak reset for session {sid[:8]}...")

    msg = "¡Correcto!" if correct else f"Incorrecto. La respuesta era {stored_correct}"
    if correct and session[streak_key] > 1:
        msg += f" Racha: {session[streak_key]}"

    logger.info(
        f"Verify {body.game_type}: answer={body.answer}, correct={correct}, "
        f"correct_answer={stored_correct}, streak={session[streak_key]}, "
        f"fails={session[fail_key]}, session={sid[:8]}..."
    )

    return {
        "session_id": sid,
        "correct": correct,
        "correct_answer": stored_correct,
        "streak": session[streak_key],
        "message": msg,
    }
