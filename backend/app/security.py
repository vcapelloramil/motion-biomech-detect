"""Seguridad de la API — tarea 7.4, decisión 025.

La identidad de quien llama es el ``sub`` de su JWT de Supabase Auth, **validado contra las claves
públicas del proyecto (JWKS)**: firma (ES256), expiración, emisor y audiencia. **Nunca es un parámetro
que mande el cliente.** El token compartido de la decisión 019 (``X-Kinetiq-Token``) se retiró: no
puede vivir en un navegador y no identificaba a nadie.

Qué NO hace este módulo: no decide si el video es del usuario. Eso lo hace el router
(``routers/analisis.py``), porque la API usa ``service_role`` y ``service_role`` **ignora RLS**: sin
ese chequeo, cualquier usuario autenticado podría procesar el video de otro.

Las claves se leen de ``<SUPABASE_URL>/auth/v1/.well-known/jwks.json`` (público) y se guardan en caché
(``PyJWKClient``); si llega un ``kid`` que no está en la caché, se vuelve a pedir el conjunto una vez
(rotación de claves). Verificado el 7/10/2026 contra el proyecto real: publica una clave ES256.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, Header, HTTPException, status
from supabase import Client, create_client

from app.config import get_supabase_service_role_key, get_supabase_url

# Supabase firma con ES256 (curva P-256). Se fija la lista: aceptar "el algoritmo que diga el token"
# habilita el ataque de confusión de algoritmos (HS256 firmado con la clave pública).
ALGORITMOS_PERMITIDOS = ["ES256"]
AUDIENCIA = "authenticated"


@dataclass(frozen=True)
class UsuarioAutenticado:
    """Quien llama. ``id`` es el ``sub`` del JWT = ``auth.users.id`` = ``videos.usuario_id``."""

    id: str


def get_admin_client() -> Client:
    """Cliente de Supabase con ``service_role``. Lo usa solo el propio servidor para leer
    y escribir resultados — nunca se expone al cliente HTTP (``backend/.env.example``
    explica por qué esta clave nunca va al frontend)."""
    return create_client(get_supabase_url(), get_supabase_service_role_key())


def emisor_esperado() -> str:
    """``iss`` de los tokens de este proyecto: ``<SUPABASE_URL>/auth/v1``."""
    return f"{get_supabase_url().rstrip('/')}/auth/v1"


@lru_cache(maxsize=1)
def _cliente_jwks() -> jwt.PyJWKClient:
    # Un solo cliente por proceso: la caché de claves vive en él. Sin `lifespan` explícito PyJWT usa 300 s.
    return jwt.PyJWKClient(f"{emisor_esperado()}/.well-known/jwks.json", cache_keys=True, timeout=10)


def get_jwks_client() -> jwt.PyJWKClient:
    """Dependency (reemplazable en las pruebas por un cliente con una clave local)."""
    return _cliente_jwks()


def _no_autenticado(detalle: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED, detalle, headers={"WWW-Authenticate": "Bearer"}
    )


def usuario_autenticado(
    authorization: str = Header(default=""),
    jwks: jwt.PyJWKClient = Depends(get_jwks_client),
) -> UsuarioAutenticado:
    """Dependency de FastAPI: 401 si no hay un JWT de Supabase válido en ``Authorization: Bearer``.

    Devuelve la identidad (``sub``). Los mensajes no distinguen *por qué* falló la firma (no se le
    explica a un atacante qué probar); sí distinguen "vencido", que es accionable para el cliente
    (renovar la sesión)."""
    esquema, _, token = authorization.partition(" ")
    if esquema.lower() != "bearer" or not token.strip():
        raise _no_autenticado("Falta el token de sesión (Authorization: Bearer ...).")
    token = token.strip()

    try:
        clave = jwks.get_signing_key_from_jwt(token)
    except jwt.PyJWKClientConnectionError:
        # No es un token malo: no se pudo pedir el JWKS. Que el cliente reintente.
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo verificar la sesión. Reintentá en un momento."
        ) from None
    except jwt.PyJWTError:
        # kid desconocido incluso después de refrescar, o token que ni siquiera se puede leer.
        raise _no_autenticado("Token de sesión inválido.") from None

    try:
        claims = jwt.decode(
            token,
            clave.key,
            algorithms=ALGORITMOS_PERMITIDOS,
            audience=AUDIENCIA,
            issuer=emisor_esperado(),
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
    except jwt.ExpiredSignatureError:
        raise _no_autenticado("La sesión venció. Iniciá sesión de nuevo.") from None
    except jwt.PyJWTError:
        raise _no_autenticado("Token de sesión inválido.") from None

    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub:
        raise _no_autenticado("Token de sesión inválido.")
    return UsuarioAutenticado(id=sub)
