"""Paso B del recálculo con la tasa real (plan de recálculo §2, "medición definitiva"; decisiones 030, 032 y 035).

Es lo que hace el producto con un archivo "Actual": lee las marcas de tiempo REALES de cada fotograma de los **originales** del iPhone
(~200 fps medios, 240 nominales), regulariza a la grilla uniforme de 240 Hz **contando los puntos interpolados** (R4), filtra con fase
cero, ancla al torso (± 300 ms) y clasifica "ordenable" con la MISMA constante en milisegundos que el producto (decisión 032).

Qué hace, por repetición del corpus (88 ubicadas en ``corpus-real-alineacion.json``):
  1. Toma su ventana en el original (``ventana_real``: índices de fotogramas decodificados) y ejecuta MediaPipe **solo** sobre esos
     fotogramas, con la **misma configuración** que la medición original (para comparar por el tiempo y no por el estimador).
  2. Guarda las poses en ``KINETIQ_CACHE_DIR/corpus-real-pose-b`` (reanudable: una repetición ya hecha no se vuelve a inferir).
  3. Mide con las mismas funciones que el Paso A (``medicion_paso_a.medir_secuencia``): Criterio 1 por tolerancia, distribución de
     Δ(tronco − cadera) y controles (corte fijo, giro axial, acople de ω).

Pre-registro: el del plan (§3). La tolerancia primaria es la de ``engine/tolerancia_orden.py``; las sensibilidades, las declaradas.
El orden de prioridad (saque de perfil, saque de tres cuartos, drive, revés) es para que la pregunta de la decisión 035 se responda primero.

Se excluyen y se informan: las repeticiones que empiezan en la rampa, y las de la toma ``02`` del saque de tres cuartos (``IMG_6391``
llegó incompleto: plan de recálculo, decisión de Valentín del 9/10).

Los videos NO van al repositorio: se leen de ``--reales`` y las poses derivadas van a la caché (ignorada por git).

Uso (desde backend/):
    python -m app.medicion_paso_b --reales "C:/Users/valen/Desktop/corpus-originales-reales" --salida ../docs/resultados/paso-b
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from app.engine.tolerancia_orden import TOLERANCIA_ORDEN_S
from app.engine.version import __version__ as version_motor
from app.medicion_criterio1 import UMBRAL, parse_toma
from app.medicion_paso_a import _git, construir_resultado, medir_secuencia

# Orden en que se miden los grupos: primero lo que decide la 035.
PRIORIDAD = ("saque|perfil", "saque|trescuartos", "drive|perfil", "reves|perfil", "drive|trescuartos", "reves|trescuartos")
IGNORAR_ORIGINALES = ("IMG_6391",)          # llegó incompleto (2.503 de ~15.200 fotogramas): sus 6 repeticiones quedan fuera
_PAT = re.compile(r"^(\d{8})_VCR_([a-z]+)_(perfil|trescuartos)_240_(\d+[a-z]?)_rep\d+\.mov$")


def prioridad(gesto: str, encuadre: str) -> int:
    clave = f"{gesto}|{encuadre}"
    return PRIORIDAD.index(clave) if clave in PRIORIDAD else len(PRIORIDAD)


def elegir_repeticiones(alineacion: dict, catalogo: dict) -> tuple[list[dict], list[dict]]:
    """Repeticiones a medir y repeticiones excluidas (con el motivo), de la tabla de alineación y el catálogo.

    Pura salvo por sus argumentos: se prueba sin videos (tests/unit/test_medicion_paso_b.py)."""
    medir, excluidas = [], []
    for r in alineacion["repeticiones"]:
        nombre = r["repeticion"]
        m = _PAT.match(nombre)
        if not m:
            continue                                # fuera de cuadro y de espaldas: controles, no entran al Criterio 1
        fila = catalogo.get(nombre)
        if fila is None or fila.get("fuente") != "propio":
            continue
        if not r["entera_en_la_meseta"]:
            excluidas.append({"repeticion": nombre, "motivo": "empieza en la rampa de velocidad"})
            continue
        if Path(r["real"]).stem in IGNORAR_ORIGINALES:
            excluidas.append({"repeticion": nombre, "motivo": f"el original {r['real']} llegó incompleto"})
            continue
        a, b = r["ventana_real"]
        medir.append({
            "repeticion": nombre, "real": r["real"], "ventana_real": [int(a), int(b)], "fecha": m.group(1),
            "gesto": m.group(2), "encuadre": m.group(3), "toma": parse_toma(nombre), "lado": fila["lado_dominante"],
        })
    medir.sort(key=lambda x: (prioridad(x["gesto"], x["encuadre"]), x["fecha"], x["repeticion"]))
    return medir, excluidas


def _poses_del_original(ruta: Path, reps: list[dict], base_cache: Path, backend, pts_dec: np.ndarray) -> None:
    """Una sola pasada por el original: MediaPipe solo en los fotogramas de las ventanas pedidas; guarda una caché por repetición."""
    import cv2

    from app.engine.pose import cache as pose_cache
    from app.engine.pose.base import PoseFrame, SecuenciaPose

    pendientes = [r for r in reps if not Path(f"{base_cache / Path(r['repeticion']).stem}.pose.json").exists()]
    if not pendientes:
        return
    cap = cv2.VideoCapture(str(ruta))
    if not cap.isOpened():
        raise SystemExit(f"OpenCV no pudo abrir {ruta}")
    cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
    ancho, alto = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_contenedor = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if abs(n_contenedor - len(pts_dec)) > 3:
        raise SystemExit(f"{ruta.name}: OpenCV cuenta {n_contenedor} fotogramas y ffprobe {len(pts_dec)}: no se puede alinear")
    ultimo = max(r["ventana_real"][1] for r in pendientes)
    acumulado: dict[str, list[PoseFrame]] = {r["repeticion"]: [] for r in pendientes}
    idx = -1
    t_dec: dict[int, float] = {}
    bordes = {r["ventana_real"][0] for r in pendientes} | {r["ventana_real"][1] for r in pendientes}
    try:
        while idx < ultimo:
            if not cap.grab():
                break
            idx += 1
            if idx in bordes:
                t_dec[idx] = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            activas = [r for r in pendientes if r["ventana_real"][0] <= idx <= r["ventana_real"][1]]
            if not activas:
                continue
            ok, frame = cap.retrieve()
            if not ok:
                raise SystemExit(f"{ruta.name}: no se pudo leer el fotograma {idx}")
            pf = backend.estimar_frame(frame, idx)     # una sola vez por fotograma, aunque dos ventanas lo incluyan
            for r in activas:
                acumulado[r["repeticion"]].append(
                    PoseFrame(indice=len(acumulado[r["repeticion"]]), detectado=pf.detectado, puntos=pf.puntos,
                              puntos_mundo=pf.puntos_mundo)
                )
    finally:
        cap.release()
    for r in pendientes:
        a, b = r["ventana_real"]
        # El decodificador y las marcas del contenedor tienen que coincidir en la DURACIÓN de la ventana (no en el origen, que
        # OpenCV corre): si no, el índice de la alineación no corresponde a estas marcas y no se mide (R3: no se adivina).
        dur_dec, dur_marcas = t_dec[b] - t_dec[a], float(pts_dec[b] - pts_dec[a])
        if abs(dur_dec - dur_marcas) > 0.005:
            raise SystemExit(
                f"{r['repeticion']}: la ventana dura {dur_dec:.3f} s en el decodificador y {dur_marcas:.3f} s en las marcas"
            )
        frames = acumulado[r["repeticion"]]
        if len(frames) != b - a + 1:
            raise SystemExit(f"{r['repeticion']}: se esperaban {b - a + 1} fotogramas y salieron {len(frames)}")
        seq = SecuenciaPose(
            backend_id=backend.id, backend_version=backend.version, articulaciones=tuple(backend.articulaciones_disponibles),
            dims=backend.dims, ancho=ancho, alto=alto, fps_efectivos=240.0, config_hash=backend.config_hash, frames=frames,
        )
        pose_cache.guardar(seq, base_cache / Path(r["repeticion"]).stem)
        np.save(f"{base_cache / Path(r['repeticion']).stem}.pts.npy", np.asarray(pts_dec[a : b + 1], dtype=float))


def medir_repeticion(base_cache: Path, rep: dict) -> dict:
    from app.engine.ingest import normalizar_fps
    from app.engine.pose import cache as pose_cache
    from app.engine.regularizacion import regularizar

    base = base_cache / Path(rep["repeticion"]).stem
    seq = pose_cache.cargar(base)
    pts = np.load(f"{base}.pts.npy")
    dif = np.diff(pts)
    fps_nominal = normalizar_fps(1.0 / float(np.median(dif)))
    seq_reg, info = regularizar(seq, pts, fps_nominal)
    fila = medir_secuencia(seq_reg, rep["lado"])
    fila.update(
        clip=rep["repeticion"], gesto=rep["gesto"], encuadre=rep["encuadre"], toma=rep["toma"], real=rep["real"],
        regularizacion=info.como_dict(),
    )
    return fila


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Paso B del recálculo: los originales a tasa real (plan de recálculo §2).")
    ap.add_argument("--reales", type=Path, required=True, help="carpeta con los originales (nunca va al repositorio)")
    ap.add_argument("--salida", type=Path, required=True, help="prefijo: escribe <prefijo>-sesion-1.json y <prefijo>-sesion-2.json")
    ap.add_argument("--grupos", default="", help="solo estos, separados por coma (p. ej. saque|perfil)")
    ap.add_argument("--permitir-sucio", action="store_true", help="NO usar para la medición formal")
    args = ap.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir
    from app.diagnosticos_e3 import _catalogo, fechas_propias
    from app.engine.pose.mediapipe_backend import MediaPipeBackend
    from app.engine.ingest import probe

    repo = Path(__file__).resolve().parents[2]
    sucio = _git(["status", "--porcelain", "--", "backend/app", "tests", "docs/decisiones"], repo)
    if sucio and not args.permitir_sucio:
        print("El árbol de git tiene cambios sin commitear en backend/app, tests o docs/decisiones:\n" + sucio)
        return 2

    alineacion = json.loads((repo / "docs" / "resultados" / "corpus-real-alineacion.json").read_text(encoding="utf-8"))
    cat = _catalogo(get_data_dir())
    fechas = fechas_propias(cat)
    medir, excluidas = elegir_repeticiones(alineacion, cat)
    if args.grupos:
        quiero = {g.strip() for g in args.grupos.split(",")}
        medir = [r for r in medir if f"{r['gesto']}|{r['encuadre']}" in quiero]
    print(f"A medir: {len(medir)} repeticiones; excluidas: {len(excluidas)}")

    base_cache = get_cache_dir() / "corpus-real-pose-b"
    base_cache.mkdir(parents=True, exist_ok=True)
    backend = MediaPipeBackend()
    por_original: dict[str, list[dict]] = {}
    for r in medir:
        por_original.setdefault(r["real"], []).append(r)

    filas: dict[str, dict] = {}

    def escribir() -> None:
        for sesion in (1, 2):
            fecha = fechas[sesion - 1]
            sub = [f for f in filas.values() if f["clip"][:8] == fecha]
            if not sub:
                continue
            salida = Path(f"{args.salida}-sesion-{sesion}.json")
            salida.parent.mkdir(parents=True, exist_ok=True)
            salida.write_text(json.dumps({
                "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "decision": "032 y 035 / plan de recálculo §2 (Paso B)", "sesion": sesion,
                "rol": "MEDICIÓN (conjunto de medición)" if sesion == 2 else "RÉPLICA EXPLORATORIA (no independiente)",
                "version_motor": version_motor, "commit": _git(["rev-parse", "HEAD"], repo), "arbol_sucio": bool(sucio),
                "origen": "originales del iPhone a tasa real, regularizados a 240 Hz", "umbral": UMBRAL,
                "tolerancia_primaria_ms": TOLERANCIA_ORDEN_S * 1000.0,
                "excluidas": excluidas, "repeticiones_medidas": len(sub), "repeticiones_previstas": sum(
                    1 for r in medir if r["fecha"] == fecha),
                "repeticiones": sub, **construir_resultado(sub),
            }, ensure_ascii=False, indent=1, default=list), encoding="utf-8")

    # Los originales se recorren en el orden de su repetición más prioritaria.
    orden = sorted(por_original, key=lambda real: min(medir.index(r) for r in por_original[real]))
    t0 = time.monotonic()
    for real in orden:
        reps = por_original[real]
        ruta = args.reales / real
        if not ruta.is_file():
            print(f"  sin original: {real}")
            continue
        md = probe(ruta)
        if md.pts_visibles is None:
            raise SystemExit(f"no se pudieron leer las marcas de {real}")
        pts_dec = np.sort(np.asarray(md.pts_visibles, dtype=float))   # por paquetes; se valida contra el decodificador abajo
        print(f"[{(time.monotonic() - t0) / 60:5.1f} min] {real}: {len(pts_dec)} fotogramas, {len(reps)} repeticiones", flush=True)
        _poses_del_original(ruta, reps, base_cache, backend, pts_dec)
        for r in reps:
            filas[r["repeticion"]] = medir_repeticion(base_cache, r)
        escribir()
    backend.cerrar()
    print(f"Listo en {(time.monotonic() - t0) / 60:.1f} min: {len(filas)} repeticiones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
