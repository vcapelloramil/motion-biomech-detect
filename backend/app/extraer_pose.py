"""E2 — Extrae y cachea las coordenadas de pose de los clips (plan, tareas 2.2/2.5).

Recorre el corpus, corre un backend de pose sobre cada clip y guarda el resultado
en la caché (``KINETIQ_CACHE_DIR`` o ``backend/.cache/``). Si ya está cacheado y el
video no cambió, no re-infiere.

Uso (desde backend/):
    python -m app.extraer_pose                       # todos los clips, MediaPipe
    python -m app.extraer_pose --clip zverev_saque_lateral_01.mp4
    python -m app.extraer_pose --backend fake --max-frames 30
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from app.engine.ingest import iterar_fotogramas, probe
from app.engine.pose import cache as pose_cache
from app.engine.pose.base import PoseBackend, SecuenciaPose

EXTENSIONES_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}
# Mismas carpetas de origen y mismas fases que el catalogador (una sola fuente de verdad).
from app.catalogador import CARPETAS_EXCLUIDAS, FASES_POR_DEFECTO  # noqa: E402


def crear_backend(nombre: str) -> PoseBackend:
    if nombre == "mediapipe":
        from app.engine.pose.mediapipe_backend import MediaPipeBackend

        return MediaPipeBackend()
    if nombre == "fake":
        from app.engine.pose.fake_backend import FakeBackend

        return FakeBackend()
    raise SystemExit(f"backend desconocido: {nombre!r} (usá 'mediapipe' o 'fake')")


def fps_efectivos_de(video: Path, verificado: Path | None) -> float:
    """fps de captura efectivos: del catalogo-verificado.csv si está, si no el declarado."""
    if verificado and verificado.is_file():
        with verificado.open(encoding="utf-8", newline="") as f:
            for fila in csv.DictReader(f):
                if fila.get("archivo") == video.name:
                    try:
                        return float(fila["fps_efectivos"])
                    except (KeyError, ValueError, TypeError):
                        break
    return probe(video, usar_ffprobe=False).fps_declarados


def extraer(
    video: Path,
    backend: PoseBackend,
    *,
    cache_dir: Path,
    fps_efectivos: float,
    max_frames: int | None = None,
    forzar: bool = False,
) -> tuple[SecuenciaPose, bool]:
    """Devuelve (secuencia, vino_de_cache)."""
    if not forzar:
        cacheada = pose_cache.cargar_si_vigente(
            cache_dir, video, backend.id, backend.config_hash
        )
        if cacheada is not None:
            return cacheada, True

    md = probe(video)
    with backend:
        seq = backend.procesar(
            iterar_fotogramas(video),
            ancho=md.ancho,
            alto=md.alto,
            fps_efectivos=fps_efectivos,
            max_frames=max_frames,
        )
    base = pose_cache.ruta_base(cache_dir, video, backend.id, backend.config_hash)
    pose_cache.guardar(seq, base, video=video)
    return seq, False


def _listar_clips(directorios: list[Path], nombres: list[str] | None) -> list[Path]:
    todos = sorted(
        p
        for directorio in directorios if directorio.is_dir()
        for p in directorio.rglob("*")
        if p.suffix.lower() in EXTENSIONES_VIDEO
        and not (CARPETAS_EXCLUIDAS & set(p.relative_to(directorio).parts))
    )
    if not nombres:
        return todos
    por_nombre = {p.name: p for p in todos}
    faltan = [n for n in nombres if n not in por_nombre]
    if faltan:
        raise SystemExit(f"no se encontraron: {', '.join(faltan)}")
    return [por_nombre[n] for n in nombres]


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Extrae coordenadas de pose del corpus.")
    parser.add_argument("--dir", type=Path, default=None,
                        help="Directorio de clips (default: fase-a/ y fase-b/ de KINETIQ_DATA_DIR).")
    parser.add_argument("--clip", action="append", default=None,
                        help="Nombre de archivo a procesar (repetible). Default: todos.")
    parser.add_argument("--backend", default="mediapipe", choices=["mediapipe", "fake"])
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--forzar", action="store_true", help="Re-infiere aunque esté cacheado.")
    args = parser.parse_args(argv)

    from app.config import get_cache_dir, get_data_dir

    base_datos = get_data_dir()
    directorios = [args.dir] if args.dir else [base_datos / f for f in FASES_POR_DEFECTO]
    verificado = base_datos / "catalogo-verificado.csv"
    cache_dir = get_cache_dir()

    clips = _listar_clips(directorios, args.clip)
    if not clips:
        print("No hay clips bajo " + ", ".join(map(str, directorios)) + ".")
        return 1

    print(f"Backend: {args.backend}  | caché: {cache_dir}")
    print(f"{'archivo':<32} {'frames':>7} {'cobertura':>10} {'origen':>8}")
    print("-" * 62)
    for video in clips:
        fps = fps_efectivos_de(video, verificado)
        seq, hit = extraer(
            video, crear_backend(args.backend), cache_dir=cache_dir,
            fps_efectivos=fps, max_frames=args.max_frames, forzar=args.forzar,
        )
        print(f"{video.name:<32} {seq.n_frames:>7} {seq.cobertura:>9.1%} "
              f"{'caché' if hit else 'inferido':>8}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
