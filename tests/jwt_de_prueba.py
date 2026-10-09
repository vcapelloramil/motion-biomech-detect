"""Helper de las pruebas de integración: el JWT de un usuario de prueba REAL.

Desde la tarea 7.4 (decisión 025) la API exige el token de sesión de Supabase; las pruebas ya no tienen
un token compartido al que recurrir. El usuario lo crea la propia prueba con ``service_role`` (ya confirmado)
y acá se le inicia sesión con la clave pública, exactamente como lo haría el frontend.
"""

from __future__ import annotations


def token_de_usuario(url: str, anon_key: str, email: str, password: str) -> str:
    from supabase import create_client

    cliente = create_client(url, anon_key)
    sesion = cliente.auth.sign_in_with_password({"email": email, "password": password}).session
    return sesion.access_token


def encabezado(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
