"""Generación de clips de video sintéticos para las pruebas de integración.

El corpus real de la Fase A ya cubre 30/60 fps y oclusión (ver
tests/integration/test_corpus_fase_a.py). Estos helpers quedan para los dos casos
que el corpus real NO tiene:
  - duplicación sistemática de fotogramas (test_framehash_video, test_catalogador_sintetico)
  - par 240 fps vs su ralentizado del mismo gesto (test_slowmo_coherencia) — pendiente
    de la Fase B (plazo 22/9), ahí se reemplaza por un par real.
Los clips se generan con ffmpeg en el tmp_path de pytest; nunca entran al repo.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")

requiere_ffmpeg = pytest.mark.skipif(
    FFMPEG is None, reason="ffmpeg no está en el PATH (dependencia del catalogador)"
)


def generar_clip(
    destino: Path,
    *,
    fps: float,
    segundos: float = 1.0,
    tamano: str = "320x240",
    fuente: str = "testsrc",
) -> Path:
    """Genera un clip con un patrón en movimiento (cada fotograma distinto).

    ``testsrc`` produce una imagen que cambia en cada cuadro, así el ratio de
    fotogramas únicos de un clip sano es ~100%.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG, "-y", "-loglevel", "error",
        "-f", "lavfi",
        "-i", f"{fuente}=size={tamano}:rate={fps}:duration={segundos}",
        "-pix_fmt", "yuv420p",
        str(destino),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return destino


def ralentizar(origen: Path, destino: Path, *, factor: int, fps_salida: float) -> Path:
    """Reescribe un clip para que se reproduzca ``factor`` veces más lento.

    Estira los timestamps (setpts) y fija la tasa de salida. Conserva todos los
    fotogramas: no duplica ni descarta. Simula un clip de cámara lenta exportado a
    una tasa de reproducción baja (el caso del material de Zverev).
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG, "-y", "-loglevel", "error",
        "-i", str(origen),
        "-filter:v", f"setpts={factor}*PTS",
        "-r", str(fps_salida),
        "-pix_fmt", "yuv420p",
        str(destino),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return destino


def duplicar_fotogramas(origen: Path, destino: Path, *, fps_destino: float) -> Path:
    """Sube la tasa duplicando fotogramas (sin interpolar): genera duplicados reales.

    Codificación sin pérdida (``-qp 0``): si se re-comprimiera con pérdida, cada
    "duplicado" se decodificaría con píxeles ligeramente distintos y la huella ya
    no los reconocería como iguales. En el material real estirado por duplicación
    los cuadros repetidos sí son idénticos bit a bit.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG, "-y", "-loglevel", "error",
        "-i", str(origen),
        "-vf", f"fps={fps_destino}",
        "-fps_mode", "cfr",
        "-c:v", "libx264", "-qp", "0",
        "-pix_fmt", "yuv420p",
        str(destino),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return destino
