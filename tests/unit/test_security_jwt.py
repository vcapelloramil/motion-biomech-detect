"""Validación del JWT de Supabase por JWKS (tarea 7.4, decisión 025) y CORS acotado. Sin red: una clave
EC P-256 generada acá firma los tokens y un cliente de JWKS falso la publica.

La prueba contra el JWKS real del proyecto (y un token de un usuario real) está en
``tests/integration/test_registro_confirmacion_login.py`` y ``test_api_analisis_e2e.py``.
"""

from __future__ import annotations

import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.security import UsuarioAutenticado, get_jwks_client, usuario_autenticado

_URL = "https://proyecto-de-prueba.supabase.co"
_ISS = f"{_URL}/auth/v1"
_SUB = "11111111-1111-4111-8111-111111111111"


@pytest.fixture(autouse=True)
def _url_del_proyecto(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", _URL)


@pytest.fixture(scope="module")
def clave():
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture(scope="module")
def clave_ajena():
    return ec.generate_private_key(ec.SECP256R1())


class _JWKSFalso:
    """Lo que usa la dependency: ``get_signing_key_from_jwt(token)`` -> objeto con ``.key``."""

    def __init__(self, publica, kid="k1", falla=None):
        self.publica, self.kid, self.falla = publica, kid, falla

    def get_signing_key_from_jwt(self, token):
        if self.falla:
            raise self.falla
        if jwt.get_unverified_header(token).get("kid") != self.kid:
            raise jwt.PyJWKClientError("no hay una clave con ese kid")
        return SimpleNamespace(key=self.publica)


def _token(clave_privada, *, kid="k1", alg="ES256", **claims):
    ahora = int(time.time())
    base = {"sub": _SUB, "aud": "authenticated", "iss": _ISS, "iat": ahora, "exp": ahora + 3600, "role": "authenticated"}
    base.update(claims)
    base = {k: v for k, v in base.items() if v is not None}
    return jwt.encode(base, clave_privada, algorithm=alg, headers={"kid": kid})


def _cliente(jwks) -> TestClient:
    app = FastAPI()

    @app.get("/yo")
    def yo(u: UsuarioAutenticado = Depends(usuario_autenticado)):
        return {"id": u.id}

    app.dependency_overrides[get_jwks_client] = lambda: jwks
    return TestClient(app)


def _get(cliente, token=None, esquema="Bearer"):
    return cliente.get("/yo", headers={"Authorization": f"{esquema} {token}"} if token is not None else {})


def test_un_token_valido_identifica_al_usuario_por_su_sub(clave):
    c = _cliente(_JWKSFalso(clave.public_key()))
    resp = _get(c, _token(clave))
    assert resp.status_code == 200 and resp.json() == {"id": _SUB}


@pytest.mark.parametrize("encabezado", [None, "", "Bearer", "Bearer ", "Basic abc", "token-pelado"])
def test_sin_un_bearer_bien_formado_es_401(clave, encabezado):
    c = _cliente(_JWKSFalso(clave.public_key()))
    headers = {} if encabezado is None else {"Authorization": encabezado}
    resp = c.get("/yo", headers=headers)
    assert resp.status_code == 401 and resp.headers["www-authenticate"] == "Bearer"


def test_un_token_vencido_es_401_y_se_dice(clave):
    c = _cliente(_JWKSFalso(clave.public_key()))
    resp = _get(c, _token(clave, exp=int(time.time()) - 10))
    assert resp.status_code == 401 and "venció" in resp.json()["detail"]


@pytest.mark.parametrize(
    "cambio",
    [
        {"aud": "anon"},  # un token de otra audiencia
        {"aud": None},
        {"iss": "https://otro-proyecto.supabase.co/auth/v1"},  # emitido por otro proyecto
        {"iss": None},
        {"sub": None},
        {"exp": None},
    ],
    ids=["aud-ajena", "sin-aud", "iss-ajeno", "sin-iss", "sin-sub", "sin-exp"],
)
def test_los_claims_obligatorios_se_exigen(clave, cambio):
    c = _cliente(_JWKSFalso(clave.public_key()))
    assert _get(c, _token(clave, **cambio)).status_code == 401


def test_un_token_firmado_con_otra_clave_es_401(clave, clave_ajena):
    c = _cliente(_JWKSFalso(clave.public_key()))
    assert _get(c, _token(clave_ajena)).status_code == 401


def test_un_token_alterado_es_401(clave):
    c = _cliente(_JWKSFalso(clave.public_key()))
    token = _token(clave)
    cabeza, cuerpo, firma = token.split(".")
    # cambia un carácter del cuerpo (los claims): la firma ya no corresponde
    cuerpo_malo = cuerpo[:-2] + ("AA" if not cuerpo.endswith("AA") else "BB")
    assert _get(c, ".".join([cabeza, cuerpo_malo, firma])).status_code == 401


def test_el_algoritmo_lo_decide_el_servidor_y_no_el_token(clave):
    """Confusión de algoritmos: HS256 firmado con un secreto cualquiera, o `alg: none`, no pasan."""
    c = _cliente(_JWKSFalso(clave.public_key()))
    hs = jwt.encode({"sub": _SUB, "aud": "authenticated", "iss": _ISS, "exp": int(time.time()) + 60}, "secreto-que-el-atacante-conoce-0123456789",
                    algorithm="HS256", headers={"kid": "k1"})
    assert _get(c, hs).status_code == 401
    sin_firma = jwt.encode({"sub": _SUB, "aud": "authenticated", "iss": _ISS, "exp": int(time.time()) + 60}, None,
                           algorithm="none", headers={"kid": "k1"})
    assert _get(c, sin_firma).status_code == 401


def test_un_kid_desconocido_es_401(clave):
    c = _cliente(_JWKSFalso(clave.public_key(), kid="k1"))
    assert _get(c, _token(clave, kid="otro")).status_code == 401


def test_si_el_jwks_no_responde_es_503_y_no_un_401(clave):
    """No es culpa del token: que el cliente reintente en vez de cerrarle la sesión."""
    c = _cliente(_JWKSFalso(clave.public_key(), falla=jwt.PyJWKClientConnectionError("sin red")))
    resp = _get(c, _token(clave))
    assert resp.status_code == 503


def test_un_texto_que_no_es_un_jwt_es_401(clave):
    class _Real:  # como PyJWKClient: no puede ni leer el encabezado
        def get_signing_key_from_jwt(self, token):
            jwt.get_unverified_header(token)

    c = _cliente(_Real())
    assert _get(c, "esto.no.es-un-jwt").status_code == 401


# --- CORS -------------------------------------------------------------------------------------------------


def test_cors_sin_valor_no_admite_ningun_origen(monkeypatch):
    from app.config import get_cors_origins

    monkeypatch.delenv("KINETIQ_CORS_ORIGINS", raising=False)
    monkeypatch.setattr("app.config._read_env_var", lambda var: None)
    assert get_cors_origins() == []


def test_cors_lee_la_lista_y_normaliza(monkeypatch):
    from app.config import get_cors_origins

    monkeypatch.setenv("KINETIQ_CORS_ORIGINS", " https://kinetiq.pages.dev/ , http://localhost:5173,,")
    assert get_cors_origins() == ["https://kinetiq.pages.dev", "http://localhost:5173"]


@pytest.mark.parametrize("valor", ["*", "https://*.pages.dev", "https://a.dev,*"])
def test_cors_rechaza_comodines(monkeypatch, valor):
    from app.config import ConfigError, get_cors_origins

    monkeypatch.setenv("KINETIQ_CORS_ORIGINS", valor)
    with pytest.raises(ConfigError):
        get_cors_origins()


def test_la_api_responde_el_preflight_solo_al_origen_permitido(monkeypatch):
    """Se recarga app.main con la variable puesta (el middleware se arma al importar) y se restaura al salir."""
    import importlib

    import app.main as main

    monkeypatch.setenv("KINETIQ_CORS_ORIGINS", "https://kinetiq.pages.dev")
    try:
        main = importlib.reload(main)
        c = TestClient(main.app)
        pedido = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization"}

        ok = c.options("/analisis/x/procesar", headers={"Origin": "https://kinetiq.pages.dev", **pedido})
        assert ok.status_code == 200
        assert ok.headers["access-control-allow-origin"] == "https://kinetiq.pages.dev"
        assert "authorization" in ok.headers["access-control-allow-headers"].lower()
        assert "access-control-allow-credentials" not in ok.headers

        ajeno = c.options("/analisis/x/procesar", headers={"Origin": "https://sitio-malicioso.example", **pedido})
        assert "access-control-allow-origin" not in ajeno.headers
    finally:
        monkeypatch.delenv("KINETIQ_CORS_ORIGINS", raising=False)
        importlib.reload(main)
