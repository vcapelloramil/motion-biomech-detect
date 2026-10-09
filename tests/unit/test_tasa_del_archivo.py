"""``procesar_video._tasa_del_archivo`` y la lectura de E0 con archivos sintéticos — decisión 029 (RNF-01).

Sin Supabase ni corpus: los clips se generan con ffmpeg. Lo que se prueba es qué tasa usa el motor y de dónde sale.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from app.engine import ingest
from app.engine.ingest import AptitudFaseRapida, MetadatosVideo
from app.procesar_video import MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE, ORIGEN_FACTOR_MARCAS, _tasa_del_archivo


def _md(nominal: float | None, real: float | None, declarado: float, n: int = 400) -> MetadatosVideo:
    return MetadatosVideo(
        ruta=Path("x.mov"), fps_declarados=declarado, nb_frames=n, duracion_s=n / (real or declarado), ancho=1920, alto=1080,
        fps_nominal_marcas=nominal, fps_real_medio=real, pts_visibles=None if nominal is None else np.arange(n) / (real or 30.0),
    )


# --- de dónde sale la tasa --------------------------------------------------------------------------------


def test_un_archivo_en_tiempo_real_toma_la_tasa_de_las_marcas_y_no_de_la_declaracion():
    """El caso del recorte de Archivos: OpenCV declara 169,28 (con pre-roll) y las marcas dicen 239,98 nominales y 198,9 reales."""
    md = _md(nominal=239.98, real=198.87, declarado=169.283)
    factor, escala, origen, motivo = _tasa_del_archivo(md, "camara_lenta_240")
    assert (factor, escala, origen, motivo) == (1.0, True, ORIGEN_FACTOR_MARCAS, None)
    r = ingest.evaluar(md, factor=factor, escala_conocida=escala, origen_factor=origen)
    assert r.fps_efectivos == pytest.approx(198.87)
    assert r.aptitud is AptitudFaseRapida.REDUCIDO and r.habilita_fase_rapida


@pytest.mark.parametrize("modo", ["normal", "camara_lenta_120", "camara_lenta_240"])
def test_en_tiempo_real_la_declaracion_no_cambia_la_tasa(modo):
    """modo_captura deja de definir la tasa: ni falla ni la modifica (queda como trazabilidad)."""
    md = _md(nominal=239.98, real=198.87, declarado=169.283)
    assert _tasa_del_archivo(md, modo) == (1.0, True, ORIGEN_FACTOR_MARCAS, None)


def test_un_archivo_convertido_por_el_telefono_no_culpa_a_la_declaracion():
    """100 fps (Fotos por defecto): antes daba `modo_captura_incompatible` (240/100 = 2,4). Ahora la tasa es la del archivo y R1 decide."""
    md = _md(nominal=100.0, real=100.0, declarado=100.0)
    factor, escala, origen, motivo = _tasa_del_archivo(md, "camara_lenta_240")
    assert motivo is None and factor == 1.0
    r = ingest.evaluar(md, factor=factor, escala_conocida=escala, origen_factor=origen)
    assert r.fps_efectivos == pytest.approx(100.0) and r.aptitud is AptitudFaseRapida.SOLO_PREPARACION


def test_un_horneado_a_30_fps_conserva_la_logica_de_la_declaracion():
    """Marcas a 30 fps constantes: la tasa real se desconoce y solo hay declaración (decisión 020, sin cambios)."""
    md = _md(nominal=30.0, real=30.0, declarado=30.0, n=360)
    assert _tasa_del_archivo(md, "camara_lenta_240") == (8.0, True, "declaracion_usuario", None)
    assert _tasa_del_archivo(md, "normal") == (1.0, True, "declaracion_usuario", None)
    # y una combinación que no cierra sigue fallando con su código
    md25 = _md(nominal=25.0, real=25.0, declarado=25.0, n=360)
    assert _tasa_del_archivo(md25, "camara_lenta_240")[3] == MOTIVO_FALLO_MODO_CAPTURA_INCOMPATIBLE


def test_sin_marcas_de_tiempo_se_comporta_como_antes():
    md = _md(nominal=None, real=None, declarado=30.0)
    assert not md.es_tiempo_real
    assert _tasa_del_archivo(md, "camara_lenta_240")[:2] == (8.0, True)


def test_60_fps_normales_siguen_siendo_solo_preparacion_y_no_rechazados():
    """59,999 fps medios no pueden caer bajo el umbral de 60 por un redondeo: se normaliza a 60 como siempre."""
    md = _md(nominal=60.0, real=59.999, declarado=59.94)
    r = ingest.evaluar(md, factor=1.0, escala_conocida=True, origen_factor="declaracion_usuario")
    assert r.fps_efectivos == pytest.approx(60.0) and r.aptitud is AptitudFaseRapida.SOLO_PREPARACION


# --- lectura de archivos reales de E0 (ffmpeg) --------------------------------------------------------------

pytestmark_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None, reason="falta ffmpeg/ffprobe")


def _generar(destino: Path, *extra_entrada: str, salida: tuple[str, ...] = ()) -> Path:
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30", "-t", "1",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", *salida, str(destino)]
    subprocess.run(cmd, check=True, capture_output=True)
    return destino


@pytestmark_ffmpeg
def test_un_video_vertical_se_decodifica_derecho(tmp_path):
    """Defecto del 9/10/2026: OpenCV no aplica la rotación y la pose se calculaba sobre una persona acostada."""
    base = _generar(tmp_path / "base.mp4")
    vertical = tmp_path / "vertical.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-display_rotation", "90", "-i", str(base), "-c", "copy", str(vertical)],
                   check=True, capture_output=True)

    horizontal = ingest.probe(base)
    md = ingest.probe(vertical)
    assert (horizontal.ancho, horizontal.alto) == (320, 180) and horizontal.rotacion_grados == 0
    assert md.rotacion_grados in (90, 270)
    assert (md.ancho, md.alto) == (180, 320)               # ya girado: la resolución que ve la pose
    primero = next(iter(ingest.iterar_fotogramas(vertical)))
    assert primero.shape[:2] == (320, 180)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="falta ffmpeg")
def test_probe_de_un_horneado_a_30_fps_no_cambia(tmp_path):
    clip = _generar(tmp_path / "c30.mp4")
    md = ingest.probe(clip)
    assert md.nb_frames == 30 and md.fps_declarados == pytest.approx(30.0)
    assert md.fps_real_medio == pytest.approx(30.0, rel=0.02) and not md.es_tiempo_real and md.n_preroll == 0
    assert md.duracion_s == pytest.approx(1.0, abs=0.05)
