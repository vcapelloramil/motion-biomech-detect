"""Medición formal del Criterio 3 redefinido (decisión 012; diseño en la decisión 014).

Consistencia entre sesiones del mismo jugador: por métrica y grupo se compara la variación ENTRE sesiones con
la variación INTRA-sesión.

  σ_w  = promedio de los desvíos robustos (MAD × 1,4826) de las dos sesiones;
  Δ    = |mediana sesión 1 − mediana sesión 2|, con intervalo bootstrap de 95 %;
  consistente si Δ <= σ_w.
  Cumplimiento (con las dos métricas): >= 75 % de las combinaciones métrica × grupo consistentes.

Métricas:
  (i)  separación cadera-hombro máxima (°): máximo, dentro de la ventana ± 300 ms del ancla de torso, del
       ángulo entre el eje de caderas y el de hombros (3D, series filtradas por E3).
  (ii) instante de pico: DEFINICIÓN PENDIENTE de confirmación de Valentín (decisión 014). Propuesta:
       instante del pico de torso medido desde el instante de máxima separación cadera-hombro (ms).
       Solo se calcula con --con-instante-pico; no se usa hasta confirmar la definición.

Grupos: gesto × encuadre. Del saque de tres cuartos, la sesión 2 usa SOLO la toma 02 (las tomas 02b y 02c
quedan para el Criterio 1). Precondición (decisión 012): se informa la equivalencia de encuadre entre sesiones
(tamaño del torso en píxeles y posición horizontal) y se señalan diferencias de más de 20 % (informativo).

Se niega a correr con el árbol de git sucio (cada resultado queda atado a un commit).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from app.engine.kinematics import serie_separacion_cadera_hombro
from app.engine.pipeline import procesar_e3
from app.engine.pose import cache as pose_cache
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.mediapipe_backend import MediaPipeBackend
from app.engine.sequencing import MARGEN_ANCLA_S, instante_ancla
from app.engine.version import __version__ as version_motor

UMBRAL_CUMPLIMIENTO = 0.75
DIF_ENCUADRE_INFORMATIVA = 0.20
BOOTSTRAP_N = 10000
SEMILLA = 26092026


# --- funciones puras (probadas en tests/unit/test_medicion_criterio3.py) ------------------------

def mad_sigma(x) -> float:
    """Desvío robusto: MAD × 1,4826 (equivale al desvío estándar en una normal)."""
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    if x.size == 0:
        return float("nan")
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


def comparar_sesiones(x1, x2, *, n_boot: int = BOOTSTRAP_N, semilla: int = SEMILLA) -> dict:
    """Δ entre sesiones (con IC bootstrap), σ_w intra-sesión y veredicto de consistencia."""
    a = np.asarray([v for v in x1 if v is not None and np.isfinite(v)], float)
    b = np.asarray([v for v in x2 if v is not None and np.isfinite(v)], float)
    if a.size < 2 or b.size < 2:
        return {"n1": int(a.size), "n2": int(b.size), "consistente": None}
    sw = (mad_sigma(a) + mad_sigma(b)) / 2
    delta = abs(float(np.median(a) - np.median(b)))
    rng = np.random.default_rng(semilla)
    boot = np.abs(np.median(rng.choice(a, (n_boot, a.size)), axis=1) - np.median(rng.choice(b, (n_boot, b.size)), axis=1))
    # Lectura calibrada (agregada ANTES de medir; ver decisión 014): p de permutación de Δ. Con n = 6 por
    # sesión la regla Δ <= σ_w da "inconsistente" ~24 % de las veces aunque NO haya ningún cambio real.
    junto = np.concatenate([a, b])
    perm = np.empty(n_boot)
    for i in range(n_boot):
        rng.shuffle(junto)
        perm[i] = abs(np.median(junto[:a.size]) - np.median(junto[a.size:]))
    p_perm = float((np.sum(perm >= delta - 1e-12) + 1) / (n_boot + 1))
    return {"n1": int(a.size), "n2": int(b.size), "mediana1": float(np.median(a)), "mediana2": float(np.median(b)),
            "sigma1": mad_sigma(a), "sigma2": mad_sigma(b), "sigma_w": float(sw), "delta": delta,
            "delta_ic95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            "consistente": bool(delta <= sw), "p_permutacion": p_perm,
            "sin_evidencia_de_diferencia": bool(p_perm > 0.05)}


def fraccion_consistente(resultados: list[dict]) -> tuple[int, int, float | None]:
    """(consistentes, evaluables, fracción) sobre las combinaciones métrica × grupo."""
    ev = [r for r in resultados if r.get("consistente") is not None]
    k = sum(r["consistente"] for r in ev)
    return k, len(ev), (k / len(ev) if ev else None)


def fraccion_sin_evidencia(resultados: list[dict]) -> tuple[int, int, float | None]:
    """Lectura calibrada: combinaciones SIN evidencia de diferencia entre sesiones (p de permutación > 0,05)."""
    ev = [r for r in resultados if r.get("sin_evidencia_de_diferencia") is not None]
    k = sum(r["sin_evidencia_de_diferencia"] for r in ev)
    return k, len(ev), (k / len(ev) if ev else None)


def diferencia_relativa(a: float, b: float) -> float:
    return abs(a - b) / ((abs(a) + abs(b)) / 2) if (a or b) else 0.0


# --- medición -----------------------------------------------------------------------------

def _git(args: list[str], repo: Path) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def metricas_clip(seq, lado: str, con_instante: bool) -> dict:
    """Separación cadera-hombro máxima y, opcionalmente, el instante del pico de torso desde ella."""
    try:
        filt = procesar_e3(seq)
    except ValueError as e:
        return {"valida": False, "motivo": f"E3: {e}"}
    ft, info = instante_ancla(filt.secuencia, lado, "torso", tramos_excluidos=filt.tramos_excluidos)
    if ft is None:
        return {"valida": False, "motivo": f"sin ancla: {info}"}
    fps = seq.fps_efectivos
    m = int(round(MARGEN_ANCLA_S * fps))
    d, h = max(0, ft - m), min(seq.n_frames - 1, ft + m)
    sep = serie_separacion_cadera_hombro(filt.secuencia, espacio="mundo")[d:h + 1]
    if not np.isfinite(sep).any():
        return {"valida": False, "motivo": "sin separación cadera-hombro en la ventana"}
    k = int(np.nanargmax(sep))
    out = {"valida": True, "separacion_max_grados": float(sep[k])}
    if con_instante:
        out["instante_pico_torso_desde_max_sep_ms"] = float((ft - (d + k)) / fps * 1000)
    return out


def encuadre_clip(seq) -> dict:
    """Tamaño del torso en píxeles (medio hombros → medio caderas) y posición horizontal (medio caderas)."""
    tam, xs = [], []
    for f in seq.frames:
        p = f.puntos
        if all(a in p for a in (A.HOMBRO_IZQ, A.HOMBRO_DER, A.CADERA_IZQ, A.CADERA_DER)):
            sh = np.array([(p[A.HOMBRO_IZQ].x + p[A.HOMBRO_DER].x) / 2 * seq.ancho, (p[A.HOMBRO_IZQ].y + p[A.HOMBRO_DER].y) / 2 * seq.alto])
            ca = np.array([(p[A.CADERA_IZQ].x + p[A.CADERA_DER].x) / 2 * seq.ancho, (p[A.CADERA_IZQ].y + p[A.CADERA_DER].y) / 2 * seq.alto])
            tam.append(float(np.linalg.norm(sh - ca)))
            xs.append(float((p[A.CADERA_IZQ].x + p[A.CADERA_DER].x) / 2))
    return {"torso_px": float(np.median(tam)) if tam else None, "x_caderas": float(np.median(xs)) if xs else None}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Medición formal del Criterio 3 redefinido (decisiones 012 y 014).")
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--con-instante-pico", action="store_true",
                    help="Calcula también la métrica (ii). NO usar hasta confirmar su definición.")
    ap.add_argument("--permitir-sucio", action="store_true", help="NO usar para la medición formal")
    args = ap.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir
    from app.diagnosticos_e3 import _buscar_video, _catalogo, en_sesion, fechas_propias

    repo = Path(__file__).resolve().parents[2]
    sucio = _git(["status", "--porcelain", "--", "backend/app", "tests", "docs/decisiones"], repo)
    if sucio and not args.permitir_sucio:
        print("El árbol de git tiene cambios sin commitear:\n" + sucio + "\nCommitear antes de medir (decisión 014).")
        return 2

    base = get_data_dir()
    cat = _catalogo(base)
    fechas = fechas_propias(cat)
    b = MediaPipeBackend()
    filas = []
    for n, r in sorted(cat.items()):
        if not (r.get("fuente") == "propio" and "_rep" in n and r.get("angulo") in ("perfil", "trescuartos")
                and str(r.get("fps_efectivos")).strip() in ("240", "240.0")):
            continue
        ses = 1 if en_sesion(n, 1, fechas) else 2
        if r["gesto"] == "saque" and r["angulo"] == "trescuartos" and ses == 2 and "_240_02_rep" not in n:
            continue                                    # solo la toma 02 (02b y 02c son del Criterio 1)
        seq = pose_cache.cargar_si_vigente(get_cache_dir(), _buscar_video(base, n), b.id, b.config_hash)
        if seq is None:
            raise SystemExit(f"sin pose cacheada para {n}")
        m = metricas_clip(seq, r["lado_dominante"], args.con_instante_pico)
        filas.append({"clip": n, "sesion": ses, "gesto": r["gesto"], "encuadre": r["angulo"], **m, **encuadre_clip(seq)})
        print(f"  s{ses} {n[-34:]:34} {m.get('separacion_max_grados', m.get('motivo'))}")

    grupos = defaultdict(lambda: {1: [], 2: []})
    for f in filas:
        grupos[f"{f['gesto']}|{f['encuadre']}"][f["sesion"]].append(f)

    metricas = {"separacion_cadera_hombro_max": "separacion_max_grados"}
    if args.con_instante_pico:
        metricas["instante_pico_torso_desde_max_sep_ms"] = "instante_pico_torso_desde_max_sep_ms"
    resultado, encuadre = {}, {}
    for g, s in sorted(grupos.items()):
        resultado[g] = {}
        for nombre, campo in metricas.items():
            resultado[g][nombre] = comparar_sesiones([f.get(campo) for f in s[1] if f["valida"]],
                                                     [f.get(campo) for f in s[2] if f["valida"]])
        t1 = np.median([f["torso_px"] for f in s[1] if f["torso_px"]])
        t2 = np.median([f["torso_px"] for f in s[2] if f["torso_px"]])
        x1 = np.median([f["x_caderas"] for f in s[1] if f["x_caderas"]])
        x2 = np.median([f["x_caderas"] for f in s[2] if f["x_caderas"]])
        encuadre[g] = {"torso_px_s1": float(t1), "torso_px_s2": float(t2), "dif_torso_relativa": diferencia_relativa(t1, t2),
                       "x_caderas_s1": float(x1), "x_caderas_s2": float(x2),
                       "senalado_por_mas_de_20_pct": bool(diferencia_relativa(t1, t2) > DIF_ENCUADRE_INFORMATIVA)}

    print("\nCriterio 3 (redefinido) — Δ entre sesiones contra σ_w intra-sesión")
    for nombre in metricas:
        print(f"\nMétrica: {nombre}")
        print(f"{'grupo':22} n1 n2 | mediana s1  mediana s2 | σ_w    Δ     IC95(Δ)          | Δ<=σ_w  p_perm")
        for g, r in resultado.items():
            x = r[nombre]
            if x.get("consistente") is None:
                print(f"{g:22} {x['n1']:2d} {x['n2']:2d} | (insuficiente)")
                continue
            print(f"{g:22} {x['n1']:2d} {x['n2']:2d} | {x['mediana1']:9.2f} {x['mediana2']:10.2f} | {x['sigma_w']:5.2f} {x['delta']:5.2f} "
                  f"[{x['delta_ic95'][0]:5.2f},{x['delta_ic95'][1]:5.2f}] | {'SÍ' if x['consistente'] else 'no':3}   {x['p_permutacion']:.3f}")
    todos = [r[m] for r in resultado.values() for m in metricas]
    k, ev, frac = fraccion_consistente(todos)
    print(f"\nCombinaciones con Δ <= σ_w: {k}/{ev}" + (f" = {frac:.0%}" if frac is not None else "") +
          f" (umbral {UMBRAL_CUMPLIMIENTO:.0%}). " + ("PARCIAL: falta la métrica (ii)." if not args.con_instante_pico else ""))
    k2, ev2, frac2 = fraccion_sin_evidencia(todos)
    print(f"Lectura calibrada: combinaciones SIN evidencia de diferencia entre sesiones (p_perm > 0,05): {k2}/{ev2}"
          + (f" = {frac2:.0%}" if frac2 is not None else "")
          + ". NOTA: con n = 6 por sesión la regla Δ <= σ_w da ~76 % aunque no haya ningún cambio real.")
    print("\nEquivalencia de encuadre entre sesiones (torso en píxeles; se señalan > 20 %):")
    for g, e in encuadre.items():
        print(f"  {g:22} s1 {e['torso_px_s1']:6.1f}  s2 {e['torso_px_s2']:6.1f}  dif {e['dif_torso_relativa']:.0%}{'  <-- SEÑALADO' if e['senalado_por_mas_de_20_pct'] else ''}")

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps({
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "decision": "012/014",
        "version_motor": version_motor, "commit": _git(["rev-parse", "HEAD"], repo), "arbol_sucio": bool(sucio),
        "metricas": list(metricas), "parcial": not args.con_instante_pico, "umbral_cumplimiento": UMBRAL_CUMPLIMIENTO,
        "combinaciones_consistentes": [k, ev], "combinaciones_sin_evidencia_de_diferencia": [k2, ev2], "resultado_por_grupo": resultado, "encuadre": encuadre, "repeticiones": filas,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nEscrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
