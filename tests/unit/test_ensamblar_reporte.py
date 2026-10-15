"""``ensamblar_reporte`` (E5.4 mínimo, decisión 030): el reporte del contrato v1.1 sale válido del motor, con la confianza por
pico, el veredicto de la decisión 015 y el vocabulario de R2.

Usa la misma secuencia sintética que ``test_sequencing`` (picos en instantes conocidos): sin video ni Supabase.
"""

from __future__ import annotations

import dataclasses
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
from pydantic import ValidationError

from app.engine.ingest import MetadatosVideo
from app.engine.pipeline import procesar_e3
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.preparacion import TramoExcluido
from app.engine.sequencing import secuenciar
from app.ensamblar_reporte import (
    PREFIJO_METRICA_VELOCIDAD,
    RESPALDO_POR_GRUPO,
    _tramos_no_auditables,
    ensamblar_reporte,
    nombre_metrica_velocidad,
    segmento_de_metrica_velocidad,
)
from app.schemas.reporte import Reporte
from test_sequencing import _seq_con_picos  # mismo directorio: la secuencia sintética con picos conocidos

AHORA = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)


def _md(nominal: float | None = 239.98, real: float | None = 198.87, n: int = 180) -> MetadatosVideo:
    return MetadatosVideo(
        ruta=Path("x.mov"), fps_declarados=real or 30.0, nb_frames=n, duracion_s=n / (real or 30.0), ancho=1920, alto=1080,
        fps_nominal_marcas=nominal, fps_real_medio=real,
    )


def _ensamblar(seq, *, gesto="saque", encuadre="perfil", escala=True, tramos=None, md=None, regularizacion=None, **kw):
    filt = procesar_e3(seq)
    if tramos is not None:
        filt.tramos_excluidos.extend(tramos)
    resultados, resumen = secuenciar(
        seq, lado_dominante="der", tramos_excluidos=filt.tramos_excluidos, brazo_via="codo", ancla="torso"
    )
    return ensamblar_reporte(
        reporte_id=uuid4(), video_id=uuid4(), gesto=gesto, encuadre=encuadre, creado_en=AHORA,
        version_motor="0.4.1", backend_pose="mediapipe",
        modo_captura="camara_lenta_240", factor_ralentizacion=1.0, origen_factor="marcas_de_tiempo",
        escala_temporal_conocida=escala, apto_fase_rapida=True,
        metadatos=md or _md(), fps_real=198.87, secuencia=seq, filtrada=filt,
        resultados=resultados, resumen=resumen, lado_dominante="der", regularizacion=regularizacion, **kw,
    )


@pytest.fixture
def saque_perfil_con_veredicto(monkeypatch):
    """La tabla real suspende el veredicto del saque (decisión 035); estas pruebas ejercitan la maquinaria del veredicto."""
    from app import ensamblar_reporte as e

    tabla = dict(e.RESPALDO_POR_GRUPO)
    tabla[("saque", "perfil")] = e.RespaldoGrupo(e.REFERENCIA_ORDEN_SAQUE, True)
    monkeypatch.setattr(e, "RESPALDO_POR_GRUPO", tabla)


@pytest.fixture(scope="module")
def seq_ordenada():
    return _seq_con_picos(0.25, 0.42, 0.60, semilla=1)


@pytest.fixture(scope="module")
def seq_invertida():
    return _seq_con_picos(0.60, 0.42, 0.25, semilla=2)


# --- el reporte valida contra el contrato -----------------------------------------------------------------


def test_el_reporte_ensamblado_valida_contra_el_contrato_v1_4(seq_ordenada):
    datos = _ensamblar(seq_ordenada)
    r = Reporte.model_validate(datos)
    assert r.version_contrato == "1.4"
    assert r.trazabilidad.tolerancia_orden_ms == pytest.approx(8.333, abs=0.001)
    assert r.segmentacion.repeticiones_marcadas == 1
    assert r.secuenciacion.orden_esperado == ["pelvis", "torso", "brazo"]


def test_la_confianza_por_pico_es_la_de_las_articulaciones_del_segmento(seq_ordenada):
    """La secuencia sintética tiene confianza 0,9 en todo punto: la media por pico es 0,9 (R4)."""
    datos = _ensamblar(seq_ordenada)
    picos = datos["secuenciacion"]["repeticiones"][0]["picos"]
    assert [p["segmento"] for p in picos] == ["pelvis", "torso", "brazo"]
    assert all(p["confianza"] == pytest.approx(0.9) for p in picos)
    assert all(p["unidad"] == "grados/s" and p["instante_s"] >= 0 for p in picos)


def test_la_confianza_baja_si_las_articulaciones_del_segmento_tienen_poca(seq_ordenada):
    """Se baja la confianza solo de las caderas: el pico de pelvis cambia y los otros no."""
    import dataclasses

    from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose

    frames = []
    for f in seq_ordenada.frames:
        mundo = dict(f.puntos_mundo)
        for a in (A.CADERA_IZQ, A.CADERA_DER):
            p = mundo[a]
            mundo[a] = Punto(p.x, p.y, p.z, 0.6)
        frames.append(PoseFrame(f.indice, f.detectado, puntos=f.puntos, puntos_mundo=mundo))
    seq = dataclasses.replace(seq_ordenada, frames=frames)
    por_seg = {p["segmento"]: p["confianza"] for p in _ensamblar(seq)["secuenciacion"]["repeticiones"][0]["picos"]}
    assert por_seg["pelvis"] == pytest.approx(0.6)
    assert por_seg["torso"] == pytest.approx(0.9)


# --- veredicto: decisión 031 (referencia del orden Y Criterio 1 cumplido) ---------------------------------------


def _obs(datos, severidad):
    return [o for o in datos["observaciones"] if o["severidad"] == severidad]


def test_la_tabla_de_respaldo_es_la_de_la_decision_031_tras_la_035():
    """(a) referencia del orden: solo el saque (tesis, tabla 4.8). (b) Criterio 1, par pelvis-torso, con el tiempo real y la
    tolerancia de 8,33 ms, sesión 2 (Paso A, docs/resultados/paso-a-resumen.md): solo el saque de perfil. Veredicto = (a) y (b)."""
    con_veredicto = {g for g, r in RESPALDO_POR_GRUPO.items() if r.con_veredicto}
    assert con_veredicto == set()          # decisiones 035 y 036: ningún grupo emite veredicto
    assert all(r.suspension is not None for r in RESPALDO_POR_GRUPO.values())     # y los seis están suspendidos, no solo "sin (a)"
    assert {g for g, r in RESPALDO_POR_GRUPO.items() if r.depende_del_encuadre} == {
        ("saque", "perfil"), ("saque", "tres_cuartos"), ("drive", "perfil"), ("drive", "tres_cuartos")
    }
    assert {g for g, r in RESPALDO_POR_GRUPO.items() if r.referencia_orden} == {("saque", "perfil"), ("saque", "tres_cuartos")}
    assert {g for g, r in RESPALDO_POR_GRUPO.items() if r.criterio1_cumplido} == {("saque", "perfil")}
    assert len(RESPALDO_POR_GRUPO) == 6


@pytest.mark.parametrize("grupo", sorted(RESPALDO_POR_GRUPO))
def test_la_suspension_gana_aunque_haya_referencia_y_el_criterio_1_se_cumpla(grupo, seq_ordenada, seq_invertida, monkeypatch):
    """Decisión 036: la garantía es de la tabla y no de que falte una referencia. Con (a) y (b) en verdadero el grupo sigue sin veredicto
    (el caso del drive de perfil en el Paso B); solo levantar la suspensión a propósito lo habilita."""
    import dataclasses

    from app import ensamblar_reporte as e

    gesto, encuadre = grupo
    forzado = dataclasses.replace(RESPALDO_POR_GRUPO[grupo], referencia_orden="referencia de prueba", criterio1_cumplido=True)
    assert forzado.con_veredicto is False
    monkeypatch.setattr(e, "RESPALDO_POR_GRUPO", {**RESPALDO_POR_GRUPO, grupo: forzado})
    for seq in (seq_ordenada, seq_invertida):
        datos = _ensamblar(seq, gesto=gesto, encuadre=encuadre)
        assert datos["secuenciacion"]["repeticiones"][0]["correcto"] is None
        assert datos["secuenciacion"]["resumen"]["repeticiones_correctas"] == 0
        assert not any(o["severidad"] in ("correcto", "desvio_leve", "alerta_de_carga") for o in datos["observaciones"])
    # y levantar la suspensión es lo único que lo habilita
    levantado = dataclasses.replace(forzado, suspension=None)
    assert levantado.con_veredicto is True


def test_saque_de_perfil_con_la_cadera_primero_es_correcto_y_cita_la_tesis(seq_ordenada, saque_perfil_con_veredicto):
    datos = _ensamblar(seq_ordenada, gesto="saque", encuadre="perfil")
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["orden_observado"] == ["pelvis", "torso", "brazo"] and rep["correcto"] is True
    assert datos["secuenciacion"]["resumen"]["repeticiones_correctas"] == 1
    (obs,) = _obs(datos, "correcto")
    assert "Kovacs y Ellenbecker (2011)" in obs["referencia"] and "Fleisig et al. (2003)" in obs["referencia"]
    assert obs["fundamento"]


def test_saque_de_perfil_con_el_tronco_primero_es_desvio_leve_y_nunca_alerta_de_carga(seq_invertida, saque_perfil_con_veredicto):
    """Sin umbral con referencia no hay alerta (E5.1): el desvío del orden nunca llega a `alerta_de_carga`."""
    datos = _ensamblar(seq_invertida, gesto="saque", encuadre="perfil")
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is True and rep["correcto"] is False
    assert len(_obs(datos, "desvio_leve")) == 1
    assert "alerta_de_carga" not in {o["severidad"] for o in datos["observaciones"]}


@pytest.mark.parametrize(
    ("gesto", "encuadre", "porque"),
    [
        ("saque", "tres_cuartos", "depende del encuadre"),  # decisión 035: tiene referencia, pero el orden cambia con el encuadre
        ("drive", "perfil", "depende del encuadre"),  # decisión 036: el drive sigue el patrón del saque
        ("drive", "tres_cuartos", "depende del encuadre"),
        ("reves", "tres_cuartos", "no es confiable con una sola cámara"),  # decisión 036: el revés no sigue el patrón
        ("reves", "perfil", "no es confiable con una sola cámara"),
    ],
)
def test_sin_las_dos_condiciones_el_orden_se_documenta_sin_evaluar(seq_ordenada, gesto, encuadre, porque):
    """Decisión 031: falta (a) o (b) -> `sin_evaluar` (la etiqueta del brazo, decisión 011), no `no_auditable`: se midió."""
    datos = _ensamblar(seq_ordenada, gesto=gesto, encuadre=encuadre)
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is True and rep["orden_observado"] == ["pelvis", "torso", "brazo"]
    assert rep["correcto"] is None
    assert datos["secuenciacion"]["resumen"]["repeticiones_correctas"] == 0
    par = datos["observaciones"][0]
    # La razón técnica (con la literatura y la validación propia) va en el detalle, no en el texto que lee el jugador.
    assert par["severidad"] == "sin_evaluar" and porque in par["fundamento"] and par["referencia"] is None
    assert "Por eso lo registramos sin evaluarlo" in par["texto"]
    assert "cambia según desde dónde se grabó el golpe" in par["texto"] or "con una sola cámara" in par["texto"]
    assert "no_auditable" not in {o["severidad"] for o in datos["observaciones"]}
    assert not _obs(datos, "correcto") and not _obs(datos, "desvio_leve")


def test_un_grupo_desconocido_no_emite_veredicto(seq_ordenada):
    datos = _ensamblar(seq_ordenada, gesto="reves", encuadre="espaldas")
    assert datos["secuenciacion"]["repeticiones"][0]["correcto"] is None
    assert datos["observaciones"][0]["severidad"] == "sin_evaluar"


def test_el_brazo_siempre_se_informa_sin_evaluar(seq_ordenada):
    """Decisión 011: el balanceo del brazo no tiene referencia equivalente; nunca correcto ni desvío, ni con veredicto en el par."""
    datos = _ensamblar(seq_ordenada, gesto="saque", encuadre="perfil")
    brazo = [o for o in datos["observaciones"] if "brazo" in o["texto"]]
    assert len(brazo) == 1 and brazo[0]["severidad"] == "sin_evaluar" and brazo[0]["referencia"] is None
    assert "después del tronco" in brazo[0]["texto"]


def _rep_con_picos(t_pelvis: float, t_torso: float, t_brazo: float = 0.4):
    """Una repetición con los picos exactamente en esos instantes (sin ruido), a 240 fps."""
    from app.engine.segmentos_corporales import SegmentoCadena as S
    from app.engine.sequencing import PicoSegmento, ResultadoRepeticion, Ventana

    fps = 240.0
    picos = {
        S.PELVIS: PicoSegmento(S.PELVIS, round(t_pelvis * fps), t_pelvis, 500.0),
        S.TORSO: PicoSegmento(S.TORSO, round(t_torso * fps), t_torso, 700.0),
        S.BRAZO: PicoSegmento(S.BRAZO, round(t_brazo * fps), t_brazo, 900.0),
    }
    orden = tuple(sorted(picos, key=lambda s: picos[s].instante_s))
    return ResultadoRepeticion(1, Ventana(0, 120, fps), picos, orden, None, True)


@pytest.mark.parametrize(
    ("t_torso", "estado", "veredicto"),
    [
        (0.2 + 1 / 240.0, "no_ordenable", None),       # 4,2 ms: dentro de la tolerancia
        (0.2 + 2 / 240.0, "no_ordenable", None),       # 8,33 ms = 1/120 s: IGUAL a la tolerancia, no es "más que" (decisión 032)
        (0.2 - 2 / 240.0, "no_ordenable", None),
        (0.2 + 3 / 240.0, "cadera_primero", True),     # 12,5 ms: ordenable
        (0.2 - 3 / 240.0, "tronco_primero", False),
    ],
)
def test_el_par_cadera_tronco_respeta_la_tolerancia_de_8_3_ms(t_torso, estado, veredicto, saque_perfil_con_veredicto):
    from app.ensamblar_reporte import _evaluar_par, _veredicto

    rep = _rep_con_picos(0.2, t_torso)
    assert _evaluar_par(rep).estado == estado
    assert _veredicto("saque", "perfil", rep) is veredicto


def test_una_simultaneidad_es_sin_diferencia_medible_y_no_no_auditable():
    """Decisión 037 (corrige la 015 del 29/9): cadera y tronco empatados SE MIDIERON; 'no auditable' es solo para datos no confiables (R3)."""
    from app.ensamblar_reporte import _obs_par

    obs = _obs_par("saque", "perfil", [_rep_con_picos(0.2, 0.2 + 1 / 240.0)], True)
    assert obs["severidad"] == "sin_diferencia_medible" and "casi al mismo tiempo" in obs["texto"]
    assert "no hay diferencia medible" in obs["texto"]
    assert not re.search(r"no se pudo|no auditable|falla", obs["texto"], re.IGNORECASE)
    # la resolución que se informa es la del archivo real (5 ms a ~200 fps), no la de la grilla de 240 Hz
    assert "4 ms" in obs["fundamento"] and "8,3 ms" in obs["fundamento"]


def test_la_resolucion_se_informa_con_la_tasa_real_y_no_con_la_de_la_grilla():
    from app.ensamblar_reporte import _obs_par

    obs = _obs_par("saque", "perfil", [_rep_con_picos(0.2, 0.2 + 1 / 240.0)], True, fps_real=199.9)
    assert "1 fotograma ≈ 5 ms a 200 fps reales" in obs["fundamento"]


def test_con_escala_desconocida_el_orden_no_lleva_milisegundos(seq_ordenada):
    datos = _ensamblar(seq_ordenada, gesto="saque", encuadre="perfil", escala=False)
    assert all(" ms" not in o["texto"] for o in datos["observaciones"] if o["severidad"] in ("correcto", "sin_evaluar"))


# --- lo que no se pudo medir ------------------------------------------------------------------------------


def test_un_torso_no_auditable_deja_el_golpe_sin_orden_y_sin_inventar_numeros(seq_ordenada):
    tramos = [TramoExcluido(A.HOMBRO_DER, "x", 0, seq_ordenada.n_frames - 1)]
    datos = _ensamblar(seq_ordenada, tramos=tramos)
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is False and rep["orden_observado"] is None and rep["correcto"] is None
    assert rep["motivo_no_auditable"]
    assert datos["observaciones"][0]["severidad"] == "no_auditable"
    assert "sin_evaluar" not in {o["severidad"] for o in datos["observaciones"][:1]}
    assert all(m["valor"] is None and m["auditable"] is False for m in datos["metricas"])
    assert datos["secuenciacion"]["resumen"]["orden_predominante"] == []
    Reporte.model_validate(datos)


def test_con_escala_desconocida_las_velocidades_no_son_auditables(seq_ordenada):
    """R3: velocidades y ms con una escala sin confirmar son un dato equivocado presentado como bueno."""
    datos = _ensamblar(seq_ordenada, escala=False)
    assert datos["trazabilidad"]["escala_temporal_conocida"] is False
    velocidades = [m for m in datos["metricas"] if m["nombre"].startswith(PREFIJO_METRICA_VELOCIDAD)]
    assert velocidades and all(m["valor"] is None and m["auditable"] is False for m in velocidades)
    # un ángulo no depende de la escala de tiempo: la separación cadera-hombro sigue siendo un dato auditable
    assert next(m for m in datos["metricas"] if m["nombre"] == "separacion_cadera_hombro_max")["auditable"] is True
    assert any("escala temporal" in o["texto"] and o["severidad"] == "no_auditable" for o in datos["observaciones"])
    # el orden sí se documenta
    assert datos["secuenciacion"]["repeticiones"][0]["orden_observado"] == ["pelvis", "torso", "brazo"]


def test_las_metricas_de_velocidad_se_nombran_y_se_leen_de_vuelta(seq_ordenada):
    datos = _ensamblar(seq_ordenada)
    velocidades = [m for m in datos["metricas"] if m["nombre"].startswith(PREFIJO_METRICA_VELOCIDAD)]
    assert [m["nombre"] for m in velocidades] == [f"{PREFIJO_METRICA_VELOCIDAD}{s}" for s in ("pelvis", "torso", "brazo")]
    assert all(m["auditable"] and m["valor"] > 0 and m["unidad"] == "grados/s" for m in velocidades)
    assert segmento_de_metrica_velocidad(nombre_metrica_velocidad("torso")) == "torso"
    assert segmento_de_metrica_velocidad("angulo_max_rodilla") is None


# --- trazabilidad ------------------------------------------------------------------------------------------


def test_la_cobertura_auditable_descuenta_los_tramos_excluidos_de_la_cadena(seq_ordenada):
    """R3: 100 % al lado de tramos no auditables sería un dato presentado como bueno."""
    n = seq_ordenada.n_frames
    assert _ensamblar(seq_ordenada)["cobertura"]["auditable_pct"] == 100.0
    # un tramo de 45 de 180 fotogramas del codo dominante (articulación de la cadena): 75 %
    parcial = _ensamblar(seq_ordenada, tramos=[TramoExcluido(A.CODO_DER, "x", 0, n // 4 - 1)])["cobertura"]
    assert parcial["auditable_pct"] == pytest.approx(75.0) and len(parcial["tramos_no_auditables"]) == 1
    # una articulación ajena a la cadena no descuenta nada
    ajeno = _ensamblar(seq_ordenada, tramos=[TramoExcluido(A.RODILLA_DER, "x", 0, n - 1)])["cobertura"]
    assert ajeno["auditable_pct"] == 100.0 and ajeno["tramos_no_auditables"] == []


def test_la_trazabilidad_lleva_la_tasa_del_archivo_y_la_regularizacion(seq_ordenada):
    reg = {
        "fotogramas_fuente": 398, "puntos_de_la_grilla": 480, "puntos_copiados": 398, "puntos_interpolados": 82,
        "puntos_interpolados_pct": 17.08, "puntos_sin_dato": 0, "fps_grilla": 240.0, "fps_real_medio": 198.87,
        "hueco_maximo_ms": 12.5,
    }
    t = _ensamblar(seq_ordenada, regularizacion=reg)["trazabilidad"]
    assert t["origen_factor"] == "marcas_de_tiempo" and t["factor_ralentizacion"] == 1.0
    assert t["fps_nominal"] == pytest.approx(239.98)
    assert t["fotogramas_perdidos_pct"] == pytest.approx(17.13, abs=0.02)
    assert t["regularizacion"]["puntos_interpolados"] == 82
    assert t["filtro"]["fase_cero"] is True and t["filtro"]["corte_hz"] > 0
    assert t["version_motor"] == "0.4.1" and t["backend_pose"] == "mediapipe"


def test_un_horneado_no_informa_tasa_nominal_ni_perdidas(seq_ordenada):
    """Marcas a 30 fps constantes: la tasa real se desconoce, así que no hay nominal ni pérdidas que contar (R3)."""
    t = _ensamblar(seq_ordenada, md=_md(nominal=30.0, real=30.0))["trazabilidad"]
    assert t["fps_nominal"] is None and t["fotogramas_perdidos_pct"] is None and t["regularizacion"] is None


def test_los_tramos_no_auditables_se_unen_y_solo_cuentan_la_cadena():
    tramos = [
        TramoExcluido(A.HOMBRO_DER, "x", 10, 20),
        TramoExcluido(A.CODO_DER, "y", 15, 30),   # se superpone: un solo tramo
        TramoExcluido(A.CADERA_IZQ, "x", 100, 100),
        TramoExcluido(A.RODILLA_DER, "x", 50, 60),  # fuera de la cadena: no cuenta
    ]
    cadena = {A.HOMBRO_DER, A.CODO_DER, A.CADERA_IZQ}
    out = _tramos_no_auditables(tramos, cadena, fps=100.0)
    assert [(t["desde_s"], t["hasta_s"]) for t in out] == [(0.1, 0.31), (1.0, 1.01)]
    assert "codo_der" in out[0]["motivo"] and "hombro_der" in out[0]["motivo"]


# --- vocabulario de R2 (E5.7) -------------------------------------------------------------------------------

# Verbos y términos que CLAUDE.md §2 (R2) prohíbe en toda la interfaz, textos y reportes.
_PROHIBIDO = re.compile(
    r"\b(predic\w*|diagnostic\w*|diagnóstic\w*|prevenir|prevenc\w*|prevent\w*|epicondilitis|tendinitis|tendinopat\w*|"
    r"lesi[oó]n|lesiones|bandera roja|riesgo|reduc[ií]\w* la intensidad|consult[aá]\w* por)\b",
    re.IGNORECASE,
)


@pytest.mark.parametrize("gesto", ["saque", "drive", "reves"])
@pytest.mark.parametrize("encuadre", ["perfil", "tres_cuartos"])
@pytest.mark.parametrize("escala", [True, False])
def test_ningun_texto_del_reporte_usa_el_vocabulario_prohibido_por_r2(seq_ordenada, seq_invertida, gesto, encuadre, escala):
    textos: list[str] = []
    for seq in (seq_ordenada, seq_invertida):
        datos = _ensamblar(seq, gesto=gesto, encuadre=encuadre, escala=escala)
        for o in datos["observaciones"]:
            textos += [t for t in (o["texto"], o["fundamento"], o["referencia"]) if t]
    # y el caso sin torso medible
    tramos = [TramoExcluido(A.HOMBRO_DER, "x", 0, seq_ordenada.n_frames - 1)]
    for o in _ensamblar(seq_ordenada, gesto=gesto, encuadre=encuadre, tramos=tramos)["observaciones"]:
        textos += [t for t in (o["texto"], o["fundamento"], o["referencia"]) if t]
    assert textos
    malos = [t for t in textos if _PROHIBIDO.search(t)]
    assert not malos, malos


def test_el_contrato_rechaza_un_reporte_incompleto(seq_ordenada):
    """El ensamblador valida: lo que no cumple el contrato no llega a guardarse."""
    with pytest.raises(ValidationError):
        ensamblar_reporte(
            reporte_id=uuid4(), video_id=uuid4(), gesto="saque_inventado", encuadre="perfil", creado_en=AHORA,
            version_motor="0.4.1", backend_pose="mediapipe", modo_captura="camara_lenta_240",
            factor_ralentizacion=1.0, origen_factor="marcas_de_tiempo", escala_temporal_conocida=True,
            apto_fase_rapida=True, metadatos=_md(), fps_real=198.87, secuencia=seq_ordenada,
            filtrada=procesar_e3(seq_ordenada),
            resultados=secuenciar(seq_ordenada, lado_dominante="der", ancla="torso")[0],
            resumen=secuenciar(seq_ordenada, lado_dominante="der", ancla="torso")[1], lado_dominante="der",
        )


# --- la simultaneidad también se refleja en la repetición (decisión 015, corrección del 29/9) -----------------------


def _ensamblar_con(seq, resultados, gesto="saque", encuadre="perfil"):
    from app.engine.sequencing import agregar

    return ensamblar_reporte(
        reporte_id=uuid4(), video_id=uuid4(), gesto=gesto, encuadre=encuadre, creado_en=AHORA,
        version_motor="0.4.1", backend_pose="mediapipe", modo_captura="camara_lenta_240", factor_ralentizacion=1.0,
        origen_factor="marcas_de_tiempo", escala_temporal_conocida=True, apto_fase_rapida=True, metadatos=_md(),
        fps_real=198.87, secuencia=seq, filtrada=procesar_e3(seq), resultados=resultados, resumen=agregar(resultados),
        lado_dominante="der",
    )


def test_cadera_y_tronco_a_un_fotograma_dejan_la_repeticion_no_auditable_sin_orden(seq_ordenada):
    """El caso del 9/10 (IMG_6376.mov con la regularización): pelvis 4,2 ms después del tronco. Antes el reporte decía
    `auditable: true` con un orden y, a la vez, una observación de que el orden no se puede establecer."""
    datos = _ensamblar_con(seq_ordenada, [_rep_con_picos(0.2 + 1 / 240.0, 0.2)])
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is False and rep["orden_observado"] is None and rep["correcto"] is None
    assert "simultaneidad" in rep["motivo_no_auditable"]
    assert [p["segmento"] for p in rep["picos"]] == ["pelvis", "torso", "brazo"]  # lo medido se informa igual
    assert datos["segmentacion"]["repeticiones_auditables"] == 0
    assert datos["secuenciacion"]["resumen"]["orden_predominante"] == []
    assert datos["observaciones"][0]["severidad"] == "sin_diferencia_medible"
    Reporte.model_validate(datos)


def test_un_empate_es_un_golpe_medido_aunque_su_orden_no_se_distinga(seq_ordenada):
    """Decisión 037: 'medido' = picos de cadera y tronco con confianza; no depende de que el orden sea distinguible."""
    from app.ensamblar_reporte import par_medido

    datos = _ensamblar_con(seq_ordenada, [_rep_con_picos(0.2 + 1 / 240.0, 0.2)])
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is False and par_medido(rep) is True


def test_sin_pico_de_cadera_o_de_tronco_el_golpe_no_esta_medido():
    from app.ensamblar_reporte import par_medido

    assert par_medido({"picos": [{"segmento": "pelvis", "confianza": 0.9}]}) is False
    assert par_medido({"picos": [{"segmento": "pelvis", "confianza": 0.9}, {"segmento": "torso", "confianza": 0.2}]}) is False
    assert par_medido({"picos": [{"segmento": "pelvis", "confianza": 0.9}, {"segmento": "torso", "confianza": 0.6}]}) is True
    assert par_medido({}) is False


@pytest.mark.parametrize(
    ("motivo", "debe_decir"),
    [
        ("ventana incompleta: se midió el 43 % de la ventana (mínimo 75 %)", "43 %"),
        ("sin picos marcados por encima de la prominencia mínima", "no tuvo un momento claro"),
        ("el pico cae en un tramo no auditable", "no se lo veía con confianza"),
        ("velocidad implausible (3000 °/s > techo 2500): probable error de detección", "imposible"),
        ("serie demasiado corta o incompleta", "Casi no hubo datos"),
        (None, "No se pudo medir"),
    ],
)
def test_el_motivo_de_un_pico_no_medido_esta_en_palabras_simples(motivo, debe_decir):
    from app.engine.segmentos_corporales import SegmentoCadena
    from app.ensamblar_reporte import motivo_pico_llano

    texto = motivo_pico_llano(SegmentoCadena.BRAZO, motivo)
    assert debe_decir in texto and "brazo que golpea" in texto
    assert not _PROHIBIDO.search(texto)
    assert not re.search(r"prominencia|techo|ventana|°/s", texto)      # nada de jerga del motor


def test_el_reporte_lleva_los_picos_no_medidos_con_su_motivo(seq_ordenada):
    """El brazo sin medir no desaparece: queda en `picos_no_medidos` con el motivo (decisión 037)."""
    from app.engine.sequencing import PicoSegmento
    from app.engine.segmentos_corporales import SegmentoCadena as S

    rep = _rep_con_picos(0.2, 0.3)
    picos = dict(rep.picos)
    picos[S.BRAZO] = PicoSegmento(S.BRAZO, -1, float("nan"), float("nan"), auditable=False,
                                  motivo="ventana incompleta: se midió el 43 % de la ventana (mínimo 75 %)")
    rep = dataclasses.replace(rep, picos=picos)
    datos = _ensamblar_con(seq_ordenada, [rep])
    r0 = datos["secuenciacion"]["repeticiones"][0]
    assert [p["segmento"] for p in r0["picos_no_medidos"]] == ["brazo"]
    assert "43 %" in r0["picos_no_medidos"][0]["motivo"] and r0["picos_no_medidos"][0]["detalle"].startswith("ventana incompleta")
    assert [p["segmento"] for p in r0["picos"]] == ["pelvis", "torso"]
    Reporte.model_validate(datos)
    # y la observación del brazo trae el motivo, no solo "no se pudo medir"
    obs_brazo = [o for o in datos["observaciones"] if "brazo" in o["texto"]][0]
    assert "43 %" in obs_brazo["fundamento"]


def test_con_tres_fotogramas_de_separacion_la_repeticion_sigue_siendo_auditable(seq_ordenada):
    datos = _ensamblar_con(seq_ordenada, [_rep_con_picos(0.2, 0.2 + 3 / 240.0)])
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is True and rep["orden_observado"] == ["pelvis", "torso", "brazo"]
    assert datos["segmentacion"]["repeticiones_auditables"] == 1
    assert datos["secuenciacion"]["resumen"]["orden_predominante"] == ["pelvis", "torso", "brazo"]


# --- el texto principal no cita la literatura (ajuste del 12/10, decisión 032) -----------------------------------------


@pytest.mark.parametrize(
    ("gesto", "encuadre", "fixture"),
    [
        ("saque", "perfil", "seq_ordenada"), ("saque", "perfil", "seq_invertida"),
        ("drive", "perfil", "seq_ordenada"), ("reves", "tres_cuartos", "seq_ordenada"),
    ],
)
def test_el_texto_de_cada_observacion_no_menciona_la_literatura(request, gesto, encuadre, fixture):
    """La cita y la razón técnica viajan en `fundamento` y `referencia` (nivel 3 y PDF); el texto es para el jugador."""
    datos = _ensamblar(request.getfixturevalue(fixture), gesto=gesto, encuadre=encuadre)
    for o in datos["observaciones"]:
        assert not re.search(r"literatura|Kovacs|Fleisig|Martin|et al\.|\(20\d\d\)|Criterio|validaci", o["texto"]), o["texto"]


def test_con_veredicto_la_fuente_sigue_disponible_en_el_detalle(seq_ordenada, saque_perfil_con_veredicto):
    datos = _ensamblar(seq_ordenada, gesto="saque", encuadre="perfil")
    (obs,) = _obs(datos, "correcto")
    assert "orden esperado" in obs["texto"] and "Kovacs" not in obs["texto"]
    assert "Kovacs y Ellenbecker (2011)" in obs["referencia"]


# --- el brazo sin medir no tira abajo el par cadera-tronco (ajuste del 12/10) ----------------------------------------


def _rep_sin_brazo(t_pelvis: float, t_torso: float):
    from app.engine.segmentos_corporales import SegmentoCadena as S
    from app.engine.sequencing import PicoSegmento, ResultadoRepeticion, Ventana

    fps = 240.0
    picos = {
        S.PELVIS: PicoSegmento(S.PELVIS, round(t_pelvis * fps), t_pelvis, 500.0),
        S.TORSO: PicoSegmento(S.TORSO, round(t_torso * fps), t_torso, 700.0),
        S.BRAZO: PicoSegmento(S.BRAZO, -1, float("nan"), float("nan"), auditable=False,
                              motivo="ventana incompleta: se midió el 43 % de la ventana (mínimo 75 %)"),
    }
    return ResultadoRepeticion(1, Ventana(0, 120, fps), picos, None, None, False, "sin pico auditable para: brazo")


def test_con_el_brazo_sin_medir_la_cadera_y_el_tronco_se_informan_y_la_repeticion_es_auditable(seq_ordenada):
    datos = _ensamblar_con(seq_ordenada, [_rep_sin_brazo(0.2, 0.2 + 5 / 240.0)])
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is True and rep["orden_observado"] == ["pelvis", "torso"] and rep["motivo_no_auditable"] is None
    assert [p["segmento"] for p in rep["picos"]] == ["pelvis", "torso"]          # el brazo no tiene pico: no se inventa
    assert datos["segmentacion"]["repeticiones_auditables"] == 1
    assert datos["secuenciacion"]["resumen"]["orden_predominante"] == ["pelvis", "torso"]
    obs = {o["severidad"] for o in datos["observaciones"]}
    assert "no_auditable" in obs                                                # "no se pudo medir el brazo"
    Reporte.model_validate(datos)


def test_con_el_brazo_sin_medir_y_la_cadera_pegada_al_tronco_sigue_sin_orden(seq_ordenada):
    datos = _ensamblar_con(seq_ordenada, [_rep_sin_brazo(0.2, 0.2 + 1 / 240.0)])
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is False and rep["orden_observado"] is None and rep["correcto"] is None
    assert [p["segmento"] for p in rep["picos"]] == ["pelvis", "torso"]


# --- magnitudes articulares como dato (plan §8, punto 3) ------------------------------------------------------------


def test_el_reporte_trae_la_separacion_cadera_hombro_con_su_confianza(seq_ordenada):
    datos = _ensamblar(seq_ordenada)
    por_nombre = {m["nombre"]: m for m in datos["metricas"]}
    sep = por_nombre["separacion_cadera_hombro_max"]
    assert sep["auditable"] and sep["unidad"] == "grados" and 0 < sep["valor"] <= 180
    assert sep["confianza"] == pytest.approx(0.9)
    # la secuencia sintética no tiene puntos de imagen (solo métricos): los ángulos de rodilla y codo NO se inventan
    angulos = [m for m in datos["metricas"] if m["nombre"].startswith("angulo_")]
    assert {m["nombre"] for m in angulos} <= {"angulo_rodilla_en_pico_tronco", "angulo_codo_en_pico_tronco"}
    assert all(m["valor"] is None and m["auditable"] is False for m in angulos)
    Reporte.model_validate(datos)


def test_las_metricas_nuevas_no_son_velocidades_ni_entran_a_la_tabla_de_metricas_del_servidor(seq_ordenada):
    datos = _ensamblar(seq_ordenada)
    nuevas = [m["nombre"] for m in datos["metricas"] if not m["nombre"].startswith(PREFIJO_METRICA_VELOCIDAD)]
    assert "separacion_cadera_hombro_max" in nuevas
    assert all(segmento_de_metrica_velocidad(n) is None for n in nuevas)


# --- decisión 035: B (el saque no emite veredicto) y D (el encuadre declarado contra el visto) ------------------------


@pytest.mark.parametrize("encuadre", ["perfil", "tres_cuartos"])
def test_el_saque_no_emite_veredicto_en_ningun_encuadre_y_explica_por_que(seq_ordenada, encuadre):
    datos = _ensamblar(seq_ordenada, gesto="saque", encuadre=encuadre)
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["correcto"] is None and datos["secuenciacion"]["resumen"]["repeticiones_correctas"] == 0
    par = datos["observaciones"][0]
    assert par["severidad"] == "sin_evaluar" and par["referencia"] is None
    assert "cambia según desde dónde se grabó el golpe" in par["texto"]
    assert "depende del encuadre" in par["fundamento"]
    assert not any(o["severidad"] in ("correcto", "desvio_leve") for o in datos["observaciones"])


def test_la_explicacion_de_la_suspension_no_cita_literatura_ni_estadistica(seq_ordenada):
    texto = _ensamblar(seq_ordenada, gesto="saque", encuadre="perfil")["observaciones"][0]["texto"]
    assert not re.search(r"literatura|Kovacs|Fleisig|et al\.|Fisher|p = |Criterio|validaci", texto)


@pytest.fixture(scope="module")
def seq_larga():
    """Preparación larga (picos tarde): hombros paralelos al plano de la imagen (giro ~0°) antes del pico del tronco."""
    return _seq_con_picos(1.2, 1.4, 1.6, n=480, semilla=3)


def test_encuadre_declarado_distinto_del_visto_avisa_sin_tecnicismos_y_no_emite_veredicto(seq_larga, saque_perfil_con_veredicto):
    # el video "se ve" de perfil (giro ~0° <= 42°) y el usuario eligió tres cuartos
    datos = _ensamblar(seq_larga, gesto="saque", encuadre="tres_cuartos")
    primera = datos["observaciones"][0]
    assert primera["severidad"] == "no_auditable"
    assert primera["texto"] == "El video parece grabado de perfil, pero elegiste tres cuartos. Revisá el encuadre antes de comparar tus resultados."
    assert "Giro de la línea de hombros" in primera["fundamento"] and "no se emite veredicto" in primera["fundamento"]
    assert datos["secuenciacion"]["repeticiones"][0]["correcto"] is None
    Reporte.model_validate(datos)


def test_el_aviso_no_bloquea_el_reporte_y_el_encuadre_coincidente_no_avisa(seq_larga):
    datos = _ensamblar(seq_larga, gesto="saque", encuadre="perfil")
    assert not any("parece grabado" in o["texto"] for o in datos["observaciones"])
    assert datos["secuenciacion"]["repeticiones"][0]["orden_observado"] is not None   # el análisis sigue


def test_con_discrepancia_ni_siquiera_un_grupo_con_veredicto_lo_emite(seq_larga, saque_perfil_con_veredicto):
    """Si el video no es del encuadre declarado, el veredicto de ese grupo no corresponde (el caso del 12/10)."""
    con = _ensamblar(seq_larga, gesto="saque", encuadre="perfil")["secuenciacion"]["repeticiones"][0]["correcto"]
    sin = _ensamblar(seq_larga, gesto="saque", encuadre="tres_cuartos")["secuenciacion"]["repeticiones"][0]["correcto"]
    assert con is not None and sin is None


def test_drive_y_reves_no_se_contrastan_hasta_calibrarlos(seq_larga):
    for gesto in ("drive", "reves"):
        datos = _ensamblar(seq_larga, gesto=gesto, encuadre="tres_cuartos")
        assert not any("parece grabado" in o["texto"] for o in datos["observaciones"])


# --- nota del lado de la cámara (decisión 013, recomendación revisable) -----------------------------------------


def test_la_camara_del_lado_de_la_mano_dominante_agrega_una_nota_neutra(seq_ordenada):
    from app.ensamblar_reporte import NOTA_LADO_NO_VALIDADO

    datos = _ensamblar(seq_ordenada, lado_camara="derecha", mano_dominante="derecha")
    notas = [o for o in datos["observaciones"] if o["texto"] == NOTA_LADO_NO_VALIDADO]
    assert len(notas) == 1
    assert notas[0]["severidad"] == "sin_evaluar"  # neutra: "Solo registrado", sin color de estado
    assert "todavía no está validado" in notas[0]["texto"]
    assert "diagnóstic" not in notas[0]["texto"].lower()


def test_el_lado_validado_no_agrega_nota(seq_ordenada):
    from app.ensamblar_reporte import NOTA_LADO_NO_VALIDADO

    for lado, mano in (("izquierda", "derecha"), ("derecha", "izquierda")):
        datos = _ensamblar(seq_ordenada, lado_camara=lado, mano_dominante=mano)
        assert not any(o["texto"] == NOTA_LADO_NO_VALIDADO for o in datos["observaciones"])


def test_sin_lado_o_sin_mano_no_se_afirma_nada(seq_ordenada):
    from app.ensamblar_reporte import nota_lado_de_camara

    assert nota_lado_de_camara(None, "derecha") is None
    assert nota_lado_de_camara("derecha", None) is None
    assert nota_lado_de_camara("otro", "derecha") is None
    datos = _ensamblar(seq_ordenada)  # los llamados anteriores no pasan el lado
    assert datos["observaciones"]


def test_la_nota_del_lado_no_cambia_ningun_numero(seq_ordenada):
    sin = _ensamblar(seq_ordenada, lado_camara="izquierda", mano_dominante="derecha")
    con = _ensamblar(seq_ordenada, lado_camara="derecha", mano_dominante="derecha")
    assert sin["secuenciacion"] == con["secuenciacion"]
    assert sin["metricas"] == con["metricas"]
    assert len(con["observaciones"]) == len(sin["observaciones"]) + 1
    Reporte.model_validate(con)  # el contrato lo admite sin cambios
