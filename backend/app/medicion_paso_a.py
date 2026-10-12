"""Paso A del recálculo con la tasa real (plan de recálculo, §2 y §3; decisiones 030, 031 y 032).

Reusa la caché de pose del corpus HORNEADO (no re-extrae nada) y le pone el tiempo real de ese muestreo:
**120,2 fps uniformes** (la meseta; decisión 030) en lugar de los 240 que se asumieron. Corrige las velocidades (÷ 2),
los milisegundos (× 2), el corte de Winter, la ventana de ± 300 ms (que en realidad abarcaba ± 600 ms) y la
tolerancia: ahora en MILISEGUNDOS y con la MISMA constante que usa el producto (``engine/tolerancia_orden.py``).

Pre-registro (plan §3, aprobado el 9/10, no se ajusta a lo que dé):
  * umbral del Criterio 1: 0,8 (1a y 1b por grupo), mismos grupos y mismo método que la medición original (decisión 014);
  * tolerancia de "ordenable": primaria 1/120 s (8,3 ms), sensibilidad 4,2 / 12,5 / 16,7 ms; estricta (Δ > tolerancia);
  * se excluyen y se informan las repeticiones que empiezan en la rampa de velocidad (``corpus-real-alineacion.json``);
  * el resultado se informa igual si empeora, lado a lado con la medición original.

Además (pedido de Valentín el 12/10: "el Paso A tiene que ayudar a distinguir un artefacto de medición"), tres **controles
exploratorios** sobre las mismas poses, sin cambiar la medición: (1) la distribución de Δ = t_torso − t_pelvis en ms;
(2) la correlación y el desfase entre ω de la cadera y ω del tronco (¿la cadera es una señal propia o sigue al tronco?);
(3) sensibilidad del orden al corte del filtro y a la DEFINICIÓN de la velocidad (velocidad angular total del vector, que es
lo que mide el motor, contra el giro axial alrededor de la vertical, que es lo que se entiende por "rotación de la pelvis").

Como la medición original, se niega a correr con el árbol de git sucio: cada resultado queda atado a un commit.

Uso (desde backend/):
    python -m app.medicion_paso_a --sesion 2 --salida ../docs/resultados/paso-a-sesion-2.json
    python -m app.medicion_paso_a --sesion 1 --etiqueta replica-exploratoria --salida ../docs/resultados/paso-a-sesion-1.json
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from app.engine.kinematics import velocidad_angular_segmento
from app.engine.pipeline import procesar_e3
from app.engine.segmentos_corporales import SegmentoCadena as S
from app.engine.sequencing import MARGEN_ANCLA_S, secuenciar
from app.engine.tolerancia_orden import TOLERANCIA_ORDEN_S, TOLERANCIAS_SENSIBILIDAD_S, es_ordenable
from app.engine.version import __version__ as version_motor
from app.medicion_criterio1 import UMBRAL, parse_toma, resumir

FPS_MUESTREO_REAL = 120.2          # decisión 030: la meseta del corpus horneado, en tiempo real
CORTES_FIJOS_HZ = (4.0, 6.0, 8.0, 10.0, 12.0)   # control de sensibilidad al filtro
_LETRA = {S.PELVIS: "p", S.TORSO: "t", S.BRAZO: "b"}
ESPERADO_PAR, ESPERADO_CADENA = "pt", "ptb"


# --- funciones puras (probadas en tests/unit/test_medicion_paso_a.py) ---------------------------------------


def clasificar_ms(instantes: dict[str, float | None], valida: bool, letras: str, tolerancia_s: float) -> dict:
    """Clasifica una repetición con la tolerancia en SEGUNDOS: ordenable si cada par consecutivo del orden observado difiere
    en más que ``tolerancia_s`` (estricto, ``es_ordenable``). Misma forma de salida que ``medicion_criterio1.clasificar``."""
    if not valida or any(instantes.get(l) is None for l in letras):
        return {"valida": valida, "orden": None, "separacion_min": None, "ordenable": False}
    ordenados = sorted(letras, key=lambda l: (instantes[l], letras.index(l)))
    huecos = [instantes[b] - instantes[a] for a, b in zip(ordenados, ordenados[1:])]
    return {
        "valida": valida,
        "orden": "".join(ordenados),
        "separacion_min": min(huecos) * 1000.0,        # ms
        "ordenable": bool(all(es_ordenable(h, tolerancia_s) for h in huecos)),
    }


def delta_torso_menos_pelvis_ms(instantes: dict[str, float | None]) -> float | None:
    """Δ = t_torso − t_pelvis en ms; positivo = la cadera llegó primero (el orden esperado). ``None`` si falta un pico."""
    p, t = instantes.get("p"), instantes.get("t")
    if p is None or t is None:
        return None
    return (t - p) * 1000.0


def resumen_deltas(deltas_ms: list[float], tolerancia_s: float = TOLERANCIA_ORDEN_S) -> dict:
    """Distribución de Δ de un grupo: mediana, cuartiles, y qué fracción cae del lado de cada orden o dentro de la tolerancia."""
    if not deltas_ms:
        return {"n": 0}
    d = np.asarray(deltas_ms, dtype=float)
    tol_ms = tolerancia_s * 1000.0
    q1, med, q3 = (float(x) for x in np.percentile(d, [25, 50, 75]))
    return {
        "n": int(d.size), "mediana_ms": med, "q1_ms": q1, "q3_ms": q3,
        "media_ms": float(d.mean()), "min_ms": float(d.min()), "max_ms": float(d.max()),
        "cadera_primero": int(np.sum(d > tol_ms)), "tronco_primero": int(np.sum(d < -tol_ms)),
        "dentro_de_la_tolerancia": int(np.sum(np.abs(d) <= tol_ms + 1e-9)),
    }


def omega_giro_axial(
    puntos_izq: np.ndarray, puntos_der: np.ndarray, fps: float
) -> np.ndarray:
    """|ω| (°/s) del GIRO AXIAL (alrededor de la vertical) de la línea izquierda → derecha.

    ``puntos_izq`` y ``puntos_der``: arrays (n, 3) en coordenadas métricas de MediaPipe (x lateral, y vertical, z profundidad;
    NaN donde falta). Se proyecta la línea sobre el plano horizontal (x, z) y se deriva el ángulo desenrollado: es la rotación
    de la pelvis o de los hombros "como en la biomecánica", sin contar la inclinación lateral ni la flexión, que sí suman a la
    velocidad angular total del vector que usa el motor.
    """
    d = np.asarray(puntos_der, dtype=float) - np.asarray(puntos_izq, dtype=float)
    n = d.shape[0]
    yaw = np.arctan2(d[:, 2], d[:, 0])
    validos = ~np.isnan(yaw)
    salida = np.full(n, np.nan)
    if validos.sum() < 3:
        return salida
    ang = np.full(n, np.nan)
    ang[validos] = np.unwrap(yaw[validos])
    salida[:] = np.abs(np.degrees(np.gradient(ang)) * fps)
    return salida


def pico_en_ventana(omega: np.ndarray, desde: int, hasta: int, fps: float, min_validos: float = 0.9) -> float | None:
    """Instante (s, desde el inicio del clip) del máximo de ``omega`` en [desde, hasta]; ``None`` si hay menos de ``min_validos``
    de fotogramas válidos en la ventana. Sin prominencia ni techos: es un control, no la medición."""
    w = np.asarray(omega[desde : hasta + 1], dtype=float)
    if w.size == 0 or np.mean(~np.isnan(w)) < min_validos:
        return None
    return float((desde + int(np.nanargmax(w))) / fps)


def correlacion_y_desfase(omega_a: np.ndarray, omega_b: np.ndarray, fps: float, max_lag_s: float = 0.2) -> dict:
    """Correlación de Pearson (sin retraso) y desfase de máxima correlación entre dos series de ω.

    ``desfase_ms`` > 0: la serie B va DETRÁS de A (B(t + lag) ~ A(t)). Con la cadera como A y el tronco como B, un desfase
    positivo es "la cadera se adelanta". Los NaN se reemplazan por la media para no romper la correlación cruzada.
    """
    a = np.asarray(omega_a, dtype=float)
    b = np.asarray(omega_b, dtype=float)
    n = min(a.size, b.size)
    a, b = a[:n], b[:n]
    if n < 8 or np.all(np.isnan(a)) or np.all(np.isnan(b)):
        return {"correlacion": None, "desfase_ms": None, "correlacion_en_el_desfase": None}
    a = np.where(np.isnan(a), np.nanmean(a), a)
    b = np.where(np.isnan(b), np.nanmean(b), b)
    if np.std(a) == 0 or np.std(b) == 0:
        return {"correlacion": None, "desfase_ms": None, "correlacion_en_el_desfase": None}
    az, bz = (a - a.mean()) / a.std(), (b - b.mean()) / b.std()
    r0 = float(np.mean(az * bz))
    max_lag = int(round(max_lag_s * fps))
    mejor_lag, mejor_r = 0, r0
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            x, y = az[: n - lag], bz[lag:]
        else:
            x, y = az[-lag:], bz[: n + lag]
        if x.size < 8:
            continue
        r = float(np.mean(x * y))
        if r > mejor_r:
            mejor_lag, mejor_r = lag, r
    return {"correlacion": r0, "desfase_ms": mejor_lag / fps * 1000.0, "correlacion_en_el_desfase": mejor_r}


# --- medición -----------------------------------------------------------------------------------------------


def _git(args: list[str], repo: Path) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def _picos(seq, lado: str, corte_hz: float | None = None):
    """Instantes (s, relativos al inicio del clip) de los picos p, t, b + ventana + la serie filtrada; ``None`` si E3 falla."""
    try:
        filt = procesar_e3(seq, corte_hz=corte_hz)
    except ValueError as e:
        return None, f"E3: {e}"
    resultados, _ = secuenciar(
        filt.secuencia, lado_dominante=lado, tramos_excluidos=filt.tramos_excluidos, brazo_via="codo", ancla="torso",
        margen_ancla_s=MARGEN_ANCLA_S,
    )
    rep = resultados[0]
    fps = filt.secuencia.fps_efectivos
    instantes = {}
    for seg in (S.PELVIS, S.TORSO, S.BRAZO):
        p = rep.picos.get(seg)
        instantes[_LETRA[seg]] = (p.frame / fps) if p is not None and p.auditable else None
    return {"instantes": instantes, "rep": rep, "filt": filt, "fps": fps, "valida": instantes["t"] is not None,
            "motivo": rep.motivo_no_auditable}, None


def medir_clip_paso_a(seq, lado: str) -> dict:
    """Paso A: la secuencia horneada con el tiempo real del muestreo (120,2 fps uniformes)."""
    return medir_secuencia(dataclasses.replace(seq, fps_efectivos=FPS_MUESTREO_REAL), lado)


def medir_secuencia(seq_t, lado: str) -> dict:
    """Medición principal (3D métrico, Winter automático, ventana anclada al torso) más los controles, con la tasa de ``seq_t``.

    Sirve para el Paso A (poses del horneado con 120,2 fps) y para el Paso B (poses de los originales regularizadas a la grilla
    de 240 Hz): ``seq_t.fps_efectivos`` es la tasa de la grilla uniforme en cada caso."""
    fps = seq_t.fps_efectivos
    base, error = _picos(seq_t, lado)
    if base is None:
        return {
            "valida": False, "motivo": error, "instantes_s": {"p": None, "t": None, "b": None},
            "delta_torso_menos_pelvis_ms": None,
            "omega_cadera_vs_tronco": {"correlacion": None, "desfase_ms": None, "correlacion_en_el_desfase": None},
            "por_corte_fijo_hz": {}, "giro_axial": {"instantes_s": {"p": None, "t": None, "b": None}, "valida": False},
        }
    fila: dict = {
        "valida": base["valida"], "motivo": base["motivo"],
        "instantes_s": base["instantes"], "corte_hz": round(float(base["filt"].corte_hz), 2),
        "delta_torso_menos_pelvis_ms": delta_torso_menos_pelvis_ms(base["instantes"]),
    }
    # Control 2: ¿la cadera es una señal propia o acompaña al tronco?
    v = base["rep"].ventana
    sec = base["filt"].secuencia
    om_p = velocidad_angular_segmento(sec, S.PELVIS, lado)[v.desde_frame : v.hasta_frame + 1]
    om_t = velocidad_angular_segmento(sec, S.TORSO, lado)[v.desde_frame : v.hasta_frame + 1]
    fila["omega_cadera_vs_tronco"] = correlacion_y_desfase(om_p, om_t, fps)
    # Control 3a: sensibilidad al corte del filtro (el orden no debería depender de un corte fijo razonable).
    por_corte = {}
    for c in CORTES_FIJOS_HZ:
        r, _ = _picos(seq_t, lado, corte_hz=c)
        por_corte[str(c)] = None if r is None else {"instantes_s": r["instantes"], "valida": r["valida"]}
    fila["por_corte_fijo_hz"] = por_corte
    # Control 3b: giro AXIAL (alrededor de la vertical) en lugar de la velocidad angular total del vector. El motor mide la
    # velocidad angular total de la línea de caderas y de la de hombros; en la biomecánica la pelvis y el tronco "rotan" alrededor
    # de la vertical, y la inclinación y la flexión del tronco suman a la del hombro y no a la de la cadera.
    def serie(art):
        return np.array([
            [p.x, p.y, np.nan if p.z is None else p.z] if (p := f.puntos_mundo.get(art)) is not None else [np.nan] * 3
            for f in sec.frames
        ], dtype=float)

    from app.engine.pose.articulaciones import ArticulacionCanonica as A

    w_p = omega_giro_axial(serie(A.CADERA_IZQ), serie(A.CADERA_DER), fps)
    w_t = omega_giro_axial(serie(A.HOMBRO_IZQ), serie(A.HOMBRO_DER), fps)
    t_p = pico_en_ventana(w_p, v.desde_frame, v.hasta_frame, fps)
    t_t = pico_en_ventana(w_t, v.desde_frame, v.hasta_frame, fps)
    fila["giro_axial"] = {"instantes_s": {"p": t_p, "t": t_t, "b": None}, "valida": t_p is not None and t_t is not None}
    return fila


def _clasificar_grupo(filas: list[dict], letras: str, esperado: str, tolerancia_s: float) -> dict:
    return resumir([clasificar_ms(f["instantes_s"], f["valida"], letras, tolerancia_s) for f in filas], esperado)


def _resumen_control(filas: list[dict], extractor, tolerancia_s: float) -> dict:
    """Para un control (corte fijo o 2D): cuántas repeticiones son ordenables, el orden modal y la fracción cadera-primero."""
    clas, deltas = [], []
    for f in filas:
        x = extractor(f)
        if x is None:
            clas.append({"valida": False, "orden": None, "separacion_min": None, "ordenable": False})
            continue
        clas.append(clasificar_ms(x["instantes_s"], x["valida"], "pt", tolerancia_s))
        d = delta_torso_menos_pelvis_ms(x["instantes_s"])
        if x["valida"] and d is not None:
            deltas.append(d)
    r = resumir(clas, ESPERADO_PAR)
    return {"n": r["n"], "ordenables": r["ordenables"], "orden_modal": r["1b_orden_modal"], "1b": r["1b_repetibilidad"],
            "1c_cadera_primero": r["1c_coincidencia"], "delta_mediana_ms": (statistics.median(deltas) if deltas else None)}


def construir_resultado(filas: list[dict]) -> dict:
    """Agrega las repeticiones medidas: Criterio 1 por tolerancia, distribución de Δ y controles, por grupo y toma."""
    grupos: dict[str, list[dict]] = defaultdict(list)
    for f in filas:
        grupos[f"{f['gesto']}|{f['encuadre']}"].append(f)
        if f["gesto"] == "saque" and f["encuadre"] == "trescuartos":
            grupos[f"saque|trescuartos|toma {f['toma']}"].append(f)

    tolerancias = {"primaria": TOLERANCIA_ORDEN_S, **{f"sens_{round(t * 1000, 1)}ms": t for t in TOLERANCIAS_SENSIBILIDAD_S}}
    resultado: dict = {}
    for nombre, tol in tolerancias.items():
        resultado[nombre] = {"tolerancia_ms": tol * 1000.0, "grupos": {}}
        for g, L in sorted(grupos.items()):
            entrada = {"par_pelvis_torso": _clasificar_grupo(L, "pt", ESPERADO_PAR, tol)}
            if g.split("|")[1] == "trescuartos":
                entrada["cadena"] = _clasificar_grupo(L, "ptb", ESPERADO_CADENA, tol)
            resultado[nombre]["grupos"][g] = entrada

    deltas = {g: resumen_deltas([f["delta_torso_menos_pelvis_ms"] for f in L if f["valida"] and f["delta_torso_menos_pelvis_ms"] is not None])
              for g, L in sorted(grupos.items())}
    controles = {
        g: {
            "acople_omega": {
                "correlacion_mediana": statistics.median([f["omega_cadera_vs_tronco"]["correlacion"] for f in L
                                                         if f["omega_cadera_vs_tronco"]["correlacion"] is not None] or [float("nan")]),
                "desfase_mediano_ms": statistics.median([f["omega_cadera_vs_tronco"]["desfase_ms"] for f in L
                                                         if f["omega_cadera_vs_tronco"]["desfase_ms"] is not None] or [float("nan")]),
            },
            "por_corte_fijo_hz": {c: _resumen_control(L, lambda f, c=c: f["por_corte_fijo_hz"].get(c), TOLERANCIA_ORDEN_S)
                                  for c in map(str, CORTES_FIJOS_HZ)},
            "giro_axial": _resumen_control(L, lambda f: f["giro_axial"], TOLERANCIA_ORDEN_S),
            "winter_3d": _resumen_control(L, lambda f: {"instantes_s": f["instantes_s"], "valida": f["valida"]}, TOLERANCIA_ORDEN_S),
        }
        for g, L in sorted(grupos.items())
    }
    return {"resultado_por_tolerancia": resultado, "delta_torso_menos_pelvis_ms": deltas, "controles": controles}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Paso A del recálculo con la tasa real (plan de recálculo §2).")
    ap.add_argument("--sesion", type=int, required=True, help="1 (réplica exploratoria) o 2 (medición)")
    ap.add_argument("--etiqueta", default="")
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--permitir-sucio", action="store_true", help="NO usar para la medición formal")
    args = ap.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir
    from app.diagnosticos_e3 import _buscar_video, _catalogo, en_sesion, fechas_propias
    from app.engine.pose import cache as pose_cache
    from app.engine.pose.mediapipe_backend import MediaPipeBackend

    repo = Path(__file__).resolve().parents[2]
    sucio = _git(["status", "--porcelain", "--", "backend/app", "tests", "docs/decisiones"], repo)
    if sucio and not args.permitir_sucio:
        print("El árbol de git tiene cambios sin commitear en backend/app, tests o docs/decisiones:\n" + sucio +
              "\nCommitear antes de medir (congelamiento, decisión 014).")
        return 2

    # Repeticiones que empiezan en la rampa: se excluyen y se informan (plan §2, "qué no corrige").
    alineacion = json.loads((repo / "docs" / "resultados" / "corpus-real-alineacion.json").read_text(encoding="utf-8"))
    en_rampa = {r["repeticion"] for r in alineacion["repeticiones"] if not r["entera_en_la_meseta"]}

    base = get_data_dir()
    cat = _catalogo(base)
    fechas = fechas_propias(cat)
    b = MediaPipeBackend()
    clips = [(n, r) for n, r in sorted(cat.items())
             if r.get("fuente") == "propio" and "_rep" in n and r.get("angulo") in ("perfil", "trescuartos")
             and str(r.get("fps_efectivos")).strip() in ("240", "240.0") and en_sesion(n, args.sesion, fechas)]
    excluidas = [n for n, _ in clips if n in en_rampa]
    clips = [(n, r) for n, r in clips if n not in en_rampa]
    print(f"Sesión {args.sesion}: {len(clips)} repeticiones a {FPS_MUESTREO_REAL} fps reales; excluidas por rampa: {excluidas}")

    filas = []
    for n, r in clips:
        seq = pose_cache.cargar_si_vigente(get_cache_dir(), _buscar_video(base, n), b.id, b.config_hash)
        if seq is None:
            raise SystemExit(f"sin pose cacheada para {n}")
        m = medir_clip_paso_a(seq, r["lado_dominante"])
        filas.append({"clip": n, "gesto": r["gesto"], "encuadre": r["angulo"], "toma": parse_toma(n), **m})
    print(f"Medidas: {len(filas)}")

    agregado = construir_resultado(filas)

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps({
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "decision": "032 / plan de recálculo §2 (Paso A)", "sesion": args.sesion,
        "rol": "MEDICIÓN (conjunto de medición)" if args.sesion == 2 else "RÉPLICA EXPLORATORIA (no independiente)",
        "etiqueta": args.etiqueta, "version_motor": version_motor, "commit": _git(["rev-parse", "HEAD"], repo),
        "arbol_sucio": bool(sucio), "fps_muestreo_real": FPS_MUESTREO_REAL, "umbral": UMBRAL,
        "tolerancia_primaria_ms": TOLERANCIA_ORDEN_S * 1000.0, "margen_ancla_s": MARGEN_ANCLA_S, "brazo_via": "codo",
        "excluidas_por_rampa": excluidas, "repeticiones": filas, **agregado,
    }, ensure_ascii=False, indent=1, default=list), encoding="utf-8")
    print(f"Escrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
