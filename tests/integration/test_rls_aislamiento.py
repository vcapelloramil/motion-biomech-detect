"""Prueba de aislamiento de RLS (RNF-07, Capítulo 4) — Etapa 4.5, tarea 4.5.1, decisión 018.

Corre contra un proyecto Supabase REAL, no contra una base local: la seguridad a nivel de
fila es exactamente la garantía del proveedor que hay que verificar contra el proveedor.
Crea dos usuarios de prueba (más datos de ejemplo del usuario A) y los borra al terminar.

Se salta si no están configuradas SUPABASE_URL, SUPABASE_ANON_KEY y
SUPABASE_SERVICE_ROLE_KEY (mismo patrón que las pruebas que dependen de
KINETIQ_DATA_DIR — ver tests/integration/test_corpus_fase_a.py).

Requiere que supabase/migrations/ ya esté aplicada contra ese proyecto.
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
    """Crea un usuario de Auth ya confirmado. Devuelve (id, email, password)."""
    email = f"kinetiq-rls-{etiqueta}-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)
    resultado = admin_client.auth.admin.create_user(
        {"email": email, "password": password, "email_confirm": True}
    )
    return resultado.user.id, email, password


@pytest.fixture(scope="module")
def datos_aislamiento():
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)

    usuario_a_id, email_a, password_a = _crear_usuario_de_prueba(admin, "a")
    usuario_b_id, email_b, password_b = _crear_usuario_de_prueba(admin, "b")
    # No hace falta insertar la fila en usuarios a mano: el trigger de alta (decisión 018,
    # ajuste 3; probado en tests/integration/test_trigger_alta_usuario.py) ya la crea sola al
    # registrarse, con rol 'jugador' por defecto.

    # A partir de acá, TODO lo que puede fallar (inserts, sign-in) va dentro del try: si algo
    # revienta a mitad de camino, el finally tiene que borrar igual los usuarios de Auth ya
    # creados. Así se encontró el bug real (decisión 018): la primera corrida, antes de que
    # service_role tuviera sus GRANT, falló en el primer insert y dejó dos cuentas de prueba
    # huérfanas porque el borrado vivía después del yield, nunca alcanzado.
    version_motor_id = None
    try:
        atleta = (
            admin.table("atletas")
            .insert(
                {
                    "usuario_id": usuario_a_id,
                    "nombre": "Atleta de prueba A",
                    "mano_dominante": "derecha",
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
                    "usuario_id": usuario_a_id,
                    "atleta_id": atleta["id"],
                    "gesto": "saque",
                    "encuadre": "perfil",
                    "lado_camara": "izquierda",
                }
            )
            .execute()
            .data[0]
        )

        video = (
            admin.table("videos")
            .insert(
                {
                    "sesion_id": sesion["id"],
                    "usuario_id": usuario_a_id,
                    "ruta_almacenamiento": "privado/no-existe.mp4",
                    "estado": "completado",
                }
            )
            .execute()
            .data[0]
        )

        version_motor = (
            admin.table("versiones_motor")
            .insert({"version_motor": "test-rls", "backend_pose": "fake"})
            .execute()
            .data[0]
        )
        version_motor_id = version_motor["id"]

        reporte = (
            admin.table("reportes_biomecanicos")
            .insert({"video_id": video["id"], "version_motor_id": version_motor_id})
            .execute()
            .data[0]
        )

        metrica = (
            admin.table("metricas")
            .insert(
                {
                    "reporte_id": reporte["id"],
                    "segmento": "pelvis",
                    "tipo": "velocidad_pico",
                    "valor": 123.4,
                    "unidad": "grados/s",
                    "auditable": True,
                }
            )
            .execute()
            .data[0]
        )

        alerta = (
            admin.table("alertas")
            .insert(
                {
                    "reporte_id": reporte["id"],
                    "codigo": "TEST-001",
                    "severidad": "alerta_de_carga",
                    "mensaje_usuario": "Alerta de prueba, no real.",
                }
            )
            .execute()
            .data[0]
        )

        reporte_sesion = (
            admin.table("reportes_sesion")
            .insert({"sesion_id": sesion["id"], "estado_puntaje": "sin_referencia"})
            .execute()
            .data[0]
        )

        cliente_a = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        cliente_a.auth.sign_in_with_password({"email": email_a, "password": password_a})

        cliente_b = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        cliente_b.auth.sign_in_with_password({"email": email_b, "password": password_b})

        cliente_anonimo = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)

        datos = {
            "admin": admin,
            "cliente_a": cliente_a,
            "cliente_b": cliente_b,
            "cliente_anonimo": cliente_anonimo,
            "usuario_a_id": usuario_a_id,
            "atleta_id": atleta["id"],
            "sesion_id": sesion["id"],
            "video_id": video["id"],
            "reporte_id": reporte["id"],
            "metrica_id": metrica["id"],
            "alerta_id": alerta["id"],
            "reporte_sesion_id": reporte_sesion["id"],
            "version_motor_id": version_motor_id,
        }

        yield datos
    finally:
        # Borrar el usuario de Auth se lleva en cascada usuarios, atletas, sesiones, videos,
        # reportes_biomecanicos, metricas, alertas y reportes_sesion (ON DELETE CASCADE). Tiene
        # que pasar ANTES de borrar versiones_motor: esa FK no tiene cascada (es referencia
        # global, no un dato de usuario) y fallaría si todavía hay un reporte apuntándola.
        admin.auth.admin.delete_user(usuario_a_id)
        admin.auth.admin.delete_user(usuario_b_id)
        if version_motor_id:
            admin.table("versiones_motor").delete().eq("id", version_motor_id).execute()


def _sin_filas_visibles(cliente, tabla: str, columna: str, valor) -> None:
    try:
        resp = cliente.table(tabla).select("*").eq(columna, valor).execute()
    except Exception:
        # Sin GRANT (p. ej. el rol anon no tiene ninguno): también es aislamiento correcto,
        # el permiso se niega antes de que RLS llegue a evaluarse.
        return
    assert resp.data == [], f"{tabla}: se vieron filas ajenas con {columna}={valor}: {resp.data}"


def _sin_filas_modificadas(cliente, tabla: str, columna: str, valor, patch: dict | None = None) -> None:
    try:
        consulta = cliente.table(tabla)
        resp = (
            consulta.update(patch).eq(columna, valor).execute()
            if patch is not None
            else consulta.delete().eq(columna, valor).execute()
        )
    except Exception:
        return
    accion = "update" if patch is not None else "delete"
    assert resp.data == [], f"{tabla}: {accion} afectó filas ajenas con {columna}={valor}"


# Tablas con datos propios del usuario A (no incluye versiones_motor: esa es referencia
# global, visible a propósito para cualquier usuario autenticado).
_TABLAS_DATOS_DE_A = [
    ("usuarios", "id", "usuario_a_id"),
    ("atletas", "id", "atleta_id"),
    ("sesiones", "id", "sesion_id"),
    ("videos", "id", "video_id"),
    ("reportes_biomecanicos", "id", "reporte_id"),
    ("metricas", "id", "metrica_id"),
    ("alertas", "id", "alerta_id"),
    ("reportes_sesion", "id", "reporte_sesion_id"),
]

_TODAS_LAS_TABLAS = _TABLAS_DATOS_DE_A + [("versiones_motor", "id", "version_motor_id")]

_TABLAS_ESCRIBIBLES = [
    ("sesiones", "id", "sesion_id", {"gesto": "drive"}),
    ("videos", "id", "video_id", {"estado": "fallido"}),
]


def test_usuario_a_lee_su_propia_sesion(datos_aislamiento):
    """Control positivo: si esto falla, las pruebas de abajo podrían estar pasando porque el
    cliente de prueba está mal armado (p. ej. el sign-in no funcionó), no porque RLS
    funcione. Sin este control, un bug en el fixture se leería como "aislamiento correcto"."""
    resp = (
        datos_aislamiento["cliente_a"]
        .table("sesiones")
        .select("id")
        .eq("id", datos_aislamiento["sesion_id"])
        .execute()
    )
    assert len(resp.data) == 1


@pytest.mark.parametrize("tabla,columna,clave", _TABLAS_DATOS_DE_A)
def test_usuario_b_no_lee_datos_de_usuario_a(datos_aislamiento, tabla, columna, clave):
    _sin_filas_visibles(datos_aislamiento["cliente_b"], tabla, columna, datos_aislamiento[clave])


@pytest.mark.parametrize("tabla,columna,clave", _TODAS_LAS_TABLAS)
def test_anonimo_no_lee_nada(datos_aislamiento, tabla, columna, clave):
    _sin_filas_visibles(datos_aislamiento["cliente_anonimo"], tabla, columna, datos_aislamiento[clave])


@pytest.mark.parametrize("tabla,columna,clave,patch", _TABLAS_ESCRIBIBLES)
def test_usuario_b_no_modifica_datos_de_usuario_a(datos_aislamiento, tabla, columna, clave, patch):
    _sin_filas_modificadas(datos_aislamiento["cliente_b"], tabla, columna, datos_aislamiento[clave], patch=patch)


@pytest.mark.parametrize("tabla,columna,clave,_patch", _TABLAS_ESCRIBIBLES)
def test_usuario_b_no_borra_datos_de_usuario_a(datos_aislamiento, tabla, columna, clave, _patch):
    _sin_filas_modificadas(datos_aislamiento["cliente_b"], tabla, columna, datos_aislamiento[clave])


def test_sesion_de_a_sigue_intacta_tras_los_intentos_de_b(datos_aislamiento):
    """Confirmación final con el cliente admin (bypasea RLS): ni el intento de update ni el
    de delete de las pruebas de arriba tuvieron efecto real sobre el dato de A."""
    fila = (
        datos_aislamiento["admin"]
        .table("sesiones")
        .select("id, gesto")
        .eq("id", datos_aislamiento["sesion_id"])
        .execute()
        .data
    )
    assert len(fila) == 1, "la sesión de A desapareció: algún intento de borrado tuvo efecto"
    assert fila[0]["gesto"] == "saque", "la sesión de A cambió: algún intento de update tuvo efecto"


def test_usuario_b_no_ve_resumen_de_sesion_de_a(datos_aislamiento):
    """La vista sesiones_resumen se creó con security_invoker = true a propósito (si no,
    ignoraría la RLS de quien consulta). Esta prueba es la que detectaría el olvido."""
    _sin_filas_visibles(
        datos_aislamiento["cliente_b"],
        "sesiones_resumen",
        "sesion_id",
        datos_aislamiento["sesion_id"],
    )
