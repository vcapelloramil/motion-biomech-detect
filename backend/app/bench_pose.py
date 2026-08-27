"""E2 — Mide la velocidad de inferencia de un backend de pose (plan, tarea 2.6).

Primer dato duro del indicador de rendimiento (tesis §2.4). El resultado se
agrega a ``docs/resultados/e2-velocidad-inferencia.json`` (lista de corridas), que
queda versionado: cualquiera puede re-ejecutar el script y comparar.

Uso (desde backend/):
    python -m app.bench_pose --clip zverev_saque_lateral_01.mp4 --frames 120
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from app.engine.ingest import iterar_fotogramas, probe
from app.engine.version import __version__ as version_motor

_SALIDA_POR_DEFECTO = (
    Path(__file__).resolve().parents[2] / "docs" / "resultados" / "e2-velocidad-inferencia.json"
)


def medir(video: Path, backend, *, n_frames: int) -> list[float]:
    """Segundos por fotograma de ``estimar_frame`` sobre los primeros n_frames."""
    tiempos: list[float] = []
    with backend:
        for i, frame in enumerate(iterar_fotogramas(video)):
            if i >= n_frames:
                break
            t0 = time.perf_counter()
            backend.estimar_frame(frame, i)
            tiempos.append(time.perf_counter() - t0)
    return tiempos


def _percentil(valores: list[float], p: float) -> float:
    if not valores:
        return 0.0
    orden = sorted(valores)
    k = min(len(orden) - 1, int(round(p * (len(orden) - 1))))
    return orden[k]


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Mide la velocidad de inferencia de pose.")
    parser.add_argument("--clip", default=None, help="Nombre del clip (default: el primero apto).")
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--backend", default="mediapipe", choices=["mediapipe", "fake"])
    parser.add_argument("--salida", type=Path, default=_SALIDA_POR_DEFECTO)
    args = parser.parse_args(argv)

    from app.config import get_data_dir
    from app.extraer_pose import crear_backend

    fase_a = get_data_dir() / "fase-a"
    if args.clip:
        video = next((p for p in fase_a.rglob(args.clip) if p.is_file()), None)
    else:
        video = next(iter(sorted((fase_a / "segmentos").glob("*.mp4"))), None)
    if video is None:
        print("No se encontró un clip para medir.")
        return 1

    backend = crear_backend(args.backend)
    md = probe(video)
    tiempos = medir(video, backend, n_frames=args.frames)
    if not tiempos:
        print("No se pudo leer ningún fotograma.")
        return 1

    fps_media = len(tiempos) / sum(tiempos)
    corrida = {
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "version_motor": version_motor,
        "maquina": {
            "sistema": platform.system(),
            "release": platform.release(),
            "procesador": platform.processor() or platform.machine(),
            "python": platform.python_version(),
        },
        "backend": backend.version,
        "config": backend.config,
        "clip": video.name,
        "resolucion": f"{md.ancho}x{md.alto}",
        "n_frames": len(tiempos),
        "fps_inferencia_media": round(fps_media, 2),
        "ms_por_frame": {
            "media": round(1000 * sum(tiempos) / len(tiempos), 1),
            "p50": round(1000 * _percentil(tiempos, 0.50), 1),
            "p95": round(1000 * _percentil(tiempos, 0.95), 1),
        },
    }

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    historial = []
    if args.salida.is_file():
        try:
            historial = json.loads(args.salida.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            historial = []
    historial.append(corrida)
    args.salida.write_text(json.dumps(historial, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(corrida, indent=2, ensure_ascii=False))
    print(f"\nAgregado a {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
