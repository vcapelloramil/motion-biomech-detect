"""Diagnósticos de E3/E4 versionados (principio 5 del plan): salen de un scratchpad.

Subcomandos (desde backend/):

  sin-filtrar         Qué series (hombro/codo/muñeca del lado dominante, caderas, hombros)
                      tenían algún NaN y por lo tanto quedaban SIN FILTRAR entera en E3
                      anterior a 0.4.1 (decisión 010). Por clip y agregado por corpus.
  comparar-brazo      Velocidad del segmento brazo con hombro→codo vs hombro→muñeca, bajo
                      tres estados del pipeline: A) "decisión 008": E3 viejo y sin el detector
                      de inversión de z (v0.3.0); B) E3 viejo con detector (0.4.0);
                      C) E3 nuevo con detector (0.4.1). Sirve para revisar de forma
                      retroactiva la elección del codo y el techo de plausibilidad ×3.
  corte-brazo         ¿Un solo corte de Winter por clip sirve para el brazo? Corte por serie
                      (método actual: valores válidos concatenados vs tramo continuo más
                      largo) y barrido del corte SOLO del codo (6–20 Hz; el resto en el corte
                      del clip) sobre velocidad, orden y adelanto del brazo (ancla de torso).
  serie-articulacion  Serie fotograma a fotograma de una articulación (crudo vs filtrado,
                      confianza, ω del segmento, marcas de validación).
  salto-articulacion  Desplazamiento por fotograma de una articulación, en cm y en torsos.
  montaje             Fotogramas con el brazo/caderas/hombros dibujados en instantes dados.
  angulo-plano        Ángulo de pelvis y torso en el plano horizontal x-z, alrededor de un pico.

Todos son de SOLO LECTURA sobre la caché de pose: no modifican el motor ni el catálogo.

"E3 viejo" se reproduce aquí (`filtrar_e3_viejo`) porque el código real ya no lo hace: toda
serie con algún NaN se dejaba entera sin filtrar; las completas se filtraban de fase cero.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from app.engine.dsp import butterworth_fase_cero, butterworth_fase_cero_por_segmentos
from app.engine.pipeline import GAP_MAX_INTERPOLABLE, _reconstruir_secuencia, procesar_e3
from app.engine.pose import cache as pose_cache
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.mediapipe_backend import MediaPipeBackend
from app.engine.preparacion import preparar_series
from app.engine.segmentos_corporales import SegmentoCadena as S, vector_segmento
from app.engine.validation import largo_torso, validar
from app.engine.version import __version__ as version_motor
from app.engine.dsp import segmentos_continuos
from app.engine.sequencing import secuenciar
from app.engine.winter import (
    ARTICULACIONES_RAPIDAS,
    FACTOR_NIVEL_RUIDO,
    analizar_serie,
    elegir_corte,
)

_RESULTADOS = Path(__file__).resolve().parents[2] / "docs" / "resultados"
ESTADOS = {
    "A": ("viejo", "sin_z"),     # decisión 008: E3 viejo, sin detector de inversión de z
    "B": ("viejo", "actual"),    # 0.4.0
    "C": ("nuevo", "actual"),    # 0.4.1
}


# --- carga ----------------------------------------------------------------------------

def _catalogo(base: Path) -> dict[str, dict]:
    with (base / "catalogo.csv").open(encoding="utf-8", newline="") as f:
        return {r["archivo"]: r for r in csv.DictReader(f) if r.get("archivo")}


def _buscar_video(base: Path, nombre: str) -> Path:
    for fase in ("fase-a", "fase-b"):
        for p in (base / fase).rglob(nombre):
            if p.is_file() and not ({"originales", "compilaciones"} & set(p.relative_to(base / fase).parts)):
                return p
    raise SystemExit(f"no se encontró {nombre} bajo fase-a/ ni fase-b/")


def cargar(nombre: str):
    from app.config import get_cache_dir, get_data_dir

    base = get_data_dir()
    video = _buscar_video(base, nombre)
    b = MediaPipeBackend()
    seq = pose_cache.cargar_si_vigente(get_cache_dir(), video, b.id, b.config_hash)
    if seq is None:
        raise SystemExit(f"sin pose cacheada para {nombre} (correr app.extraer_pose)")
    fila = _catalogo(base).get(nombre, {})
    return seq, fila


# --- núcleo reutilizable (puro; probado en tests/unit/test_diagnosticos_e3.py) ---------

def validacion_estado(seq, estado: str):
    """``actual``: como el pipeline. ``sin_z``: sin el detector de inversión de z (v0.3.0)."""
    val = validar(seq, espacio="mundo")
    return dataclasses.replace(val, inversiones_z=[]) if estado == "sin_z" else val


def filtrar_e3_viejo(series: dict, *, fps: float, corte_hz: float, orden: int = 4) -> dict:
    """Reproduce E3 anterior a 0.4.1: la serie con algún NaN queda entera cruda."""
    salida = {}
    for clave, s in series.items():
        if np.isnan(s).any():
            salida[clave] = s
            continue
        try:
            salida[clave] = butterworth_fase_cero(s, fps=fps, corte_hz=corte_hz, orden=orden)
        except Exception:
            salida[clave] = s
    return salida


def filtrar_e3_nuevo(series: dict, *, fps: float, corte_hz: float, orden: int = 4) -> dict:
    return {
        k: butterworth_fase_cero_por_segmentos(s, fps=fps, corte_hz=corte_hz, orden=orden)[0]
        for k, s in series.items()
    }


def series_filtradas(seq, estado_pipeline: str, estado_validacion: str):
    """(series_preparadas, series_filtradas, corte_hz) del estado pedido."""
    fps = seq.fps_efectivos
    val = validacion_estado(seq, estado_validacion)
    series, _ = preparar_series(seq, val, espacio="mundo", gap_max=GAP_MAX_INTERPOLABLE)
    corte = elegir_corte(series, fps=fps, orden=4).corte_elegido_hz
    filtro = filtrar_e3_viejo if estado_pipeline == "viejo" else filtrar_e3_nuevo
    return series, filtro(series, fps=fps, corte_hz=corte), corte


def vector_unitario(series: dict, a, b) -> np.ndarray:
    """Vector a→b unitario por fotograma; NaN si falta cualquier coordenada de un extremo."""
    n = len(next(iter(series.values())))
    u = np.full((n, 3), np.nan)
    try:
        d = np.stack([series[(b, c)] - series[(a, c)] for c in "xyz"], axis=1)
    except KeyError:
        return u
    norma = np.linalg.norm(d, axis=1)
    ok = np.isfinite(norma) & (norma > 0)
    u[ok] = d[ok] / norma[ok, None]
    return u


def omega_k(u: np.ndarray, fps: float, k: int = 1) -> np.ndarray:
    """ω_k (°/s) = ∠(u[i], u[i+k]) · fps / k, alineada a i+k; NaN donde falte un extremo."""
    salida = np.full(len(u), np.nan)
    cos = np.einsum("ij,ij->i", u[:-k], u[k:])
    salida[k:] = np.degrees(np.arccos(np.clip(cos, -1, 1))) * fps / k
    return salida


def p99(x: np.ndarray) -> float | None:
    v = x[np.isfinite(x)]
    return float(np.percentile(v, 99)) if v.size else None


def articulaciones_brazo(lado: str, via: str):
    return vector_segmento(S.BRAZO, lado, brazo_via=via)


# --- sin-filtrar ---------------------------------------------------------------------

def _grupos_series(lado: str) -> dict[str, tuple]:
    dom = "DER" if lado == "der" else "IZQ"
    return {
        "pelvis": (A.CADERA_IZQ, A.CADERA_DER),
        "torso": (A.HOMBRO_IZQ, A.HOMBRO_DER),
        "hombro": (A[f"HOMBRO_{dom}"],),
        "codo": (A[f"CODO_{dom}"],),
        "muneca": (A[f"MUNECA_{dom}"],),
    }


def cmd_sin_filtrar(args) -> int:
    from app.config import get_data_dir

    base = get_data_dir()
    cat = _catalogo(base)
    nombres = args.clip or [n for n, r in cat.items() if r.get("lado_dominante") in ("der", "izq")]
    conteo = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # [(corpus, estado)][grupo] = [sin_filtrar, total]
    filas = []
    for nombre in nombres:
        fila = cat.get(nombre, {})
        lado = fila.get("lado_dominante")
        if lado not in ("der", "izq"):
            continue
        try:
            seq, _ = cargar(nombre)
        except SystemExit:
            continue
        corpus = "propio" if fila.get("fuente") == "propio" else "publico"
        for est in ("sin_z", "actual"):
            series, _ = preparar_series(seq, validacion_estado(seq, est), espacio="mundo",
                                        gap_max=GAP_MAX_INTERPOLABLE)
            for g, arts in _grupos_series(lado).items():
                claves = [(a, c) for a in arts for c in "xyz" if (a, c) in series]
                sin = sum(bool(np.isnan(series[k]).any()) for k in claves)
                frac = float(np.mean([np.isnan(series[k]).mean() for k in claves])) if claves else None
                conteo[(corpus, est)][g][0] += sin
                conteo[(corpus, est)][g][1] += len(claves)
                filas.append({"clip": nombre, "corpus": corpus, "validacion": est, "grupo": g,
                              "series_sin_filtrar": sin, "series": len(claves),
                              "fraccion_nan_media": None if frac is None else round(frac, 3)})
    print("Series con algún NaN (= SIN FILTRAR en E3 anterior a 0.4.1)")
    print("  validacion: sin_z = sin detector de inversión de z (v0.3.0) | actual = con detector")
    for (corpus, est), g in sorted(conteo.items()):
        print(f"\n[{corpus} | {est}]")
        for grupo, (sin, tot) in g.items():
            print(f"  {grupo:8} {sin:4d}/{tot:<4d} ({100 * sin / tot if tot else 0:3.0f}%)")
    if args.salida:
        Path(args.salida).write_text(json.dumps({"version_motor": version_motor, "filas": filas},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nEscrito: {args.salida}")
    return 0


# --- comparar-brazo -------------------------------------------------------------------

def medir_brazo(seq, lado: str) -> dict:
    """p99 de ω a k=1 y k=8 del brazo (codo y muñeca) en los tres estados A/B/C."""
    fps = seq.fps_efectivos
    salida = {}
    cache_series: dict = {}
    for est, (pipe, val) in ESTADOS.items():
        series, filtradas, corte = series_filtradas(seq, pipe, val)
        cache_series[est] = (series, filtradas)
        r = {"corte_hz": round(corte, 1)}
        for via in ("codo", "muneca"):
            a, b = articulaciones_brazo(lado, via)
            u = vector_unitario(filtradas, a, b)
            w1, w8 = omega_k(u, fps, 1), omega_k(u, fps, 8)
            r[via] = {
                "p99_k1": p99(w1), "p99_k8": p99(w8),
                "fraccion_validos": round(float(np.isfinite(w1).mean()), 3),
                "serie_distal_con_nan": bool(np.isnan(series.get((b, "x"), np.array([np.nan]))).any()),
            }
        salida[est] = r
    return salida


def cmd_comparar_brazo(args) -> int:
    from app.config import get_data_dir

    cat = _catalogo(get_data_dir())
    nombres = args.clip or [n for n, r in cat.items()
                            if (r.get("fuente") != "propio") and r.get("lado_dominante") in ("der", "izq")]
    resultados = {}
    print("p99 de ω del brazo (°/s) — A: E3 viejo sin z (decisión 008) | B: E3 viejo con z (0.4.0) | C: E3 nuevo (0.4.1)")
    print(f"{'clip':34} {'via':6} | {'A k1':>7} {'A k8':>7} | {'B k1':>7} {'B k8':>7} | {'C k1':>7} {'C k8':>7} | distal con NaN (A/B/C)")
    for nombre in nombres:
        lado = cat[nombre].get("lado_dominante")
        if lado not in ("der", "izq"):
            continue
        try:
            seq, _ = cargar(nombre)
        except SystemExit:
            continue
        m = medir_brazo(seq, lado)
        resultados[nombre] = m
        for via in ("codo", "muneca"):
            f = lambda e, k: m[e][via][k]
            fmt = lambda x: f"{x:7.0f}" if x is not None else "      -"
            nans = "/".join("S" if m[e][via]["serie_distal_con_nan"] else "n" for e in "ABC")
            print(f"{nombre[:34]:34} {via:6} | {fmt(f('A','p99_k1'))} {fmt(f('A','p99_k8'))} | "
                  f"{fmt(f('B','p99_k1'))} {fmt(f('B','p99_k8'))} | {fmt(f('C','p99_k1'))} {fmt(f('C','p99_k8'))} | {nans}")
    if args.salida:
        Path(args.salida).write_text(json.dumps({"version_motor": version_motor, "clips": resultados},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nEscrito: {args.salida}")
    return 0


# --- corte-brazo ----------------------------------------------------------------------

CORTES_BARRIDO = (6.0, 8.0, 10.0, 12.0, 15.0, 20.0)
MIN_MUESTRAS_WINTER = 30          # el mismo mínimo que engine.winter.elegir_corte


def corte_de_serie(serie: np.ndarray, *, fps: float, orden: int = 4) -> float | None:
    """Corte de Winter de UNA serie (mismo criterio que ``elegir_corte``), o None si es corta."""
    v = serie[~np.isnan(serie)]
    if v.size <= MIN_MUESTRAS_WINTER:
        return None
    cortes, residuos, nivel = analizar_serie(v, fps=fps, orden=orden)
    bajo = np.where(residuos <= nivel * FACTOR_NIVEL_RUIDO)[0]
    return float(cortes[bajo[0]] if len(bajo) else cortes[-1])


def tramo_mas_largo(serie: np.ndarray) -> np.ndarray:
    """Tramo continuo (sin NaN) más largo; array vacío si no hay ninguno."""
    tramos = segmentos_continuos(serie)
    if not tramos:
        return np.array([])
    d, h = max(tramos, key=lambda t: t[1] - t[0])
    return serie[d:h + 1]


def cortes_por_articulacion(series: dict, *, fps: float, metodo: str) -> dict:
    """{articulacion: [corte por coordenada]}; metodo: 'concatenado' (el del pipeline) o 'tramo'."""
    salida: dict = defaultdict(list)
    for (art, _c), s_ in sorted(series.items(), key=lambda kv: (kv[0][0].value, kv[0][1])):
        base = s_ if metodo == "concatenado" else tramo_mas_largo(s_)
        c = corte_de_serie(base, fps=fps)
        if c is not None:
            salida[art].append(c)
    return dict(salida)


def filtrar_con_cortes(series: dict, *, fps: float, corte_base: float, especiales: dict) -> dict:
    """Filtra por segmentos con ``corte_base`` salvo las articulaciones de ``especiales``."""
    return {
        (art, c): butterworth_fase_cero_por_segmentos(
            s_, fps=fps, corte_hz=especiales.get(art, corte_base), orden=4)[0]
        for (art, c), s_ in series.items()
    }


def barrer_corte_codo(seq, filt, series, lado: str) -> dict:
    """Barre el corte del codo dominante; devuelve {corte: métricas del brazo}."""
    fps = seq.fps_efectivos
    codo = A[f"CODO_{'DER' if lado == 'der' else 'IZQ'}"]
    a, b = articulaciones_brazo(lado, "codo")
    salida = {}
    for x in CORTES_BARRIDO:
        f = filtrar_con_cortes(series, fps=fps, corte_base=filt.corte_hz, especiales={codo: x})
        u = vector_unitario(f, a, b)
        w1, w8 = omega_k(u, fps, 1), omega_k(u, fps, 8)
        sec = _reconstruir_secuencia(seq, f, espacio="mundo")
        r, _ = secuenciar(sec, lado_dominante=lado, tramos_excluidos=filt.tramos_excluidos,
                          brazo_via="codo", ancla="torso")
        rep_ = r[0]
        pb, pt = rep_.picos.get(S.BRAZO), rep_.picos.get(S.TORSO)
        dt = None
        if pb and pt and pb.auditable and pt.auditable:
            dt = round((pb.instante_s - pt.instante_s) * 1000, 1)     # + => el brazo llega después
        salida[str(x)] = {
            "p99_k1": p99(w1), "p99_k8": p99(w8),
            "orden": "".join(o.value[0] for o in rep_.orden_observado) if rep_.orden_observado else None,
            "dt_torso_a_brazo_ms": dt,
            "pico_brazo": round(pb.velocidad, 1) if pb and pb.auditable else None,
        }
    return salida


def cmd_corte_brazo(args) -> int:
    from app.config import get_data_dir

    cat = _catalogo(get_data_dir())
    grupos = args.grupo or [f"{g}_{e}" for g in ("saque", "drive", "reves") for e in ("perfil", "trescuartos")]
    filas = {}
    for nombre, r in cat.items():
        g = f"{r.get('gesto')}_{r.get('angulo')}"
        if r.get("fuente") != "propio" or "_rep" not in nombre or g not in grupos:
            continue
        seq, _ = cargar(nombre)
        lado = r["lado_dominante"]
        fps = seq.fps_efectivos
        try:
            filt = procesar_e3(seq)
        except ValueError:
            continue
        series, _ = preparar_series(seq, filt.validacion, espacio="mundo", gap_max=GAP_MAX_INTERPOLABLE)
        dom = "DER" if lado == "der" else "IZQ"
        conc = cortes_por_articulacion(series, fps=fps, metodo="concatenado")
        tram = cortes_por_articulacion(series, fps=fps, metodo="tramo")
        rapidas = [c for a_, cs in conc.items() if a_ in ARTICULACIONES_RAPIDAS for c in cs]
        rapidas_t = [c for a_, cs in tram.items() if a_ in ARTICULACIONES_RAPIDAS for c in cs]

        def mx(d, *arts):
            v = [max(d[a_]) for a_ in arts if a_ in d]
            return max(v) if v else None

        por_art = {
            "pelvis": mx(conc, A.CADERA_IZQ, A.CADERA_DER),
            "torso": mx(conc, A.HOMBRO_IZQ, A.HOMBRO_DER),
            "hombro_dom": mx(conc, A[f"HOMBRO_{dom}"]),
            "codo_dom": mx(conc, A[f"CODO_{dom}"]),
            "muneca_dom": mx(conc, A[f"MUNECA_{dom}"]),
        }
        filas[nombre] = {
            "grupo": g, "corte_clip_hz": filt.corte_hz,
            "corte_rapidas_concatenado": max(rapidas) if rapidas else None,
            "corte_rapidas_tramo_largo": max(rapidas_t) if rapidas_t else None,
            "por_articulacion_concatenado": por_art,
            "barrido_codo": barrer_corte_codo(seq, filt, series, lado),
        }
        print(f"{nombre[-22:]:22} corte clip {filt.corte_hz:4.1f} | tramo largo {filas[nombre]['corte_rapidas_tramo_largo']} | "
              f"codo {por_art['codo_dom']} muñeca {por_art['muneca_dom']} pelvis {por_art['pelvis']} torso {por_art['torso']}")
    por_grupo = defaultdict(list)
    for f in filas.values():
        por_grupo[f["grupo"]].append(f)
    print("\nBarrido del corte del codo (mediana por grupo): p99 ω k=1 | caída k1→k8 | brazo primero | p>t>b | adelanto (ms, + = brazo después)")
    for g, L in por_grupo.items():
        print(f"\n{g} (corte clip mediano {np.median([f['corte_clip_hz'] for f in L]):.0f} Hz)")
        for x in CORTES_BARRIDO:
            k = str(x)
            v1 = [f["barrido_codo"][k]["p99_k1"] for f in L if f["barrido_codo"][k]["p99_k1"]]
            cai = [100 * (1 - f["barrido_codo"][k]["p99_k8"] / f["barrido_codo"][k]["p99_k1"])
                   for f in L if f["barrido_codo"][k]["p99_k1"]]
            ords = [f["barrido_codo"][k]["orden"] for f in L if f["barrido_codo"][k]["orden"]]
            dts = [f["barrido_codo"][k]["dt_torso_a_brazo_ms"] for f in L
                   if f["barrido_codo"][k]["dt_torso_a_brazo_ms"] is not None]
            print(f"  codo a {x:4.0f} Hz: p99 {np.median(v1):6.0f} | caída {np.median(cai):3.0f}% | "
                  f"brazo primero {sum(o[0] == 'b' for o in ords)}/{len(ords)} | p>t>b {sum(o == 'ptb' for o in ords)} | "
                  f"adelanto {np.median(dts) if dts else float('nan'):5.0f}")
    if args.salida:
        Path(args.salida).write_text(json.dumps({"version_motor": version_motor, "clips": filas},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nEscrito: {args.salida}")
    return 0


# --- serie-articulacion / salto-articulacion --------------------------------------------

def _art(nombre: str):
    return A[nombre.upper()]


def cmd_serie_articulacion(args) -> int:
    seq, fila = cargar(args.clip)
    lado = args.lado or fila.get("lado_dominante") or "der"
    filt = procesar_e3(seq)
    fs, fps, val = filt.secuencia, seq.fps_efectivos, filt.validacion
    art = _art(args.articulacion)
    saltos = {(s.frame_hasta, s.articulacion) for s in val.saltos_imposibles}
    bajos = set(val.puntos_baja_confianza)
    a, b = articulaciones_brazo(lado, "codo")

    def xyz(s, i, ar):
        p = s.frames[i].puntos_mundo.get(ar)
        return np.array([p.x, p.y, p.z]) if p is not None and p.z is not None else np.full(3, np.nan)

    print(f"{args.clip}  {args.articulacion}  fps={fps}  (ω = segmento {a.value}→{b.value}, °/s)")
    print(" frame   t(s) | crudo x       y       z    conf | filtrado x     y       z | ω crudo ω filtr | marcas")
    for i in range(args.desde, args.hasta + 1):
        c, f = xyz(seq, i, art), xyz(fs, i, art)
        p = seq.frames[i].puntos_mundo.get(art)

        def w(s):
            u0 = xyz(s, i - 1, b) - xyz(s, i - 1, a)
            u1 = xyz(s, i, b) - xyz(s, i, a)
            cs = np.dot(u0, u1) / (np.linalg.norm(u0) * np.linalg.norm(u1))
            return np.degrees(np.arccos(np.clip(cs, -1, 1))) * fps

        marcas = ("SALTO " if (i, art) in saltos else "") + ("BAJA" if (i, art) in bajos else "")
        print(f"{i:5d} {i / fps:6.3f} | {c[0]:7.3f} {c[1]:7.3f} {c[2]:7.3f} {p.confianza if p else float('nan'):5.2f} | "
              f"{f[0]:7.3f} {f[1]:7.3f} {f[2]:7.3f} | {w(seq):7.0f} {w(fs):7.0f} | {marcas or '-'}")
    return 0


def cmd_salto_articulacion(args) -> int:
    seq, _ = cargar(args.clip)
    art = _art(args.articulacion)
    fps = seq.fps_efectivos
    torso = np.array([largo_torso(f, espacio="mundo") or np.nan for f in seq.frames])
    T = float(np.nanmedian(torso))
    P = np.array([[f.puntos_mundo[art].x, f.puntos_mundo[art].y, f.puntos_mundo[art].z]
                  if art in f.puntos_mundo and f.puntos_mundo[art].z is not None else [np.nan] * 3
                  for f in seq.frames])
    d = np.linalg.norm(np.diff(P, axis=0), axis=1)
    print(f"largo de torso (mediana) = {T:.3f} m; umbral de salto imposible (0,5 torsos) = "
          f"{0.5 * T * 100:.1f} cm/fotograma = {0.5 * T * fps:.0f} m/s")
    print(f"{args.articulacion}: mediana {np.nanmedian(d) * 100:.1f} cm/f, p95 {np.nanpercentile(d, 95) * 100:.1f}, "
          f"máx {np.nanmax(d) * 100:.1f} cm/f ({np.nanmax(d) / T:.2f} torsos)")
    print(f"fotogramas con > {args.limite_cm:g} cm/f: {int(np.nansum(d > args.limite_cm / 100))} de {int(np.sum(~np.isnan(d)))} válidos")
    if args.desde is not None:
        r = d[args.desde - 1: args.hasta]
        print(f"tramo {args.desde}-{args.hasta}: mediana {np.median(r) * 100:.1f} cm/f, máx {r.max() * 100:.1f} cm/f "
              f"({r.max() / T:.2f} torsos, {r.max() * fps:.0f} m/s)")
    return 0


# --- montaje / angulo-plano -------------------------------------------------------------

def cmd_montaje(args) -> int:
    import cv2

    seq, fila = cargar(args.clip)
    lado = args.lado or fila.get("lado_dominante") or "der"
    dom = "DER" if lado == "der" else "IZQ"
    from app.config import get_data_dir
    video = _buscar_video(get_data_dir(), args.clip)
    fps = seq.fps_efectivos
    tiempos = [float(x) for x in args.tiempos.split(",")]
    etiquetas = (args.etiquetas.split(",") if args.etiquetas else [""] * len(tiempos))
    cap = cv2.VideoCapture(str(video))
    tiles = []
    for t, et in zip(tiempos, etiquetas):
        fi = int(round(t * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, img = cap.read()
        if not ok:
            raise SystemExit(f"no se pudo leer el fotograma {fi}")
        h, w = img.shape[:2]
        p = seq.frames[fi].puntos

        def pt(a):
            return (int(p[a].x * w), int(p[a].y * h))

        cv2.line(img, pt(A[f"HOMBRO_{dom}"]), pt(A[f"CODO_{dom}"]), (0, 255, 0), 6)        # brazo
        cv2.line(img, pt(A[f"CODO_{dom}"]), pt(A[f"MUNECA_{dom}"]), (0, 200, 255), 4)      # antebrazo
        cv2.line(img, pt(A.HOMBRO_IZQ), pt(A.HOMBRO_DER), (255, 128, 0), 4)                # hombros
        cv2.line(img, pt(A.CADERA_IZQ), pt(A.CADERA_DER), (0, 0, 255), 4)                  # caderas
        cx = int(np.mean([pt(A.HOMBRO_IZQ)[0], pt(A.CADERA_DER)[0]]))
        x0 = int(np.clip(cx - 500, 0, max(0, w - 1000)))
        img = img[:, x0:x0 + 1000]
        cv2.rectangle(img, (0, 0), (1000, 90), (0, 0, 0), -1)
        cv2.putText(img, f"t={t:.3f}s f{fi} {et}", (15, 62), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        tiles.append(cv2.resize(img, None, fx=0.42, fy=0.42))
    cv2.imwrite(str(args.salida), np.hstack(tiles))
    print(f"Escrito: {args.salida}")
    return 0


def cmd_angulo_plano(args) -> int:
    seq, _ = cargar(args.clip)
    s = procesar_e3(seq).secuencia
    fps = s.fps_efectivos

    def theta(o, e):
        t = np.full(s.n_frames, np.nan)
        for i, f in enumerate(s.frames):
            p = f.puntos_mundo
            if o in p and e in p and p[e].z is not None:
                t[i] = np.arctan2(p[e].z - p[o].z, p[e].x - p[o].x)
        return np.degrees(np.unwrap(t))

    tp, tt = theta(A.CADERA_IZQ, A.CADERA_DER), theta(A.HOMBRO_IZQ, A.HOMBRO_DER)
    wp = np.abs(np.diff(tp)) * fps
    i = int(np.nanargmax(wp))
    print(f"{args.clip}: pico de pelvis {wp[i]:.0f} °/s en el fotograma {i}; recorrido de la pelvis "
          f"{np.nanmax(tp) - np.nanmin(tp):.0f}°, del torso {np.nanmax(tt) - np.nanmin(tt):.0f}°")
    print(" frame  ang_pelvis ang_torso (plano x-z, grados)")
    for j in range(max(0, i - 24), min(s.n_frames, i + 25), args.paso):
        print(f" {j:5d} {tp[j]:10.1f} {tt[j]:9.1f}")
    return 0


# --- CLI -------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Diagnósticos de E3/E4 (solo lectura).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sin-filtrar", help="series con NaN (sin filtrar en E3 < 0.4.1)")
    p.add_argument("--clip", action="append", default=None)
    p.add_argument("--salida", default=None)
    p.set_defaults(fn=cmd_sin_filtrar)

    p = sub.add_parser("comparar-brazo", help="codo vs muñeca en los estados A/B/C")
    p.add_argument("--clip", action="append", default=None, help="default: todo el corpus público con lado dominante")
    p.add_argument("--salida", default=None)
    p.set_defaults(fn=cmd_comparar_brazo)

    p = sub.add_parser("corte-brazo", help="¿un corte por clip sirve para el brazo?")
    p.add_argument("--grupo", action="append", default=None)
    p.add_argument("--salida", default=None)
    p.set_defaults(fn=cmd_corte_brazo)

    p = sub.add_parser("serie-articulacion", help="serie fotograma a fotograma")
    p.add_argument("clip"); p.add_argument("articulacion"); p.add_argument("desde", type=int); p.add_argument("hasta", type=int)
    p.add_argument("--lado", choices=["der", "izq"], default=None)
    p.set_defaults(fn=cmd_serie_articulacion)

    p = sub.add_parser("salto-articulacion", help="desplazamiento por fotograma")
    p.add_argument("clip"); p.add_argument("articulacion")
    p.add_argument("--desde", type=int, default=None); p.add_argument("--hasta", type=int, default=None)
    p.add_argument("--limite-cm", type=float, default=4.0)
    p.set_defaults(fn=cmd_salto_articulacion)

    p = sub.add_parser("montaje", help="fotogramas con el esqueleto dibujado")
    p.add_argument("clip"); p.add_argument("tiempos", help="segundos separados por coma")
    p.add_argument("salida", type=Path)
    p.add_argument("--etiquetas", default=None); p.add_argument("--lado", choices=["der", "izq"], default=None)
    p.set_defaults(fn=cmd_montaje)

    p = sub.add_parser("angulo-plano", help="ángulo de pelvis y torso en el plano x-z")
    p.add_argument("clip"); p.add_argument("--paso", type=int, default=4)
    p.set_defaults(fn=cmd_angulo_plano)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
