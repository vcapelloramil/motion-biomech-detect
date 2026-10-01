"""Prueba del trigger de alta de usuario — Etapa 4.5, tarea 4.5.1, decisión 018 (ajuste 3).

Verifica que crear un usuario en auth.users dispare la creación automática de su fila en
public.usuarios (trigger al_registrarse / manejar_alta_usuario,
supabase/migrations/20261001090000_esquema_inicial.sql), con rol 'jugador' por defecto
salvo que los metadatos del registro digan otra cosa, y que un rol fuera del vocabulario
cerrado haga fallar el alta completa en vez de guardar un dato inconsistente.

Corre contra un proyecto Supabase real; se salta sin credenciales configuradas.
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

pytestmark = [
    pytest.mark.slow,
    pytest.mark.requiere_supabase,
    pytest.mark.skipif(
        not (_SUPABASE_URL and _SUPABASE_SERVICE_ROLE_KEY),
        reason="Falta SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY (backend/.env)",
    ),
]


@pytest.fixture
def admin():
    from supabase import create_client

    return create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)


def _email_de_prueba() -> str:
    return f"kinetiq-trigger-{uuid.uuid4().hex[:12]}@example.invalid"


def test_trigger_crea_fila_con_rol_jugador_por_defecto(admin):
    email = _email_de_prueba()
    usuario_id = admin.auth.admin.create_user(
        {"email": email, "password": secrets.token_urlsafe(18), "email_confirm": True}
    ).user.id
    try:
        fila = (
            admin.table("usuarios").select("id, email, rol").eq("id", usuario_id).execute().data
        )
        assert len(fila) == 1, "el trigger no creó la fila en usuarios"
        assert fila[0]["email"] == email
        assert fila[0]["rol"] == "jugador"
    finally:
        admin.auth.admin.delete_user(usuario_id)


def test_trigger_respeta_rol_y_nombre_de_los_metadatos_de_registro(admin):
    email = _email_de_prueba()
    usuario_id = admin.auth.admin.create_user(
        {
            "email": email,
            "password": secrets.token_urlsafe(18),
            "email_confirm": True,
            "user_metadata": {"rol": "entrenador", "nombre": "Entrenador de prueba"},
        }
    ).user.id
    try:
        fila = admin.table("usuarios").select("rol, nombre").eq("id", usuario_id).execute().data[0]
        assert fila["rol"] == "entrenador"
        assert fila["nombre"] == "Entrenador de prueba"
    finally:
        admin.auth.admin.delete_user(usuario_id)


def test_trigger_rechaza_rol_invalido(admin):
    """Si los metadatos traen un rol fuera del vocabulario cerrado, la restricción CHECK de
    usuarios.rol lo rechaza DENTRO de la misma transacción que el INSERT en auth.users: el
    alta completa falla. No queda fila en usuarios para ese email (no se verifica el lado de
    auth.users acá: la forma exacta de list_users() varía entre versiones del cliente, y
    el lado que a este esquema le importa es que no quede un perfil con un rol inválido)."""
    email = _email_de_prueba()
    with pytest.raises(Exception):
        admin.auth.admin.create_user(
            {
                "email": email,
                "password": secrets.token_urlsafe(18),
                "email_confirm": True,
                "user_metadata": {"rol": "administrador"},
            }
        )
    fila = admin.table("usuarios").select("id").eq("email", email).execute().data
    assert fila == [], "quedó un perfil en usuarios pese al rol inválido"
