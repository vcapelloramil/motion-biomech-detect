"""``workers.procesamiento``: el cupo de análisis simultáneos (carga de varios golpes). Sin red ni video: ``procesar_video`` es un doble."""

from __future__ import annotations

import threading
import time

import pytest

from app.workers import procesamiento


@pytest.fixture(autouse=True)
def _cupo_limpio(monkeypatch):
    monkeypatch.setattr(procesamiento, "_CUPO", None)


def _correr(monkeypatch, n_golpes: int, cupo: int | None) -> int:
    """Lanza ``n_golpes`` análisis a la vez y devuelve el máximo que corrió en simultáneo (``cupo=None``: sin configurar)."""
    if cupo is None:
        monkeypatch.delenv("KINETIQ_MAX_ANALISIS_SIMULTANEOS", raising=False)
    else:
        monkeypatch.setenv("KINETIQ_MAX_ANALISIS_SIMULTANEOS", str(cupo))
    activos = 0
    maximo = 0
    candado = threading.Lock()

    def falso(_admin, _video_id):
        nonlocal activos, maximo
        with candado:
            activos += 1
            maximo = max(maximo, activos)
        time.sleep(0.05)
        with candado:
            activos -= 1

    monkeypatch.setattr(procesamiento, "procesar_video", falso)
    hilos = [threading.Thread(target=procesamiento.procesar_en_segundo_plano, args=(None, f"v{i}")) for i in range(n_golpes)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=10)
    return maximo


def test_por_defecto_corre_de_a_un_golpe(monkeypatch):
    assert _correr(monkeypatch, 6, cupo=None) == 1


def test_con_cupo_dos_nunca_corren_mas_de_dos(monkeypatch):
    assert _correr(monkeypatch, 6, cupo=2) == 2


def test_un_golpe_que_falla_libera_el_cupo(monkeypatch):
    monkeypatch.setenv("KINETIQ_MAX_ANALISIS_SIMULTANEOS", "1")
    llamados: list[str] = []

    def falso(_a, video_id):
        llamados.append(video_id)
        if video_id == "malo":
            raise RuntimeError("reventó")

    monkeypatch.setattr(procesamiento, "procesar_video", falso)
    procesamiento.procesar_en_segundo_plano(None, "malo")     # no relanza
    procesamiento.procesar_en_segundo_plano(None, "bueno")    # y el siguiente corre: el cupo se liberó
    assert llamados == ["malo", "bueno"]


def test_el_cupo_invalido_es_un_error_claro(monkeypatch):
    from app.config import ConfigError, get_max_analisis_simultaneos

    monkeypatch.setenv("KINETIQ_MAX_ANALISIS_SIMULTANEOS", "0")
    with pytest.raises(ConfigError):
        get_max_analisis_simultaneos()
    monkeypatch.setenv("KINETIQ_MAX_ANALISIS_SIMULTANEOS", "tres")
    with pytest.raises(ConfigError):
        get_max_analisis_simultaneos()
