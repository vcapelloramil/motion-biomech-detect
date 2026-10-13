"""GET /sesiones/{id}/consistencia — identidad, propiedad y forma de la respuesta. Cliente de Supabase falso, sin red."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security import UsuarioAutenticado, get_admin_client, usuario_autenticado

_USUARIO = "11111111-1111-4111-8111-111111111111"


class _Q:
    def __init__(self, data):
        self.data = data

    def select(self, *_a, **_k):
        return self

    def eq(self, *_a, **_k):
        return self

    def order(self, *_a, **_k):
        return self

    def execute(self):
        return SimpleNamespace(data=self.data)


class _Admin:
    def __init__(self, sesion, videos):
        self.sesion, self.videos = sesion, videos

    def table(self, nombre):
        return _Q([self.sesion] if nombre == "sesiones" and self.sesion else self.videos if nombre == "videos" else [])


def _reporte(sep):
    return {
        "trazabilidad": {"version_motor": "0.5.3", "tolerancia_orden_ms": 8.33},
        "secuenciacion": {
            "repeticiones": [
                {"auditable": True, "picos": [{"segmento": "pelvis", "instante_s": 0.3}, {"segmento": "torso", "instante_s": 0.4}]}
            ]
        },
        "metricas": [{"nombre": "separacion_cadera_hombro_max", "valor": sep, "auditable": True}],
    }


@pytest.fixture
def cliente():
    def _armar(admin, usuario=_USUARIO):
        app.dependency_overrides[get_admin_client] = lambda: admin
        app.dependency_overrides[usuario_autenticado] = lambda: UsuarioAutenticado(id=usuario)
        return TestClient(app)

    yield _armar
    app.dependency_overrides.clear()


_SESION = {"id": "s1", "usuario_id": _USUARIO, "gesto": "saque", "encuadre": "tres_cuartos", "fecha": "2026-09-24"}


def test_devuelve_la_consistencia_de_la_sesion(cliente):
    videos = [
        {"id": f"v{i}", "estado": "completado", "reportes_biomecanicos": [{"reporte": _reporte(s)}]} for i, s in enumerate((28, 30, 31, 33))
    ]
    r = cliente(_Admin(_SESION, videos)).get("/sesiones/s1/consistencia")
    assert r.status_code == 200
    d = r.json()
    assert d["gesto"] == "saque" and d["golpes"]["medidos"] == 4
    assert d["separacion_cadera_hombro"]["mediana"] == 30.5 and d["golpe_tipico"] in ("v1", "v2")


def test_una_sesion_de_otro_usuario_es_404(cliente):
    ajena = {**_SESION, "usuario_id": "22222222-2222-4222-8222-222222222222"}
    assert cliente(_Admin(ajena, [])).get("/sesiones/s1/consistencia").status_code == 404


def test_una_sesion_inexistente_es_404(cliente):
    assert cliente(_Admin(None, [])).get("/sesiones/s1/consistencia").status_code == 404


def test_sin_sesion_iniciada_es_401():
    app.dependency_overrides.clear()
    assert TestClient(app).get("/sesiones/s1/consistencia").status_code == 401
