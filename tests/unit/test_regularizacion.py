"""``app.engine.regularizacion`` — decisión 029. Función pura sobre ``SecuenciaPose``, sin video ni pose real.

El caso de referencia es el de un archivo "Actual" del iPhone: nominal 240 fps con fotogramas perdidos (intervalos de 1 y 3 períodos,
~199 fps reales).
"""

from __future__ import annotations

import numpy as np
import pytest

from app.engine.pose.articulaciones import ArticulacionCanonica
from app.engine.pose.base import PoseFrame, Punto, SecuenciaPose
from app.engine.regularizacion import regularizar

_ART = tuple(ArticulacionCanonica)[:2]
_FPS = 240.0


def _pts_con_perdidos(n_intervalos: int = 397, cada: int = 10) -> np.ndarray:
    """1 período, salvo uno de 3 cada ``cada``: el patrón medido en el archivo real. Múltiplos exactos de 1/240."""
    pasos = np.array([3 if (i + 1) % cada == 0 else 1 for i in range(n_intervalos)])
    return np.concatenate([[0], np.cumsum(pasos)]) / _FPS


def _secuencia(pts: np.ndarray, f=lambda t: np.sin(2 * np.pi * 5.0 * t), detectado=None) -> SecuenciaPose:
    """Una señal conocida f(t) en x; y = 2 f(t); z = None (2D); confianza 0,9. Un fotograma por marca de tiempo."""
    detectado = np.ones(pts.size, dtype=bool) if detectado is None else detectado
    frames = []
    for i, t in enumerate(pts):
        if not detectado[i]:
            frames.append(PoseFrame(indice=i, detectado=False))
            continue
        v = float(f(t))
        pt = {a: Punto(v + 0.1 * k, 2 * v, None, 0.9) for k, a in enumerate(_ART)}
        frames.append(PoseFrame(indice=i, detectado=True, puntos=pt, puntos_mundo=dict(pt)))
    return SecuenciaPose(
        backend_id="test", backend_version="0", articulaciones=_ART, dims=2, ancho=1920, alto=1080,
        fps_efectivos=199.0, config_hash="x", frames=frames,
    )


def test_la_grilla_es_uniforme_y_cubre_el_mismo_intervalo():
    pts = _pts_con_perdidos()
    seq, info = regularizar(_secuencia(pts), pts, _FPS)
    assert info.n_grilla == round((pts[-1] - pts[0]) * _FPS) + 1
    assert seq.n_frames == info.n_grilla and seq.fps_efectivos == _FPS
    assert [f.indice for f in seq.frames] == list(range(info.n_grilla))


def test_los_fotogramas_que_ya_caen_en_la_grilla_se_copian_sin_tocar():
    pts = _pts_con_perdidos()
    orig = _secuencia(pts)
    seq, info = regularizar(orig, pts, _FPS)
    assert info.n_copiados == pts.size                       # todos los fuente caen sobre la grilla de 240
    # el fotograma fuente i está en la posición round(pts[i] * 240) de la grilla, con los mismos valores
    for i in (0, 11, 150, pts.size - 1):
        k = round((pts[i] - pts[0]) * _FPS)
        assert seq.frames[k].puntos == orig.frames[i].puntos


def test_los_puntos_que_faltan_se_interpolan_y_se_cuentan():
    pts = _pts_con_perdidos()
    _, info = regularizar(_secuencia(pts), pts, _FPS)
    assert info.n_interpolados == info.n_grilla - info.n_copiados - info.n_sin_dato
    assert info.n_interpolados == 78 and info.n_sin_dato == 0          # 39 huecos de 2 fotogramas (uno cada 10 intervalos)
    assert info.fraccion_interpolada == pytest.approx(78 / info.n_grilla)
    assert info.hueco_maximo_ms == pytest.approx(12.5, abs=0.01)
    assert info.fps_real_medio == pytest.approx(200.6, abs=0.1)


def test_el_valor_interpolado_se_parece_a_la_senal_real():
    """Un gesto de 5 Hz con huecos de 12,5 ms: el spline cúbico lo reconstruye con un error despreciable."""
    pts = _pts_con_perdidos()
    seq, info = regularizar(_secuencia(pts), pts, _FPS)
    t = pts[0] + np.arange(info.n_grilla) / _FPS
    esperado = np.sin(2 * np.pi * 5.0 * t)
    x = np.array([f.puntos[_ART[0]].x for f in seq.frames])
    assert np.max(np.abs(x - esperado)) < 1e-3


def test_la_interpolacion_es_mejor_que_tratar_la_serie_como_uniforme():
    """Lo que justifica la etapa: leer los fotogramas con huecos como si fueran consecutivos distorsiona la señal."""
    pts = _pts_con_perdidos()
    seq, info = regularizar(_secuencia(pts), pts, _FPS)
    t_grilla = pts[0] + np.arange(info.n_grilla) / _FPS
    verdad = np.sin(2 * np.pi * 5.0 * t_grilla)
    como_uniforme = np.sin(2 * np.pi * 5.0 * pts)               # lo que ve un archivo horneado: fotograma k <-> k/fps
    x_reg = np.array([f.puntos[_ART[0]].x for f in seq.frames])
    # error de la serie regularizada en la grilla contra el error de poner los fotogramas fuente en una grilla uniforme
    err_reg = np.max(np.abs(x_reg - verdad))
    err_unif = np.max(np.abs(como_uniforme - np.sin(2 * np.pi * 5.0 * np.arange(pts.size) / _FPS)))
    assert err_reg < 1e-3 < err_unif


def test_un_hueco_demasiado_largo_no_se_interpola():
    """Faltan 9 períodos seguidos (37,5 ms): ese tramo queda sin detectar, no se inventa (R3)."""
    pts = np.concatenate([np.arange(0, 20), np.arange(29, 60)]) / _FPS
    seq, info = regularizar(_secuencia(pts), pts, _FPS, hueco_max_periodos=6)
    sin_dato = [f.indice for f in seq.frames if not f.detectado]
    assert info.n_sin_dato == 9 and sin_dato == list(range(20, 29))
    assert info.n_interpolados == 0


def test_un_hueco_corto_dentro_del_maximo_si_se_interpola():
    pts = np.concatenate([np.arange(0, 20), np.arange(24, 60)]) / _FPS     # faltan 4 períodos
    _, info = regularizar(_secuencia(pts), pts, _FPS, hueco_max_periodos=6)
    assert info.n_interpolados == 4 and info.n_sin_dato == 0


def test_si_un_vecino_no_fue_detectado_el_punto_interpolado_queda_sin_dato():
    pts = _pts_con_perdidos(60)
    det = np.ones(pts.size, dtype=bool)
    det[10] = False
    seq, info = regularizar(_secuencia(pts, detectado=det), pts, _FPS)
    # el fotograma fuente 10 no está detectado y cae sobre la grilla: se copia tal cual (sin detectar)
    k = round((pts[10] - pts[0]) * _FPS)
    assert not seq.frames[k].detectado
    # los puntos interpolados que dependen de él también quedan sin dato
    assert info.n_sin_dato >= 0 and all(not f.detectado for f in seq.frames if f.indice == k)


def test_una_serie_ya_uniforme_no_cambia():
    pts = np.arange(100) / _FPS
    orig = _secuencia(pts)
    seq, info = regularizar(orig, pts, _FPS)
    assert info.n_interpolados == 0 and info.n_grilla == 100 and info.fraccion_interpolada == 0.0
    assert [f.puntos for f in seq.frames] == [f.puntos for f in orig.frames]


def test_la_confianza_interpolada_queda_en_el_rango_unitario():
    pts = _pts_con_perdidos()
    seq, _ = regularizar(_secuencia(pts), pts, _FPS)
    c = [p.confianza for f in seq.frames if f.detectado for p in f.puntos.values()]
    assert min(c) >= 0.0 and max(c) <= 1.0


def test_marcas_no_crecientes_se_rechazan():
    pts = np.array([0.0, 0.0, 0.1])
    with pytest.raises(ValueError, match="estrictamente crecientes"):
        regularizar(_secuencia(pts), pts, _FPS)


def test_una_tasa_de_grilla_invalida_se_rechaza():
    pts = np.arange(3) / _FPS
    with pytest.raises(ValueError, match="positiva"):
        regularizar(_secuencia(pts), pts, 0.0)


def test_la_cantidad_de_marcas_tiene_que_coincidir_con_la_de_fotogramas():
    seq = _secuencia(np.arange(10) / _FPS)
    with pytest.raises(ValueError, match="no se puede asignar tiempo"):
        regularizar(seq, np.arange(9) / _FPS, _FPS)


def test_el_resumen_para_la_trazabilidad_tiene_los_conteos():
    pts = _pts_con_perdidos()
    _, info = regularizar(_secuencia(pts), pts, _FPS)
    d = info.como_dict()
    assert d["puntos_interpolados"] == 78 and d["puntos_sin_dato"] == 0 and d["fps_grilla"] == _FPS
    assert d["fotogramas_fuente"] == 398 and d["puntos_de_la_grilla"] == info.n_grilla
