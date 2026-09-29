"""Medición formal del Criterio 1 (plan, tarea 4.7): decisión 014.

Pelvis, torso y brazo *distinguibles y ordenables de forma repetible* en al menos 8 de cada 10
repeticiones. Se miden dos cosas SEPARADAS (no se fusionan en una sola regla):

  1  Repetibilidad del orden (regla del criterio original), cualquiera sea el orden:
       1a = ordenables / TODAS las repeticiones del grupo (y también ordenables / válidas);
       1b = entre las ordenables, fracción que comparte el orden modal.
     El criterio se cumple en un grupo si 1a >= 0,8 y 1b >= 0,8.
  1c Coincidencia con el orden esperado (pelvis -> torso[ -> brazo]): SIN umbral, no cuenta como éxito
     ni fallo del criterio. Para el brazo no tiene fundamento bibliográfico (decisión 011).

Ordenable con tolerancia tau (fotogramas enteros): todos los picos del conjunto son auditables y cada par
consecutivo del orden observado difiere en MÁS de tau fotogramas. tau = 1 (primaria), 2 y 3 (sensibilidad).

Unidad: la repetición (un clip), ventana anclada al torso (± 300 ms), brazo vía codo, E3 con corte de
Winter automático. Solo lee la caché de pose. Se niega a correr con el árbol de git sucio: cada resultado
queda atado a un commit.

Uso (desde backend/):
    python -m app.medicion_criterio1 --sesion 2 --salida ../docs/resultados/criterio1-sesion-2.json
    python -m app.medicion_criterio1 --sesion 1 --etiqueta replica-exploratoria \\
        --salida ../docs/resultados/criterio1-sesion-1-replica-exploratoria.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from app.engine.pipeline import procesar_e3
from app.engine.pose import cache as pose_cache
from app.engine.pose.mediapipe_backend import MediaPipeBackend
from app.engine.segmentos_corporales import SegmentoCadena as S
from app.engine.sequencing import MARGEN_ANCLA_S, secuenciar
from app.engine.version import __version__ as version_motor

TAUS = (1, 2, 3)                  # fotogramas; 1 = primaria, 2 y 3 = sensibilidad declarada
UMBRAL = 0.8                      # 8 de cada 10
ESPERADO_PAR, ESPERADO_CADENA = "pt", "ptb"
_LETRA = {S.PELVIS: "p", S.TORSO: "t", S.BRAZO: "b"}


# --- funciones puras (probadas en tests/unit/test_medicion_criterio1.py) ---------------------

def parse_toma(nombre: str) -> str | None:
    """'02', '02b', '02c'... de nombres como ..._240_02b_rep01.mov; None si no hay."""
    m = re.search(r"_240_(\d+[a-z]?)_rep", nombre)
    return m.group(1) if m else None


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalo de Wilson de una proporción k/n."""
    if n == 0:
        return None
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centro - mitad), min(1.0, centro + mitad)


def orden_y_separacion(frames: dict[str, int | None], letras: str) -> tuple[str | None, int | None]:
    """Orden observado (p. ej. 'ptb') y menor separación entre picos consecutivos, en fotogramas.

    Devuelve (None, None) si algún pico falta. Con empates el orden es ambiguo pero se devuelve
    igualmente; la separación mínima será 0 y nunca será "ordenable" (0 no es > tau).
    """
    if any(frames.get(l) is None for l in letras):
        return None, None
    ordenados = sorted(letras, key=lambda l: (frames[l], letras.index(l)))
    gaps = [frames[b] - frames[a] for a, b in zip(ordenados, ordenados[1:])]
    return "".join(ordenados), min(gaps)


def clasificar(frames: dict[str, int | None], valida: bool, letras: str, tau: int) -> dict:
    """Clasifica una repetición para el conjunto de picos ``letras`` ('pt' o 'ptb') y una tolerancia."""
    orden, sep = orden_y_separacion(frames, letras) if valida else (None, None)
    return {"valida": valida, "orden": orden, "separacion_min": sep,
            "ordenable": bool(valida and sep is not None and sep > tau)}


def resumir(clasif: list[dict], esperado: str) -> dict:
    """Resumen de un grupo: 1a, 1b y 1c (ver el docstring del módulo)."""
    n = len(clasif)
    validas = sum(c["valida"] for c in clasif)
    ordenables = [c for c in clasif if c["ordenable"]]
    k = len(ordenables)
    cnt = Counter(c["orden"] for c in ordenables)
    modal, k_modal = (cnt.most_common(1)[0] if cnt else (None, 0))
    k_esp = cnt.get(esperado, 0)
    r = lambda a, b: (a / b) if b else None
    return {
        "n": n, "validas": validas, "ordenables": k,
        "1a_sobre_todas": r(k, n), "1a_sobre_todas_ic95": wilson(k, n),
        "1a_sobre_validas": r(k, validas),
        "1b_orden_modal": modal, "1b_repetibilidad": r(k_modal, k), "1b_ic95": wilson(k_modal, k),
        "1c_esperado": esperado, "1c_coincidencia": r(k_esp, k), "1c_ic95": wilson(k_esp, k),
        "ordenes": dict(cnt),
        "criterio_1_cumplido": bool(n and r(k, n) >= UMBRAL and k and r(k_modal, k) >= UMBRAL),
    }


# --- medición -----------------------------------------------------------------------------

def _git(args: list[str], repo: Path) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def medir_clip(seq, lado: str) -> dict:
    """Frames de los picos de pelvis, torso y brazo de una repetición (ventana anclada al torso)."""
    try:
        filt = procesar_e3(seq)
    except ValueError as e:
        return {"valida": False, "motivo": f"E3: {e}", "frames": {"p": None, "t": None, "b": None}}
    resultados, _ = secuenciar(
        filt.secuencia, lado_dominante=lado, tramos_excluidos=filt.tramos_excluidos,
        brazo_via="codo", ancla="torso", margen_ancla_s=MARGEN_ANCLA_S,
    )
    rep = resultados[0]
    frames = {}
    for seg in (S.PELVIS, S.TORSO, S.BRAZO):
        p = rep.picos.get(seg)
        frames[_LETRA[seg]] = int(p.frame) if p is not None and p.auditable else None
    return {"valida": frames["t"] is not None, "motivo": rep.motivo_no_auditable, "frames": frames,
            "corte_hz": round(float(filt.corte_hz), 2)}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Medición formal del Criterio 1 (decisión 014).")
    ap.add_argument("--sesion", type=int, required=True, help="1 (réplica exploratoria) o 2 (medición)")
    ap.add_argument("--etiqueta", default="", help="p. ej. replica-exploratoria")
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--permitir-sucio", action="store_true", help="NO usar para la medición formal")
    args = ap.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir
    from app.diagnosticos_e3 import _buscar_video, _catalogo, en_sesion, fechas_propias

    repo = Path(__file__).resolve().parents[2]
    sucio = _git(["status", "--porcelain", "--", "backend/app", "tests", "docs/decisiones"], repo)
    if sucio and not args.permitir_sucio:
        print("El árbol de git tiene cambios sin commitear en backend/app, tests o docs/decisiones:\n" + sucio +
              "\nCommitear antes de medir (congelamiento, decisión 014).")
        return 2

    base = get_data_dir()
    cat = _catalogo(base)
    fechas = fechas_propias(cat)
    b = MediaPipeBackend()
    clips = [(n, r) for n, r in sorted(cat.items())
             if r.get("fuente") == "propio" and "_rep" in n and r.get("angulo") in ("perfil", "trescuartos")
             and str(r.get("fps_efectivos")).strip() in ("240", "240.0") and en_sesion(n, args.sesion, fechas)]
    print(f"Sesión {args.sesion}: {len(clips)} repeticiones a 240 fps (perfil y tres cuartos).")

    filas = []
    for n, r in clips:
        seq = pose_cache.cargar_si_vigente(get_cache_dir(), _buscar_video(base, n), b.id, b.config_hash)
        if seq is None:
            raise SystemExit(f"sin pose cacheada para {n}")
        m = medir_clip(seq, r["lado_dominante"])
        filas.append({"clip": n, "gesto": r["gesto"], "encuadre": r["angulo"], "toma": parse_toma(n), **m})
        print(f"  {n[-34:]:34} válida={m['valida']!s:5} frames={m['frames']}")

    grupos: dict[str, list[dict]] = defaultdict(list)
    for f in filas:
        grupos[f"{f['gesto']}|{f['encuadre']}"].append(f)
        if f["gesto"] == "saque" and f["encuadre"] == "trescuartos":
            grupos[f"saque|trescuartos|toma {f['toma']}"].append(f)

    resultado = {}
    for tau in TAUS:
        resultado[str(tau)] = {}
        for g, L in sorted(grupos.items()):
            entrada = {"par_pelvis_torso": resumir([clasificar(f["frames"], f["valida"], "pt", tau) for f in L], ESPERADO_PAR)}
            if g.split("|")[1] == "trescuartos":
                entrada["cadena"] = resumir([clasificar(f["frames"], f["valida"], "ptb", tau) for f in L], ESPERADO_CADENA)
            resultado[str(tau)][g] = entrada

    fmt = lambda x: "  -  " if x is None else f"{x:5.2f}"
    for tau in TAUS:
        print(f"\n=== tau = {tau} fotograma(s){' (PRIMARIA)' if tau == 1 else ' (sensibilidad)'} ===")
        print(f"{'grupo':36} {'conj':6} {'n':>3} {'val':>3} {'ord':>3} | 1a(todas) 1a(vál) | 1b(modal)  orden | 1c(esp)  | criterio 1")
        for g, e in resultado[str(tau)].items():
            for conj, x in e.items():
                print(f"{g:36} {'par' if conj.startswith('par') else 'cadena':6} {x['n']:3d} {x['validas']:3d} {x['ordenables']:3d} | "
                      f"{fmt(x['1a_sobre_todas'])}     {fmt(x['1a_sobre_validas'])}  | {fmt(x['1b_repetibilidad'])}     {x['1b_orden_modal'] or '-':5} | "
                      f"{fmt(x['1c_coincidencia'])}    | {'CUMPLE' if x['criterio_1_cumplido'] else 'no cumple'}")

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps({
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "decision": "014", "sesion": args.sesion,
        "rol": "MEDICIÓN (conjunto de medición)" if args.sesion == 2 else "RÉPLICA EXPLORATORIA (no independiente)",
        "etiqueta": args.etiqueta, "version_motor": version_motor, "commit": _git(["rev-parse", "HEAD"], repo),
        "arbol_sucio": bool(sucio), "tau_primaria": 1, "taus": list(TAUS), "umbral": UMBRAL,
        "margen_ancla_s": MARGEN_ANCLA_S, "brazo_via": "codo",
        "repeticiones": filas, "resultado_por_tau": resultado,
    }, ensure_ascii=False, indent=1, default=list), encoding="utf-8")
    print(f"\nEscrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
