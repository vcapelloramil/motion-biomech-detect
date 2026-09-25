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
  fleisig-brazo       Compara, en el saque, dos magnitudes DISTINTAS del brazo contra los valores de
                      Fleisig (2003): ω del vector hombro→codo (orientación del brazo en el
                      espacio; lo que mide el motor) y ω del ÁNGULO del codo (tres puntos:
                      extensión de codo, comparable con los 1510 °/s). Ninguna mide la rotación
                      interna del hombro (2368 °/s), que es axial.
  ventana-brazo       Barrido de cuánto se permite buscar el pico del BRAZO ANTES del pico del
                      torso (adelanto 300…0 ms; después siempre +300 ms). Mide cuántos picos se
                      desplazan al acotar (lo que la ventana enmascara). Con adelanto 0 "brazo
                      antes que torso" es imposible por construcción: no usarlo para refutar.
  oclusion-lado       Confianza y cobertura de hombro/codo/muñeca del lado DOMINANTE contra el no
                      dominante, por encuadre y por sesión, en tres tramos (clip completo, ventana
                      del gesto y reposo). Si el dominante es peor también en REPOSO, apunta a
                      oclusión por la posición de la cámara; si solo lo es durante el gesto,
                      apunta a desenfoque por velocidad. Solo lee la caché de pose.
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
from app.engine.kinematics import _xyz, serie_angulo_articular, velocidad_angular_segmento
from app.engine.sequencing import (
    _frames_excluidos_por_segmento,
    detectar_pico,
    instante_ancla,
    secuenciar,
    techo_velocidad,
    ventana_anclada,
)
from scipy.stats import binomtest

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


# --- fleisig-brazo --------------------------------------------------------------------

# Fleisig et al. (2003), tabla del apartado 3.3.2.8 de la tesis, en °/s.
FLEISIG = {"codo (extension)": 1510.0, "muneca (flexion)": 1950.0, "hombro (rotacion interna)": 2368.0}


def omega_angulo(theta: np.ndarray, fps: float, k: int = 1) -> np.ndarray:
    """|Δθ| · fps / k (°/s) de una serie de ángulos (grados), alineada a i+k."""
    w = np.full(len(theta), np.nan)
    w[k:] = np.abs(theta[k:] - theta[:-k]) * fps / k
    return w


def maximo_en(w: np.ndarray, desde: int, hasta: int) -> float | None:
    v = w[desde:hasta + 1]
    v = v[np.isfinite(v)]
    return float(v.max()) if v.size else None


def cmd_fleisig_brazo(args) -> int:
    from app.config import get_data_dir

    cat = _catalogo(get_data_dir())
    grupos = args.grupo or ["saque_perfil", "saque_trescuartos"]
    filas = {}
    for nombre, r in cat.items():
        g = f"{r.get('gesto')}_{r.get('angulo')}"
        if r.get("fuente") != "propio" or "_rep" not in nombre or g not in grupos:
            continue
        seq, _ = cargar(nombre)
        lado = r["lado_dominante"]
        try:
            filt = procesar_e3(seq)
        except ValueError:
            continue
        sf, fps = filt.secuencia, seq.fps_efectivos
        w_vec = velocidad_angular_segmento(sf, S.BRAZO, lado, brazo_via="codo")
        th = serie_angulo_articular(sf, "codo", lado)
        w_ang, w_ang4 = omega_angulo(th, fps, 1), omega_angulo(th, fps, 4)
        u = vector_unitario(  # ω del vector a k=4, para ver si el pico es ruido
            {(a_, c): np.array([getattr(f.puntos_mundo[a_], c) if a_ in f.puntos_mundo else np.nan
                                for f in sf.frames]) for a_ in articulaciones_brazo(lado, "codo") for c in "xyz"},
            *articulaciones_brazo(lado, "codo"))
        w_vec4 = omega_k(u, fps, 4)
        v, motivo = ventana_anclada(sf, lado, "torso", tramos_excluidos=filt.tramos_excluidos)
        d, h = (v.desde_frame, v.hasta_frame) if v is not None else (0, len(w_vec) - 1)
        filas[nombre] = {
            "grupo": g, "ventana_anclada": v is not None,
            "vector_hombro_codo": {"pico_ventana_k1": maximo_en(w_vec, d, h), "pico_ventana_k4": maximo_en(w_vec4, d, h),
                                   "p99_clip": p99(w_vec)},
            "angulo_codo": {"pico_ventana_k1": maximo_en(w_ang, d, h), "pico_ventana_k4": maximo_en(w_ang4, d, h),
                            "p99_clip": p99(w_ang),
                            "cobertura": round(float(np.isfinite(th).mean()), 3)},
        }
        f_ = filas[nombre]
        print(f"{nombre[-22:]:22} {g:18} vector: pico {f_['vector_hombro_codo']['pico_ventana_k1']} (k4 {f_['vector_hombro_codo']['pico_ventana_k4']}) | "
              f"ángulo codo: pico {f_['angulo_codo']['pico_ventana_k1']} (k4 {f_['angulo_codo']['pico_ventana_k4']}) cob {f_['angulo_codo']['cobertura']}")
    print("\nMedianas por grupo (pico en la ventana anclada al torso, °/s) y cociente contra cada valor de Fleisig")
    por = defaultdict(list)
    for f in filas.values():
        por[f["grupo"]].append(f)
    resumen = {}
    for g, L in por.items():
        med = lambda tipo, k: np.median([f[tipo][k] for f in L if f[tipo][k] is not None])
        v1, v4 = med("vector_hombro_codo", "pico_ventana_k1"), med("vector_hombro_codo", "pico_ventana_k4")
        a1, a4 = med("angulo_codo", "pico_ventana_k1"), med("angulo_codo", "pico_ventana_k4")
        resumen[g] = {"vector_k1": v1, "vector_k4": v4, "angulo_codo_k1": a1, "angulo_codo_k4": a4}
        print(f"\n{g} ({len(L)} clips)")
        print(f"  ω del VECTOR hombro→codo:  k1 {v1:6.0f}  k4 {v4:6.0f}   = {v1 / FLEISIG['hombro (rotacion interna)']:.2f}× (2368 hombro)  "
              f"{v1 / FLEISIG['codo (extension)']:.2f}× (1510 codo)")
        print(f"  ω del ÁNGULO del codo:     k1 {a1:6.0f}  k4 {a4:6.0f}   = {a1 / FLEISIG['codo (extension)']:.2f}× (1510 codo, comparable)")
    if args.salida:
        Path(args.salida).write_text(json.dumps({"version_motor": version_motor, "fleisig": FLEISIG,
                                                 "resumen": resumen, "clips": filas},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nEscrito: {args.salida}")
    return 0


# --- ventana-brazo --------------------------------------------------------------------

ADELANTOS_MS = (300, 200, 150, 100, 50, 0)
POST_MS = 300


def pico_brazo_en_ventana(omega: np.ndarray, frame_torso: int, *, adelanto_ms: float, post_ms: float,
                          fps: float, excluidos: set, techo: float):
    """Pico del brazo dentro de [torso − adelanto, torso + post]; (frame, °/s) o (None, motivo)."""
    d = max(0, frame_torso - int(round(adelanto_ms * fps / 1000)))
    h = min(len(omega) - 1, frame_torso + int(round(post_ms * fps / 1000)))
    return detectar_pico(omega[d:h + 1], fps=fps, offset_frame=d, frames_excluidos=excluidos, techo=techo)


def cmd_ventana_brazo(args) -> int:
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
        try:
            filt = procesar_e3(seq)
        except ValueError:
            continue
        sf, fps = filt.secuencia, seq.fps_efectivos
        ft, _ = instante_ancla(sf, lado, "torso", tramos_excluidos=filt.tramos_excluidos)
        if ft is None:
            filas[nombre] = {"grupo": g, "sin_ancla": True}
            continue
        omega = velocidad_angular_segmento(sf, S.BRAZO, lado, brazo_via="codo")
        excl = _frames_excluidos_por_segmento(filt.tramos_excluidos, S.BRAZO, lado, "codo")
        techo = techo_velocidad(S.BRAZO)
        base = None
        por_adelanto = {}
        for a in ADELANTOS_MS:
            fr, info = pico_brazo_en_ventana(omega, ft, adelanto_ms=a, post_ms=POST_MS, fps=fps,
                                             excluidos=excl, techo=techo)
            if a == ADELANTOS_MS[0]:
                base = fr
            por_adelanto[str(a)] = {
                "dt_torso_a_brazo_ms": None if fr is None else round((fr - ft) / fps * 1000, 1),
                "vel": None if fr is None else round(float(info), 1),
                "desplazado_vs_300": None if (fr is None or base is None) else bool(fr != base),
            }
        filas[nombre] = {"grupo": g, "frame_torso": int(ft), "por_adelanto": por_adelanto}
    por_grupo = defaultdict(list)
    for f in filas.values():
        if "sin_ancla" not in f:
            por_grupo[f["grupo"]].append(f)
    print("Barrido del adelanto de la ventana del brazo (post = +300 ms). Por grupo y adelanto:")
    print("  aud = brazo auditable | antes = pico del brazo ANTES que el del torso | desplaz. = el pico cambia respecto de ±300 | dt = mediana (ms, − = antes)")
    for g, L in por_grupo.items():
        print(f"\n{g} ({len(L)} clips)")
        for a in ADELANTOS_MS:
            k = str(a)
            d = [f["por_adelanto"][k] for f in L]
            aud = [x for x in d if x["dt_torso_a_brazo_ms"] is not None]
            dts = [x["dt_torso_a_brazo_ms"] for x in aud]
            print(f"  adelanto {a:3d} ms: aud {len(aud)}/{len(L)} | antes {sum(t < 0 for t in dts)}/{len(aud)} | "
                  f"desplaz. {sum(bool(x['desplazado_vs_300']) for x in aud)}/{len(aud)} | "
                  f"dt {np.median(dts) if dts else float('nan'):6.0f}")
    if args.salida:
        Path(args.salida).write_text(json.dumps({"version_motor": version_motor, "post_ms": POST_MS,
                                                 "clips": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nEscrito: {args.salida}")
    return 0


# --- oclusion-lado ---------------------------------------------------------------------

UMBRAL_CONF = 0.5                 # el mismo de engine.validation.UMBRAL_CONFIANZA
JUEGO_ART = ("HOMBRO", "CODO", "MUNECA", "CADERA")   # la cadera: la otra articulación que la cámara podría tapar
VENTANA_GESTO_S = 0.3             # ± alrededor del pico crudo del torso
REPOSO_DESDE_S = 0.6              # reposo = a más de esto del pico
# Criterio de trabajo declarado ANTES de mirar los datos (juicio de Claude; ajustable):
# "posible oclusión sistemática del dominante" si, en un grupo, la cobertura del dominante es menor
# que la del no dominante por >= DELTA_COB en la mediana, en >= FRAC_NEG de los clips, con p < ALFA.
DELTA_COB, FRAC_NEG, ALFA = -0.10, 0.75, 0.05


def confianza_por_frame(seq, art) -> np.ndarray:
    """Confianza (visibility) de ``art`` por fotograma; NaN si el punto no está."""
    return np.array([f.puntos[art].confianza if art in f.puntos else np.nan for f in seq.frames])


def ancla_cruda(seq) -> int | None:
    """Fotograma del pico de ω del eje de hombros, SIN E3 (suavizado a 9 fotogramas)."""
    n = seq.n_frames
    u = np.full((n, 3), np.nan)
    for i, f in enumerate(seq.frames):
        p = f.puntos_mundo
        if A.HOMBRO_IZQ in p and A.HOMBRO_DER in p and p[A.HOMBRO_IZQ].z is not None and p[A.HOMBRO_DER].z is not None:
            d = _xyz(p[A.HOMBRO_DER]) - _xyz(p[A.HOMBRO_IZQ])
            nd = np.linalg.norm(d)
            if nd > 0:
                u[i] = d / nd
    w = np.nan_to_num(omega_k(u, seq.fps_efectivos, 1), nan=0.0)
    if not np.any(w > 0):
        return None
    return int(np.argmax(np.convolve(w, np.ones(9) / 9, mode="same")))


def mascaras_tramos(n: int, ancla: int | None, fps: float) -> dict:
    idx = np.arange(n)
    salida = {"clip": np.ones(n, dtype=bool)}
    if ancla is not None:
        salida["ventana"] = np.abs(idx - ancla) <= VENTANA_GESTO_S * fps
        salida["reposo"] = np.abs(idx - ancla) > REPOSO_DESDE_S * fps
    return salida


def metricas_mascara(conf: np.ndarray, mascara: np.ndarray) -> tuple[float | None, float | None]:
    """(confianza media entre los fotogramas donde el punto está, cobertura ≥ umbral sobre TODOS)."""
    c = conf[mascara]
    if c.size == 0:
        return None, None
    presentes = c[np.isfinite(c)]
    media = float(presentes.mean()) if presentes.size else None
    cobertura = float(np.mean(np.nan_to_num(c, nan=0.0) >= UMBRAL_CONF))
    return media, cobertura


def resumen_pareado(deltas: list[float]) -> dict:
    """Resumen de diferencias dominante − no dominante por clip: mediana, fracción negativa, signo."""
    d = np.array([x for x in deltas if x is not None and np.isfinite(x)])
    if d.size == 0:
        return {"n": 0}
    neg, pos = int((d < 0).sum()), int((d > 0).sum())
    p = float(binomtest(neg, neg + pos, 0.5).pvalue) if neg + pos > 0 else 1.0
    return {"n": int(d.size), "mediana": float(np.median(d)), "frac_neg": neg / d.size,
            "p_signo": p}


def sesion_de(nombre: str, fechas: list[str]) -> int:
    return fechas.index(nombre[:8]) + 1


def lado_cercano(seq, mascara: np.ndarray) -> str | None:
    """Lado del cuerpo más cercano a la cámara según la z relativa de los hombros (menor = más cerca)."""
    dz = []
    for i in np.flatnonzero(mascara):
        p = seq.frames[i].puntos
        if A.HOMBRO_DER in p and A.HOMBRO_IZQ in p and p[A.HOMBRO_DER].z is not None and p[A.HOMBRO_IZQ].z is not None:
            dz.append(p[A.HOMBRO_DER].z - p[A.HOMBRO_IZQ].z)
    if not dz:
        return None
    return "der" if np.median(dz) < 0 else "izq"


def cmd_oclusion_lado(args) -> int:
    from app.config import get_cache_dir, get_data_dir

    base = get_data_dir()
    cat = _catalogo(base)
    b = MediaPipeBackend()
    clips = [(n, r) for n, r in cat.items()
             if r.get("fuente") == "propio" and "_rep" in n and r.get("angulo") in ("perfil", "trescuartos")
             and str(r.get("fps_efectivos")).strip() in ("240", "240.0")]
    fechas = sorted({n[:8] for n, _ in clips})
    filas, sin_pose = [], defaultdict(int)
    for n, r in clips:
        video = _buscar_video(base, n)
        seq = pose_cache.cargar_si_vigente(get_cache_dir(), video, b.id, b.config_hash)
        ses = sesion_de(n, fechas)
        if seq is None:
            sin_pose[(ses, r["angulo"])] += 1
            continue
        lado_dom = r["lado_dominante"]
        no_dom = "izq" if lado_dom == "der" else "der"
        m = mascaras_tramos(seq.n_frames, ancla_cruda(seq), seq.fps_efectivos)
        fila = {"clip": n, "sesion": ses, "angulo": r["angulo"], "gesto": r["gesto"],
                "lado_cercano": lado_cercano(seq, m.get("ventana", m["clip"])), "tramos": {}}
        for tramo, mask in m.items():
            fila["tramos"][tramo] = {}
            for j in JUEGO_ART:
                d = metricas_mascara(confianza_por_frame(seq, A[f"{j}_{'DER' if lado_dom == 'der' else 'IZQ'}"]), mask)
                nd = metricas_mascara(confianza_por_frame(seq, A[f"{j}_{'DER' if no_dom == 'der' else 'IZQ'}"]), mask)
                fila["tramos"][tramo][j] = {"dom": d, "nodom": nd}
        filas.append(fila)

    grupos = defaultdict(list)
    for f in filas:
        grupos[(f["sesion"], f["angulo"])].append(f)
    salida = {}
    print(f"Criterio de trabajo (declarado antes de mirar): posible oclusión del dominante si, para una articulación,\n"
          f"  mediana de Δcobertura (dom − no dom) <= {DELTA_COB}, Δ<0 en >= {int(FRAC_NEG * 100)} % de los clips y p_signo < {ALFA}.\n")
    for tramo in ("reposo", "ventana", "clip"):
        print(f"=== tramo: {tramo} (Δ = dominante − no dominante; conf = confianza media, cob = fracción de fotogramas con conf ≥ {UMBRAL_CONF}) ===")
        print(f"{'ses':>3} {'encuadre':12} {'art':7} {'n':>3} | conf dom  no dom  Δ     | cob dom  no dom  Δmed    Δ<0   p     | flag")
        for (ses, ang), L in sorted(grupos.items()):
            for j in JUEGO_ART:
                pares = [f["tramos"][tramo][j] for f in L if tramo in f["tramos"]]
                cdom = [x["dom"][0] for x in pares if x["dom"][0] is not None and x["nodom"][0] is not None]
                cno = [x["nodom"][0] for x in pares if x["dom"][0] is not None and x["nodom"][0] is not None]
                kdom = [x["dom"][1] for x in pares if x["dom"][1] is not None]
                kno = [x["nodom"][1] for x in pares if x["nodom"][1] is not None]
                res = resumen_pareado([a_ - b_ for a_, b_ in zip(kdom, kno)])
                if not res["n"]:
                    continue
                flag = (res["mediana"] <= DELTA_COB and res["frac_neg"] >= FRAC_NEG and res["p_signo"] < ALFA)
                salida[f"{tramo}|s{ses}|{ang}|{j}"] = {
                    "n": res["n"], "conf_dom": float(np.median(cdom)), "conf_nodom": float(np.median(cno)),
                    "cob_dom": float(np.median(kdom)), "cob_nodom": float(np.median(kno)),
                    "delta_cob_mediana": res["mediana"], "frac_delta_neg": res["frac_neg"], "p_signo": res["p_signo"],
                    "posible_oclusion": bool(flag)}
                print(f"{ses:>3} {ang:12} {j.lower():7} {res['n']:3d} | {np.median(cdom):6.2f} {np.median(cno):7.2f} {np.median(cdom) - np.median(cno):+5.2f} | "
                      f"{np.median(kdom):6.2f} {np.median(kno):7.2f} {res['mediana']:+6.2f} {res['frac_neg']:5.0%} {res['p_signo']:6.3f} | {'POSIBLE OCLUSIÓN' if flag else '-'}")
        print()
    print("Lado del cuerpo más cercano a la cámara (z relativa de hombros, en la ventana), clips por (sesión, encuadre):")
    for (ses, ang), L in sorted(grupos.items()):
        c = defaultdict(int)
        for f in L:
            c[f["lado_cercano"]] += 1
        print(f"  sesión {ses} {ang:12}: {dict(c)}   (lado dominante = der)")
    if sin_pose:
        print("\nClips SIN pose cacheada (no incluidos):", dict(sin_pose))
    if args.salida:
        Path(args.salida).write_text(json.dumps({"version_motor": version_motor, "criterio": {
            "delta_cob": DELTA_COB, "frac_neg": FRAC_NEG, "alfa": ALFA}, "resumen": salida, "clips": filas},
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

    p = sub.add_parser("fleisig-brazo", help="ω del vector vs ω del ángulo del codo, contra Fleisig")
    p.add_argument("--grupo", action="append", default=None)
    p.add_argument("--salida", default=None)
    p.set_defaults(fn=cmd_fleisig_brazo)

    p = sub.add_parser("ventana-brazo", help="barrido del adelanto de la ventana del brazo")
    p.add_argument("--grupo", action="append", default=None)
    p.add_argument("--salida", default=None)
    p.set_defaults(fn=cmd_ventana_brazo)

    p = sub.add_parser("oclusion-lado", help="confianza/cobertura del lado dominante vs no dominante")
    p.add_argument("--salida", default=None)
    p.set_defaults(fn=cmd_oclusion_lado)

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
