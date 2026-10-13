"""Consistencia entre los golpes de una sesión — paso 3 del plan §8, ``docs/ux/valor-sin-veredictos.md`` §3.2.

Función **pura**: recibe los reportes ya calculados de los golpes de una sesión y devuelve un resumen. No toca la base, ni archivos, ni el
reloj; no recalcula nada biomecánico (usa lo que cada reporte ya trae). No emite veredicto: describe cuánto se parecen los golpes **entre
sí** (decisiones 035 y 036: el orden cadera → tronco no se evalúa, solo se informa si fue el mismo).

Qué devuelve y con qué regla:

* **Golpes**: cuántos se **midieron** (cadera y tronco con pico y confianza suficiente, **aunque empaten**: decisión 037), cuántos no se
  pudieron medir y cuántos siguen en análisis; y, aparte, en cuántos de los medidos el orden es **distinguible** (más de la tolerancia).
* **Separación cadera-hombro máxima** (°), mediana y dispersión robusta (MAD × 1,4826, la regla de la decisión 014). La dispersión solo
  se da con ``MIN_GOLPES_DISPERSION`` golpes o más: con menos, una desviación no describe nada.
* **Repetibilidad del orden**: de los golpes en que cadera y tronco son *ordenables* (más de 8,33 ms, decisión 032), en cuántos fue el
  mismo orden. Es el Criterio 1b del proyecto. Mide si fue **el mismo**, no cuál es el correcto. Se da con ``MIN_ORDENABLES_REPETIBILIDAD``
  o más.
* **Golpe típico**: el más cercano a la mediana de la separación (representativo; no "el mejor").
* **Golpes que se apartan**: los que están a más de ``UMBRAL_APARTA`` desviaciones robustas de la mediana (con ``MIN_GOLPES_APARTA`` o más).
  Se informan como "se parecieron menos a los demás", sin decir que estén mal: puede ser el golpe o la medición.
* **Motores**: las versiones de motor que calcularon los reportes; si hay más de una, la comparación mezcla versiones y se declara.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from app.engine.tolerancia_orden import TOLERANCIA_ORDEN_S, es_ordenable
from app.ensamblar_reporte import par_medido

VERSION_REGLA = "1"

ESTADOS_EN_CURSO = ("pendiente", "encolado", "procesando")

MIN_GOLPES_DISPERSION = 4
MIN_ORDENABLES_REPETIBILIDAD = 5
MIN_GOLPES_APARTA = 5
UMBRAL_APARTA = 3.0          # desviaciones robustas de la mediana
PISO_DISPERSION_GRADOS = 1.0  # piso para el umbral: con golpes casi idénticos, 3 × ~0° marcaría ruido de medición

_METRICA_SEPARACION = "separacion_cadera_hombro_max"


def _mad_robusta(valores: list[float]) -> float:
    """MAD × 1,4826 (equivale al desvío estándar en una normal). Mismo criterio que ``medicion_criterio3``."""
    med = _mediana(valores)
    return 1.4826 * _mediana([abs(v - med) for v in valores])


def _mediana(valores: list[float]) -> float:
    s = sorted(valores)
    n = len(s)
    mitad = n // 2
    return s[mitad] if n % 2 else (s[mitad - 1] + s[mitad]) / 2.0


def _repeticiones(reporte: dict[str, Any] | None) -> list[dict[str, Any]]:
    reps = ((reporte or {}).get("secuenciacion") or {}).get("repeticiones")
    return [r for r in reps if isinstance(r, dict)] if isinstance(reps, list) else []


def _medido(reporte: dict[str, Any] | None) -> bool:
    """Los picos de cadera y tronco se midieron con confianza suficiente (aunque empaten): ``ensamblar_reporte.par_medido``."""
    return any(par_medido(r) for r in _repeticiones(reporte))


def _separacion(reporte: dict[str, Any] | None) -> float | None:
    for m in (reporte or {}).get("metricas") or []:
        if isinstance(m, dict) and m.get("nombre") == _METRICA_SEPARACION and m.get("auditable") is True:
            v = m.get("valor")
            if isinstance(v, (int, float)) and math.isfinite(v):
                return float(v)
    return None


def _orden_del_par(reporte: dict[str, Any] | None) -> tuple[str, ...] | None:
    """Orden de cadera y tronco del golpe (de su primera repetición auditable), o ``None`` si no es ordenable o no se midió."""
    tolerancia_ms = ((reporte or {}).get("trazabilidad") or {}).get("tolerancia_orden_ms")
    tolerancia_s = float(tolerancia_ms) / 1000.0 if isinstance(tolerancia_ms, (int, float)) and tolerancia_ms > 0 else TOLERANCIA_ORDEN_S
    for rep in _repeticiones(reporte):
        if not par_medido(rep):
            continue
        instantes: dict[str, float] = {}
        for p in rep.get("picos") or []:
            if isinstance(p, dict) and isinstance(p.get("instante_s"), (int, float)) and p.get("segmento") in ("pelvis", "torso"):
                instantes[p["segmento"]] = float(p["instante_s"])
        if "pelvis" not in instantes or "torso" not in instantes:
            return None
        delta = instantes["torso"] - instantes["pelvis"]
        if not es_ordenable(delta, tolerancia_s):
            return None
        return ("pelvis", "torso") if delta > 0 else ("torso", "pelvis")
    return None


def resumen_de_sesion(golpes: list[dict[str, Any]]) -> dict[str, Any]:
    """``golpes``: una fila por video con ``video_id``, ``estado`` y ``reporte`` (``dict`` o ``None``).

    Devuelve un ``dict`` serializable (ver ``schemas.api.RespuestaConsistencia``)."""
    medidos: list[dict[str, Any]] = []
    no_medibles = 0
    en_analisis = 0
    for g in golpes:
        if g.get("estado") in ESTADOS_EN_CURSO:
            en_analisis += 1
        elif _medido(g.get("reporte")):
            medidos.append(g)
        else:
            no_medibles += 1

    # --- separación cadera-hombro -----------------------------------------------------------------------------------------
    valores = [(g["video_id"], v) for g in medidos if (v := _separacion(g.get("reporte"))) is not None]
    nums = [v for _, v in valores]
    separacion: dict[str, Any] = {
        "n": len(nums),
        "unidad": "grados",
        "mediana": round(_mediana(nums), 2) if nums else None,
        "dispersion": round(_mad_robusta(nums), 2) if len(nums) >= MIN_GOLPES_DISPERSION else None,
        "minimo": round(min(nums), 2) if nums else None,
        "maximo": round(max(nums), 2) if nums else None,
        "valores": [{"video_id": vid, "valor": round(v, 2)} for vid, v in valores],
    }

    # --- repetibilidad del orden -------------------------------------------------------------------------------------------
    ordenes = [o for g in medidos if (o := _orden_del_par(g.get("reporte"))) is not None]
    modal, k = (Counter(ordenes).most_common(1)[0] if ordenes else (None, 0))
    orden = {
        "medidos": len(medidos),
        "ordenables": len(ordenes),
        "mismo_orden": k,
        "orden_modal": list(modal) if modal else None,
        "suficiente": len(ordenes) >= MIN_ORDENABLES_REPETIBILIDAD,
    }

    # --- golpe típico y golpes que se apartan ---------------------------------------------------------------------------------
    tipico = None
    se_apartan: list[str] = []
    if nums:
        med = _mediana(nums)
        tipico = min(valores, key=lambda t: (abs(t[1] - med), t[0]))[0]
        if len(nums) >= MIN_GOLPES_APARTA:
            sigma = max(_mad_robusta(nums), PISO_DISPERSION_GRADOS)
            se_apartan = [vid for vid, v in valores if abs(v - med) > UMBRAL_APARTA * sigma]

    versiones = sorted({
        str(((g.get("reporte") or {}).get("trazabilidad") or {}).get("version_motor"))
        for g in medidos
        if ((g.get("reporte") or {}).get("trazabilidad") or {}).get("version_motor")
    })

    return {
        "version_regla": VERSION_REGLA,
        "golpes": {
            "total": len(golpes),
            "medidos": len(medidos),
            "no_medibles": no_medibles,
            "en_analisis": en_analisis,
            "con_orden_distinguible": len(ordenes),
        },
        "separacion_cadera_hombro": separacion,
        "orden": orden,
        "golpe_tipico": tipico,
        "golpes_que_se_apartan": se_apartan,
        "versiones_motor": versiones,
        "mezcla_de_versiones": len(versiones) > 1,
        "minimos": {
            "dispersion": MIN_GOLPES_DISPERSION,
            "repetibilidad": MIN_ORDENABLES_REPETIBILIDAD,
            "se_apartan": MIN_GOLPES_APARTA,
        },
    }


# --- Evolución: la misma consistencia, sesión por sesión ---------------------------------------------------------------------------------


def serie_de_evolucion(sesiones: list[dict[str, Any]]) -> dict[str, Any]:
    """La serie de sesiones de un mismo jugador, golpe y encuadre (paso 6 del plan §8, ``docs/ux/valor-sin-veredictos.md`` §3.3).

    ``sesiones``: en orden cronológico, cada una con ``sesion_id``, ``fecha``, ``lado_camara`` y ``golpes`` (como ``resumen_de_sesion``).
    Cada sesión se resume con la MISMA función que la vista de sesión: no hay una segunda definición de "medido" ni de "mismo orden".

    No juzga: informa el cambio entre las dos últimas sesiones y lo compara con la variación habitual del propio jugador (la media de las
    dispersiones robustas de sus sesiones), en la misma lógica del Criterio 3 (Δ ≤ σ_w = "dentro de lo habitual"). No dice si el cambio es
    para bien o para mal: no hay referencia para eso."""
    filas = []
    for s in sesiones:
        r = resumen_de_sesion(s["golpes"])
        filas.append(
            {
                "sesion_id": s["sesion_id"],
                "fecha": str(s["fecha"]),
                "lado_camara": s.get("lado_camara"),
                "golpes": r["golpes"],
                "separacion_cadera_hombro": r["separacion_cadera_hombro"],
                "orden": r["orden"],
                "versiones_motor": r["versiones_motor"],
                "golpes_que_se_apartan": len(r["golpes_que_se_apartan"]),
            }
        )

    dispersiones = [f["separacion_cadera_hombro"]["dispersion"] for f in filas if f["separacion_cadera_hombro"]["dispersion"] is not None]
    variacion = round(sum(dispersiones) / len(dispersiones), 2) if dispersiones else None

    con_dato = [f for f in filas if f["separacion_cadera_hombro"]["mediana"] is not None]
    cambio = None
    if len(con_dato) >= 2:
        antes, ahora = con_dato[-2], con_dato[-1]
        delta = round(ahora["separacion_cadera_hombro"]["mediana"] - antes["separacion_cadera_hombro"]["mediana"], 2)
        cambio = {
            "anterior": antes["separacion_cadera_hombro"]["mediana"],
            "actual": ahora["separacion_cadera_hombro"]["mediana"],
            "delta": delta,
            "dentro_de_lo_habitual": (abs(delta) <= variacion) if variacion is not None else None,
        }

    medianas = [f["separacion_cadera_hombro"]["mediana"] for f in con_dato]
    versiones = sorted({v for f in filas for v in f["versiones_motor"]})
    lados = sorted({f["lado_camara"] for f in filas if f["lado_camara"]})
    return {
        "version_regla": VERSION_REGLA,
        "sesiones": filas,
        "variacion_habitual": variacion,
        "centro_habitual": round(_mediana(medianas), 2) if len(medianas) >= 3 else None,
        "cambio_separacion": cambio,
        "lados_de_camara": lados,
        "versiones_motor": versiones,
        "mezcla_de_versiones": len(versiones) > 1,
    }
