"""``app.engine.uniformidad_temporal`` — decisión 028. Lógica pura, sin video: los tres casos de llegada de un golpe
grabado a 240 fps (a: tiempo real, b: cámara lenta horneada, c: 30 fps con fotogramas descartados) y la detección de
tramos con velocidad no uniforme (rampas de la cámara lenta de iPhone)."""

from __future__ import annotations

import numpy as np
import pytest

from app.engine.uniformidad_temporal import (
    CasoArchivo,
    MarcasDeTiempo,
    clasificar_caso,
    detectar_tramos_acelerados,
)


def _marcas(fps: float, n: int = 360, variable: bool = False) -> MarcasDeTiempo:
    dt = 1.0 / fps
    return MarcasDeTiempo(n, dt, dt * (0.5 if variable else 1.0), dt * (1.5 if variable else 1.0), 0.5 if variable else 1.0)


# --- Clasificación (a / b / c) --------------------------------------------------------------------


def test_a_marcas_a_240_es_tiempo_real_aunque_no_se_sepa_la_duracion():
    c = clasificar_caso(_marcas(240.0, 360), 360, None)
    assert c.caso is CasoArchivo.TIEMPO_REAL and c.es_valido is True


def test_100_fps_en_tiempo_real_no_es_el_caso_c():
    """Caso real del 7/10/2026: Safari del iPhone entregó el recorte a 100 fps (H.264), 201 fotogramas en 2,01 s. Con el umbral anterior
    (100,0) quedaba justo por debajo y se lo clasificaba, mal, como (c) "fotogramas descartados"."""
    for fps_marcas in (100.0, 99.99, 100.01):
        c = clasificar_caso(_marcas(fps_marcas, 201), 201, 2.0)
        assert c.caso is CasoArchivo.TIEMPO_REAL, fps_marcas
        assert "solo_preparacion" in c.explicacion  # 100 fps: no alcanza para la fase rápida (R1)


@pytest.mark.parametrize("fps,aptitud", [(240.0, "completo"), (120.0, "reducido"), (100.0, "solo_preparacion"), (60.0, "solo_preparacion")])
def test_tiempo_real_informa_la_aptitud_de_r1(fps, aptitud):
    assert aptitud in clasificar_caso(_marcas(fps, 300), 300, 2.0).explicacion


def test_a_tambien_a_120():
    assert clasificar_caso(_marcas(120.0, 180), 180, 1.5, fps_captura=120.0).caso is CasoArchivo.TIEMPO_REAL


def test_b_marcas_a_30_con_todos_los_fotogramas_es_camara_lenta_horneada():
    # Gesto de 1,5 s reales a 240 fps = 360 fotogramas, reproducidos a 30 fps (12 s).
    c = clasificar_caso(_marcas(30.0, 360), 360, 1.5)
    assert c.caso is CasoArchivo.HORNEADO and c.es_valido is True
    assert c.fotogramas_esperados == 360 and c.fraccion_del_esperado == pytest.approx(1.0)


def test_c_marcas_a_30_con_un_octavo_de_los_fotogramas_es_el_invalido():
    # El mismo gesto de 1,5 s en tiempo real a 30 fps = 45 fotogramas.
    c = clasificar_caso(_marcas(30.0, 45), 45, 1.5)
    assert c.caso is CasoArchivo.DESCARTADO and c.es_valido is False
    assert c.fraccion_del_esperado == pytest.approx(45 / 360)


def test_las_marcas_solas_no_distinguen_b_de_c_y_no_se_adivina():
    """Las dos tienen marcas a 1/30 s constante: sin la duración real, queda indeterminado (R3)."""
    for n in (360, 45):
        c = clasificar_caso(_marcas(30.0, n), n, None)
        assert c.caso is CasoArchivo.INDETERMINADO and c.es_valido is None


def test_una_cantidad_de_fotogramas_que_no_coincide_con_ningun_caso_es_indeterminada():
    c = clasificar_caso(_marcas(30.0, 150), 150, 1.5)  # 150 / 360 = 42 %: ni 100 % ni 12,5 %
    assert c.caso is CasoArchivo.INDETERMINADO and c.es_valido is None


def test_la_tolerancia_acepta_pequenas_diferencias_de_conteo():
    assert clasificar_caso(_marcas(30.0, 330), 330, 1.5).caso is CasoArchivo.HORNEADO  # 92 % del esperado


def test_marcas_variables_se_informan_como_no_constantes():
    assert _marcas(30.0, variable=False).es_constante is True
    assert _marcas(30.0, variable=True).es_constante is False


def test_un_unico_intervalo_atipico_no_vuelve_variable_a_un_archivo():
    """Caso real del corpus: un recorte de 439 fotogramas con 437 intervalos de 33,33 ms y uno de 66,67 ms al final."""
    m = MarcasDeTiempo(439, 1 / 30, 1 / 30, 2 / 30, fraccion_regular=437 / 438)
    assert m.es_constante is True


# --- Tramos con velocidad no uniforme -------------------------------------------------------------

_FPS = 30.0


def _serie(n=600, base=0.5, ruido=0.03, semilla=1):
    rng = np.random.default_rng(semilla)
    return base + rng.normal(0, ruido, n)


def test_una_serie_pareja_no_tiene_tramos_acelerados():
    assert detectar_tramos_acelerados(_serie(), _FPS) == []


def test_un_golpe_normal_sube_poco_y_no_se_marca():
    """El golpe real eleva la energía unas pocas veces sobre la base, no 5 o más."""
    e = _serie()
    e[250:330] *= np.hanning(80) * 2.5 + 1  # pico de ~3,5x la base, suave
    assert detectar_tramos_acelerados(e, _FPS) == []


def test_una_rampa_final_a_velocidad_normal_se_detecta_y_se_ubica():
    e = _serie(600)
    e[500:] *= 12  # los últimos 100 cuadros (3,3 s) a velocidad normal horneada: ~8-20x de movimiento por cuadro
    tramos = detectar_tramos_acelerados(e, _FPS)
    assert len(tramos) == 1
    assert tramos[0].desde_s == pytest.approx(500 / _FPS, abs=0.6)
    assert tramos[0].hasta_s == pytest.approx(600 / _FPS, abs=0.1)
    assert tramos[0].razon_maxima > 5


def test_rampas_en_los_dos_extremos_dan_dos_tramos():
    e = _serie(600)
    e[:60] *= 10
    e[540:] *= 10
    assert len(detectar_tramos_acelerados(e, _FPS)) == 2


def test_un_pico_aislado_de_pocos_cuadros_no_cuenta():
    """Un destello o un salto de compresión de 3 cuadros no es una rampa de velocidad."""
    e = _serie()
    e[300:303] *= 30
    assert detectar_tramos_acelerados(e, _FPS) == []


def test_un_tramo_corto_acelerado_no_alcanza_la_duracion_minima():
    e = _serie()
    e[300:310] *= 12  # 10 cuadros = 0,33 s < 0,5 s
    assert detectar_tramos_acelerados(e, _FPS) == []
    assert len(detectar_tramos_acelerados(e, _FPS, duracion_minima_s=0.2)) == 1


def test_serie_sin_movimiento_o_demasiado_corta_no_produce_tramos():
    assert detectar_tramos_acelerados(np.zeros(300), _FPS) == []
    assert detectar_tramos_acelerados(np.array([1.0, 2.0]), _FPS) == []


def test_los_umbrales_son_parametros():
    e = _serie()
    e[200:260] *= 4  # 4x: bajo el umbral por defecto (5x)
    assert detectar_tramos_acelerados(e, _FPS) == []
    assert len(detectar_tramos_acelerados(e, _FPS, razon_minima=3.0)) == 1


# --- Tasa real: marcas de tiempo variables (decisión 029) ----------------------------------------
# Un recorte de Archivos (HEVC original del iPhone) trae las marcas de tiempo REALES de la captura: nominal 240 fps, pero con fotogramas
# perdidos. Medido el 9/10/2026 sobre los fotogramas visibles: 398 fotogramas en 2,005 s = 198,9 fps medios; 88 % de los intervalos de
# un período (4,17 ms) y 10 % de tres (12,5 ms). Estas pruebas reproducen esa estructura sin video.

from app.engine.uniformidad_temporal import marcas_desde_pts


def _pts_con_perdidos(n_intervalos: int = 397, cada: int = 10, periodo: float = 1 / 240):
    """Marcas con un intervalo de 3 períodos cada ``cada`` (el resto de 1): el patrón medido en el archivo real."""
    pasos = [3 if (i + 1) % cada == 0 else 1 for i in range(n_intervalos)]
    return np.concatenate([[0.0], np.cumsum(pasos) * periodo])


def test_la_tasa_nominal_y_la_real_media_son_distintas_si_se_pierden_fotogramas():
    m = marcas_desde_pts(_pts_con_perdidos())
    assert m.fps_por_marcas == pytest.approx(240.0, rel=1e-6)           # nominal: la inversa de la mediana
    assert m.fps_real == pytest.approx(240.0 / 1.2, rel=0.01)            # real media: ~200 fps
    assert m.fraccion_perdida == pytest.approx(1 - 1 / 1.2, abs=0.01)   # ~17 % de los fotogramas nominales
    assert set(m.intervalos_en_periodos) == {1, 3}
    assert not m.es_constante                                            # 10 % de intervalos irregulares


def test_una_captura_uniforme_no_pierde_fotogramas():
    m = marcas_desde_pts(np.arange(0, 480) / 240)
    assert m.fps_real == pytest.approx(240.0) and m.fraccion_perdida == pytest.approx(0.0, abs=1e-9)
    assert m.es_constante and set(m.intervalos_en_periodos) == {1}


def test_el_preroll_se_informa_aparte_y_no_cuenta():
    m = marcas_desde_pts(np.arange(0, 100) / 240, n_preroll=81)
    assert m.n_paquetes == 100 and m.n_preroll == 81


def test_la_clasificacion_de_tiempo_real_usa_la_tasa_real_media_para_r1():
    """Nominal 240 pero 200 reales sigue siendo 'reducido' (120-239), no 'completo': la aptitud sale de lo real."""
    c = clasificar_caso(marcas_desde_pts(_pts_con_perdidos()), 398, 2.0)
    assert c.caso is CasoArchivo.TIEMPO_REAL
    assert "reducido" in c.explicacion and "perdidos" in c.explicacion and "nominal 240" in c.explicacion


def test_marcas_no_crecientes_o_insuficientes_se_rechazan():
    with pytest.raises(ValueError):
        marcas_desde_pts(np.array([0.0]))
    with pytest.raises(ValueError):
        marcas_desde_pts(np.array([0.0, 0.0, 0.0]))
