"""POST /analisis/{video_id}/procesar — pruebas rápidas, sin red: cliente de Supabase
falso y el worker de fondo reemplazado por un espía. Prueban el ruteo, el token y los
códigos de estado; el pipeline real ya lo prueba
tests/integration/test_procesar_video_e2e.py (y el disparo end-to-end a través de la API,
tests/integration/test_api_analisis_e2e.py)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.routers.analisis as analisis_router
from app.main import app
from app.security import get_admin_client

_TOKEN_ENV_VAR = "KINETIQ_API_TOKEN"
_TOKEN_VALIDO = "token-de-prueba-no-real"


class _ConsultaFalsa:
    def __init__(self, data):
        self._data = data

    def select(self, *_a, **_kw):
        return self

    def update(self, *_a, **_kw):
        return self

    def eq(self, *_a, **_kw):
        return self

    def execute(self):
        return SimpleNamespace(data=self._data)


class _AdminFalso:
    """No es un cliente de Supabase real: solo responde a videos.select/update/eq.execute,
    lo único que toca el router hoy."""

    def __init__(self, video_existe: bool):
        self._video_existe = video_existe

    def table(self, nombre: str):
        assert nombre == "videos", f"tabla inesperada en esta prueba: {nombre}"
        return _ConsultaFalsa([{"id": "video-de-prueba"}] if self._video_existe else [])


@pytest.fixture(autouse=True)
def _token_configurado(monkeypatch):
    monkeypatch.setenv(_TOKEN_ENV_VAR, _TOKEN_VALIDO)


@pytest.fixture
def espia_worker(monkeypatch):
    llamadas: list[str] = []
    monkeypatch.setattr(
        analisis_router,
        "procesar_en_segundo_plano",
        lambda admin, video_id: llamadas.append(video_id),
    )
    return llamadas


@pytest.fixture
def cliente_con_video(espia_worker):
    app.dependency_overrides[get_admin_client] = lambda: _AdminFalso(video_existe=True)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def cliente_sin_video(espia_worker):
    app.dependency_overrides[get_admin_client] = lambda: _AdminFalso(video_existe=False)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_sin_token_responde_401(cliente_con_video, espia_worker):
    resp = cliente_con_video.post("/analisis/video-de-prueba/procesar")
    assert resp.status_code == 401
    assert espia_worker == []


def test_token_incorrecto_responde_401(cliente_con_video, espia_worker):
    resp = cliente_con_video.post(
        "/analisis/video-de-prueba/procesar", headers={"x-kinetiq-token": "token-equivocado"}
    )
    assert resp.status_code == 401
    assert espia_worker == []


def test_token_correcto_video_inexistente_responde_404(cliente_sin_video, espia_worker):
    resp = cliente_sin_video.post(
        "/analisis/no-existe/procesar", headers={"x-kinetiq-token": _TOKEN_VALIDO}
    )
    assert resp.status_code == 404
    assert espia_worker == []


def test_token_correcto_video_existente_responde_202_y_encola(cliente_con_video, espia_worker):
    resp = cliente_con_video.post(
        "/analisis/video-de-prueba/procesar", headers={"x-kinetiq-token": _TOKEN_VALIDO}
    )
    assert resp.status_code == 202
    assert resp.json() == {"video_id": "video-de-prueba", "estado": "encolado"}
    # TestClient corre las BackgroundTasks antes de devolver la respuesta: el espía ya
    # tiene que haber sido llamado para acá.
    assert espia_worker == ["video-de-prueba"]


def test_sin_KINETIQ_API_TOKEN_en_el_servidor_responde_500(cliente_con_video, espia_worker, monkeypatch):
    """Servidor mal configurado (variable no cargada en Render) es un error distinto de
    "token inválido" — no debería poder confundirse con un ataque."""
    monkeypatch.delenv(_TOKEN_ENV_VAR, raising=False)
    resp = cliente_con_video.post(
        "/analisis/video-de-prueba/procesar", headers={"x-kinetiq-token": _TOKEN_VALIDO}
    )
    assert resp.status_code == 500
    assert espia_worker == []
