"""Diagnóstico de uniformidad temporal sobre el corpus propio de la Fase B (decisión 028).

Mide, para cada ``.mov`` de ``fase-b/``: las marcas de tiempo de los paquetes (¿constantes? ¿a cuántos fps?) y la energía de movimiento
entre fotogramas consecutivos, y resume qué marca el detector experimental ``detectar_tramos_acelerados`` con distintos umbrales.
Es el instrumento que respalda la decisión 028: **de solo lectura**, sin Supabase, y reproducible (la energía se guarda en caché).

Uso (desde ``backend/``):
    python -m app.diagnostico_uniformidad_corpus [--salida ../docs/resultados/uniformidad-temporal-corpus.json]

Decodificar los originales (~190 a 320 s de video a 30 fps de reproducción) es lo lento: la primera corrida tarda decenas de minutos;
las siguientes usan la caché de ``KINETIQ_CACHE_DIR/uniformidad``.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from app.config import get_cache_dir, get_data_dir
from app.engine.uniformidad_temporal import detectar_tramos_acelerados, energia_de_movimiento, marcas_de_tiempo

FPS_REPRODUCCION = 30.0
RAZONES = (3, 4, 5, 6, 8, 10)
DURACIONES = (0.3, 0.5, 1.0)


def _nombre(ruta: Path) -> str:
    # sesion-01 / drive / originales | recortes / archivo
    return "__".join([ruta.parent.parent.parent.name, ruta.parent.parent.name, ruta.parent.name, ruta.stem])


def _tipo(ruta: Path) -> str:
    """original | golpe (recorte de una repetición, ``..._repNN``) | clip_completo (un recorte que es el clip entero, p. ej. los de velocidad normal)."""
    if ruta.parent.name == "originales":
        return "original"
    return "golpe" if "_rep" in ruta.stem else "clip_completo"


def _energia_cacheada(args: tuple[str, str]) -> str:
    ruta, cache = Path(args[0]), Path(args[1])
    destino = cache / (_nombre(ruta) + ".npy")
    if not destino.exists():
        np.save(destino, energia_de_movimiento(ruta))
    return str(destino)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--salida", type=Path, default=Path("../docs/resultados/uniformidad-temporal-corpus.json"))
    ap.add_argument("--procesos", type=int, default=4)
    args = ap.parse_args(argv)

    archivos = sorted((get_data_dir() / "fase-b").rglob("*.mov"))
    cache = get_cache_dir() / "uniformidad"
    cache.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.procesos) as ex:
        list(ex.map(_energia_cacheada, [(str(a), str(cache)) for a in archivos]))

    filas = []
    for a in archivos:
        energia = np.load(cache / (_nombre(a) + ".npy"))
        marcas = marcas_de_tiempo(a)
        tramos = detectar_tramos_acelerados(energia, FPS_REPRODUCCION)
        filas.append(
            {
                "archivo": _nombre(a),
                "tipo": _tipo(a),
                "fotogramas": int(energia.size) + 1,
                "fps_por_marcas": round(marcas.fps_por_marcas, 3),
                "marcas_constantes": marcas.es_constante,
                "tramos_por_defecto": [
                    {"desde_s": round(t.desde_s, 1), "hasta_s": round(t.hasta_s, 1), "razon_maxima": round(t.razon_maxima, 1)} for t in tramos
                ],
                "_energia": energia,
            }
        )

    barrido = {}
    for razon in RAZONES:
        for dur in DURACIONES:
            marcado = {"golpe": 0, "clip_completo": 0, "original": 0}
            for f in filas:
                if detectar_tramos_acelerados(f["_energia"], FPS_REPRODUCCION, razon_minima=razon, duracion_minima_s=dur):
                    marcado[f["tipo"]] += 1
            barrido[f"razon>={razon}_duracion>={dur}s"] = marcado

    n = {t: sum(1 for f in filas if f["tipo"] == t) for t in ("original", "golpe", "clip_completo")}
    resultado = {
        "descripcion": "Diagnóstico de uniformidad temporal del corpus propio (decisión 028). Solo lectura.",
        "parametros_por_defecto": {"razon_minima": 5.0, "duracion_minima_s": 0.5, "ventana_mediana": 15, "percentil_base": 25.0},
        "archivos": n,
        "marcas_de_tiempo": {
            "todas_constantes": all(f["marcas_constantes"] for f in filas),
            "fps_por_marcas_distintos": sorted({round(f["fps_por_marcas"]) for f in filas}),
        },
        "marcados_segun_umbral": barrido,
        "nota": "Los originales NO tienen rampas de velocidad (toda la grabación es cámara lenta): lo que marca el detector al principio y al final es la persona "
                "caminando hacia el teléfono y manipulándolo. Se verificó mirando los fotogramas. El corpus no contiene ninguna rampa real.",
        "archivos_detalle": [{k: v for k, v in f.items() if not k.startswith("_")} for f in filas],
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Archivos: {n}. Marcas constantes en todos: {resultado['marcas_de_tiempo']['todas_constantes']}; "
          f"fps por marcas: {resultado['marcas_de_tiempo']['fps_por_marcas_distintos']}")
    for clave in ("razon>=5_duracion>=0.5s", "razon>=8_duracion>=0.5s"):
        print(f"  {clave}: {barrido[clave]}")
    print(f"Escrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
