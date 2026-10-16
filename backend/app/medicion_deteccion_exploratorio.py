"""Decisión 038, etapa 1 — análisis EXPLORATORIO POSTERIOR (post hoc, NO pre-registrado, NO cuenta para el criterio de aceptación).

Después de la corrida formal (``medicion_deteccion.py``, commit ``fee1003``) la regla pre-registrada del saque dio ``s_saque = 0`` en todos los saques con dato y
las reglas de drive contra revés y de encuadre para drive y revés no separaron las dos sesiones por extremos observados. Este módulo mira **por qué** y si hay
una señal que valga la pena **validar con datos nuevos**. Lo que sale de acá **se diseñó viendo ambas sesiones**: es optimista por construcción y no puede
usarse para decir que la detección "cumple". Sirve para decidir qué grabar y qué reglas probar después, no para el producto.

Qué se fijó antes de correr este análisis (escrito en el commit, antes de ver sus números):

* ``x_muneca_alta``: fracción de fotogramas con dato, de 0,15 s antes a 0,10 s después del pico del tronco, con la muñeca dominante por encima de la nariz
  (el momento del contacto, no la preparación); se exige el 25 % de la ventana con dato.
* Corte "por la mitad de las medianas": entre la mediana de cada clase en la sesión de ajuste (sin franja de "no determinado": todo se decide). Mide separabilidad,
  no cobertura.
* Orientación del encuadre por gesto: la que tenga la mediana de ajuste (en el contraste D, el revés queda invertido respecto del saque).
* Las mismas dos particiones (ajuste 24/9 → evaluación 25/9 y al revés).

Uso (desde backend/; la primera vez recalcula las series filtradas, ~25 min):
    PYTHONPATH=. python -m app.medicion_deteccion_exploratorio --salida ../docs/resultados/deteccion-038-etapa1-exploratorio
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import Punto
from app.medicion_deteccion import (
    _PAT,
    CANDIDATAS,
    ENCUADRES,
    GESTOS,
    MIN_FRACCION_VALIDA,
    SESIONES,
    estadisticos,
    resumen,
)

ARTS = (A.NARIZ, A.HOMBRO_IZQ, A.HOMBRO_DER, A.CODO_IZQ, A.CODO_DER, A.MUNECA_IZQ, A.MUNECA_DER, A.CADERA_IZQ, A.CADERA_DER)
CONTACTO_DESDE_S = 0.15            # antes del pico del tronco
CONTACTO_HASTA_S = -0.10           # (negativo: después)


def frames_desde_series(series: dict[str, np.ndarray]) -> list[dict]:
    """Reconstruye ``frames_mundo`` (lista de ``{articulación: Punto}``) desde los arrays guardados (NaN = sin dato)."""
    n = len(next(iter(series.values())))
    frames: list[dict] = []
    for i in range(n):
        f = {}
        for art in ARTS:
            v = series[art.value][i]
            if np.all(np.isfinite(v)):
                f[art] = Punto(float(v[0]), float(v[1]), float(v[2]), 0.9)
        frames.append(f)
    return frames


def muneca_alta_en_contacto(frames_mundo: list[dict], frame_pico: int, fps: float, mano: str = "der") -> float | None:
    """Fracción de fotogramas con dato, alrededor del pico del tronco, con la muñeca dominante por encima de la nariz (y crece hacia abajo)."""
    muneca = A.MUNECA_DER if mano == "der" else A.MUNECA_IZQ
    a = frame_pico - int(round(CONTACTO_DESDE_S * fps))
    b = frame_pico - int(round(CONTACTO_HASTA_S * fps))
    idx = range(max(0, a), min(len(frames_mundo) - 1, b) + 1)
    validos = cumple = 0
    for i in idx:
        nariz, m = frames_mundo[i].get(A.NARIZ), frames_mundo[i].get(muneca)
        if nariz is None or m is None:
            continue
        validos += 1
        cumple += int(m.y < nariz.y)
    if not validos or validos < MIN_FRACCION_VALIDA * max(1, len(idx)):
        return None
    return cumple / validos


def corte_mitad(baja: list[float], alta: list[float]) -> float | None:
    """Corte entre las medianas de cada clase (``None`` si falta una clase)."""
    if not baja or not alta:
        return None
    return 0.5 * (statistics.median(baja) + statistics.median(alta))


def decidir_mitad(valor: float | None, corte: float | None, alta_es_mayor: bool) -> bool | None:
    """``True`` = clase alta; ``False`` = clase baja; ``None`` = sin dato."""
    if valor is None or corte is None:
        return None
    return (valor >= corte) if alta_es_mayor else (valor < corte)


def evaluar_binaria(filas: list[dict], clave: str, verdad_alta: str, campo_verdad: str, sesion_ajuste: int, universo=None) -> dict:
    """Corte por la mitad de las medianas, ajustado en ``sesion_ajuste`` y evaluado en la otra; ``verdad_alta`` es el valor de ``campo_verdad`` de la clase alta."""
    aj = [f for f in filas if f["sesion"] == sesion_ajuste and f.get(clave) is not None and (universo is None or universo(f))]
    clases = [f[campo_verdad] for f in aj]
    otras = sorted(set(clases) - {verdad_alta})
    if verdad_alta not in clases or not otras:
        return {"corte": None, "pares": []}
    alta = [f[clave] for f in aj if f[campo_verdad] == verdad_alta]
    baja = [f[clave] for f in aj if f[campo_verdad] != verdad_alta]
    corte = corte_mitad(baja, alta)
    alta_mayor = statistics.median(alta) >= statistics.median(baja)
    pares = []
    for f in filas:
        if f["sesion"] == sesion_ajuste or (universo is not None and not universo(f)):
            continue
        d = decidir_mitad(f.get(clave), corte, alta_mayor)
        pares.append((f[campo_verdad], None if d is None else (verdad_alta if d else otras[0]), f["repeticion"]))
    return {"corte": corte, "alta_es_mayor": alta_mayor, "pares": pares}


def _ambas_particiones(filas, clave, verdad_alta, campo_verdad, universo=None):
    pares, cortes = [], {}
    for s in SESIONES:
        r = evaluar_binaria(filas, clave, verdad_alta, campo_verdad, s, universo)
        cortes[f"ajuste_s{s}"] = None if r["corte"] is None else round(r["corte"], 4)
        pares += [(v, p) for v, p, _ in r["pares"]]
    return pares, cortes


def exploratorio(filas: list[dict]) -> dict[str, Any]:
    sal: dict[str, Any] = {}
    # 1) saque contra el resto con la muñeca alta en el contacto
    pares, cortes = _ambas_particiones(filas, "x_muneca_alta", "saque", "gesto")
    pares = [(("saque" if v == "saque" else "resto"), (None if p is None else ("saque" if p == "saque" else "resto"))) for v, p in pares]
    sal["saque_contra_resto_muneca_alta_en_contacto"] = {"cortes": cortes, **resumen(pares, ("saque", "resto"))}
    # 2) drive contra revés (solo entre los golpes que no son saque), una candidata por vez
    for k in CANDIDATAS:
        pares, cortes = _ambas_particiones(filas, k, "drive", "gesto", universo=lambda f: f["gesto"] != "saque")
        sal[f"drive_contra_reves_{k}"] = {"cortes": cortes, **resumen(pares, ("drive", "reves"))}
    # 3) encuadre por gesto, con el gesto verdadero y la orientación por la mediana de ajuste
    for g in GESTOS:
        pares, cortes = _ambas_particiones(filas, "giro_hombros", "tres_cuartos", "encuadre", universo=lambda f, g=g: f["gesto"] == g)
        sal[f"encuadre_{g}_giro_hombros"] = {"cortes": cortes, **resumen(pares, ENCUADRES)}
    return sal


def volcar_series(base: Path, destino: Path, mano: str) -> None:
    """Guarda, por repetición, las series filtradas (las que usa el producto) de las articulaciones de interés y el pico del tronco."""
    from app.engine.ingest import normalizar_fps
    from app.engine.pose import cache as pose_cache
    from app.engine.regularizacion import regularizar
    from app.engine.segmentos_corporales import SegmentoCadena as S
    from app.medicion_paso_a import _picos

    destino.mkdir(parents=True, exist_ok=True)
    nombres = sorted({p.name.split(".")[0] for p in base.glob("*.pose.json")})
    t0 = time.monotonic()
    for i, nombre in enumerate(nombres):
        salida = destino / f"{nombre}.npz"
        if salida.exists():
            continue
        seq = pose_cache.cargar(base / nombre)
        pts = np.load(base / f"{nombre}.pts.npy")
        seq_reg, _ = regularizar(seq, pts, normalizar_fps(1.0 / float(np.median(np.diff(pts)))))
        b, _ = _picos(seq_reg, mano)
        pico = None if b is None else b["rep"].picos.get(S.TORSO)
        if b is None or pico is None or not pico.auditable:
            np.savez_compressed(salida, pico=-1, fps=240.0)
            continue
        frames = [f.puntos_mundo for f in b["filt"].secuencia.frames]
        datos = {
            art.value: np.array([[p.x, p.y, np.nan if p.z is None else p.z] if (p := f.get(art)) is not None else [np.nan] * 3 for f in frames], dtype=float)
            for art in ARTS
        }
        np.savez_compressed(salida, pico=int(pico.frame), fps=float(b["fps"]), **datos)
        print(f"[{(time.monotonic() - t0) / 60:5.1f} min] {i + 1}/{len(nombres)} {nombre}", flush=True)


def filas_desde_series(destino: Path, mano: str) -> list[dict]:
    fechas = sorted({p.name[:8] for p in destino.glob("*.npz")})
    filas = []
    for ruta in sorted(destino.glob("*.npz")):
        m = _PAT.match(ruta.stem)
        if not m:
            continue
        z = np.load(ruta)
        pico = int(z["pico"])
        fila = {
            "repeticion": ruta.stem, "sesion": fechas.index(ruta.stem[:8]) + 1, "gesto": m.group(2),
            "encuadre": "tres_cuartos" if m.group(3) == "trescuartos" else "perfil", "con_pico": pico >= 0,
        }
        if pico < 0:
            fila.update({k: None for k in ("s_saque", *CANDIDATAS, "giro_hombros", "x_muneca_alta")})
        else:
            frames = frames_desde_series({a.value: z[a.value] for a in ARTS})
            fps = float(z["fps"])
            fila.update(estadisticos(frames, pico, fps, mano))
            fila["x_muneca_alta"] = muneca_alta_en_contacto(frames, pico, fps, mano)
        filas.append(fila)
    return filas


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Decisión 038, etapa 1: análisis exploratorio posterior (post hoc).")
    ap.add_argument("--salida", type=Path, required=True, help="prefijo: escribe <prefijo>.json")
    ap.add_argument("--mano", default="der", choices=("der", "izq"))
    args = ap.parse_args(argv)

    from app.config import get_cache_dir
    from app.medicion_paso_a import _git

    repo = Path(__file__).resolve().parents[2]
    sucio = _git(["status", "--porcelain", "--", "backend/app", "tests", "docs/decisiones"], repo)
    commit = _git(["rev-parse", "HEAD"], repo)
    destino_series = get_cache_dir() / "deteccion-series"
    volcar_series(get_cache_dir() / "corpus-real-pose-b", destino_series, args.mano)
    filas = filas_desde_series(destino_series, args.mano)
    resultado = {
        "aviso": "EXPLORATORIO POSTERIOR (post hoc). Se diseñó viendo ambas sesiones: no cuenta para el criterio de aceptación ni se puede citar como acierto de la detección.",
        "commit": commit, "arbol_sucio": bool(sucio), "repeticiones": len(filas), "resultados": exploratorio(filas),
        "x_muneca_alta_por_clase": {
            f"s{s}|{g}": [round(f["x_muneca_alta"], 3) for f in filas if f["sesion"] == s and f["gesto"] == g and f["x_muneca_alta"] is not None]
            for s in SESIONES for g in GESTOS
        },
    }
    destino = Path(f"{args.salida}.json")
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
