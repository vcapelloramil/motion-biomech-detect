"""E4 — Exploración cualitativa de la Fase B por grupo (gesto, encuadre).

Reúne en un solo script reproducible (principio 5 del plan) tres análisis que se
hicieron primero en un scratchpad:

  1. **Sensibilidad al paso de muestreo.** Pico p99 de la velocidad angular de pelvis,
     torso y brazo calculada entre fotogramas separados por k = 1, 2, 4, 8
     (ω_k = ∠(u[i], u[i+k]) · fps / k). El movimiento real sostenido casi no cambia
     con k; el ruido de alta frecuencia cae. Un pico real pero BREVE (el brazo en el
     impacto, < 30 ms) también cae: no leer la caída del brazo como ruido.
  2. **Inversiones de z** (`detectar_inversiones_z`) y fracción de fotogramas con algún
     tramo excluido en E3 (cualquier articulación y coordenada: sobreestima lo que
     afecta a pelvis/torso/brazo).
  3. **Comparación por grupo**: orden pelvis → torso → brazo, desfase pelvis→torso, y si
     el pico de la pelvis cae en vuelo (detector aproximado: ambos tobillos en imagen
     por encima de su nivel de apoyo; solo tiene sentido para el saque).

Es EXPLORATORIO: no toca umbrales ni calibra nada. Usa solo material propio
(`fuente = propio`) del catálogo. Escribe un JSON en ``docs/resultados/`` y una tabla
por consola.

Uso (desde backend/):
    python -m app.explorar_fase_b                       # todos los grupos, 1 clip = 1 repetición
    python -m app.explorar_fase_b --segmentacion auto   # segmentación automática (valles)
    python -m app.explorar_fase_b --grupo drive_perfil --grupo reves_trescuartos
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from app.engine.kinematics import _xyz
from app.engine.pipeline import procesar_e3
from app.engine.pose import cache as pose_cache
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.mediapipe_backend import MediaPipeBackend
from app.engine.segmentos_corporales import ORDEN_ESPERADO, SegmentoCadena as S, vector_segmento
from app.engine.sequencing import secuenciar
from app.engine.version import __version__ as version_motor

PASOS = (1, 2, 4, 8)
# Grupos por defecto: los seis con repeticiones controladas. Los casos deficientes
# (saque_fueracuadro, saque_espaldas) se piden explícitamente con --grupo: E3 puede no
# tener series suficientes y el clip se registra como no auditable.
GRUPOS_BASE = tuple(
    f"{g}_{e}" for g in ("saque", "drive", "reves") for e in ("perfil", "trescuartos")
)
_RESULTADOS = Path(__file__).resolve().parents[2] / "docs" / "resultados"
# Vuelo: ambos tobillos (coordenada de imagen normalizada) por encima de su nivel de
# apoyo (percentil 90 de y = tobillos más bajos) en más de este margen.
_MARGEN_VUELO = 0.03


def _vectores(seq, seg, lado: str, brazo_via: str) -> np.ndarray:
    """Vector director unitario del segmento por fotograma (NaN si falta un extremo)."""
    origen, extremo = vector_segmento(seg, lado, brazo_via=brazo_via)
    u = np.full((seq.n_frames, 3), np.nan)
    for i, frame in enumerate(seq.frames):
        p = frame.puntos_mundo
        if origen in p and extremo in p and p[extremo].z is not None:
            d = _xyz(p[extremo]) - _xyz(p[origen])
            n = np.linalg.norm(d)
            if n > 0:
                u[i] = d / n
    return u


def pico_p99_por_paso(u: np.ndarray, fps: float) -> list[float]:
    """p99 de ω_k (°/s) para cada k de PASOS."""
    salida = []
    for k in PASOS:
        cos = np.einsum("ij,ij->i", u[:-k], u[k:])
        w = np.degrees(np.arccos(np.clip(cos, -1, 1))) * fps / k
        salida.append(float(np.nanpercentile(w, 99)))
    return salida


def frames_en_vuelo(seq) -> np.ndarray:
    ys = []
    for frame in seq.frames:
        vals = [frame.puntos[a].y for a in (A.TOBILLO_IZQ, A.TOBILLO_DER) if a in frame.puntos]
        ys.append(float(np.mean(vals)) if vals else np.nan)
    ys = np.array(ys)
    return ys < np.nanpercentile(ys, 90) - _MARGEN_VUELO


def analizar_clip(seq, lado: str, *, clip_completo: bool, brazo_via: str) -> dict:
    try:
        filt = procesar_e3(seq)
    except ValueError as e:
        # Sin series utilizables (p. ej. jugador fuera de cuadro): no se estima nada.
        return {"n_frames": seq.n_frames, "no_auditable": str(e)}
    s, fps = filt.secuencia, filt.secuencia.fps_efectivos

    picos_p99 = {
        seg.value: pico_p99_por_paso(_vectores(s, seg, lado, brazo_via), fps)
        for seg in ORDEN_ESPERADO
    }
    excluidos: set[int] = set()
    for t in filt.tramos_excluidos:
        excluidos.update(range(t.desde_frame, t.hasta_frame + 1))

    resultados, _ = secuenciar(
        s, lado_dominante=lado, tramos_excluidos=filt.tramos_excluidos,
        brazo_via=brazo_via, clip_completo=clip_completo, corpus_publico=False,
    )
    vuelo = frames_en_vuelo(seq)
    reps = []
    for r in resultados:
        pp, pt = r.picos.get(S.PELVIS), r.picos.get(S.TORSO)
        dt = None
        if pp and pt and pp.auditable and pt.auditable:
            dt = round((pt.instante_s - pp.instante_s) * 1000, 1)   # + => pelvis primero
        en_vuelo = None
        if pp and pp.auditable:
            fr = int(r.ventana.desde_frame + round(pp.instante_s * fps))
            en_vuelo = bool(vuelo[min(fr, len(vuelo) - 1)])
        reps.append({
            "indice": r.indice,
            "ventana_s": [round(r.ventana.desde_s, 3), round(r.ventana.hasta_s, 3)],
            "orden": [x.value for x in r.orden_observado] if r.orden_observado else None,
            "dt_pelvis_a_torso_ms": dt,
            "pico_pelvis_en_vuelo": en_vuelo,
            "picos": {
                seg.value: (
                    {"instante_s": round(p.instante_s, 4), "velocidad": round(p.velocidad, 1)}
                    if p and p.auditable else {"no_auditable": p.motivo if p else None}
                )
                for seg, p in r.picos.items()
            },
        })
    return {
        "n_frames": seq.n_frames,
        "fps_efectivos": fps,
        "pico_p99_por_paso": {k: [round(x, 1) for x in v] for k, v in picos_p99.items()},
        "inversiones_z": len(filt.validacion.inversiones_z),
        "frames_con_tramo_excluido_pct": round(100 * len(excluidos) / seq.n_frames, 1),
        "repeticiones": reps,
    }


def _mediana(valores) -> float | None:
    return float(np.median(valores)) if len(valores) else None


def resumir_grupo(todos: list[dict]) -> dict:
    clips = [c for c in todos if "no_auditable" not in c]
    if not clips:
        return {"clips": 0, "clips_no_auditables": len(todos)}
    pel = np.array([c["pico_p99_por_paso"]["pelvis"] for c in clips])
    tor = np.array([c["pico_p99_por_paso"]["torso"] for c in clips])
    bra = np.array([c["pico_p99_por_paso"]["brazo"] for c in clips])
    return {
        "clips": len(clips),
        "clips_no_auditables": len(todos) - len(clips),
        "pelvis_k1_mediana": _mediana(pel[:, 0]),
        "torso_k1_mediana": _mediana(tor[:, 0]),
        "pelvis_sobre_torso_mediana": _mediana(pel[:, 0] / tor[:, 0]),
        "caida_pelvis_k1_a_k8_pct": _mediana(100 * (1 - pel[:, -1] / pel[:, 0])),
        "caida_brazo_k1_a_k8_pct": _mediana(100 * (1 - bra[:, -1] / bra[:, 0])),
        "inversiones_z_mediana": _mediana([c["inversiones_z"] for c in clips]),
    }


def _fmt(x, ancho=6):
    return f"{x:{ancho}.0f}" if x is not None else "-".rjust(ancho)


def _imprimir(grupos: dict[str, dict]) -> None:
    for g, datos in grupos.items():
        print(f"\n=== {g} ({datos['resumen']['clips']} clips, "
              f"{datos['resumen']['clips_no_auditables']} no auditables) ===")
        print(" clip  reps | pelvis k=1,2,4,8         | torso k=1..8            | "
              "brazo k=1..8            | inv_z | orden(es), dt pelvis→torso (ms)")
        for c in datos["clips"]:
            if "no_auditable" in c:
                print(f" {c['archivo'][-9:-4]}  no auditable: {c['no_auditable']}")
                continue
            p = c["pico_p99_por_paso"]
            ordenes = ",".join(
                (">".join(x[0] for x in r["orden"]) if r["orden"] else "-") for r in c["repeticiones"]
            )
            dts = ",".join(
                f"{r['dt_pelvis_a_torso_ms']:.0f}" if r["dt_pelvis_a_torso_ms"] is not None else "-"
                for r in c["repeticiones"]
            )
            fila = " | ".join(" ".join(_fmt(x) for x in p[s]) for s in ("pelvis", "torso", "brazo"))
            print(f" {c['archivo'][-9:-4]} {len(c['repeticiones']):3d}  | {fila} | "
                  f"{c['inversiones_z']:5d} | {ordenes:20} {dts}")
        r = datos["resumen"]
        if not r["clips"]:
            continue
        print(f" MEDIANAS: pelvis {_fmt(r['pelvis_k1_mediana'])}  torso {_fmt(r['torso_k1_mediana'])}  "
              f"pelvis/torso {r['pelvis_sobre_torso_mediana']:.2f} | caída k1→k8: "
              f"pelvis {r['caida_pelvis_k1_a_k8_pct']:.0f}%  brazo {r['caida_brazo_k1_a_k8_pct']:.0f}%")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Exploración cualitativa de la Fase B por grupo.")
    parser.add_argument("--segmentacion", choices=["clip", "auto"], default="clip",
                        help="clip: cada clip pre-cortado es 1 repetición (default); "
                             "auto: valles de quietud.")
    parser.add_argument("--brazo-via", choices=["codo", "muneca"], default="codo")
    parser.add_argument("--grupo", action="append", default=None,
                        help="gesto_encuadre (repetible), p. ej. drive_perfil. Default: los seis grupos base.")
    parser.add_argument("--salida", type=Path, default=None,
                        help="JSON de salida (default: docs/resultados/e4-fase-b-exploratorio-<segmentacion>.json).")
    args = parser.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir

    base = get_data_dir()
    backend = MediaPipeBackend()
    with (base / "catalogo.csv").open(encoding="utf-8", newline="") as f:
        filas = [r for r in csv.DictReader(f)
                 if r.get("fuente") == "propio" and "_rep" in r["archivo"]]

    grupos: dict[str, dict] = defaultdict(lambda: {"clips": []})
    for fila in filas:
        g = f"{fila['gesto']}_{fila['angulo']}"
        if g not in (args.grupo or GRUPOS_BASE):
            continue
        video = next((p for p in (base / "fase-b").rglob(fila["archivo"])
                      if "originales" not in p.parts), None)
        seq = (pose_cache.cargar_si_vigente(get_cache_dir(), video, backend.id, backend.config_hash)
               if video else None)
        if seq is None:
            print(f"[aviso] sin pose cacheada: {fila['archivo']} (correr app.extraer_pose)")
            continue
        clip = analizar_clip(seq, fila["lado_dominante"], clip_completo=args.segmentacion == "clip",
                             brazo_via=args.brazo_via)
        clip["archivo"] = fila["archivo"]
        grupos[g]["clips"].append(clip)

    if not grupos:
        print("No hay clips propios con pose cacheada para los grupos pedidos.")
        return 1
    for datos in grupos.values():
        datos["resumen"] = resumir_grupo(datos["clips"])
    _imprimir(grupos)

    salida = args.salida or _RESULTADOS / f"e4-fase-b-exploratorio-{args.segmentacion}.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps({
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "version_motor": version_motor,
        "backend_pose": backend.version,
        "maquina": platform.platform(),
        "segmentacion": args.segmentacion,
        "brazo_via": args.brazo_via,
        "pasos_k": list(PASOS),
        "nota": "Exploratorio (E4): no calibra ni mide criterios. Un pico real breve "
                "(brazo) tambien cae con k; no leerlo como ruido.",
        "grupos": grupos,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nEscrito: {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
