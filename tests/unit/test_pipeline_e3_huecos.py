"""procesar_e3 con huecos: las series con NaN se filtran por segmentos (v0.4.1)."""

from __future__ import annotations

import numpy as np

from app.engine.pipeline import procesar_e3
from app.engine.pose.articulaciones import ArticulacionCanonica as A
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.pose.fake_backend import FakeBackend

_KW = dict(ancho=1920, alto=1080, fps_efectivos=240.0)
_SIGMA = 0.02      # ruido de posición (m)


def _serie_x(seq: SecuenciaPose, art) -> np.ndarray:
    return np.array([
        f.puntos_mundo[art].x if art in f.puntos_mundo else np.nan for f in seq.frames
    ])


def _con_ruido(seq: SecuenciaPose, semilla: int = 0) -> SecuenciaPose:
    rng = np.random.default_rng(semilla)
    frames = []
    for f in seq.frames:
        nuevos = {
            a: Punto(p.x + rng.normal(0, _SIGMA), p.y + rng.normal(0, _SIGMA),
                     None if p.z is None else p.z + rng.normal(0, _SIGMA), p.confianza)
            for a, p in f.puntos_mundo.items()
        }
        frames.append(PoseFrame(f.indice, f.detectado, puntos=f.puntos, puntos_mundo=nuevos))
    return SecuenciaPose(
        backend_id=seq.backend_id, backend_version=seq.backend_version,
        articulaciones=seq.articulaciones, dims=seq.dims, ancho=seq.ancho, alto=seq.alto,
        fps_efectivos=seq.fps_efectivos, config_hash=seq.config_hash, frames=frames,
    )


def _rugosidad(x: np.ndarray) -> float:
    """Desvío de la segunda diferencia sobre los tramos válidos: mide el ruido de alta frecuencia."""
    return float(np.nanstd(np.diff(x, n=2)))


def test_una_serie_con_hueco_largo_se_filtra_igual_que_una_completa():
    # Un hueco de 25 fotogramas sin detección (> gap_max) deja NaN en TODAS las
    # articulaciones. Antes de 0.4.1 eso dejaba cada serie entera cruda.
    base = FakeBackend(dims=3, frames_sin_deteccion=set(range(180, 205))).procesar(range(420), **_KW)
    seq = _con_ruido(base)
    filt = procesar_e3(seq)

    crudo = _serie_x(seq, A.HOMBRO_DER)
    filtrado = _serie_x(filt.secuencia, A.HOMBRO_DER)

    assert np.isnan(filtrado[180:205]).all()                     # el hueco no se rellena
    assert not np.isnan(filtrado[:180]).any()
    # el ruido de alta frecuencia cae claramente en ambos lados del hueco
    for lado in (slice(0, 180), slice(205, 420)):
        assert _rugosidad(filtrado[lado]) < 0.2 * _rugosidad(crudo[lado])


def test_un_segmento_demasiado_corto_queda_excluido_y_no_crudo():
    # Entre dos huecos largos queda un segmento de 8 fotogramas: no se puede filtrar.
    faltan = set(range(100, 150)) | set(range(158, 210))
    seq = _con_ruido(FakeBackend(dims=3, frames_sin_deteccion=faltan).procesar(range(320), **_KW))
    filt = procesar_e3(seq)

    filtrado = _serie_x(filt.secuencia, A.HOMBRO_DER)
    assert np.isnan(filtrado[150:158]).all()                     # 8 fotogramas: ni crudos ni rellenos
    excluidos = [t for t in filt.tramos_excluidos
                 if t.articulacion is A.HOMBRO_DER and t.coordenada == "x"]
    assert any(t.desde_frame <= 150 and t.hasta_frame >= 157 for t in excluidos)
