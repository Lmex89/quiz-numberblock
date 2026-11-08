import uuid

from loguru import logger

from game_logic import generate_repeated_sum_quiz, generate_sum_quiz


_sesiones: dict[str, dict] = {}


class ErrorSesion(Exception):
    pass


class SesionDesconocida(ErrorSesion):
    pass


class TipoDeJuegoInvalido(ErrorSesion):
    pass


class SinUltimoQuiz(ErrorSesion):
    pass


class TipoDeJuegoNoCoincide(ErrorSesion):
    pass


def _validar_tipo(game_type: str) -> None:
    if game_type != "sum":
        raise TipoDeJuegoInvalido(f"unsupported game type: {game_type}")


def _nueva_sesion() -> dict:
    return {
        "streak_sum": 0,
        "fail_count_sum": 0,
        "hito_consumido": None,
        "reto_activo": False,
        "last_quiz": None,
    }


def _normalizar(sesion: dict) -> None:
    for clave, valor in _nueva_sesion().items():
        sesion.setdefault(clave, valor)


def _resolver_sesion(session_id: str | None) -> str:
    if session_id and session_id in _sesiones:
        return session_id
    nuevo = str(uuid.uuid4())
    _sesiones[nuevo] = _nueva_sesion()
    logger.info(f"Sesión creada: {nuevo[:8]}...")
    return nuevo


def servir_quiz(session_id: str | None, game_type: str = "sum") -> tuple[str, dict]:
    _validar_tipo(game_type)
    sid = _resolver_sesion(session_id)
    sesion = _sesiones[sid]
    _normalizar(sesion)
    racha = sesion["streak_sum"]
    es_reto = racha > 0 and racha % 10 == 0 and racha != sesion["hito_consumido"]
    if es_reto:
        quiz = generate_repeated_sum_quiz()
        # game_logic todavía emite el flag heredado con otro nombre.
        quiz = {clave: valor for clave, valor in quiz.items() if not clave.endswith("_active")}
        quiz["reto_active"] = True
    else:
        quiz = generate_sum_quiz(streak=racha)
    sesion["reto_activo"] = es_reto
    sesion["last_quiz"] = quiz
    logger.info(f"Quiz servido: session={sid[:8]}..., racha={racha}, reto={es_reto}")
    return sid, quiz


def registrar_respuesta(session_id: str, game_type: str, answer: int) -> dict:
    _validar_tipo(game_type)
    sesion = _sesiones.get(session_id)
    if sesion is None:
        raise SesionDesconocida("session not found")
    _normalizar(sesion)
    ultimo = sesion["last_quiz"]
    if ultimo is None:
        raise SinUltimoQuiz("no quiz loaded, generate a quiz first")
    if ultimo["game_type"] != game_type:
        raise TipoDeJuegoNoCoincide(
            f"game type mismatch: stored '{ultimo['game_type']}', "
            f"received '{game_type}'"
        )

    correcto = answer == ultimo["correct_answer"]
    fue_reto = sesion["reto_activo"]
    racha = sesion["streak_sum"]
    fallos = sesion["fail_count_sum"]
    hito = sesion["hito_consumido"]

    if correcto:
        if fue_reto:
            racha += 2
            hito = racha - 2
        else:
            racha += 1
        fallos = 0
    else:
        fallos += 1
        if fue_reto:
            hito = racha

    if fallos >= 3:
        racha = 0
        fallos = 0
        hito = None

    sesion["streak_sum"] = racha
    sesion["fail_count_sum"] = fallos
    sesion["hito_consumido"] = hito
    sesion["reto_activo"] = False

    if correcto:
        if fue_reto:
            mensaje = "🎉 ¡Reto superado! +2 estrellas"
        else:
            mensaje = "¡Correcto!"
            if racha > 1:
                mensaje += f" Racha: {racha}"
    else:
        mensaje = f"Incorrecto. La respuesta era {ultimo['correct_answer']}"

    return {
        "correct": correcto,
        "correct_answer": ultimo["correct_answer"],
        "streak": racha,
        "message": mensaje,
        "reto_active": fue_reto,
    }


def get_summary() -> dict:
    return {
        "active_sessions": len(_sesiones),
        "session_ids": [sid[:8] + "..." for sid in _sesiones],
    }
