"""Etapa 1 de la decisión 038: validación de la detección automática del TIPO DE GOLPE y del ENCUADRE (sin tocar el producto).

Este módulo es un arnés de medición, como ``medicion_paso_b.py``: lee las poses ya cacheadas del corpus (Paso B, originales a tasa real,
regularizadas a 240 Hz), calcula unos pocos estadísticos por repetición con el MISMO camino del producto (regularizar → E3 → pico del tronco,
``encuadre.encuadre_visto``) y evalúa reglas simples con la partición pre-registrada: **los cortes se fijan en una sesión y se evalúan en la
otra** (24/9 ↔ 25/9). No lo importa ningún módulo del producto.

Reglas (fijadas ANTES de calcular cualquier acierto; ver ``docs/resultados/deteccion-038-etapa1.md``, "Qué se fijó antes de medir"):

* Todo se mide en la ventana de PREPARACIÓN (de 0,8 a 0,3 s antes del pico del tronco; la misma que usa el contraste de encuadre D) y en la de
  ACELERACIÓN (de 0,3 s antes del pico del tronco hasta el pico). Sin pico del tronco auditable no hay detección: "no determinado".
* Estadísticos (mano dominante conocida: es un dato del jugador, no se detecta):
    - ``s_saque``: fracción de fotogramas de la preparación con la muñeca dominante por encima de la nariz Y el codo dominante por encima
      del hombro dominante ("posición de trofeo");
    - ``c1_giro``: giro neto (°) de la línea de hombros alrededor de la vertical en la aceleración (de 0,3 s antes al pico), con el signo
      espejado para el zurdo; ``c2_munecas``: mediana de la distancia entre las dos muñecas en la aceleración, en anchos de hombros;
      ``c3_eje``: mediana de la posición lateral de la muñeca dominante respecto del centro de los hombros, medida sobre el eje de los
      hombros (positivo = del lado de la mano dominante), en anchos de hombros;
    - ``giro_hombros``: el contraste D (``encuadre.giro_hombros_grados``), tal cual lo usa el producto.
* Cortes: por **extremos observados** en la sesión de ajuste (como D con el saque: perfil ≤ P, tres cuartos ≥ T, entre ambos "no determinado").
  Gesto: primero saque contra el resto con ``s_saque``; después drive contra revés con la candidata (``c1``, ``c2``, ``c3``) que separe sin
  errores la sesión de ajuste y tenga la mayor brecha relativa; si ninguna separa, drive/revés queda "no determinado" (se pregunta).
  Encuadre: un par (P, T) por gesto, con el gesto DETECTADO (el producto no conoce el verdadero); con el gesto "no determinado" solo se
  afirma si el giro cae del mismo lado bajo los cortes de todos los gestos.

Salida: ``docs/resultados/deteccion-038-etapa1.json`` (todo por repetición y por pliegue) y la tabla de estadísticos por clase.

Uso (desde backend/):
    PYTHONPATH=. python -m app.medicion_deteccion --salida ../docs/resultados/deteccion-038-etapa1
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from app.engine.encuadre import (
    PERFIL_MAX_GRADOS,
    PREPARACION_DESDE_S,
    PREPARACION_HASTA_S,
    TRES_CUARTOS_MIN_GRADOS,
    giro_hombros_grados,
)
from app.engine.pose.articulaciones import ArticulacionCanonica as A

ACELERACION_DESDE_S = 0.3          # antes del pico del tronco
ACELERACION_HASTA_S = 0.0
MIN_FRACCION_VALIDA = 0.25         # de los fotogramas de una ventana (la misma proporción que D: 30 de 120)
MUESTRA_EXTREMOS_S = 0.05          # ancho de las muestras inicial y final del giro neto
GESTOS = ("saque", "drive", "reves")
ENCUADRES = ("perfil", "tres_cuartos")
CANDIDATAS = ("c1_giro", "c2_munecas", "c3_eje")
UMBRAL_ERROR = 0.05               # criterio de aceptación pre-registrado (decisión 038)
UMBRAL_NO_DETERMINADO = 0.20
SESIONES = (1, 2)

_PAT = re.compile(r"^(\d{8})_VCR_(saque|drive|reves)_(perfil|trescuartos)_240_")


# --- estadísticos por repetición (puros) ----------------------------------------------------------------------------------------


def _articulaciones(mano: str) -> dict[str, A]:
    if mano not in ("der", "izq"):
        raise ValueError(f"mano debe ser 'der' o 'izq' (se recibió {mano!r})")
    d, n = ("DER", "IZQ") if mano == "der" else ("IZQ", "DER")
    return {
        "muneca_d": A[f"MUNECA_{d}"], "codo_d": A[f"CODO_{d}"], "hombro_d": A[f"HOMBRO_{d}"],
        "muneca_n": A[f"MUNECA_{n}"], "hombro_n": A[f"HOMBRO_{n}"],
    }


def _xyz(frame: dict, art: A) -> np.ndarray | None:
    p = frame.get(art)
    if p is None or p.z is None:
        return None
    v = np.array([p.x, p.y, p.z], dtype=float)
    return v if np.all(np.isfinite(v)) else None


def _indices(frame_pico: int, fps: float, desde_s: float, hasta_s: float, n: int) -> range:
    a = frame_pico - int(round(desde_s * fps))
    b = frame_pico - int(round(hasta_s * fps))
    return range(max(0, a), min(n - 1, b) + 1)


def estadisticos(frames_mundo: list[dict], frame_pico_tronco: int, fps: float, mano: str = "der") -> dict[str, Any]:
    """Estadísticos de detección de UNA repetición, sobre la secuencia filtrada y regularizada que usa el producto.

    ``frames_mundo``: lista de ``{articulación: Punto}`` en metros (el eje y crece hacia abajo, como MediaPipe); ``frame_pico_tronco``: fotograma
    del pico del tronco. Cada valor es ``None`` si la ventana no tiene al menos ``MIN_FRACCION_VALIDA`` de fotogramas utilizables."""
    art = _articulaciones(mano)
    n = len(frames_mundo)
    prep = _indices(frame_pico_tronco, fps, PREPARACION_DESDE_S, PREPARACION_HASTA_S, n)
    acel = _indices(frame_pico_tronco, fps, ACELERACION_DESDE_S, ACELERACION_HASTA_S, n)
    signo = 1.0 if mano == "der" else -1.0

    # s_saque: muñeca dominante sobre la nariz y codo dominante sobre el hombro dominante (y crece hacia abajo).
    cumple = validos = 0
    for i in prep:
        f = frames_mundo[i]
        nariz = f.get(A.NARIZ)
        m, c, h = f.get(art["muneca_d"]), f.get(art["codo_d"]), f.get(art["hombro_d"])
        if nariz is None or m is None or c is None or h is None:
            continue
        validos += 1
        cumple += int(m.y < nariz.y and c.y < h.y)
    s_saque = cumple / validos if validos >= MIN_FRACCION_VALIDA * max(1, len(prep)) and validos > 0 else None

    # Aceleración: giro neto de la línea de hombros, distancia entre muñecas y posición lateral de la muñeca dominante.
    yaw, dist, lateral = [], [], []
    for i in acel:
        f = frames_mundo[i]
        hd, hn = _xyz(f, art["hombro_d"]), _xyz(f, art["hombro_n"])
        md, mn = _xyz(f, art["muneca_d"]), _xyz(f, art["muneca_n"])
        if hd is None or hn is None:
            continue
        ancho = float(np.linalg.norm(hd - hn))
        if ancho < 1e-6:
            continue
        d_der_izq = (hd - hn) if mano == "der" else (hn - hd)   # derecha − izquierda, anatómicas
        yaw.append(math.atan2(d_der_izq[2], d_der_izq[0]))
        if md is not None and mn is not None:
            dist.append(float(np.linalg.norm(md - mn)) / ancho)
        if md is not None:
            u = (hd - hn) / ancho
            lateral.append(float(np.dot(md - 0.5 * (hd + hn), u)) / ancho)
    minimo = MIN_FRACCION_VALIDA * max(1, len(acel))
    c1 = c2 = c3 = None
    k = max(1, int(round(MUESTRA_EXTREMOS_S * fps)))
    if len(yaw) >= max(minimo, 2 * k):
        ang = np.unwrap(np.array(yaw))
        neto = float(np.median(ang[-k:]) - np.median(ang[:k]))
        c1 = float(np.degrees(((neto + math.pi) % (2 * math.pi)) - math.pi)) * signo
    if len(dist) >= minimo and dist:
        c2 = float(np.median(dist))
    if len(lateral) >= minimo and lateral:
        c3 = float(np.median(lateral))

    giro = giro_hombros_grados(frames_mundo, prep.start, prep.stop - 1) if len(prep) else None
    return {"s_saque": s_saque, "c1_giro": c1, "c2_munecas": c2, "c3_eje": c3, "giro_hombros": giro}


# --- cortes, decisión y evaluación (puros) --------------------------------------------------------------------------------------


def ajustar_cortes(baja: list[float], alta: list[float]) -> dict[str, Any]:
    """Cortes por extremos observados: ``baja`` ≤ ``p`` y ``alta`` ≥ ``t``; entre ambos, "no determinado".

    ``separable`` es verdadero si el mayor valor de ``baja`` queda por debajo del menor de ``alta`` (0 errores en la sesión de ajuste)."""
    if not baja or not alta:
        return {"p": None, "t": None, "separable": False, "brecha": None, "n_baja": len(baja), "n_alta": len(alta)}
    p, t = max(baja), min(alta)
    return {
        "p": float(p), "t": float(t), "separable": bool(p < t), "brecha": float(t - p), "n_baja": len(baja), "n_alta": len(alta),
        "mediana_baja": float(statistics.median(baja)), "mediana_alta": float(statistics.median(alta)),
    }


def decidir(valor: float | None, cortes: dict[str, Any] | None) -> str | None:
    """``"baja"``, ``"alta"`` o ``None`` (sin dato, sin cortes o en la franja en que no se afirma nada)."""
    if valor is None or cortes is None or cortes.get("p") is None:
        return None
    p, t = cortes["p"], cortes["t"]
    if cortes["separable"]:
        return "baja" if valor <= p else "alta" if valor >= t else None
    return "baja" if valor < t else "alta" if valor > p else None   # solapadas: lo que cae en [t, p] no se afirma


def ajustar_gesto(filas: list[dict]) -> dict[str, Any]:
    """Cortes del gesto con las filas de UNA sesión (cada fila: ``gesto`` verdadero y estadísticos)."""
    con = [f for f in filas if f.get("s_saque") is not None]
    saque = ajustar_cortes([f["s_saque"] for f in con if f["gesto"] != "saque"], [f["s_saque"] for f in con if f["gesto"] == "saque"])
    cand: dict[str, dict] = {}
    for nombre in CANDIDATAS:
        d = [f[nombre] for f in filas if f["gesto"] == "drive" and f.get(nombre) is not None]
        r = [f[nombre] for f in filas if f["gesto"] == "reves" and f.get(nombre) is not None]
        if not d or not r:
            cand[nombre] = {"separable": False, "p": None, "t": None, "brecha": None}
            continue
        drive_es_alta = statistics.median(d) >= statistics.median(r)
        c = ajustar_cortes(r if drive_es_alta else d, d if drive_es_alta else r)
        c["alta"] = "drive" if drive_es_alta else "reves"
        c["baja"] = "reves" if drive_es_alta else "drive"
        sep = abs(c["mediana_alta"] - c["mediana_baja"])
        c["brecha_relativa"] = (c["brecha"] / sep) if sep > 0 else None
        cand[nombre] = c
    separables = {k: v for k, v in cand.items() if v.get("separable")}
    elegida = max(separables, key=lambda k: separables[k]["brecha_relativa"] or 0.0) if separables else None
    return {"saque": saque, "candidatas": cand, "elegida": elegida}


def detectar_gesto(est: dict | None, ajuste: dict[str, Any]) -> tuple[str | None, str]:
    """``(gesto | None, motivo)``. ``est`` es ``None`` si no hubo pico del tronco."""
    if est is None:
        return None, "sin pico del tronco"
    paso1 = decidir(est.get("s_saque"), ajuste["saque"])
    if paso1 is None:
        return None, "ni saque ni resto: sin dato o en la franja"
    if paso1 == "alta":
        return "saque", "trofeo sostenido"
    elegida = ajuste["elegida"]
    if elegida is None:
        return None, "ninguna candidata separa drive de revés en la sesión de ajuste"
    c = ajuste["candidatas"][elegida]
    paso2 = decidir(est.get(elegida), c)
    if paso2 is None:
        return None, f"{elegida} sin dato o en la franja"
    return (c["alta"] if paso2 == "alta" else c["baja"]), elegida


def ajustar_encuadre(filas: list[dict]) -> dict[str, dict]:
    """Un par de cortes (perfil ≤ P, tres cuartos ≥ T) por gesto, con el gesto VERDADERO de la sesión de ajuste."""
    sal = {}
    for g in GESTOS:
        sub = [f for f in filas if f["gesto"] == g and f.get("giro_hombros") is not None]
        sal[g] = ajustar_cortes(
            [f["giro_hombros"] for f in sub if f["encuadre"] == "perfil"],
            [f["giro_hombros"] for f in sub if f["encuadre"] == "tres_cuartos"],
        )
    return sal


def detectar_encuadre(est: dict | None, gesto: str | None, ajuste_enc: dict[str, dict]) -> str | None:
    if est is None or est.get("giro_hombros") is None:
        return None
    giro = est["giro_hombros"]
    nombre = {"baja": "perfil", "alta": "tres_cuartos"}
    if gesto is not None:
        return nombre.get(decidir(giro, ajuste_enc.get(gesto)) or "")
    posibles = {decidir(giro, ajuste_enc.get(g)) for g in GESTOS}
    return nombre.get(next(iter(posibles))) if len(posibles) == 1 and None not in posibles else None


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float] | None:
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def resumen(pares: list[tuple[str, str | None]], clases: tuple[str, ...]) -> dict[str, Any]:
    """Matriz de confusión (verdad × predicho, con columna ``no_determinado``), error entre los determinados y % de no determinado."""
    matriz = {v: {c: 0 for c in (*clases, "no_determinado")} for v in clases}
    for v, p in pares:
        matriz[v][p if p is not None else "no_determinado"] += 1
    n = len(pares)
    nd = sum(1 for _, p in pares if p is None)
    det = n - nd
    err = sum(1 for v, p in pares if p is not None and p != v)
    ic = wilson(err, det)
    ic_nd = wilson(nd, n)
    return {
        "n": n, "determinados": det, "aciertos": det - err, "errores": err, "no_determinados": nd,
        "error_entre_determinados": (err / det) if det else None,
        "error_ic95": None if ic is None else [round(ic[0], 4), round(ic[1], 4)],
        "no_determinado_pct": (nd / n) if n else None,
        "no_determinado_ic95": None if ic_nd is None else [round(ic_nd[0], 4), round(ic_nd[1], 4)],
        "acierto_sobre_todas": ((det - err) / n) if n else None,
        "cumple": bool(det > 0 and err / det <= UMBRAL_ERROR and nd / n <= UMBRAL_NO_DETERMINADO),
        "matriz": matriz,
    }


# --- corrida --------------------------------------------------------------------------------------------------------------------


def _estadisticos_de_cache(base: Path, nombre: str, mano: str) -> tuple[dict | None, dict]:
    from app.engine.ingest import normalizar_fps
    from app.engine.pose import cache as pose_cache
    from app.engine.regularizacion import regularizar
    from app.engine.segmentos_corporales import SegmentoCadena as S
    from app.medicion_paso_a import _picos

    seq = pose_cache.cargar(base / nombre)
    pts = np.load(base / f"{nombre}.pts.npy")
    seq_reg, info = regularizar(seq, pts, normalizar_fps(1.0 / float(np.median(np.diff(pts)))))
    b, error = _picos(seq_reg, mano)
    traza = {"fps_grilla": info.fps_grilla}
    if b is None:
        return None, {**traza, "motivo": error}
    pico = b["rep"].picos.get(S.TORSO)
    if pico is None or not pico.auditable:
        return None, {**traza, "motivo": "pico del tronco no auditable"}
    frames = [f.puntos_mundo for f in b["filt"].secuencia.frames]
    est = estadisticos(frames, pico.frame, float(b["fps"]), mano)
    return est, {**traza, "frame_pico_tronco": int(pico.frame), "motivo": None}


def construir_filas(base: Path, mano: str, nombres: list[str] | None = None) -> list[dict]:
    todos = sorted({p.name.split(".")[0] for p in base.glob("*.pose.json")})
    fechas = sorted({n[:8] for n in todos})
    filas = []
    t0 = time.monotonic()
    for i, nombre in enumerate(todos):
        if nombres is not None and nombre not in nombres:
            continue
        m = _PAT.match(nombre)
        if not m:
            continue
        est, traza = _estadisticos_de_cache(base, nombre, mano)
        filas.append({
            "repeticion": nombre, "sesion": fechas.index(m.group(1)) + 1, "fecha": m.group(1),
            "gesto": m.group(2), "encuadre": "tres_cuartos" if m.group(3) == "trescuartos" else "perfil",
            "con_pico": est is not None, **(est or {k: None for k in ("s_saque", *CANDIDATAS, "giro_hombros")}), **traza,
        })
        print(f"[{(time.monotonic() - t0) / 60:5.1f} min] {i + 1}/{len(todos)} {nombre}", flush=True)
    return filas


def evaluar_pliegue(filas: list[dict], sesion_ajuste: int) -> dict[str, Any]:
    ajuste_f = [f for f in filas if f["sesion"] == sesion_ajuste and f["con_pico"]]
    prueba = [f for f in filas if f["sesion"] != sesion_ajuste]
    aj_g = ajustar_gesto(ajuste_f)
    aj_e = ajustar_encuadre(ajuste_f)
    detalle = []
    for f in prueba:
        est = {k: f[k] for k in ("s_saque", *CANDIDATAS, "giro_hombros")} if f["con_pico"] else None
        g, motivo_g = detectar_gesto(est, aj_g)
        enc_dado_verdadero = detectar_encuadre(est, f["gesto"], aj_e)
        enc_detectado = detectar_encuadre(est, g, aj_e)
        detalle.append({
            "repeticion": f["repeticion"], "sesion": f["sesion"], "gesto": f["gesto"], "encuadre": f["encuadre"],
            "gesto_detectado": g, "motivo_gesto": motivo_g, "encuadre_con_gesto_verdadero": enc_dado_verdadero,
            "encuadre_con_gesto_detectado": enc_detectado, "con_pico": f["con_pico"],
        })
    return {"sesion_ajuste": sesion_ajuste, "sesion_evaluacion": 3 - sesion_ajuste, "ajuste_gesto": aj_g, "ajuste_encuadre": aj_e, "detalle": detalle}


def resumir_evaluacion(detalle: list[dict]) -> dict[str, Any]:
    sal: dict[str, Any] = {
        "gesto": resumen([(d["gesto"], d["gesto_detectado"]) for d in detalle], GESTOS),
        "gesto_por_verdad": {g: resumen([(d["gesto"], d["gesto_detectado"]) for d in detalle if d["gesto"] == g], GESTOS) for g in GESTOS},
        "encuadre_con_gesto_verdadero": resumen([(d["encuadre"], d["encuadre_con_gesto_verdadero"]) for d in detalle], ENCUADRES),
        "encuadre_con_gesto_detectado": resumen([(d["encuadre"], d["encuadre_con_gesto_detectado"]) for d in detalle], ENCUADRES),
        "encuadre_por_gesto_con_gesto_verdadero": {},
        "encuadre_por_gesto_con_gesto_detectado": {},
    }
    for g in GESTOS:
        sub = [d for d in detalle if d["gesto"] == g]
        sal["encuadre_por_gesto_con_gesto_verdadero"][g] = resumen([(d["encuadre"], d["encuadre_con_gesto_verdadero"]) for d in sub], ENCUADRES)
        sal["encuadre_por_gesto_con_gesto_detectado"][g] = resumen([(d["encuadre"], d["encuadre_con_gesto_detectado"]) for d in sub], ENCUADRES)
    return sal


def descriptivo(filas: list[dict]) -> dict[str, Any]:
    """Mínimo, mediana y máximo de cada estadístico por sesión, gesto y encuadre (para el capítulo; no decide nada)."""
    out: dict[str, Any] = {}
    for s in SESIONES:
        for g in GESTOS:
            for e in ENCUADRES:
                sub = [f for f in filas if f["sesion"] == s and f["gesto"] == g and f["encuadre"] == e]
                celda: dict[str, Any] = {"n": len(sub), "con_pico": sum(1 for f in sub if f["con_pico"])}
                for k in ("s_saque", *CANDIDATAS, "giro_hombros"):
                    v = [f[k] for f in sub if f.get(k) is not None]
                    celda[k] = None if not v else {"n": len(v), "min": round(min(v), 3), "mediana": round(statistics.median(v), 3), "max": round(max(v), 3)}
                out[f"s{s}|{g}|{e}"] = celda
    return out


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Etapa 1 de la decisión 038: validación de la detección de tipo de golpe y encuadre.")
    ap.add_argument("--salida", type=Path, required=True, help="prefijo: escribe <prefijo>.json y <prefijo>-estadisticos.json")
    ap.add_argument("--mano", default="der", choices=("der", "izq"))
    ap.add_argument("--reusar", action="store_true", help="usa <prefijo>-estadisticos.json si existe (no recalcula las poses)")
    ap.add_argument("--permitir-sucio", action="store_true", help="NO usar para la medición formal")
    args = ap.parse_args(argv)

    from app.config import get_cache_dir
    from app.engine.version import __version__ as version_motor
    from app.medicion_paso_a import _git

    repo = Path(__file__).resolve().parents[2]
    sucio = _git(["status", "--porcelain", "--", "backend/app", "tests", "docs/decisiones"], repo)
    if sucio and not args.permitir_sucio:
        print("El árbol de git tiene cambios sin commitear en backend/app, tests o docs/decisiones:\n" + sucio)
        return 2
    commit = _git(["rev-parse", "HEAD"], repo)

    destino_est = Path(f"{args.salida}-estadisticos.json")
    if args.reusar and destino_est.exists():
        filas = json.loads(destino_est.read_text(encoding="utf-8"))["repeticiones"]
    else:
        filas = construir_filas(get_cache_dir() / "corpus-real-pose-b", args.mano)
        destino_est.parent.mkdir(parents=True, exist_ok=True)
        destino_est.write_text(json.dumps({"commit": commit, "repeticiones": filas}, ensure_ascii=False, indent=1), encoding="utf-8")

    pliegues = [evaluar_pliegue(filas, s) for s in SESIONES]
    detalle = [d for p in pliegues for d in p["detalle"]]
    resultado = {
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "decision": "038 (etapa 1: validación, sin tocar el producto)",
        "version_motor": version_motor, "commit": commit, "arbol_sucio": bool(sucio), "mano_dominante": args.mano,
        "criterio": {"error_entre_determinados_max": UMBRAL_ERROR, "no_determinado_max": UMBRAL_NO_DETERMINADO},
        "reglas_contraste_saque_vigente": {"perfil_max": PERFIL_MAX_GRADOS, "tres_cuartos_min": TRES_CUARTOS_MIN_GRADOS},
        "repeticiones": len(filas), "con_pico_del_tronco": sum(1 for f in filas if f["con_pico"]),
        "pliegues": [
            {**{k: v for k, v in p.items() if k != "detalle"}, "resumen": resumir_evaluacion(p["detalle"])} for p in pliegues
        ],
        "agregado": resumir_evaluacion(detalle),
        "detalle": detalle,
        "descriptivo": descriptivo(filas),
    }
    destino = Path(f"{args.salida}.json")
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
