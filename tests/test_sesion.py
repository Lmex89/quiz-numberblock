import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import sesion


def _servir(session_id=None, game_type="sum"):
    sid, quiz, _ = sesion.servir_quiz(session_id, game_type)
    return sid, quiz


def _estado(session_id):
    return sesion._sesiones[session_id]


def test_nueva_sesion_tiene_solo_claves_fijas():
    sid, quiz = _servir()

    assert _estado(sid) == {
        "streak_sum": 0,
        "fail_count_sum": 0,
        "hito_consumido": None,
        "reto_activo": False,
        "last_quiz": quiz,
    }
    assert quiz["game_type"] == "sum"


def test_respuesta_correcta_normal():
    sid, quiz = _servir()

    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])

    assert veredicto == {
        "correct": True,
        "correct_answer": quiz["correct_answer"],
        "streak": 1,
        "message": "¡Correcto!",
        "reto_active": False,
    }

    sid, quiz = _servir(sid)
    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])

    assert veredicto["streak"] == 2
    assert veredicto["message"] == "¡Correcto! Racha: 2"


def test_respuesta_incorrecta_normal():
    sid, quiz = _servir()

    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"] + 1)

    assert veredicto == {
        "correct": False,
        "correct_answer": quiz["correct_answer"],
        "streak": 0,
        "message": f"Incorrecto. La respuesta era {quiz['correct_answer']}",
        "reto_active": False,
    }
    assert _estado(sid)["fail_count_sum"] == 1


def test_respuesta_correcta_resetea_fallos():
    sid, quiz = _servir()
    for _ in range(2):
        sid, quiz = _servir(sid)
        sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"] + 1)

    sid, quiz = _servir(sid)
    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])

    assert veredicto["streak"] == 1
    assert _estado(sid)["fail_count_sum"] == 0


def test_tres_fallos_resetean_racha_fallos_e_hito():
    sid, quiz = _servir()
    for _ in range(3):
        sid, quiz = _servir(sid)
        sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])
    assert _estado(sid)["streak_sum"] == 3

    for _ in range(3):
        sid, quiz = _servir(sid)
        veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"] + 1)

    assert veredicto["streak"] == 0
    estado = _estado(sid)
    assert estado["streak_sum"] == 0
    assert estado["fail_count_sum"] == 0
    assert estado["hito_consumido"] is None


def _servir_en_racha(sid, objetivo):
    while _estado(sid)["streak_sum"] < objetivo:
        sid, quiz = _servir(sid)
        sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])
    return _servir(sid)


def test_reto_se_ofrece_solo_en_hitos_10_20_30():
    sid, _ = _servir()

    sid, quiz = _servir_en_racha(sid, 9)
    assert not quiz.get("reto_active")

    for hito in (10, 20, 30):
        sid, quiz = _servir_en_racha(sid, hito)

        assert quiz.get("reto_active") is True
        assert quiz["base_value"] * quiz["repeats"] == quiz["correct_answer"]
        assert len(quiz["images"]) == quiz["repeats"]
        assert all(img["value"] == quiz["base_value"] for img in quiz["images"])

        veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])
        assert veredicto == {
            "correct": True,
            "correct_answer": quiz["correct_answer"],
            "streak": hito + 2,
            "message": "🎉 ¡Reto superado! +2 estrellas",
            "reto_active": True,
        }

        sid, quiz = _servir(sid)
        assert not quiz.get("reto_active")


def test_reto_correcto_resetea_fallos_y_consume_hito():
    sid, _ = _servir()
    _estado(sid).update(
        {"streak_sum": 10, "fail_count_sum": 2, "hito_consumido": None}
    )

    sid, quiz = _servir(sid)
    assert quiz["reto_active"]

    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])

    assert veredicto["streak"] == 12
    estado = _estado(sid)
    assert estado["fail_count_sum"] == 0
    assert estado["hito_consumido"] == 10
    assert estado["reto_activo"] is False


def test_reto_fallado_consume_el_hito_y_no_se_repite():
    sid, _ = _servir()
    sid, quiz = _servir_en_racha(sid, 10)

    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"] + 1)

    assert veredicto["correct"] is False
    assert veredicto["streak"] == 10
    assert veredicto["reto_active"] is True
    assert veredicto["message"] == f"Incorrecto. La respuesta era {quiz['correct_answer']}"
    estado = _estado(sid)
    assert estado["hito_consumido"] == 10
    assert estado["fail_count_sum"] == 1

    sid, quiz = _servir(sid)
    assert not quiz.get("reto_active")


def test_reto_fallado_se_rearma_tras_el_reset():
    sid, _ = _servir()
    sid, quiz = _servir_en_racha(sid, 10)
    sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"] + 1)

    for _ in range(2):
        sid, quiz = _servir(sid)
        assert not quiz.get("reto_active")
        sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"] + 1)

    estado = _estado(sid)
    assert estado["streak_sum"] == 0
    assert estado["fail_count_sum"] == 0
    assert estado["hito_consumido"] is None

    sid, quiz = _servir_en_racha(sid, 10)
    assert quiz.get("reto_active") is True


def test_reset_de_tres_fallos_anula_rama_de_reto_fallado():
    sid, _ = _servir()
    _estado(sid).update(
        {"streak_sum": 10, "fail_count_sum": 2, "hito_consumido": None}
    )
    sid, quiz = _servir(sid)
    assert quiz["reto_active"]

    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"] + 1)

    assert veredicto["streak"] == 0
    assert veredicto["reto_active"] is True
    estado = _estado(sid)
    assert estado["streak_sum"] == 0
    assert estado["fail_count_sum"] == 0
    assert estado["hito_consumido"] is None


def test_servir_quiz_resuelve_o_crea_sesion():
    sid_nueva, _ = _servir(None)
    sid_desconocida, _ = _servir(str(uuid.uuid4()))
    sid_repetida, _ = _servir(sid_nueva)

    assert sid_desconocida != sid_nueva
    assert sid_repetida == sid_nueva
    assert _estado(sid_desconocida)["streak_sum"] == 0


def test_registrar_respuesta_desconocida_falla_sin_crear_sesion():
    sid = str(uuid.uuid4())
    antes = sesion.get_summary()

    with pytest.raises(sesion.SesionDesconocida):
        sesion.registrar_respuesta(sid, "sum", 1)

    assert sesion.get_summary() == antes


def test_tipos_de_juego_no_suma_rechazados_sin_tocar_estado():
    antes = sesion.get_summary()
    sid_desconocida = str(uuid.uuid4())
    for tipo in ("count", "streak_count"):
        with pytest.raises(sesion.TipoDeJuegoInvalido):
            sesion.servir_quiz(sid_desconocida, tipo)
    assert sesion.get_summary() == antes

    sid, _ = _servir()
    estado_antes = dict(_estado(sid))
    with pytest.raises(sesion.TipoDeJuegoInvalido):
        sesion.registrar_respuesta(sid, "streak_count", 1)
    assert _estado(sid) == estado_antes
    assert "streak_count" not in _estado(sid)
    assert "fail_count_count" not in _estado(sid)


def test_sin_ultimo_quiz_falla():
    sid, _ = _servir()
    _estado(sid)["last_quiz"] = None

    with pytest.raises(sesion.SinUltimoQuiz):
        sesion.registrar_respuesta(sid, "sum", 1)


def test_tipo_de_juego_no_coincide_falla():
    sid, quiz = _servir()
    quiz["game_type"] = "count"

    with pytest.raises(sesion.TipoDeJuegoNoCoincide):
        sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])


def test_sesion_legacy_con_claves_extra_sigue_funcionando():
    sid, _ = _servir()
    estado = _estado(sid)
    estado["streak_count"] = 7
    estado["fail_count_count"] = 7
    estado["last_count_active"] = True
    del estado["hito_consumido"]

    sid, quiz = _servir(sid)
    veredicto = sesion.registrar_respuesta(sid, "sum", quiz["correct_answer"])

    assert veredicto["streak"] == 1
    assert estado["streak_count"] == 7
    assert estado["fail_count_count"] == 7
    assert estado["last_count_active"] is True
    assert estado["hito_consumido"] is None


def test_get_summary_mantiene_la_forma_actual():
    antes = sesion.get_summary()
    sid, _ = _servir()

    despues = sesion.get_summary()

    assert despues["active_sessions"] == antes["active_sessions"] + 1
    assert sid[:8] + "..." in despues["session_ids"]
    assert set(despues) == {"active_sessions", "session_ids"}


def test_racha_llega_a_la_generacion_con_un_quiz_valido(monkeypatch):
    sid, _ = _servir()
    sid, _ = _servir_en_racha(sid, 24)

    rachas_generadas = []
    generar_original = sesion.generate_sum_quiz

    def espia(streak=0):
        rachas_generadas.append(streak)
        return generar_original(streak=streak)

    monkeypatch.setattr(sesion, "generate_sum_quiz", espia)

    sid, quiz = _servir_en_racha(sid, 25)

    assert rachas_generadas[-1] == 25
    assert not quiz.get("reto_active")
    assert quiz["game_type"] == "sum"
    assert quiz["total_sum"] == sum(img["value"] for img in quiz["images"])
    assert quiz["correct_answer"] == quiz["total_sum"]
    assert quiz["correct_answer"] in quiz["options"]
    assert len(quiz["options"]) == 3
