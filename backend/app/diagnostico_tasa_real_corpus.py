"""Sensibilidad de los resultados del corpus a una tasa real distinta de la supuesta (decisión 029).

El corpus propio está **horneado a 30 fps** (cámara lenta, todos los fotogramas, marcas de tiempo reescritas a 1/30 s): el archivo **no trae
la tasa real de la captura** y el motor supuso 240 fps. Medido el 9/10/2026 sobre un recorte con marcas reales, el iPhone captura "a 240" con
una **tasa media real de ~199 fps**, perdiendo fotogramas con un patrón casi periódico (cada ~12 fotogramas faltan dos).

Este script **no recalcula los criterios**. Mide cuánto cambian los resultados si el tiempo es irregular de esa manera:

  referencia  = las poses cacheadas, tratadas como una captura uniforme a 240 fps (lo que el motor midió);
  perturbada  = las mismas poses con fotogramas quitados según la **huella real** de pérdidas (``docs/resultados/tasa-real-iphone-huella.json``),
                tratadas **igual** como si fueran uniformes a 240 fps, que es lo que el motor hace con un archivo horneado.

Comparación, por repetición y por desplazamiento inicial de la huella:
  * orden de los picos (pelvis, torso, brazo) y si siguen siendo "ordenables" con la tolerancia del Criterio 1 (1, 2 y 3 fotogramas);
  * error en el instante de cada pico, en tiempo REAL (el instante real del fotograma perturbado es el de la referencia);
  * separación pelvis-torso aparente (lo que el motor reportaría) contra la real;
  * velocidad pico aparente contra la real;
  * el resultado del Criterio 1 por grupo, recalculado en cada "mundo" perturbado.

Solo lee la caché de pose. Determinista (los desplazamientos de la huella son fijos). Uso (desde ``backend/``):
    python -m app.diagnostico_tasa_real_corpus [--replicas 12]
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from app.engine.pipeline import procesar_e3
from app.engine.pose import cache as pose_cache
from app.engine.pose.mediapipe_backend import MediaPipeBackend
from app.engine.segmentos_corporales import SegmentoCadena as S
from app.engine.sequencing import MARGEN_ANCLA_S, secuenciar
from app.medicion_criterio1 import ESPERADO_CADENA, ESPERADO_PAR, TAUS, clasificar, parse_toma, resumir

FPS_SUPUESTO = 240.0
_LETRA = {S.PELVIS: "p", S.TORSO: "t", S.BRAZO: "b"}
_RAIZ = Path(__file__).resolve().parents[2]


def indices_con_perdidas(n_frames: int, intervalos: list[int], desplazamiento: int) -> list[int]:
    """Índices de la referencia que sobreviven al aplicar la huella de pérdidas (pura).

    ``intervalos[k]`` = períodos entre el fotograma k y el k+1 (1 = consecutivos, 3 = faltan dos). La huella se recorre cíclicamente desde
    ``desplazamiento``. Devuelve [0, i1, i2, ...] con todos los índices < n_frames.
    """
    if not intervalos or n_frames <= 0:
        return list(range(max(n_frames, 0)))
    indices, pos, k = [0], 0, desplazamiento % len(intervalos)
    while True:
        pos += int(intervalos[k % len(intervalos)])
        if pos >= n_frames:
            return indices
        indices.append(pos)
        k += 1


def quitar_fotogramas(seq, indices: list[int]):
    """Secuencia con solo los fotogramas ``indices``, reindexados 0..m-1 (lo que ve un archivo horneado: fotogramas consecutivos)."""
    frames = [dataclasses.replace(seq.frames[i], indice=j) for j, i in enumerate(indices)]
    return dataclasses.replace(seq, frames=frames)


def medir_picos(seq, lado: str) -> dict:
    """Frame, instante aparente (s) y velocidad (°/s) del pico de cada segmento; ``None`` si no es auditable."""
    try:
        filt = procesar_e3(seq)
    except ValueError as e:
        return {"valida": False, "motivo": str(e), "picos": {}}
    resultados, _ = secuenciar(
        filt.secuencia, lado_dominante=lado, tramos_excluidos=filt.tramos_excluidos,
        brazo_via="codo", ancla="torso", margen_ancla_s=MARGEN_ANCLA_S,
    )
    rep = resultados[0]
    picos = {}
    for seg in (S.PELVIS, S.TORSO, S.BRAZO):
        p = rep.picos.get(seg)
        picos[_LETRA[seg]] = (
            {"frame": int(p.frame), "velocidad": float(p.velocidad)} if p is not None and p.auditable else None
        )
    return {"valida": picos["t"] is not None, "motivo": rep.motivo_no_auditable, "picos": picos, "corte_hz": float(filt.corte_hz)}


def _procesar_clip(args: tuple) -> dict:
    """Una repetición: la referencia y las perturbadas. Corre en un proceso aparte (cada una tarda varios segundos por el filtrado de Winter)."""
    nombre, lado, intervalos, desplazamientos = args
    from app.config import get_cache_dir, get_data_dir
    from app.diagnosticos_e3 import _buscar_video

    b = MediaPipeBackend()
    seq = pose_cache.cargar_si_vigente(get_cache_dir(), _buscar_video(get_data_dir(), nombre), b.id, b.config_hash)
    if seq is None:
        raise RuntimeError(f"sin pose cacheada para {nombre}")
    salida = {"ref": medir_picos(seq, lado), "pert": {}, "tasa": []}
    for d in desplazamientos:
        idx = indices_con_perdidas(seq.n_frames, intervalos, d)
        salida["tasa"].append(FPS_SUPUESTO * len(idx) / seq.n_frames)
        m = medir_picos(quitar_fotogramas(seq, idx), lado)
        m["idx"] = idx
        salida["pert"][d] = m
    return salida


def _pct(a, q):
    a = np.asarray([x for x in a if x is not None and np.isfinite(x)], dtype=float)
    return round(float(np.percentile(a, q)), 3) if a.size else None


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--replicas", type=int, default=12, help="desplazamientos de la huella por repetición")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--huella", type=Path, default=_RAIZ / "docs/resultados/tasa-real-iphone-huella.json")
    ap.add_argument("--salida", type=Path, default=_RAIZ / "docs/resultados/tasa-real-sensibilidad.json")
    args = ap.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir
    from app.diagnosticos_e3 import _buscar_video, _catalogo, en_sesion, fechas_propias

    huella = json.loads(args.huella.read_text(encoding="utf-8"))
    intervalos = [int(x) for x in huella["intervalos_en_periodos"]]
    desplazamientos = [round(i * len(intervalos) / args.replicas) for i in range(args.replicas)]

    base = get_data_dir()
    cat = _catalogo(base)
    fechas = fechas_propias(cat)
    clips = [(n, r) for n, r in sorted(cat.items())
             if r.get("fuente") == "propio" and "_rep" in n and r.get("angulo") in ("perfil", "trescuartos")
             and str(r.get("fps_efectivos")).strip() in ("240", "240.0") and (en_sesion(n, 1, fechas) or en_sesion(n, 2, fechas))]
    print(f"{len(clips)} repeticiones; {args.replicas} desplazamientos de la huella; huella de {len(intervalos)} intervalos "
          f"({huella['fps_real_media']} fps reales de {huella['fps_nominal']} nominales); {args.procesos} procesos.", flush=True)

    ref, pert = {}, defaultdict(dict)          # pert[desplazamiento][clip]
    tasa_efectiva = []
    tareas = [(n, r["lado_dominante"], intervalos, desplazamientos) for n, r in clips]
    with ProcessPoolExecutor(max_workers=args.procesos) as ex:
        for (n, r), res in zip(clips, ex.map(_procesar_clip, tareas)):
            ref[n] = {"meta": r, "med": res["ref"]}
            tasa_efectiva.extend(res["tasa"])
            for d, m in res["pert"].items():
                pert[d][n] = m
            print(f"  {n[-40:]:40} ref válida={res['ref']['valida']!s:5} p/t/b="
                  f"{[(res['ref']['picos'].get(l) or {}).get('frame') for l in 'ptb']}", flush=True)

    # --- por repetición y desplazamiento -----------------------------------------------------------
    err_ms = {l: [] for l in "ptb"}
    sep_pt_aparente, sep_pt_real, razon_vel = [], [], {l: [] for l in "ptb"}
    orden_igual = {"pt": [0, 0], "ptb": [0, 0]}
    filas = []   # una por corrida válida: separación pelvis-torso de la referencia, si el orden cambia, errores de pico
    ordenable_cambia = {tau: [0, 0] for tau in TAUS}
    for d, por_clip in pert.items():
        for n, m in por_clip.items():
            rf, pf = ref[n]["med"], m
            if not (rf["valida"] and pf["valida"]):
                continue
            idx = m["idx"]
            tiempos_ref = {l: (rf["picos"][l]["frame"] / FPS_SUPUESTO if rf["picos"].get(l) else None) for l in "ptb"}
            tiempos_real = {l: (idx[pf["picos"][l]["frame"]] / FPS_SUPUESTO if pf["picos"].get(l) else None) for l in "ptb"}
            for l in "ptb":
                if tiempos_ref[l] is not None and tiempos_real[l] is not None:
                    err_ms[l].append(abs(tiempos_real[l] - tiempos_ref[l]) * 1000)
                    razon_vel[l].append(pf["picos"][l]["velocidad"] / rf["picos"][l]["velocidad"])
            if tiempos_ref["p"] is not None and tiempos_real["p"] is not None and tiempos_ref["t"] is not None:
                sep_pt_real.append((tiempos_ref["t"] - tiempos_ref["p"]) * 1000)
                sep_pt_aparente.append((pf["picos"]["t"]["frame"] - pf["picos"]["p"]["frame"]) / FPS_SUPUESTO * 1000)
            fr_ref = {l: (rf["picos"][l] or {}).get("frame") if rf["picos"].get(l) else None for l in "ptb"}
            fr_pert = {l: (pf["picos"][l] or {}).get("frame") if pf["picos"].get(l) else None for l in "ptb"}
            if fr_ref["p"] is not None and fr_ref["t"] is not None and fr_pert["p"] is not None:
                filas.append({
                    "sep_ref": abs(fr_ref["t"] - fr_ref["p"]),
                    "orden_cambia": clasificar(fr_ref, True, "pt", 1)["orden"] != clasificar(fr_pert, True, "pt", 1)["orden"],
                    "err": {l: (abs(tiempos_real[l] - tiempos_ref[l]) * 1000 if tiempos_ref[l] is not None and tiempos_real[l] is not None else None) for l in "ptb"},
                })
            letras = ["pt"] + (["ptb"] if ref[n]["meta"]["angulo"] == "trescuartos" else [])
            for letra in letras:
                a = clasificar(fr_ref, True, letra, 1)["orden"]
                c = clasificar(fr_pert, True, letra, 1)["orden"]
                if a is not None and c is not None:
                    orden_igual[letra][1] += 1
                    orden_igual[letra][0] += int(a == c)
            for tau in TAUS:
                a = clasificar(fr_ref, True, "pt", tau)["ordenable"]
                c = clasificar(fr_pert, True, "pt", tau)["ordenable"]
                ordenable_cambia[tau][1] += 1
                ordenable_cambia[tau][0] += int(a != c)

    # --- por separación pelvis-torso de la referencia, y saltos de pico ------------------------------
    SALTO_MS = 50.0   # un pico que se corre más que esto no es "jitter": la perturbación hizo ganar a OTRO máximo local
    bins = [("0-1 fotogramas", 0, 1), ("2-3", 2, 3), ("4-8", 4, 8), ("9-20", 9, 20), (">20", 21, 10**9)]
    por_separacion = {}
    for nombre, lo, hi in bins:
        sub = [f for f in filas if lo <= f["sep_ref"] <= hi]
        por_separacion[nombre] = {
            "corridas": len(sub),
            "orden_cambia_fraccion": round(sum(f["orden_cambia"] for f in sub) / len(sub), 3) if sub else None,
        }
    saltos = {}
    for l in "ptb":
        e = [f["err"][l] for f in filas if f["err"][l] is not None]
        chicos = [x for x in e if x <= SALTO_MS]
        saltos[l] = {
            "corridas": len(e),
            "salto_a_otro_pico_fraccion": round(1 - len(chicos) / len(e), 3) if e else None,
            "error_ms_sin_saltos_p50": _pct(chicos, 50), "error_ms_sin_saltos_p90": _pct(chicos, 90),
        }
    seps = [f["sep_ref"] for f in {id(x): x for x in filas}.values()]

    # --- Criterio 1 por grupo, referencia contra cada "mundo" perturbado ---------------------------
    def criterio1(medidas: dict[str, dict]) -> dict:
        grupos = defaultdict(list)
        for n, m in medidas.items():
            r = ref[n]["meta"]
            fr = {l: (m["picos"].get(l) or {}).get("frame") for l in "ptb"}
            fila = {"frames": fr, "valida": m["valida"], "tres": r["angulo"] == "trescuartos"}
            grupos[f"{r['gesto']}|{r['angulo']}"].append(fila)
        salida = {}
        for g, L in sorted(grupos.items()):
            salida[g] = {}
            for tau in TAUS:
                e = {"par": resumir([clasificar(f["frames"], f["valida"], "pt", tau) for f in L], ESPERADO_PAR)}
                if g.endswith("trescuartos"):
                    e["cadena"] = resumir([clasificar(f["frames"], f["valida"], "ptb", tau) for f in L], ESPERADO_CADENA)
                salida[g][str(tau)] = e
        return salida

    c_ref = criterio1({n: v["med"] for n, v in ref.items()})
    c_pert = [criterio1(por_clip) for por_clip in pert.values()]
    cambios = {}
    for g, porTau in c_ref.items():
        for tau, conjuntos in porTau.items():
            for conj, x in conjuntos.items():
                mundos = [w[g][tau][conj] for w in c_pert]
                cambios[f"{g}|tau={tau}|{conj}"] = {
                    "referencia_cumple": x["criterio_1_cumplido"],
                    "mundos_que_cumplen": sum(m["criterio_1_cumplido"] for m in mundos),
                    "mundos": len(mundos),
                    "1a_referencia": None if x["1a_sobre_todas"] is None else round(x["1a_sobre_todas"], 3),
                    "1a_mundos_min_max": [round(min((m["1a_sobre_todas"] or 0) for m in mundos), 3), round(max((m["1a_sobre_todas"] or 0) for m in mundos), 3)],
                    "1b_referencia": None if x["1b_repetibilidad"] is None else round(x["1b_repetibilidad"], 3),
                    "1b_mundos_min_max": [round(min((m["1b_repetibilidad"] or 0) for m in mundos), 3), round(max((m["1b_repetibilidad"] or 0) for m in mundos), 3)],
                }

    resumen = {
        "descripcion": "Sensibilidad del corpus a una tasa real distinta de la supuesta (decisión 029). NO recalcula los criterios.",
        "huella": {k: huella[k] for k in ("fps_nominal", "fps_real_media", "fotogramas_perdidos_pct", "intervalos_en_periodos_resumen")},
        "repeticiones": len(clips), "replicas": args.replicas, "corridas": len(clips) * args.replicas,
        "tasa_efectiva_simulada_fps": {"p10": _pct(tasa_efectiva, 10), "p50": _pct(tasa_efectiva, 50), "p90": _pct(tasa_efectiva, 90)},
        "orden_de_los_picos": {k: {"igual": v[0], "de": v[1], "fraccion": round(v[0] / v[1], 4) if v[1] else None} for k, v in orden_igual.items()},
        "ordenable_cambia_par_pelvis_torso": {f"tau={t}": {"cambia": v[0], "de": v[1], "fraccion": round(v[0] / v[1], 4) if v[1] else None} for t, v in ordenable_cambia.items()},
        "separacion_pelvis_torso_de_la_referencia_en_fotogramas": {
            "p25": _pct(seps, 25), "p50": _pct(seps, 50), "p75": _pct(seps, 75),
            "fraccion_menor_o_igual_a": {f"{t}": round(sum(1 for x in seps if x <= t) / len(seps), 3) for t in (0, 1, 2, 3, 5, 8)},
        },
        "orden_cambia_segun_la_separacion_de_la_referencia": por_separacion,
        "picos_que_saltan_a_otro_maximo_mas_de_50_ms": saltos,
        "error_instante_pico_ms_en_tiempo_real": {l: {"p50": _pct(err_ms[l], 50), "p90": _pct(err_ms[l], 90), "max": _pct(err_ms[l], 100), "n": len(err_ms[l])} for l in "ptb"},
        "separacion_pelvis_torso_ms": {
            "real_p50": _pct(sep_pt_real, 50), "aparente_p50": _pct(sep_pt_aparente, 50),
            "razon_aparente_sobre_real_mediana": round(float(np.median(np.array(sep_pt_aparente) / np.array(sep_pt_real))), 3)
            if sep_pt_real and all(x != 0 for x in sep_pt_real) else None,
        },
        "velocidad_pico_aparente_sobre_real": {l: {"p10": _pct(razon_vel[l], 10), "p50": _pct(razon_vel[l], 50), "p90": _pct(razon_vel[l], 90)} for l in "ptb"},
        "factor_teorico_de_escala": {"velocidades": round(FPS_SUPUESTO / huella["fps_real_media"], 3), "intervalos_en_ms": round(huella["fps_real_media"] / FPS_SUPUESTO, 3)},
        "criterio_1_por_grupo": cambios,
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in resumen.items() if k != "criterio_1_por_grupo"}, ensure_ascii=False, indent=1))
    print(f"\nEscrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
