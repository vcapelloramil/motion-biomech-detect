"""Empareja los originales REALES del iPhone con los archivos horneados del corpus y mide cómo se relacionan (decisión 030).

Entradas (se leen, nunca se copian al repositorio):
  * una carpeta con los originales reales ("original sin modificar" de iCloud / Archivos: HEVC con marcas de tiempo reales),
  * ``kinetiq-data/fase-b/**/originales`` (los horneados con que se midió todo) y sus ``recortes`` (las repeticiones).

Qué hace:
  1. Inventario de los reales: códec, fotogramas visibles, pre-roll, tasa nominal y real media (marcas de tiempo), fecha de creación.
  2. Empareja real <-> horneado por la fecha de creación (``com.apple.quicktime.creationdate``).
  3. Alinea por CONTENIDO (miniaturas de 64x36) cada fotograma horneado con su fotograma real más parecido; de ahí sale la
     pendiente (fotogramas reales por fotograma horneado): 1,67 en la meseta = 120 fps de muestreo, ~6,7 en las rampas a velocidad normal.
  4. Ubica cada repetición (recorte con copia de flujo) dentro del horneado y del real, y dice si cae entera en la meseta.

Los derivados (miniaturas) se guardan en ``KINETIQ_CACHE_DIR/corpus-real`` (carpeta ignorada por git). El resultado agregado, sin
ningún video, va a ``docs/resultados/corpus-real-alineacion.json``.

Uso (desde ``backend/``):
    python -m app.diagnostico_originales_reales --reales "C:/Users/valen/Desktop/corpus-originales-reales"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from app.config import get_cache_dir, get_data_dir
from app.engine.uniformidad_temporal import marcas_de_tiempo

_RAIZ = Path(__file__).resolve().parents[2]
_LADO = (64, 36)
# Una pendiente "de meseta" (cámara lenta 4x a 120 fps de muestreo con una captura de ~200 fps reales).
PENDIENTE_MESETA = (1.5, 1.85)


def pendientes_por_ventana(j: np.ndarray, ancho: int = 200) -> list[float]:
    """Fotogramas reales por fotograma horneado, en ventanas de ``ancho`` fotogramas horneados (pura)."""
    j = np.asarray(j)
    return [float((j[k + ancho] - j[k]) / ancho) for k in range(0, len(j) - ancho, ancho)]


def en_meseta(pendientes: list[float]) -> list[float]:
    return [p for p in pendientes if PENDIENTE_MESETA[0] < p < PENDIENTE_MESETA[1]]


def _miniaturas(ruta: Path) -> np.ndarray:
    w, h = _LADO
    cmd = ["ffmpeg", "-v", "error", "-i", str(ruta), "-an", "-vf", f"scale={w}:{h}:flags=area,format=gray",
           "-fps_mode", "passthrough", "-f", "rawvideo", "-"]
    out = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.uint8).reshape(-1, w * h)


def _cargar(ruta: Path, cache: Path, etiqueta: str) -> np.ndarray:
    destino = cache / f"{etiqueta}.npy"
    if destino.exists():
        return np.load(destino)
    a = _miniaturas(ruta)
    np.save(destino, a)
    return a


def _vecino_mas_cercano(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Para cada fila de ``a``, el índice de la fila más parecida de ``b`` (L2), por bloques."""
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    bn = (b ** 2).sum(1)
    salida = np.empty(len(a), dtype=np.int64)
    for i in range(0, len(a), 600):
        blk = a[i:i + 600]
        salida[i:i + 600] = ((blk ** 2).sum(1)[:, None] + bn[None, :] - 2 * blk @ b.T).argmin(1)
    return salida


def _fecha(ruta: Path) -> str | None:
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags=com.apple.quicktime.creationdate",
                        "-of", "json", str(ruta)], capture_output=True, text=True).stdout
    return (json.loads(o).get("format", {}).get("tags") or {}).get("com.apple.quicktime.creationdate")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reales", type=Path, required=True, help="carpeta con los originales reales (.MOV)")
    ap.add_argument("--salida", type=Path, default=_RAIZ / "docs/resultados/corpus-real-alineacion.json")
    ap.add_argument("--esperado-completo", type=float, default=0.30,
                    help="un real con menos de esta fracción de los fotogramas esperados se marca incompleto")
    args = ap.parse_args(argv)

    cache = get_cache_dir() / "corpus-real"
    cache.mkdir(parents=True, exist_ok=True)
    base = get_data_dir() / "fase-b"

    # 1. inventario de los reales ----------------------------------------------------------------------
    reales = {}
    for f in sorted(args.reales.glob("*.[Mm][Oo][Vv]")):
        m = marcas_de_tiempo(f)
        reales[f.name] = {
            "ruta": f, "creado": _fecha(f), "visibles": m.n_paquetes, "preroll": m.n_preroll,
            "fps_nominal": round(m.fps_por_marcas, 2), "fps_real_medio": round(m.fps_real, 2),
            "perdidos_pct": round(100 * m.fraccion_perdida, 1), "marcas_constantes": m.es_constante,
        }
    horneados = {}
    for f in sorted(base.rglob("originales/*.mov")):
        m = marcas_de_tiempo(f)
        horneados[f.name] = {"ruta": f, "creado": _fecha(f), "frames": m.n_paquetes, "fps": round(m.fps_por_marcas, 2)}
    por_fecha = {h["creado"]: n for n, h in horneados.items()}

    # 2-3. emparejar y alinear --------------------------------------------------------------------------
    pares, sin_par, incompletos = [], [], []
    for nombre_r, r in reales.items():
        nombre_h = por_fecha.get(r["creado"])
        if nombre_h is None:
            sin_par.append(nombre_r)
            continue
        h = horneados[nombre_h]
        esperado = h["frames"] / 0.4606        # el horneado conserva ~46 % de los fotogramas reales
        if r["visibles"] < args.esperado_completo * esperado:
            incompletos.append({"real": nombre_r, "horneado": nombre_h, "visibles": r["visibles"], "esperados_aprox": round(esperado)})
            continue
        R = _cargar(r["ruta"], cache, "real_" + Path(nombre_r).stem)
        B = _cargar(h["ruta"], cache, "horn_" + Path(nombre_h).stem)
        j = _vecino_mas_cercano(B, R)
        pend = pendientes_por_ventana(j)
        mes = en_meseta(pend)
        bb = np.sqrt(((B[1:].astype(np.float32) - B[:-1].astype(np.float32)) ** 2).mean(1))
        pares.append({
            "real": nombre_r, "horneado": nombre_h, "creado": r["creado"],
            "fotogramas_reales_visibles": r["visibles"], "fotogramas_horneados": h["frames"],
            "relacion_horneado_sobre_real": round(h["frames"] / r["visibles"], 3),
            "fps_real_medio": r["fps_real_medio"],
            "pendiente_meseta": round(float(np.median(mes)), 3) if mes else None,
            "muestreo_equivalente_fps": round(r["fps_real_medio"] / float(np.median(mes)), 1) if mes else None,
            "fraccion_de_ventanas_en_meseta": round(len(mes) / max(len(pend), 1), 2),
            "pendiente_primera_ventana": round(pend[0], 2), "pendiente_ultima_ventana": round(pend[-1], 2),
            "orden_monotono_pct": round(float(100 * np.mean(np.diff(j) >= 0)), 1),
            "fotogramas_horneados_repetidos_pct": round(float(100 * np.mean(bb < 0.3)), 1),
            "_j": j, "_R": R, "_B": B,
        })

    # 4. ubicar las repeticiones ------------------------------------------------------------------------
    repeticiones = []
    for par in pares:
        stem = Path(par["horneado"]).stem
        for rep in sorted(p for c in base.glob("*/*/recortes") for p in c.glob(stem + "_rep*.mov")):
            Rp = _miniaturas(rep)
            ib = _vecino_mas_cercano(Rp, par["_B"])
            a, b = int(ib[0]), int(ib[-1])
            j = par["_j"]
            t = np.linspace(a, b, 4).astype(int)
            tercios = [(int(j[t[k + 1]]) - int(j[t[k]])) / max(int(t[k + 1] - t[k]), 1) for k in range(3)]
            repeticiones.append({
                "repeticion": rep.name, "horneado": par["horneado"], "real": par["real"],
                "fotogramas": int(len(Rp)), "ventana_horneada": [a, b], "ventana_real": [int(j[a]), int(j[b])],
                "largo_ventana_igual_al_recorte": abs((b - a + 1) - len(Rp)) <= 2,
                "pendiente": round((int(j[b]) - int(j[a])) / max(b - a, 1), 3), "pendiente_por_tercios": [round(x, 2) for x in tercios],
                "entera_en_la_meseta": all(PENDIENTE_MESETA[0] < x < PENDIENTE_MESETA[1] for x in tercios),
            })

    pend_meseta = [p["pendiente_meseta"] for p in pares if p["pendiente_meseta"]]
    resultado = {
        "descripcion": "Reales vs horneados del corpus (decisión 030). Sin videos: solo conteos, índices y estadísticas.",
        "reales": {
            n: {k: v for k, v in r.items() if k != "ruta"} for n, r in reales.items()
        },
        "pares": [{k: v for k, v in p.items() if not k.startswith("_")} for p in pares],
        "reales_sin_par": sin_par,
        "reales_incompletos": incompletos,
        "horneados_sin_real": sorted(n for n in horneados if n not in {p["horneado"] for p in pares} and n not in {i["horneado"] for i in incompletos}),
        "repeticiones": repeticiones,
        "resumen": {
            "reales": len(reales), "pares": len(pares), "repeticiones_ubicadas": len(repeticiones),
            "repeticiones_enteras_en_la_meseta": sum(r["entera_en_la_meseta"] for r in repeticiones),
            "pendiente_meseta": {"min": min(pend_meseta), "mediana": float(np.median(pend_meseta)), "max": max(pend_meseta)} if pend_meseta else None,
            "muestreo_equivalente_fps_mediana": float(np.median([p["muestreo_equivalente_fps"] for p in pares])) if pares else None,
            "fotogramas_reales_a_extraer_para_las_repeticiones": int(sum(r["ventana_real"][1] - r["ventana_real"][0] + 1 for r in repeticiones)),
        },
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resultado["resumen"], ensure_ascii=False, indent=1))
    print(f"sin par: {sin_par} | incompletos: {[i['real'] for i in incompletos]}")
    print(f"Escrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
