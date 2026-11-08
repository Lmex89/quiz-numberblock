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

import sesion
from game_logic import generate_gallery_page

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


@app.get("/galeria.html")
def serve_galeria():
    path = os.path.join(FRONTEND_DIR, "galeria.html")
    logger.debug(f"Serving galeria page: {path}")
    if not os.path.isfile(path):
        logger.error(f"Galeria page not found: {path}")
        return JSONResponse(status_code=404, content={"error": "galeria page not found"})
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


def _provided_session_id(request: Request) -> str | None:
    sid = request.headers.get("x-session-id") or request.cookies.get("session_id")
    logger.debug(f"Provided session_id={sid[:20] if sid else None}")
    return sid


def _set_session_cookie(response: Response, sid: str) -> None:
    response.set_cookie(key="session_id", value=sid, httponly=False)


@app.get("/api/gallery")
def api_gallery(page: int = 1, per_page: int = 50):
    logger.debug(f"Gallery request: page={page}, per_page={per_page}")
    data = generate_gallery_page(page, per_page)
    logger.debug(f"Gallery response: page={data['page']}/{data['total_pages']}, images={len(data['images'])}")
    return data


@app.get("/api/quiz/sum")
def api_quiz_sum(request: Request, response: Response):
    provided = _provided_session_id(request)
    # Resolve before generating so a generation failure can still set the cookie.
    sid = sesion.resolver_sesion(provided)
    _set_session_cookie(response, sid)
    logger.info(f"Generating sum quiz for session {sid[:8]}...")
    try:
        _, quiz, racha = sesion.servir_quiz(sid, "sum")
    except Exception as e:
        logger.error(f"Failed to generate sum quiz: {e}\n{traceback.format_exc()}")
        fallo = JSONResponse(status_code=500, content={"error": "failed to generate sum quiz"})
        _set_session_cookie(fallo, sid)
        return fallo
    logger.info(f"Sum quiz served: total={quiz['total_sum']}, correct={quiz['correct_answer']}, options={quiz['options']}, images={[img['value'] for img in quiz['images']]}")
    return {"session_id": sid, "streak": racha, **quiz}


@app.get("/api/debug")
def api_debug():
    summary = sesion.get_summary()
    logger.debug(f"Debug endpoint: {summary}")
    return summary


class VerifyRequest(BaseModel):
    game_type: str
    answer: int


@app.post("/api/verify")
def api_verify(body: VerifyRequest, request: Request, response: Response):
    sid = _provided_session_id(request)
    logger.debug(f"Verify request: session={sid[:8] if sid else None}..., game_type={body.game_type}, answer={body.answer}")
    try:
        veredicto = sesion.registrar_respuesta(sid, body.game_type, body.answer)
    except sesion.ErrorSesion as e:
        logger.error(f"Verify rejected: {e}, session={sid[:8] if sid else None}...")
        return JSONResponse(status_code=400, content={"error": str(e)})

    _set_session_cookie(response, sid)
    logger.info(
        f"Verify {body.game_type}: answer={body.answer}, correct={veredicto['correct']}, "
        f"reto={veredicto['reto_active']}, correct_answer={veredicto['correct_answer']}, "
        f"streak={veredicto['streak']}, session={sid[:8]}..."
    )

    return {"session_id": sid, **veredicto}
