"""``ensamblar_reporte`` (E5.4 mínimo, decisión 030): el reporte del contrato v1.1 sale válido del motor, con la confianza por
pico, el veredicto de la decisión 015 y el vocabulario de R2.

Usa la misma secuencia sintética que ``test_sequencing`` (picos en instantes conocidos): sin video ni Supabase.
"""

from __future__ import annotations

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


@pytest.fixture(scope="module")
def seq_ordenada():
    return _seq_con_picos(0.25, 0.42, 0.60, semilla=1)


@pytest.fixture(scope="module")
def seq_invertida():
    return _seq_con_picos(0.60, 0.42, 0.25, semilla=2)


# --- el reporte valida contra el contrato -----------------------------------------------------------------


def test_el_reporte_ensamblado_valida_contra_el_contrato_v1_2(seq_ordenada):
    datos = _ensamblar(seq_ordenada)
    r = Reporte.model_validate(datos)
    assert r.version_contrato == "1.2"
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


def test_la_tabla_de_respaldo_es_la_de_la_decision_031():
    """(a) referencia del orden: solo el saque (tesis, tabla 4.8). (b) Criterio 1, par pelvis-torso, tau = 1, sesión 2
    (docs/resultados/criterio1-resumen.md): saque perfil, drive perfil y revés tres cuartos. Veredicto = (a) y (b)."""
    con_veredicto = {g for g, r in RESPALDO_POR_GRUPO.items() if r.con_veredicto}
    assert con_veredicto == {("saque", "perfil")}
    assert {g for g, r in RESPALDO_POR_GRUPO.items() if r.referencia_orden} == {("saque", "perfil"), ("saque", "tres_cuartos")}
    assert {g for g, r in RESPALDO_POR_GRUPO.items() if r.criterio1_cumplido} == {
        ("saque", "perfil"), ("drive", "perfil"), ("reves", "tres_cuartos")
    }
    assert len(RESPALDO_POR_GRUPO) == 6


def test_saque_de_perfil_con_la_cadera_primero_es_correcto_y_cita_la_tesis(seq_ordenada):
    datos = _ensamblar(seq_ordenada, gesto="saque", encuadre="perfil")
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["orden_observado"] == ["pelvis", "torso", "brazo"] and rep["correcto"] is True
    assert datos["secuenciacion"]["resumen"]["repeticiones_correctas"] == 1
    (obs,) = _obs(datos, "correcto")
    assert "Kovacs y Ellenbecker (2011)" in obs["referencia"] and "Fleisig et al. (2003)" in obs["referencia"]
    assert obs["fundamento"]


def test_saque_de_perfil_con_el_tronco_primero_es_desvio_leve_y_nunca_alerta_de_carga(seq_invertida):
    """Sin umbral con referencia no hay alerta (E5.1): el desvío del orden nunca llega a `alerta_de_carga`."""
    datos = _ensamblar(seq_invertida, gesto="saque", encuadre="perfil")
    rep = datos["secuenciacion"]["repeticiones"][0]
    assert rep["auditable"] is True and rep["correcto"] is False
    assert len(_obs(datos, "desvio_leve")) == 1
    assert "alerta_de_carga" not in {o["severidad"] for o in datos["observaciones"]}


@pytest.mark.parametrize(
    ("gesto", "encuadre", "porque"),
    [
        ("saque", "tres_cuartos", "criterio de repetibilidad"),  # tiene referencia, no cumple el Criterio 1
        ("drive", "perfil", "referencia del orden esperado en la literatura"),  # cumple el Criterio 1, sin referencia
        ("reves", "tres_cuartos", "referencia del orden esperado en la literatura"),
        ("drive", "tres_cuartos", "ni una validación propia"),  # ninguna de las dos
        ("reves", "perfil", "ni una validación propia"),
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
    assert par["severidad"] == "sin_evaluar" and porque in par["texto"] and par["referencia"] is None
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
        (0.2 + 1 / 240.0, "no_ordenable", None),       # exactamente 1 fotograma: dentro de la tolerancia (decisión 014)
        (0.2 + 2 / 240.0, "cadera_primero", True),     # 2 fotogramas (8,3 ms): ordenable
        (0.2 - 2 / 240.0, "tronco_primero", False),
    ],
)
def test_el_par_cadera_tronco_respeta_la_tolerancia_de_un_fotograma(t_torso, estado, veredicto):
    from app.ensamblar_reporte import _evaluar_par, _veredicto

    rep = _rep_con_picos(0.2, t_torso)
    assert _evaluar_par(rep).estado == estado
    assert _veredicto("saque", "perfil", rep) is veredicto


def test_una_simultaneidad_se_informa_como_no_auditable_y_no_como_sin_evaluar():
    """Decisión 015 (corrección del 29/9): 'no ordenable' es un motivo de no auditable, no un estado nuevo."""
    from app.ensamblar_reporte import _obs_par

    obs = _obs_par("saque", "perfil", [_rep_con_picos(0.2, 0.2 + 1 / 240.0)], True)
    assert obs["severidad"] == "no_auditable" and "casi al mismo tiempo" in obs["texto"]
    assert "4.2 ms" in obs["fundamento"]


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
    assert all(m["valor"] is None and m["auditable"] is False for m in datos["metricas"])
    assert any("escala temporal" in o["texto"] and o["severidad"] == "no_auditable" for o in datos["observaciones"])
    # el orden sí se documenta
    assert datos["secuenciacion"]["repeticiones"][0]["orden_observado"] == ["pelvis", "torso", "brazo"]


def test_las_metricas_de_velocidad_se_nombran_y_se_leen_de_vuelta(seq_ordenada):
    datos = _ensamblar(seq_ordenada)
    assert [m["nombre"] for m in datos["metricas"]] == [f"{PREFIJO_METRICA_VELOCIDAD}{s}" for s in ("pelvis", "torso", "brazo")]
    assert all(m["auditable"] and m["valor"] > 0 and m["unidad"] == "grados/s" for m in datos["metricas"])
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
