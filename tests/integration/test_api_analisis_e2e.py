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

    # Solo recortes a 240 fps (cámara lenta real): estas pruebas declaran `camara_lenta_240`, y desde que
    # existe el recorte de 60 fps en modo normal ("el primer .mov") ya no garantiza un clip de cámara lenta.
    _CLIP = next(get_data_dir().glob("fase-b/*/*/recortes/*_240_*.mov"), None)
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

def test_disparar_analisis_por_api_produce_reporte_real():
    from fastapi.testclient import TestClient
    from supabase import create_client

    from app.config import get_supabase_anon_key
    from app.main import app
    from jwt_de_prueba import encabezado, token_de_usuario

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)

    email = f"kinetiq-api-e2e-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)
    usuario_id = admin.auth.admin.create_user({"email": email, "password": password, "email_confirm": True}).user.id
    # Un segundo usuario, para comprobar que no puede procesar el video del primero (decisión 025).
    email_ajeno = f"kinetiq-api-e2e-ajeno-{uuid.uuid4().hex[:12]}@example.invalid"
    password_ajeno = secrets.token_urlsafe(18)
    ajeno_id = admin.auth.admin.create_user(
        {"email": email_ajeno, "password": password_ajeno, "email_confirm": True}
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
                    # Los clips de la Fase B son capturas Apple en cámara lenta (el
                    # contenedor declara 30 fps, la captura real es 240 — decisión 020).
                    "modo_captura": "camara_lenta_240",
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
        anon = get_supabase_anon_key()
        token = token_de_usuario(_SUPABASE_URL, anon, email, password)
        token_ajeno = token_de_usuario(_SUPABASE_URL, anon, email_ajeno, password_ajeno)

        def _estado() -> str:
            return admin.table("videos").select("estado").eq("id", video["id"]).single().execute().data["estado"]

        # Controles: sin token o con uno inválido, 401; con el token de OTRO usuario, 404 (igual que si el
        # video no existiera). Ninguno dispara nada.
        assert cliente.post(f"/analisis/{video['id']}/procesar").status_code == 401
        assert (
            cliente.post(f"/analisis/{video['id']}/procesar", headers=encabezado(token + "x")).status_code == 401
        )
        resp_ajeno = cliente.post(f"/analisis/{video['id']}/procesar", headers=encabezado(token_ajeno))
        assert resp_ajeno.status_code == 404
        # Mismo código y misma forma que un video que no existe: no se revela qué ids hay.
        inexistente = cliente.post(f"/analisis/{uuid.uuid4()}/procesar", headers=encabezado(token_ajeno))
        assert inexistente.status_code == 404
        assert resp_ajeno.json()["detail"].startswith("No existe el video")
        assert _estado() == "pendiente"

        resp = cliente.post(f"/analisis/{video['id']}/procesar", headers=encabezado(token))
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
        admin.auth.admin.delete_user(ajeno_id)
        # versiones_motor no se borra: es una fila real de referencia, no un dato
        # sintético (ver tests/integration/test_procesar_video_e2e.py).
