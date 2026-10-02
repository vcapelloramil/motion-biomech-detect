"""GET /health — operación pública del apartado 4.2.5. Sin red: no depende de Supabase."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.engine.version import __version__ as VERSION_MOTOR
from app.main import app


def test_salud_responde_estado_y_version_sin_token():
    cliente = TestClient(app)
    resp = cliente.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"estado": "ok", "version_motor": VERSION_MOTOR}
