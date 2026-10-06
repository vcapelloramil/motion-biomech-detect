"""POST /analisis/{video_id}/procesar — pruebas rápidas, sin red: cliente de Supabase
falso y el worker de fondo reemplazado por un espía. Prueban el ruteo, el token, los
códigos de estado y las transiciones del reintento (decisión 022: 202 / 409); el pipeline real
ya lo prueba tests/integration/test_procesar_video_e2e.py (y el disparo end-to-end a través de la
API, tests/integration/test_api_analisis_e2e.py)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.routers.analisis as analisis_router
from app.main import app
from app.security import get_admin_client

_TOKEN_ENV_VAR = "KINETIQ_API_TOKEN"
_TOKEN_VALIDO = "token-de-prueba-no-real"
_HEADERS = {"x-kinetiq-token": _TOKEN_VALIDO}


class _ConsultaFalsa:
    """Encadena select/update/eq como el cliente real. execute() devuelve ``data``; un update
    deja registrado su patch y los filtros .eq() que lo acompañaron (el compare-and-swap)."""

    def __init__(self, data, registro: list | None = None, es_update: bool = False, patch=None):
        self._data = data
        self._registro = registro
        self._es_update = es_update
        self._patch = patch
        self._filtros: dict = {}

    def select(self, *_a, **_kw):
        return self

    def update(self, patch, *_a, **_kw):
        return _ConsultaFalsa(self._data, self._registro, es_update=True, patch=patch)

    def eq(self, columna, valor):
        self._filtros[columna] = valor
        return self

    def execute(self):
        if self._es_update and self._registro is not None:
            self._registro.append({"patch": self._patch, "filtros": dict(self._filtros)})
        return SimpleNamespace(data=self._data)


def _video(**cambios) -> dict:
    """Fila de videos tal como la devuelve el select del router (con su sesión embebida)."""
    base = {
        "id": "video-de-prueba",
        "estado": "pendiente",
        "motivo_fallo": None,
        "modo_captura_intentado": None,
        "intentos": 0,
        "sesiones": {"modo_captura": "camara_lenta_240"},
    }
    base.update(cambios)
    return base


class _AdminFalso:
    """No es un cliente de Supabase real: solo responde a videos.select/update/eq.execute,
    lo único que toca el router. ``video=None`` simula un video inexistente;
    ``update_afecta=False`` simula perder la carrera del compare-and-swap (0 filas)."""

    def __init__(self, video: dict | None, update_afecta: bool = True):
        self.video = video
        self.update_afecta = update_afecta
        self.updates: list = []

    def table(self, nombre: str):
        assert nombre == "videos", f"tabla inesperada en esta prueba: {nombre}"
        return _TablaVideos(self)


class _TablaVideos(_ConsultaFalsa):
    def __init__(self, admin: _AdminFalso):
        super().__init__([admin.video] if admin.video else [])
        self._admin = admin

    def update(self, patch, *_a, **_kw):
        datos = [self._admin.video] if self._admin.update_afecta else []
        return _ConsultaFalsa(datos, self._admin.updates, es_update=True, patch=patch)


@pytest.fixture(autouse=True)
def _token_configurado(monkeypatch):
    monkeypatch.setenv(_TOKEN_ENV_VAR, _TOKEN_VALIDO)


@pytest.fixture(autouse=True)
def _tope_de_intentos(monkeypatch):
    monkeypatch.setenv("KINETIQ_MAX_INTENTOS", "3")


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
def cliente_con(espia_worker):
    """Fábrica: ``cliente, admin = cliente_con(_video(estado="fallido", ...))``."""

    def _armar(video: dict | None, update_afecta: bool = True):
        admin = _AdminFalso(video, update_afecta)
        app.dependency_overrides[get_admin_client] = lambda: admin
        return TestClient(app), admin

    yield _armar
    app.dependency_overrides.clear()


@pytest.fixture
def cliente_con_video(cliente_con):
    return cliente_con(_video())[0]


@pytest.fixture
def cliente_sin_video(cliente_con):
    return cliente_con(None)[0]


def _post(cliente):
    return cliente.post("/analisis/video-de-prueba/procesar", headers=_HEADERS)


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
    resp = cliente_sin_video.post("/analisis/no-existe/procesar", headers=_HEADERS)
    assert resp.status_code == 404
    assert espia_worker == []


def test_token_correcto_video_existente_responde_202_y_encola(cliente_con_video, espia_worker):
    resp = _post(cliente_con_video)
    assert resp.status_code == 202
    assert resp.json() == {"video_id": "video-de-prueba", "estado": "encolado"}
    # TestClient corre las BackgroundTasks antes de devolver la respuesta: el espía ya
    # tiene que haber sido llamado para acá.
    assert espia_worker == ["video-de-prueba"]


def test_sin_KINETIQ_API_TOKEN_en_el_servidor_responde_500(cliente_con_video, espia_worker, monkeypatch):
    """Servidor mal configurado (variable no cargada en Render) es un error distinto de
    "token inválido" — no debería poder confundirse con un ataque."""
    monkeypatch.delenv(_TOKEN_ENV_VAR, raising=False)
    resp = _post(cliente_con_video)
    assert resp.status_code == 500
    assert espia_worker == []


# --- Reintento fallido -> encolado (decisión 022) ---------------------------------------------


def test_encolar_un_pendiente_limpia_resultados_viejos_y_cuenta_el_intento(cliente_con, espia_worker):
    cliente, admin = cliente_con(_video(estado="pendiente", intentos=0))
    assert _post(cliente).status_code == 202
    (u,) = admin.updates
    assert u["patch"] == {
        "estado": "encolado",
        "motivo_fallo": None,
        "fps_real": None,
        "apto_fase_rapida": None,
        "intentos": 1,
    }
    # Compare-and-swap: el update solo pega si el video sigue como se leyó.
    assert u["filtros"] == {"id": "video-de-prueba", "estado": "pendiente", "intentos": 0}
    assert espia_worker == ["video-de-prueba"]


@pytest.mark.parametrize("estado", ["encolado", "procesando", "completado", "parcial"])
def test_estados_no_reintentables_dan_409_y_no_encolan(cliente_con, espia_worker, estado):
    cliente, admin = cliente_con(_video(estado=estado))
    resp = _post(cliente)
    assert resp.status_code == 409
    assert resp.json()["detail"] == {"codigo": "estado_no_reintentable", "estado_actual": estado}
    assert admin.updates == [] and espia_worker == []


def test_modo_incompatible_con_la_declaracion_sin_cambios_da_409(cliente_con, espia_worker):
    cliente, admin = cliente_con(
        _video(
            estado="fallido",
            motivo_fallo="modo_captura_incompatible",
            modo_captura_intentado="camara_lenta_240",  # la sesión sigue declarando camara_lenta_240
        )
    )
    resp = _post(cliente)
    assert resp.status_code == 409
    assert resp.json()["detail"] == {"codigo": "declaracion_sin_cambios", "estado_actual": "fallido"}
    assert admin.updates == [] and espia_worker == []


def test_modo_incompatible_con_la_declaracion_corregida_se_encola(cliente_con, espia_worker):
    cliente, admin = cliente_con(
        _video(
            estado="fallido",
            motivo_fallo="modo_captura_incompatible",
            modo_captura_intentado="normal",  # la sesión ahora declara camara_lenta_240
            intentos=1,
        )
    )
    assert _post(cliente).status_code == 202
    (u,) = admin.updates
    assert u["patch"]["motivo_fallo"] is None
    assert u["patch"]["intentos"] == 2
    assert u["filtros"]["estado"] == "fallido"
    assert espia_worker == ["video-de-prueba"]


def test_error_inesperado_se_reintenta_hasta_el_tope(cliente_con):
    cliente, _ = cliente_con(_video(estado="fallido", motivo_fallo="error_inesperado", intentos=2))
    assert _post(cliente).status_code == 202  # el 3.er intento todavía entra

    cliente, admin = cliente_con(_video(estado="fallido", motivo_fallo="error_inesperado", intentos=3))
    resp = _post(cliente)
    assert resp.status_code == 409
    assert resp.json()["detail"] == {"codigo": "intentos_agotados", "estado_actual": "fallido"}
    assert admin.updates == []


def test_el_tope_de_intentos_es_un_parametro(cliente_con, monkeypatch):
    monkeypatch.setenv("KINETIQ_MAX_INTENTOS", "5")
    cliente, _ = cliente_con(_video(estado="fallido", motivo_fallo="error_inesperado", intentos=4))
    assert _post(cliente).status_code == 202


def test_perder_la_carrera_del_compare_and_swap_da_409_y_no_encola(cliente_con, espia_worker):
    """Dos pedidos simultáneos leen el mismo estado; el segundo no actualiza ninguna fila."""
    cliente, admin = cliente_con(_video(estado="pendiente"), update_afecta=False)
    resp = _post(cliente)
    assert resp.status_code == 409
    assert resp.json()["detail"]["codigo"] == "estado_no_reintentable"
    assert len(admin.updates) == 1  # lo intentó, no pegó
    assert espia_worker == []
