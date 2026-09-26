"""Criterio 2 (plan, tarea 4.8): error angular contra goniometría manual CIEGA (decisión 014).

Dos subcomandos (desde backend/):

  preparar   Elige 18 fotogramas de la sesión 2 con una regla fija y una semilla, exporta los recortes SIN
             esqueleto con identificadores opacos, escribe la planilla CSV y el LEEME, y guarda la CLAVE
             (clip, fotograma y valor del sistema) FUERA del repositorio, en una carpeta que no hay que abrir
             hasta terminar de medir. No imprime ningún valor del sistema.
  analizar   Con la planilla ya completa, calcula el error por articulación (media, mediana, percentil 95,
             sesgo con signo), el error intra-observador si se repitieron fotogramas, y el veredicto (< 20,6°).

Regla de selección (decisión 014): por estrato (gesto × encuadre; del saque de tres cuartos solo la toma 02),
3 fotogramas, uno por repetición, sorteados con semilla entre los elegibles; candidatos a -300, -150 y 0 ms del
pico crudo del torso; elegible si en ese fotograma los tres puntos de la rodilla Y los tres del codo tienen
confianza >= 0,6 (para cada ángulo, se toma el lado con mayor confianza mínima).
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

from app.engine.pose.articulaciones import ArticulacionCanonica as A

SEMILLA = 26092026
OFFSETS_MS = (-300, -150, 0)
UMBRAL_CONF = 0.6
POR_ESTRATO = 3
META_ERROR_GRADOS = 20.6
GESTOS = ("saque", "drive", "reves")
ENCUADRES = ("perfil", "trescuartos")
TRIPLETES = {
    "rodilla": {"izq": (A.CADERA_IZQ, A.RODILLA_IZQ, A.TOBILLO_IZQ), "der": (A.CADERA_DER, A.RODILLA_DER, A.TOBILLO_DER)},
    "codo": {"izq": (A.HOMBRO_IZQ, A.CODO_IZQ, A.MUNECA_IZQ), "der": (A.HOMBRO_DER, A.CODO_DER, A.MUNECA_DER)},
}


# --- funciones puras (probadas en tests/unit/test_criterio2.py) --------------------------------

def angulo_en_vertice(a, v, c) -> float:
    """Ángulo interior (0–180°) en el vértice ``v`` entre los segmentos v→a y v→c (2D o 3D)."""
    u, w = np.asarray(a, float) - np.asarray(v, float), np.asarray(c, float) - np.asarray(v, float)
    nu, nw = np.linalg.norm(u), np.linalg.norm(w)
    if nu == 0 or nw == 0:
        return float("nan")
    return float(np.degrees(np.arccos(np.clip(np.dot(u, w) / (nu * nw), -1.0, 1.0))))


def mejor_lado(frame_puntos: dict, angulo: str) -> tuple[str, float] | None:
    """Lado ('izq'/'der') con mayor confianza mínima de los tres puntos del ángulo; None si falta un punto."""
    mejor = None
    for lado, arts in TRIPLETES[angulo].items():
        if not all(a in frame_puntos for a in arts):
            continue
        conf = min(frame_puntos[a].confianza for a in arts)
        if mejor is None or conf > mejor[1]:
            mejor = (lado, float(conf))
    return mejor


def es_elegible(frame_puntos: dict) -> dict | None:
    """Devuelve {angulo: (lado, conf)} si AMBOS ángulos tienen confianza mínima >= UMBRAL_CONF; si no, None."""
    salida = {}
    for angulo in TRIPLETES:
        m = mejor_lado(frame_puntos, angulo)
        if m is None or m[1] < UMBRAL_CONF:
            return None
        salida[angulo] = m
    return salida


def seleccionar_por_estrato(candidatos: dict, semilla: int, k: int) -> dict:
    """candidatos[estrato][clip] = [candidato, ...]. Devuelve {estrato: [(clip, candidato), ...]} (<= k).

    Determinista: clips en orden alfabético, barajados con la semilla; un candidato por clip.
    """
    rng = random.Random(semilla)
    elegidos = {}
    for estrato in sorted(candidatos):
        clips = sorted(c for c, lista in candidatos[estrato].items() if lista)
        rng.shuffle(clips)
        elegidos[estrato] = [(c, rng.choice(candidatos[estrato][c])) for c in clips[:k]]
    return elegidos


def resumen_errores(errores: list[float], sesgos: list[float]) -> dict:
    e = np.array([x for x in errores if np.isfinite(x)])
    s = np.array([x for x in sesgos if np.isfinite(x)])
    if e.size == 0:
        return {"n": 0}
    return {"n": int(e.size), "media": float(e.mean()), "mediana": float(np.median(e)),
            "p95": float(np.percentile(e, 95)), "max": float(e.max()), "sesgo_medio": float(s.mean()),
            "cumple": bool(e.mean() < META_ERROR_GRADOS)}


# --- preparar --------------------------------------------------------------------------------

def _pixeles(punto, ancho, alto):
    return (punto.x * ancho, punto.y * alto)


def _angulo_sistema_2d(frame_puntos, angulo, lado, ancho, alto) -> float:
    a, v, c = (_pixeles(frame_puntos[x], ancho, alto) for x in TRIPLETES[angulo][lado])
    return angulo_en_vertice(a, v, c)


def _recortar(img, frame_puntos, margen=0.30, minimo=420):
    h, w = img.shape[:2]
    xs = [p.x * w for p in frame_puntos.values()]
    ys = [p.y * h for p in frame_puntos.values()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    lado = max(x1 - x0, y1 - y0, minimo) * (1 + 2 * margen)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    xa, xb = int(max(0, cx - lado / 2)), int(min(w, cx + lado / 2))
    ya, yb = int(max(0, cy - lado / 2)), int(min(h, cy + lado / 2))
    return img[ya:yb, xa:xb]


LEEME = """# Criterio 2 — goniometría manual CIEGA

**Qué hacer.** Para cada fila de `planilla-manual.csv` abrí la imagen `ciego/<id_ciego>.png` y medí el ángulo
pedido en el plano de la imagen (2D):

- `rodilla`: ángulo interior en la **rodilla**, entre el muslo (hacia la cadera) y la pierna (hacia el tobillo).
- `codo`: ángulo interior en el **codo**, entre el brazo (hacia el hombro) y el antebrazo (hacia la muñeca).

`lado_del_jugador` es el lado ANATÓMICO del jugador (`der` = su derecha, `izq` = su izquierda), no el de la imagen.
El valor va en **grados, entre 0 y 180**, en la columna `valor_manual_grados`. Usá un goniómetro sobre la imagen
(Kinovea, ImageJ o similar) apoyándote en los puntos anatómicos (centro de la articulación); **no hay esqueleto
superpuesto a propósito**.

- `calidad`: 1 = nítido, 2 = algo borroso, 3 = muy borroso o dudoso.
- `comentario`: lo que quieras (oclusión, dudas).
- Las filas con `repetir_medicion = S` hay que medirlas **dos veces**, separadas en el tiempo y sin mirar el primer valor;
  el segundo va en `valor_manual_2` (sirve para estimar el error intra-observador).

**Importante.** No abras la carpeta `.clave-NO-ABRIR`: contiene qué valor dio el sistema. Se abre recién con la
planilla completa (la usa `python -m app.criterio2 analizar`).
"""


def preparar(args) -> int:
    import cv2

    from app.config import get_cache_dir, get_data_dir
    from app.diagnosticos_e3 import _buscar_video, _catalogo, ancla_cruda, en_sesion, fechas_propias
    from app.engine.kinematics import serie_angulo_articular
    from app.engine.pipeline import procesar_e3
    from app.engine.pose import cache as pose_cache
    from app.engine.pose.mediapipe_backend import MediaPipeBackend
    from app.engine.version import __version__ as version_motor

    base = get_data_dir()
    cat = _catalogo(base)
    fechas = fechas_propias(cat)
    b = MediaPipeBackend()
    destino = Path(args.destino) if args.destino else base / "fase-b" / "criterio2"
    (destino / "ciego").mkdir(parents=True, exist_ok=True)
    (destino / ".clave-NO-ABRIR").mkdir(parents=True, exist_ok=True)

    clips = [(n, r) for n, r in sorted(cat.items())
             if r.get("fuente") == "propio" and "_rep" in n and r.get("angulo") in ENCUADRES
             and r.get("gesto") in GESTOS and str(r.get("fps_efectivos")).strip() in ("240", "240.0")
             and en_sesion(n, 2, fechas)
             and not (r["gesto"] == "saque" and r["angulo"] == "trescuartos" and "_240_02_rep" not in n)]

    candidatos: dict = {f"{g}|{e}": {} for g in GESTOS for e in ENCUADRES}
    seqs = {}
    for n, r in clips:
        seq = pose_cache.cargar_si_vigente(get_cache_dir(), _buscar_video(base, n), b.id, b.config_hash)
        if seq is None:
            raise SystemExit(f"sin pose cacheada para {n}")
        seqs[n] = seq
        ancla = ancla_cruda(seq)
        if ancla is None:
            continue
        lista = []
        for off in OFFSETS_MS:
            fr = ancla + int(round(off * seq.fps_efectivos / 1000))
            if not 0 <= fr < seq.n_frames:
                continue
            el = es_elegible(seq.frames[fr].puntos)
            if el is not None:
                lista.append({"frame": fr, "offset_ms": off, "lados": {k: v[0] for k, v in el.items()},
                              "conf_min": {k: v[1] for k, v in el.items()}})
        candidatos[f"{r['gesto']}|{r['angulo']}"][n] = lista

    elegidos = seleccionar_por_estrato(candidatos, SEMILLA, POR_ESTRATO)
    seleccion = [(estrato, clip, cand) for estrato, L in elegidos.items() for clip, cand in L]
    random.Random(SEMILLA + 1).shuffle(seleccion)           # el orden de los ids no revela el estrato
    repetir = set(random.Random(SEMILLA + 2).sample(range(len(seleccion)), min(5, len(seleccion))))

    clave, filas = [], []
    for i, (estrato, clip, cand) in enumerate(seleccion, start=1):
        id_ = f"C2-{i:02d}"
        seq = seqs[clip]
        fr = cand["frame"]
        video = _buscar_video(base, clip)
        cap = cv2.VideoCapture(str(video))
        cap.set(cv2.CAP_PROP_POS_FRAMES, fr)
        ok, img = cap.read()
        cap.release()
        if not ok:
            raise SystemExit(f"no se pudo leer el fotograma {fr} de {clip}")
        cv2.imwrite(str(destino / "ciego" / f"{id_}.png"), _recortar(img, seq.frames[fr].puntos))
        filt = procesar_e3(seq)
        entrada = {"id_ciego": id_, "estrato": estrato, "clip": clip, "frame": fr, "offset_ms": cand["offset_ms"],
                   "angulos": {}}
        for angulo in ("rodilla", "codo"):
            lado = cand["lados"][angulo]
            s2d = _angulo_sistema_2d(seq.frames[fr].puntos, angulo, lado, seq.ancho, seq.alto)
            s3d = float(serie_angulo_articular(filt.secuencia, angulo, lado)[fr])
            entrada["angulos"][angulo] = {"lado": lado, "conf_min": cand["conf_min"][angulo],
                                          "sistema_2d": s2d, "sistema_3d_filtrado": s3d}
            filas.append({"id_ciego": id_, "angulo": angulo, "lado_del_jugador": lado, "valor_manual_grados": "",
                          "calidad": "", "comentario": "", "repetir_medicion": "S" if (i - 1) in repetir else "N",
                          "valor_manual_2": ""})
        clave.append(entrada)

    filas.sort(key=lambda f: (f["id_ciego"], f["angulo"]))
    with (destino / "planilla-manual.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    (destino / "LEEME.md").write_text(LEEME, encoding="utf-8")

    repo = Path(__file__).resolve().parents[2]
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = ""
    (destino / ".clave-NO-ABRIR" / "clave.json").write_text(json.dumps({
        "decision": "014", "semilla": SEMILLA, "offsets_ms": list(OFFSETS_MS), "umbral_conf": UMBRAL_CONF,
        "version_motor": version_motor, "commit": commit, "seleccion": clave}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    print(f"Paquete ciego escrito en {destino}")
    print("Fotogramas por estrato (sin valores del sistema):")
    for estrato in sorted(elegidos):
        n_el = sum(1 for lista in candidatos[estrato].values() if lista)
        print(f"  {estrato:22} elegidos {len(elegidos[estrato])}/{POR_ESTRATO}  (repeticiones con algún fotograma elegible: {n_el}/{len(candidatos[estrato])})")
    print(f"Total: {len(clave)} fotogramas, {len(filas)} mediciones; {len(repetir)} fotogramas marcados para repetir.")
    return 0


# --- analizar --------------------------------------------------------------------------------

def analizar(args) -> int:
    clave = json.loads((Path(args.carpeta) / ".clave-NO-ABRIR" / "clave.json").read_text(encoding="utf-8"))
    sistema = {(e["id_ciego"], a): v for e in clave["seleccion"] for a, v in e["angulos"].items()}
    with (Path(args.carpeta) / "planilla-manual.csv").open(encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    vacias = [f["id_ciego"] + "/" + f["angulo"] for f in filas if not f["valor_manual_grados"].strip()]
    if vacias:
        print(f"Faltan {len(vacias)} mediciones: {vacias[:6]}...")
        return 2
    porart, porart3, intra = {"rodilla": ([], []), "codo": ([], [])}, {"rodilla": ([], []), "codo": ([], [])}, []
    for f in filas:
        s = sistema[(f["id_ciego"], f["angulo"])]
        m = float(f["valor_manual_grados"].replace(",", "."))
        porart[f["angulo"]][0].append(abs(m - s["sistema_2d"]))
        porart[f["angulo"]][1].append(m - s["sistema_2d"])
        porart3[f["angulo"]][0].append(abs(m - s["sistema_3d_filtrado"]))
        porart3[f["angulo"]][1].append(m - s["sistema_3d_filtrado"])
        if f["repetir_medicion"] == "S" and f["valor_manual_2"].strip():
            intra.append(abs(m - float(f["valor_manual_2"].replace(",", "."))))
    res = {a: resumen_errores(*porart[a]) for a in porart}
    res3 = {a: resumen_errores(*porart3[a]) for a in porart3}
    print("Error angular contra la goniometría manual (grados). PRIMARIO: sistema en el plano de la imagen.")
    for a, r in res.items():
        print(f"  {a:8} n={r['n']:3d} media={r['media']:5.1f} mediana={r['mediana']:5.1f} p95={r['p95']:5.1f} "
              f"máx={r['max']:5.1f} sesgo={r['sesgo_medio']:+5.1f}  -> {'CUMPLE' if r['cumple'] else 'NO CUMPLE'} (< {META_ERROR_GRADOS}°)")
    print("Secundario (3D filtrado, NO validado por goniometría 2D):", {a: round(r["media"], 1) for a, r in res3.items()})
    if intra:
        print(f"Error intra-observador (media de |m1 - m2|, n={len(intra)}): {np.mean(intra):.1f}°")
    if args.salida:
        Path(args.salida).write_text(json.dumps({"primario_2d": res, "secundario_3d": res3,
                                                 "intra_observador_media": float(np.mean(intra)) if intra else None,
                                                 "clave": {k: v for k, v in clave.items() if k != "seleccion"}},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Criterio 2: goniometría manual ciega (decisión 014).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("--destino", default=None, help="default: KINETIQ_DATA_DIR/fase-b/criterio2")
    p.set_defaults(fn=preparar)
    p = sub.add_parser("analizar")
    p.add_argument("carpeta", help="la carpeta criterio2 con la planilla completa")
    p.add_argument("--salida", default=None)
    p.set_defaults(fn=analizar)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
