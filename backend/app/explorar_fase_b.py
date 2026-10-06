"""E4 — Exploración cualitativa de la Fase B por grupo (gesto, encuadre).

Reúne en un solo script reproducible (principio 5 del plan) tres análisis que se
hicieron primero en un scratchpad:

  1. **Sensibilidad al paso de muestreo.** Pico p99 de la velocidad angular de pelvis,
     torso y brazo calculada entre fotogramas separados por k = 1, 2, 4, 8
     (ω_k = ∠(u[i], u[i+k]) · fps / k). El movimiento real sostenido casi no cambia
     con k; el ruido de alta frecuencia cae. Un pico real pero BREVE (el brazo en el
     impacto, < 30 ms) también cae: no leer la caída del brazo como ruido. No depende
     de la segmentación.
  2. **Inversiones de z** (`detectar_inversiones_z`) y fracción de fotogramas con algún
     tramo excluido en E3 (cualquier articulación y coordenada: sobreestima lo que
     afecta a pelvis/torso/brazo).
  3. **Comparación por grupo**: orden pelvis → torso → brazo, desfases pelvis→torso y
     torso→brazo, y si el pico de la pelvis cae en vuelo (detector aproximado: ambos
     tobillos en imagen por encima de su nivel de apoyo; solo tiene sentido en el saque).

**Modos de segmentación** (`--segmentacion`, repetible; E3 se calcula una sola vez por clip):

  - ``clip``: el clip pre-cortado es UNA repetición; el pico de cada segmento es el
    máximo global del clip (puede ser otro evento).
  - ``auto``: valles de quietud (puede partir un clip en varias ventanas).
  - ``ancla-torso`` / ``ancla-pelvis``: UNA repetición por clip, ventana centrada en el
    pico global de ese segmento (± ``--margen-ms``, default 300). Sesgo a tener presente:
    al restringir la búsqueda a la vecindad del tronco se excluyen por construcción los
    picos tempranos del brazo; por eso cada repetición registra si el pico global del
    brazo (modo ``clip``) cae FUERA de la ventana (``brazo_global_fuera_de_ventana``).
    Además se registra cuánto difieren entre sí los instantes ancla de torso y de pelvis.

Es EXPLORATORIO: no toca umbrales ni calibra nada. Usa solo material propio
(`fuente = propio`) del catálogo. Escribe un JSON por modo en ``docs/resultados/`` y una
tabla por consola.

Uso (desde backend/):
    python -m app.explorar_fase_b                                # modo clip
    python -m app.explorar_fase_b -s clip -s auto -s ancla-torso -s ancla-pelvis
    python -m app.explorar_fase_b -s ancla-torso --grupo drive_perfil
    python -m app.explorar_fase_b -s clip -s ancla-torso --etiqueta e3-0.4.1   # no pisa corridas previas
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
from app.engine.sequencing import MARGEN_ANCLA_S, instante_ancla, secuenciar
from app.engine.version import __version__ as version_motor

PASOS = (1, 2, 4, 8)
MODOS = ("clip", "auto", "ancla-torso", "ancla-pelvis")
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
_ESPERADO = [s.value for s in ORDEN_ESPERADO]


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


def _secuenciar_modo(filt, lado: str, modo: str, brazo_via: str, margen_s: float):
    kw = dict(
        lado_dominante=lado, tramos_excluidos=filt.tramos_excluidos,
        brazo_via=brazo_via, corpus_publico=False,
    )
    if modo == "clip":
        kw["clip_completo"] = True
    elif modo.startswith("ancla-"):
        kw.update(ancla=modo.split("-", 1)[1], margen_ancla_s=margen_s)
    resultados, _ = secuenciar(filt.secuencia, **kw)
    return resultados


def _pico_abs_s(r, seg) -> float | None:
    p = r.picos.get(seg)
    return round(r.ventana.desde_s + p.instante_s, 4) if p and p.auditable else None


def _repeticiones(resultados, fps: float, vuelo, brazo_global_s: float | None) -> list[dict]:
    reps = []
    for r in resultados:
        abs_s = {seg: _pico_abs_s(r, seg) for seg in ORDEN_ESPERADO}
        pel, tor, bra = abs_s[S.PELVIS], abs_s[S.TORSO], abs_s[S.BRAZO]
        # + => el primero llega antes que el segundo
        dt_pt = round((tor - pel) * 1000, 1) if pel is not None and tor is not None else None
        dt_tb = round((bra - tor) * 1000, 1) if bra is not None and tor is not None else None
        en_vuelo = None
        if pel is not None:
            en_vuelo = bool(vuelo[min(int(round(pel * fps)), len(vuelo) - 1)])
        fuera = None
        if brazo_global_s is not None:
            fuera = not (r.ventana.desde_s <= brazo_global_s <= r.ventana.hasta_s)
        reps.append({
            "indice": r.indice,
            "ventana_s": [round(r.ventana.desde_s, 3), round(r.ventana.hasta_s, 3)],
            "orden": [x.value for x in r.orden_observado] if r.orden_observado else None,
            "motivo_no_auditable": r.motivo_no_auditable,
            "dt_pelvis_a_torso_ms": dt_pt,
            "dt_torso_a_brazo_ms": dt_tb,
            "pico_pelvis_en_vuelo": en_vuelo,
            "brazo_global_fuera_de_ventana": fuera,
            "picos": {
                seg.value: (
                    {"instante_abs_s": abs_s[seg], "velocidad": round(p.velocidad, 1)}
                    if p and p.auditable else {"no_auditable": p.motivo if p else None}
                )
                for seg, p in r.picos.items()
            },
        })
    return reps


def analizar_clip(seq, lado: str, *, modos: list[str], brazo_via: str, margen_s: float) -> dict:
    """Analiza un clip; devuelve {'comun': ..., 'modos': {modo: [repeticiones]}}."""
    try:
        filt = procesar_e3(seq)
    except ValueError as e:
        # Sin series utilizables (p. ej. jugador fuera de cuadro): no se estima nada.
        return {"comun": {"n_frames": seq.n_frames, "no_auditable": str(e)}, "modos": {}}
    s, fps = filt.secuencia, filt.secuencia.fps_efectivos

    excluidos: set[int] = set()
    for t in filt.tramos_excluidos:
        excluidos.update(range(t.desde_frame, t.hasta_frame + 1))

    # Instantes ancla (independientes del modo) y su acuerdo.
    anclas = {}
    for a in ("torso", "pelvis"):
        fr, _ = instante_ancla(s, lado, a, tramos_excluidos=filt.tramos_excluidos, brazo_via=brazo_via)
        anclas[a] = round(fr / fps, 4) if fr is not None else None
    dif = (round(abs(anclas["torso"] - anclas["pelvis"]) * 1000, 1)
           if None not in anclas.values() else None)

    # Pico global del brazo (modo clip): referencia del sesgo de selección.
    res_clip = _secuenciar_modo(filt, lado, "clip", brazo_via, margen_s)
    brazo_global = _pico_abs_s(res_clip[0], S.BRAZO)

    vuelo = frames_en_vuelo(seq)
    por_modo = {
        m: _repeticiones(_secuenciar_modo(filt, lado, m, brazo_via, margen_s), fps, vuelo, brazo_global)
        for m in modos
    }
    comun = {
        "n_frames": seq.n_frames,
        "fps_efectivos": fps,
        "pico_p99_por_paso": {
            seg.value: [round(x, 1) for x in pico_p99_por_paso(_vectores(s, seg, lado, brazo_via), fps)]
            for seg in ORDEN_ESPERADO
        },
        "inversiones_z": len(filt.validacion.inversiones_z),
        "frames_con_tramo_excluido_pct": round(100 * len(excluidos) / seq.n_frames, 1),
        "ancla_torso_s": anclas["torso"],
        "ancla_pelvis_s": anclas["pelvis"],
        "ancla_torso_vs_pelvis_ms": dif,
        "brazo_pico_global_s": brazo_global,
    }
    return {"comun": comun, "modos": por_modo}


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


def resumir_ordenes(clips: list[dict]) -> dict:
    """Conteos de órdenes sobre las repeticiones de un modo (un clip puede tener varias)."""
    reps = [r for c in clips if "no_auditable" not in c for r in c["repeticiones"]]
    aud = [r for r in reps if r["orden"]]
    fuera = [r["brazo_global_fuera_de_ventana"] for r in reps if r["brazo_global_fuera_de_ventana"] is not None]
    difs = [c["ancla_torso_vs_pelvis_ms"] for c in clips
            if "no_auditable" not in c and c.get("ancla_torso_vs_pelvis_ms") is not None]
    return {
        "repeticiones": len(reps),
        "auditables": len(aud),
        "pelvis_torso_brazo": sum(r["orden"] == _ESPERADO for r in aud),
        "brazo_primero": sum(r["orden"][0] == "brazo" for r in aud),
        "brazo_global_fuera_de_ventana": sum(fuera),
        "anclas_torso_vs_pelvis_dif_mediana_ms": _mediana(difs),
    }


def _fmt(x, ancho=6):
    return f"{x:{ancho}.0f}" if x is not None else "-".rjust(ancho)


def _n(x):
    return f"{x:.0f}" if x is not None else "-"


def _imprimir(modo: str, grupos: dict[str, dict], con_p99: bool) -> None:
    print(f"\n################ segmentación: {modo} ################")
    for g, datos in grupos.items():
        res, r = datos["resumen"], datos["resumen"]
        print(f"\n=== {g} ({r['clips']} clips, {r['clips_no_auditables']} no auditables) ===")
        for c in datos["clips"]:
            if "no_auditable" in c:
                print(f" {c['archivo'][-9:-4]}  no auditable: {c['no_auditable']}")
                continue
            p = c["pico_p99_por_paso"]
            linea = (" | ".join(" ".join(_fmt(x) for x in p[s]) for s in ("pelvis", "torso", "brazo"))
                     + f" | inv_z {c['inversiones_z']:3d} | ") if con_p99 else ""
            for rep in c["repeticiones"]:
                orden = ">".join(x[0] for x in rep["orden"]) if rep["orden"] else "-"
                extra = ""
                if rep["brazo_global_fuera_de_ventana"]:
                    extra = " [pico global del brazo FUERA de la ventana]"
                print(f" {c['archivo'][-9:-4]} {linea}{orden:6} p→t {_n(rep['dt_pelvis_a_torso_ms']):>5} "
                      f"t→b {_n(rep['dt_torso_a_brazo_ms']):>5} ms{extra}")
        if r["clips"] and con_p99:
            print(f" MEDIANAS: pelvis {_fmt(r['pelvis_k1_mediana'])}  torso {_fmt(r['torso_k1_mediana'])}  "
                  f"pelvis/torso {r['pelvis_sobre_torso_mediana']:.2f} | caída k1→k8: "
                  f"pelvis {r['caida_pelvis_k1_a_k8_pct']:.0f}%  brazo {r['caida_brazo_k1_a_k8_pct']:.0f}%")
        o = datos["ordenes"]
        print(f" ÓRDENES: {o['repeticiones']} repeticiones, {o['auditables']} auditables, "
              f"{o['pelvis_torso_brazo']} pelvis>torso>brazo, {o['brazo_primero']} con brazo primero"
              + (f", pico global del brazo fuera de la ventana en {o['brazo_global_fuera_de_ventana']}"
                 if modo.startswith("ancla") else ""))


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Exploración cualitativa de la Fase B por grupo.")
    parser.add_argument("-s", "--segmentacion", action="append", choices=MODOS, default=None,
                        help="Modo de segmentación (repetible). Default: clip.")
    parser.add_argument("--margen-ms", type=float, default=MARGEN_ANCLA_S * 1000,
                        help="± alrededor del ancla, en ms (default 300).")
    parser.add_argument("--brazo-via", choices=["codo", "muneca"], default="codo")
    parser.add_argument("--grupo", action="append", default=None,
                        help="gesto_encuadre (repetible), p. ej. drive_perfil. Default: los seis grupos base.")
    parser.add_argument("--sesion", type=int, default=None,
                        help="1 o 2 (fecha del nombre del clip). Default: todas las sesiones juntas.")
    parser.add_argument("--etiqueta", default="",
                        help="Sufijo del nombre de los JSON (p. ej. e3-0.4.1) para no pisar corridas previas.")
    parser.add_argument("--salida-dir", type=Path, default=_RESULTADOS,
                        help="Carpeta de los JSON (default: docs/resultados/).")
    args = parser.parse_args(argv)
    modos = args.segmentacion or ["clip"]

    from app.config import get_cache_dir, get_data_dir

    base = get_data_dir()
    backend = MediaPipeBackend()
    with (base / "catalogo.csv").open(encoding="utf-8", newline="") as f:
        filas = [r for r in csv.DictReader(f)
                 if r.get("fuente") == "propio" and "_rep" in r["archivo"]
                 and str(r.get("fps_efectivos")).strip() in ("240", "240.0")]  # los controles a 60/30 fps no son parte del conjunto

    fechas = sorted({r["archivo"][:8] for r in filas})
    # grupos[modo][grupo] = {"clips": [...]}
    grupos: dict[str, dict[str, dict]] = {m: defaultdict(lambda: {"clips": []}) for m in modos}
    for fila in filas:
        g = f"{fila['gesto']}_{fila['angulo']}"
        if g not in (args.grupo or GRUPOS_BASE):
            continue
        if args.sesion and fila["archivo"][:8] != fechas[args.sesion - 1]:
            continue
        video = next((p for p in (base / "fase-b").rglob(fila["archivo"])
                      if "originales" not in p.parts), None)
        seq = (pose_cache.cargar_si_vigente(get_cache_dir(), video, backend.id, backend.config_hash)
               if video else None)
        if seq is None:
            print(f"[aviso] sin pose cacheada: {fila['archivo']} (correr app.extraer_pose)")
            continue
        r = analizar_clip(seq, fila["lado_dominante"], modos=modos, brazo_via=args.brazo_via,
                          margen_s=args.margen_ms / 1000)
        for m in modos:
            clip = dict(r["comun"], archivo=fila["archivo"], repeticiones=r["modos"].get(m, []))
            grupos[m][g]["clips"].append(clip)

    if not any(grupos[m] for m in modos):
        print("No hay clips propios con pose cacheada para los grupos pedidos.")
        return 1

    args.salida_dir.mkdir(parents=True, exist_ok=True)
    for i, m in enumerate(modos):
        for datos in grupos[m].values():
            datos["resumen"] = resumir_grupo(datos["clips"])
            datos["ordenes"] = resumir_ordenes(datos["clips"])
        _imprimir(m, grupos[m], con_p99=(i == 0))
        sufijo = f"-{args.etiqueta}" if args.etiqueta else ""
        salida = args.salida_dir / f"e4-fase-b-exploratorio-{m}{sufijo}.json"
        salida.write_text(json.dumps({
            "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "version_motor": version_motor,
            "backend_pose": backend.version,
            "maquina": platform.platform(),
            "segmentacion": m,
            "margen_ancla_ms": args.margen_ms if m.startswith("ancla") else None,
            "brazo_via": args.brazo_via,
            "pasos_k": list(PASOS),
            "nota": "Exploratorio (E4): no calibra ni mide criterios. Un pico real breve "
                    "(brazo) tambien cae con k; no leerlo como ruido. En modos ancla la "
                    "ventana excluye por construccion los picos tempranos del brazo: ver "
                    "brazo_global_fuera_de_ventana.",
            "grupos": grupos[m],
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nEscrito: {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
