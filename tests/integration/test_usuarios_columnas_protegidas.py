"""Un usuario autenticado solo edita `nombre`, `rol` y `vista_por_defecto` de su fila de `usuarios`, y no
puede insertarla — tarea 7.4, migración 20261009130000_endurecer_usuarios.sql.

Mismo patrón que ``test_columnas_protegidas.py``: contra un proyecto Supabase REAL, exigiendo el error de
permiso (42501) y no "cualquier error", y confirmando con el cliente admin que la fila no cambió.

**Falla (en rojo) hasta que Valentín aplica la migración.**
"""

from __future__ import annotations

import secrets
import uuid

import pytest

try:
    from app.config import get_supabase_anon_key, get_supabase_service_role_key, get_supabase_url

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

_PERMISO_DENEGADO = "42501"


@pytest.fixture(scope="module")
def datos():
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    email = f"kinetiq-usuarios-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)
    usuario_id = admin.auth.admin.create_user({"email": email, "password": password, "email_confirm": True}).user.id
    try:
        cliente = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        cliente.auth.sign_in_with_password({"email": email, "password": password})
        yield {"admin": admin, "cliente": cliente, "usuario_id": usuario_id, "email": email}
    finally:
        admin.auth.admin.delete_user(usuario_id)


def _fila(datos) -> dict:
    return datos["admin"].table("usuarios").select("*").eq("id", datos["usuario_id"]).single().execute().data


def _exigir_permiso_denegado(operacion) -> None:
    from postgrest.exceptions import APIError

    with pytest.raises(APIError) as info:
        operacion()
    assert info.value.code == _PERMISO_DENEGADO, (
        f"se esperaba permiso denegado (42501) y fue {info.value.code}: {info.value.message}"
    )


def test_el_usuario_edita_nombre_rol_y_vista(datos):
    """Control positivo: lo que el perfil edita sigue funcionando."""
    cambios = {"nombre": "Nombre editado", "rol": "entrenador", "vista_por_defecto": "detallada"}
    resp = datos["cliente"].table("usuarios").update(cambios).eq("id", datos["usuario_id"]).execute()
    assert len(resp.data) == 1
    fila = _fila(datos)
    assert (fila["nombre"], fila["rol"], fila["vista_por_defecto"]) == ("Nombre editado", "entrenador", "detallada")


@pytest.mark.parametrize(
    "patch",
    [
        {"email": "otro@example.invalid"},
        {"creado_en": "2020-01-01T00:00:00Z"},
        {"id": str(uuid.uuid4())},
    ],
    ids=lambda p: next(iter(p)),
)
def test_el_usuario_no_reescribe_email_id_ni_fecha_de_alta(datos, patch):
    antes = _fila(datos)
    _exigir_permiso_denegado(
        lambda: datos["cliente"].table("usuarios").update(patch).eq("id", datos["usuario_id"]).execute()
    )
    assert _fila(datos) == antes


def test_el_usuario_no_inserta_filas_en_usuarios(datos):
    """La fila la crea el trigger de alta; la aplicación no la crea a mano (decisión 018, ajuste 3)."""
    _exigir_permiso_denegado(
        lambda: datos["cliente"]
        .table("usuarios")
        .insert({"id": str(uuid.uuid4()), "email": "nuevo@example.invalid", "nombre": "X", "rol": "jugador"})
        .execute()
    )
