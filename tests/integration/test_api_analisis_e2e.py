"""POST /analisis/{video_id}/procesar de punta a punta — Etapa 4.5, tarea 4.5.4.

Dispara el análisis a través de la API real (no llamando a `procesar_video` directamente
— eso ya lo prueba `tests/integration/test_procesar_video_e2e.py`): sube un clip real de
la Fase B, registra la sesión/video, pega al endpoint protegido con el token correcto y
confirma que terminó escribiendo un reporte real. `TestClient` corre las
`BackgroundTasks` de forma síncrona, así que esta prueba tarda lo mismo que la inferencia
real de MediaPipe (~100 s) — es la prueba que confirma que el cableado nuevo (router,
token, worker) funciona con el stack real, no con falsos.

Corre contra un proyecto Supabase real; se salta sin credenciales configuradas o sin
ningún clip de la Fase B disponible en KINETIQ_DATA_DIR.
"""

from __future__ import annotations

import secrets
import uuid

import pytest

try:
    from app.config import get_supabase_service_role_key, get_supabase_url

    _SUPABASE_URL = get_supabase_url()
    _SUPABASE_SERVICE_ROLE_KEY = get_supabase_service_role_key()
except Exception:  # ConfigError u otra: no hay proyecto Supabase configurado
    _SUPABASE_URL = _SUPABASE_SERVICE_ROLE_KEY = None

try:
    from app.config import get_data_dir

    _CLIP = next(get_data_dir().glob("fase-b/*/*/recortes/*.mov"), None)
except Exception:
    _CLIP = None

pytestmark = [
    pytest.mark.slow,
    pytest.mark.requiere_supabase,
    pytest.mark.skipif(
        not (_SUPABASE_URL and _SUPABASE_SERVICE_ROLE_KEY),
        reason="Falta SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY (backend/.env)",
    ),
    pytest.mark.skipif(
        _CLIP is None, reason="No hay ningún clip de la Fase B en KINETIQ_DATA_DIR para subir"
    ),
]

_TOKEN_ENV_VAR = "KINETIQ_API_TOKEN"


def test_disparar_analisis_por_api_produce_reporte_real(monkeypatch):
    from fastapi.testclient import TestClient
    from supabase import create_client

    token = secrets.token_urlsafe(24)
    monkeypatch.setenv(_TOKEN_ENV_VAR, token)

    from app.main import app

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)

    email = f"kinetiq-api-e2e-{uuid.uuid4().hex[:12]}@example.invalid"
    usuario_id = admin.auth.admin.create_user(
        {"email": email, "password": secrets.token_urlsafe(18), "email_confirm": True}
    ).user.id

    ruta_storage = None
    try:
        atleta = (
            admin.table("atletas")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "nombre": "Atleta de prueba API E2E",
                    "mano_dominante": "izquierda",
                    "nivel": "intermedio",
                }
            )
            .execute()
            .data[0]
        )
        sesion = (
            admin.table("sesiones")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "atleta_id": atleta["id"],
                    "gesto": "saque",
                    "encuadre": "tres_cuartos",
                    "lado_camara": "derecha",
                }
            )
            .execute()
            .data[0]
        )

        # El nombre real del archivo (no solo la carpeta) se conserva a propósito: es
        # la clave con la que procesar_video busca el factor de cámara lenta en
        # catalogo.csv (ver app/procesar_video._factor_de_catalogo). Perderlo acá
        # haría que la prueba corriera con factor=1.0 en vez del real.
        ruta_storage = f"{usuario_id}/{uuid.uuid4().hex}/{_CLIP.name}"
        admin.storage.from_("videos").upload(
            ruta_storage, _CLIP.read_bytes(), file_options={"content-type": "video/quicktime"}
        )

        video = (
            admin.table("videos")
            .insert(
                {
                    "sesion_id": sesion["id"],
                    "usuario_id": usuario_id,
                    "ruta_almacenamiento": ruta_storage,
                }
            )
            .execute()
            .data[0]
        )

        cliente = TestClient(app)

        # Control: sin token, 401, y no dispara nada.
        resp_sin_token = cliente.post(f"/analisis/{video['id']}/procesar")
        assert resp_sin_token.status_code == 401

        resp = cliente.post(
            f"/analisis/{video['id']}/procesar", headers={"x-kinetiq-token": token}
        )
        assert resp.status_code == 202
        assert resp.json() == {"video_id": video["id"], "estado": "encolado"}

        fila_video = (
            admin.table("videos")
            .select("estado, fps_real")
            .eq("id", video["id"])
            .single()
            .execute()
            .data
        )
        assert fila_video["estado"] in ("completado", "parcial")
        assert fila_video["fps_real"] is not None

        reportes = (
            admin.table("reportes_biomecanicos")
            .select("id, cobertura_auditable_pct")
            .eq("video_id", video["id"])
            .execute()
            .data
        )
        assert len(reportes) == 1
        assert reportes[0]["cobertura_auditable_pct"] is not None
    finally:
        if ruta_storage:
            admin.storage.from_("videos").remove([ruta_storage])
        admin.auth.admin.delete_user(usuario_id)
        # versiones_motor no se borra: es una fila real de referencia, no un dato
        # sintético (ver tests/integration/test_procesar_video_e2e.py).
