"""Aislamiento de Storage (RNF-07 aplicado a objetos, no solo a filas) — Etapa 4.5, tarea 4.5.2.

Mismo principio que tests/integration/test_rls_aislamiento.py, aplicado a storage.objects
en vez de a las tablas de public/: un usuario autenticado no puede leer ni subir archivos
dentro del prefijo de ruta "<usuario_id>/..." de otro usuario en el bucket "videos"
(supabase/migrations/20261001090300_bucket_videos.sql), y un cliente sin sesión tampoco.

Corre contra un proyecto Supabase real; se salta sin credenciales configuradas.
"""

from __future__ import annotations

import secrets
import uuid

import pytest

try:
    from app.config import (
        get_supabase_anon_key,
        get_supabase_service_role_key,
        get_supabase_url,
    )

    _SUPABASE_URL = get_supabase_url()
    _SUPABASE_ANON_KEY = get_supabase_anon_key()
    _SUPABASE_SERVICE_ROLE_KEY = get_supabase_service_role_key()
except Exception:  # ConfigError u otra: no hay proyecto Supabase configurado
    _SUPABASE_URL = _SUPABASE_ANON_KEY = _SUPABASE_SERVICE_ROLE_KEY = None

pytestmark = [
    pytest.mark.slow,
    pytest.mark.requiere_supabase,
    pytest.mark.skipif(
        not (_SUPABASE_URL and _SUPABASE_ANON_KEY and _SUPABASE_SERVICE_ROLE_KEY),
        reason="Falta SUPABASE_URL / SUPABASE_ANON_KEY / SUPABASE_SERVICE_ROLE_KEY (backend/.env)",
    ),
]


def _crear_usuario_de_prueba(admin_client, etiqueta: str) -> tuple[str, str, str]:
    email = f"kinetiq-storage-{etiqueta}-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)
    resultado = admin_client.auth.admin.create_user(
        {"email": email, "password": password, "email_confirm": True}
    )
    return resultado.user.id, email, password


@pytest.fixture
def datos_aislamiento_storage():
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    usuario_a_id, email_a, password_a = _crear_usuario_de_prueba(admin, "a")
    usuario_b_id, email_b, password_b = _crear_usuario_de_prueba(admin, "b")

    # Todo lo que puede fallar va después de crear los usuarios, dentro del try: mismo motivo que
    # en test_rls_aislamiento.py (decisión 018) — si algo revienta a mitad de camino, el finally
    # tiene que borrar igual los usuarios de Auth ya creados.
    ruta_de_a = None
    try:
        cliente_a = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        cliente_a.auth.sign_in_with_password({"email": email_a, "password": password_a})

        cliente_b = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        cliente_b.auth.sign_in_with_password({"email": email_b, "password": password_b})

        ruta_de_a = f"{usuario_a_id}/test-storage-aislamiento/{uuid.uuid4().hex}.mp4"
        contenido = b"contenido de prueba para el aislamiento de storage, no es un video real"
        cliente_a.storage.from_("videos").upload(
            ruta_de_a, contenido, file_options={"content-type": "video/mp4"}
        )

        yield {
            "admin": admin,
            "cliente_a": cliente_a,
            "cliente_b": cliente_b,
            "usuario_a_id": usuario_a_id,
            "ruta_de_a": ruta_de_a,
            "contenido": contenido,
        }
    finally:
        if ruta_de_a:
            admin.storage.from_("videos").remove([ruta_de_a])
        admin.auth.admin.delete_user(usuario_a_id)
        admin.auth.admin.delete_user(usuario_b_id)


def test_usuario_a_lee_su_propio_archivo(datos_aislamiento_storage):
    """Control positivo, mismo motivo que en test_rls_aislamiento.py: si esto falla, las
    pruebas de abajo podrían estar "pasando" solo porque el cliente de prueba está mal
    armado (p. ej. el sign-in no funcionó), no porque el aislamiento funcione de verdad."""
    datos = datos_aislamiento_storage
    assert datos["cliente_a"].storage.from_("videos").download(datos["ruta_de_a"]) == datos["contenido"]


def test_usuario_b_no_lee_archivo_de_usuario_a(datos_aislamiento_storage):
    datos = datos_aislamiento_storage
    with pytest.raises(Exception):
        datos["cliente_b"].storage.from_("videos").download(datos["ruta_de_a"])


def test_anonimo_no_lee_archivo_de_usuario_a(datos_aislamiento_storage):
    from supabase import create_client

    datos = datos_aislamiento_storage
    cliente_anonimo = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
    with pytest.raises(Exception):
        cliente_anonimo.storage.from_("videos").download(datos["ruta_de_a"])


def test_usuario_b_no_sube_archivo_en_carpeta_de_usuario_a(datos_aislamiento_storage):
    datos = datos_aislamiento_storage
    ruta_intrusa = f"{datos['usuario_a_id']}/intento-de-b-{uuid.uuid4().hex}.mp4"

    with pytest.raises(Exception):
        datos["cliente_b"].storage.from_("videos").upload(
            ruta_intrusa, b"contenido intruso, no deberia quedar subido", file_options={"content-type": "video/mp4"}
        )

    # Por si el upload "tuviera éxito" del lado del cliente de alguna forma rara: confirmar con
    # el admin que no quedó el objeto, y limpiarlo si por algún motivo quedó.
    try:
        datos["admin"].storage.from_("videos").download(ruta_intrusa)
        quedo = True
    except Exception:
        quedo = False
    if quedo:
        datos["admin"].storage.from_("videos").remove([ruta_intrusa])
    assert not quedo, "el intento de subida de B dejó un objeto en la carpeta de A"
