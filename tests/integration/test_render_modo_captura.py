"""Prueba contra el servicio DESPLEGADO en Render — decisión 020, tarea 4.5.4.

Confirma que el código desplegado es el que combina `sesiones.modo_captura` con el fps del
contenedor: un clip real de 25 fps declarado `camara_lenta_240` (240/25 = 9,6, no cierra)
tiene que quedar `fallido` con `motivo_fallo = 'modo_captura_incompatible'`. Solo el código
nuevo hace eso: la versión anterior buscaba el factor en catalogo.csv (para este clip daba
factor 20) y habría corrido el análisis completo, así que esta prueba distingue "se
desplegó el commit nuevo" de "el servicio responde" — algo que /health no puede hacer
(devuelve solo estado y versión del motor, que no cambió).

También verifica el contrato de seguridad del endpoint real: sin token → 401, token
equivocado → 401.

El token NUNCA se imprime: ni en la salida ni en los mensajes de las aserciones (se
comparan códigos de estado, no cabeceras).

**Solo corre a pedido:** `pytest -m requiere_render` (marcador propio; ver tests/conftest.py).
No entra en la suite normal ni en `-m requiere_supabase`. Corre contra el proyecto Supabase real
y contra Render; se salta sin KINETIQ_API_URL / KINETIQ_API_TOKEN / credenciales de Supabase,
o sin el clip del corpus público. El plan gratuito se duerme tras 15 min sin tráfico: el primer
pedido puede tardar ~1 minuto.
"""

from __future__ import annotations

import secrets
import time
import uuid

import httpx
import pytest

try:
    from app.config import (
        get_kinetiq_api_token,
        get_kinetiq_api_url,
        get_supabase_service_role_key,
        get_supabase_url,
    )

    _API_URL = get_kinetiq_api_url()
    _API_TOKEN = get_kinetiq_api_token()
    _SUPABASE_URL = get_supabase_url()
    _SUPABASE_SERVICE_ROLE_KEY = get_supabase_service_role_key()
except Exception:  # ConfigError u otra: falta alguna variable
    _API_URL = _API_TOKEN = _SUPABASE_URL = _SUPABASE_SERVICE_ROLE_KEY = None

try:
    from app.config import get_data_dir

    _CLIP = get_data_dir() / "fase-a" / "segmentos" / "zverev_saque_lateral_01.mp4"
    if not _CLIP.is_file():
        _CLIP = None
except Exception:
    _CLIP = None

# Marcador propio, SIN `requiere_supabase` a propósito: `pytest -m requiere_supabase` (la suite de
# integración habitual) no la selecciona, y tests/conftest.py la salta en cualquier corrida que no
# pida `-m requiere_render`. Usa Supabase igual (prepara y limpia datos con service_role), pero lo
# que la define es que pega al servicio desplegado.
pytestmark = [
    pytest.mark.slow,
    pytest.mark.requiere_render,
    pytest.mark.skipif(
        not (_API_URL and _API_TOKEN and _SUPABASE_URL and _SUPABASE_SERVICE_ROLE_KEY),
        reason="Falta KINETIQ_API_URL / KINETIQ_API_TOKEN / credenciales de Supabase (backend/.env)",
    ),
    pytest.mark.skipif(
        _CLIP is None, reason="No está fase-a/segmentos/zverev_saque_lateral_01.mp4 en KINETIQ_DATA_DIR"
    ),
]

_ESPERA_MAXIMA_DESPERTAR_S = 150
_ESPERA_MAXIMA_PROCESAMIENTO_S = 360
_PERIODO_SONDEO_S = 5


def _despertar_servicio() -> dict:
    """GET /health con reintentos: el plan gratuito de Render se duerme y tarda en volver."""
    limite = time.monotonic() + _ESPERA_MAXIMA_DESPERTAR_S
    ultimo_error = None
    while time.monotonic() < limite:
        try:
            resp = httpx.get(f"{_API_URL}/health", timeout=40.0)
            if resp.status_code == 200:
                return resp.json()
            ultimo_error = f"HTTP {resp.status_code}"
        except httpx.HTTPError as e:
            ultimo_error = type(e).__name__
        time.sleep(_PERIODO_SONDEO_S)
    pytest.fail(f"El servicio de Render no respondió /health en {_ESPERA_MAXIMA_DESPERTAR_S} s ({ultimo_error})")


def test_render_desplegado_rechaza_modo_captura_incompatible():
    from supabase import create_client

    salud = _despertar_servicio()
    assert salud["estado"] == "ok"

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)

    email = f"kinetiq-render-{uuid.uuid4().hex[:12]}@example.invalid"
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
                    "nombre": "Atleta de prueba Render modo_captura",
                    "mano_dominante": "derecha",
                    "nivel": "avanzado",
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
                    "encuadre": "perfil",
                    "lado_camara": "izquierda",
                    # 25 fps reales declarados como cámara lenta a 240: no cierra.
                    "modo_captura": "camara_lenta_240",
                }
            )
            .execute()
            .data[0]
        )

        ruta_storage = f"{usuario_id}/{uuid.uuid4().hex}/{_CLIP.name}"
        admin.storage.from_("videos").upload(
            ruta_storage, _CLIP.read_bytes(), file_options={"content-type": "video/mp4"}
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
        url_procesar = f"{_API_URL}/analisis/{video['id']}/procesar"

        # Contrato de seguridad del endpoint REAL: sin token y con token equivocado, 401,
        # y el video no se toca.
        assert httpx.post(url_procesar, timeout=60.0).status_code == 401
        assert (
            httpx.post(url_procesar, headers={"x-kinetiq-token": "token-equivocado"}, timeout=60.0).status_code
            == 401
        )
        estado_intacto = (
            admin.table("videos").select("estado").eq("id", video["id"]).single().execute().data["estado"]
        )
        assert estado_intacto == "pendiente"

        resp = httpx.post(url_procesar, headers={"x-kinetiq-token": _API_TOKEN}, timeout=60.0)
        assert resp.status_code == 202, f"POST con token válido devolvió HTTP {resp.status_code}"
        assert resp.json() == {"video_id": video["id"], "estado": "encolado"}

        # El procesamiento es en segundo plano: se sondea la base hasta que el video salga
        # de encolado/procesando (o se agote la espera: ahí el servicio se cortó o colgó).
        limite = time.monotonic() + _ESPERA_MAXIMA_PROCESAMIENTO_S
        fila = None
        while time.monotonic() < limite:
            fila = (
                admin.table("videos")
                .select("estado, motivo_fallo, fps_real, apto_fase_rapida")
                .eq("id", video["id"])
                .single()
                .execute()
                .data
            )
            if fila["estado"] not in ("encolado", "procesando"):
                break
            time.sleep(_PERIODO_SONDEO_S)

        assert fila["estado"] == "fallido", f"estado final = {fila['estado']!r} (se esperaba 'fallido')"
        assert fila["motivo_fallo"] == "modo_captura_incompatible"
        assert fila["fps_real"] is None
        assert fila["apto_fase_rapida"] is None
        assert (
            admin.table("reportes_biomecanicos").select("id").eq("video_id", video["id"]).execute().data == []
        )
    finally:
        if ruta_storage:
            admin.storage.from_("videos").remove([ruta_storage])
        admin.auth.admin.delete_user(usuario_id)
