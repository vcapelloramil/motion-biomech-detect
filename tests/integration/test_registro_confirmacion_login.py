"""Un usuario nuevo se registra, confirma su correo y entra — decisión 027 (y 025 para el token).

Corre contra un proyecto Supabase REAL. Prueba la LÓGICA de la confirmación obligatoria:

1. El registro crea al usuario **sin confirmar**.
2. Sin confirmar, **no puede entrar** (si esto falla, la confirmación por correo está desactivada en el
   proyecto: Authentication -> Sign In / Providers -> Email -> "Confirm email").
3. Con el enlace de confirmación, **confirma y entra**.
4. El token que recibe se valida **contra las claves públicas (JWKS)** del proyecto, que es lo que va a
   hacer la API (decisión 025): firma, expiración, emisor y audiencia.

**NO prueba la entrega del correo.** El enlace se genera por la API de administración
(``generate_link``), que no envía nada: así la prueba no gasta la cuota de envío ni ensucia la reputación
del remitente con direcciones inexistentes. La entrega real (que llegue, dónde, con qué remitente) se
comprueba a mano una vez, ver la decisión 027.

Se salta si no están configuradas SUPABASE_URL, SUPABASE_ANON_KEY y SUPABASE_SERVICE_ROLE_KEY.
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


def test_usuario_nuevo_se_registra_confirma_y_entra():
    import httpx
    import jwt  # PyJWT
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    email = f"kinetiq-registro-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)

    # 1. Registro: crea el usuario sin confirmar y devuelve el enlace (sin enviar ningún correo).
    registro = admin.auth.admin.generate_link({"type": "signup", "email": email, "password": password})
    usuario_id = registro.user.id
    try:
        assert registro.user.email_confirmed_at is None, "el usuario no debería nacer confirmado"
        enlace = registro.properties.action_link

        # El trigger de alta (decisión 018) ya creó su fila en usuarios, con rol 'jugador' por defecto.
        fila = admin.table("usuarios").select("id, rol").eq("id", usuario_id).single().execute().data
        assert fila["rol"] == "jugador"

        # 2. Sin confirmar, no entra.
        cliente = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        with pytest.raises(Exception) as sin_confirmar:
            cliente.auth.sign_in_with_password({"email": email, "password": password})
        assert "confirm" in str(sin_confirmar.value).lower(), (
            f"se esperaba 'correo sin confirmar' y fue: {sin_confirmar.value}"
        )

        # 3. Confirma con el enlace. No se sigue la redirección (apunta al Site URL del proyecto, que puede
        #    no existir todavía): alcanza con que Supabase responda una redirección con la sesión.
        resp = httpx.get(enlace, follow_redirects=False, timeout=30)
        assert resp.status_code in (302, 303), f"el enlace no confirmó: HTTP {resp.status_code} {resp.text[:200]}"
        assert "access_token=" in resp.headers["location"], "la redirección no trae la sesión"
        confirmado = admin.auth.admin.get_user_by_id(usuario_id).user
        assert confirmado.email_confirmed_at is not None

        # 4. Ahora entra.
        sesion = cliente.auth.sign_in_with_password({"email": email, "password": password}).session
        assert sesion and sesion.access_token

        # El usuario ve su propia fila (RLS) y ninguna ajena.
        propias = cliente.table("usuarios").select("id").execute().data
        assert [f["id"] for f in propias] == [usuario_id]

        # 5. El token se valida contra el JWKS público del proyecto (lo que hará la API, decisión 025).
        jwks_url = f"{_SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        clave = jwt.PyJWKClient(jwks_url).get_signing_key_from_jwt(sesion.access_token)
        cabecera = jwt.get_unverified_header(sesion.access_token)
        datos = jwt.decode(
            sesion.access_token,
            clave.key,
            algorithms=[cabecera["alg"]],
            audience="authenticated",
            issuer=f"{_SUPABASE_URL.rstrip('/')}/auth/v1",
        )
        assert cabecera["alg"] in ("ES256", "RS256"), f"se esperaba una firma asimétrica y es {cabecera['alg']}"
        assert datos["sub"] == usuario_id and datos["role"] == "authenticated"
    finally:
        admin.auth.admin.delete_user(usuario_id)


def test_un_token_alterado_no_pasa_la_validacion_por_jwks():
    """El otro lado de la prueba anterior: un token que no firmó el proyecto se rechaza."""
    import jwt  # PyJWT
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    email = f"kinetiq-token-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)
    usuario_id = admin.auth.admin.create_user({"email": email, "password": password, "email_confirm": True}).user.id
    try:
        cliente = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        token = cliente.auth.sign_in_with_password({"email": email, "password": password}).session.access_token
        cabecera, cuerpo, firma = token.split(".")
        # Misma cabecera y firma, cuerpo cambiado (otro "sub"): la firma ya no corresponde.
        import base64
        import json

        datos = json.loads(base64.urlsafe_b64decode(cuerpo + "=" * (-len(cuerpo) % 4)))
        datos["sub"] = str(uuid.uuid4())
        cuerpo_falso = base64.urlsafe_b64encode(json.dumps(datos).encode()).rstrip(b"=").decode()
        falso = f"{cabecera}.{cuerpo_falso}.{firma}"

        jwks_url = f"{_SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        clave = jwt.PyJWKClient(jwks_url).get_signing_key_from_jwt(falso)
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(falso, clave.key, algorithms=["ES256", "RS256"], audience="authenticated")
    finally:
        admin.auth.admin.delete_user(usuario_id)
