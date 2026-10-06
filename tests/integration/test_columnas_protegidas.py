"""Un usuario autenticado no puede escribir las columnas que escribe el motor — decisión 022,
paso (a), migración 20261006130000_columnas_protegidas_videos_sesiones.sql.

Corre contra un proyecto Supabase REAL (mismo patrón que test_rls_aislamiento.py): los permisos
por columna son una garantía del proveedor y hay que verificarlos contra el proveedor. Crea un
usuario de prueba con su atleta, su sesión y su video, y lo borra al terminar.

Cada prueba negativa exige el error de permiso (SQLSTATE 42501) y NO "cualquier error": un nombre
de columna mal escrito o una restricción CHECK también fallarían, y se leerían como "protegido".
Después de cada intento, el cliente admin (bypasea RLS y permisos) confirma que la fila no cambió.

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

_PERMISO_DENEGADO = "42501"


@pytest.fixture(scope="module")
def datos():
    from supabase import create_client

    admin = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    email = f"kinetiq-colprot-{uuid.uuid4().hex[:12]}@example.invalid"
    password = secrets.token_urlsafe(18)
    usuario_id = admin.auth.admin.create_user(
        {"email": email, "password": password, "email_confirm": True}
    ).user.id
    # Todo lo que puede fallar va dentro del try: el finally tiene que borrar igual el usuario de
    # Auth (se lleva en cascada atletas, sesiones y videos). Mismo cuidado que test_rls_aislamiento.
    try:
        atleta = (
            admin.table("atletas")
            .insert(
                {
                    "usuario_id": usuario_id,
                    "nombre": "Atleta de prueba",
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
                    "usuario_id": usuario_id,
                    "atleta_id": atleta["id"],
                    "gesto": "saque",
                    "encuadre": "perfil",
                    "lado_camara": "izquierda",
                    "modo_captura": "normal",
                }
            )
            .execute()
            .data[0]
        )
        # Estado 'pendiente' (default): un golpe recién dado de alta, todavía sin procesar.
        video = (
            admin.table("videos")
            .insert(
                {
                    "sesion_id": sesion["id"],
                    "usuario_id": usuario_id,
                    "ruta_almacenamiento": "privado/no-existe.mp4",
                }
            )
            .execute()
            .data[0]
        )

        cliente = create_client(_SUPABASE_URL, _SUPABASE_ANON_KEY)
        cliente.auth.sign_in_with_password({"email": email, "password": password})

        yield {
            "admin": admin,
            "cliente": cliente,
            "usuario_id": usuario_id,
            "atleta_id": atleta["id"],
            "sesion_id": sesion["id"],
            "video_id": video["id"],
        }
    finally:
        admin.auth.admin.delete_user(usuario_id)


def _exigir_permiso_denegado(operacion) -> None:
    from postgrest.exceptions import APIError

    with pytest.raises(APIError) as info:
        operacion()
    assert info.value.code == _PERMISO_DENEGADO, (
        f"se esperaba permiso denegado (42501) y fue {info.value.code}: {info.value.message}"
    )


def _fila(datos, tabla: str, id_: str) -> dict:
    return datos["admin"].table(tabla).select("*").eq("id", id_).single().execute().data


# --- Controles positivos: sin esto, un cliente mal armado se leería como "protegido" ---------------


def test_usuario_inserta_su_video_con_las_columnas_permitidas(datos):
    """Es el alta real de un golpe. El estado sale del default ('pendiente'), no del usuario."""
    resp = (
        datos["cliente"]
        .table("videos")
        .insert(
            {
                "sesion_id": datos["sesion_id"],
                "usuario_id": datos["usuario_id"],
                "ruta_almacenamiento": f"{datos['usuario_id']}/{uuid.uuid4().hex}/golpe.mov",
            }
        )
        .execute()
    )
    assert len(resp.data) == 1
    assert resp.data[0]["estado"] == "pendiente"


def test_usuario_edita_lo_que_declara_de_su_sesion(datos):
    """Corregir la declaración de la sesión (incluido modo_captura: es el flujo del reintento,
    decisión 020/022) tiene que seguir funcionando."""
    resp = (
        datos["cliente"]
        .table("sesiones")
        .update({"gesto": "drive", "modo_captura": "camara_lenta_120"})
        .eq("id", datos["sesion_id"])
        .execute()
    )
    assert len(resp.data) == 1
    fila = _fila(datos, "sesiones", datos["sesion_id"])
    assert (fila["gesto"], fila["modo_captura"]) == ("drive", "camara_lenta_120")


# --- Lo que el usuario NO puede escribir ---------------------------------------------------------

_COLUMNAS_DEL_MOTOR_EN_VIDEOS = [
    {"estado": "completado"},
    {"estado": "fallido"},
    {"estado": "encolado"},
    {"motivo_fallo": "modo_captura_incompatible"},
    {"fps_real": 240},
    {"apto_fase_rapida": True},
    {"total_fotogramas": 1},
    {"duracion_s": 1},
    {"resolucion": "1x1"},
    {"ruta_miniatura": "x"},
    {"ruta_fotograma_pelvis": "x"},
    {"eliminado_en": "2026-01-01T00:00:00Z"},
]


@pytest.mark.parametrize("patch", _COLUMNAS_DEL_MOTOR_EN_VIDEOS, ids=lambda p: next(iter(p)) + "=" + str(next(iter(p.values()))))
def test_usuario_no_actualiza_columnas_del_motor_en_videos(datos, patch):
    antes = _fila(datos, "videos", datos["video_id"])
    _exigir_permiso_denegado(
        lambda: datos["cliente"].table("videos").update(patch).eq("id", datos["video_id"]).execute()
    )
    assert _fila(datos, "videos", datos["video_id"]) == antes


def test_usuario_no_cambia_el_estado_de_su_video(datos):
    """La prueba que pidió la decisión 022, explícita: estado no se puede cambiar, ni a un valor
    válido del vocabulario cerrado. Sin esto, la máquina de estados del reintento no vale nada."""
    for estado in ("pendiente", "encolado", "procesando", "completado", "parcial", "fallido"):
        _exigir_permiso_denegado(
            lambda e=estado: datos["cliente"]
            .table("videos")
            .update({"estado": e})
            .eq("id", datos["video_id"])
            .execute()
        )
    assert _fila(datos, "videos", datos["video_id"])["estado"] == "pendiente"


def test_usuario_no_reubica_ni_reescribe_su_video(datos):
    """Hoy ninguna columna de videos es actualizable por el usuario (ver la migración)."""
    for patch in ({"ruta_almacenamiento": "otra/ruta.mp4"}, {"sesion_id": datos["sesion_id"]}):
        _exigir_permiso_denegado(
            lambda p=patch: datos["cliente"].table("videos").update(p).eq("id", datos["video_id"]).execute()
        )


_COLUMNAS_DEL_MOTOR_AL_INSERTAR = [
    {"estado": "completado"},
    {"estado": "fallido"},
    {"motivo_fallo": "modo_captura_incompatible"},
    {"fps_real": 240},
    {"apto_fase_rapida": True},
]


@pytest.mark.parametrize("extra", _COLUMNAS_DEL_MOTOR_AL_INSERTAR, ids=lambda p: next(iter(p)) + "=" + str(next(iter(p.values()))))
def test_usuario_no_inserta_un_video_con_columnas_del_motor(datos, extra):
    """Dar de alta un golpe ya 'completado' (o 'fallido') es la misma falsificación que
    actualizarlo después."""
    fila = {
        "sesion_id": datos["sesion_id"],
        "usuario_id": datos["usuario_id"],
        "ruta_almacenamiento": f"{datos['usuario_id']}/{uuid.uuid4().hex}/falso.mov",
        **extra,
    }
    _exigir_permiso_denegado(lambda: datos["cliente"].table("videos").insert(fila).execute())


@pytest.mark.parametrize(
    "patch",
    [{"creado_en": "2020-01-01T00:00:00Z"}, {"usuario_id": "00000000-0000-0000-0000-000000000000"}],
    ids=["creado_en", "usuario_id"],
)
def test_usuario_no_reescribe_columnas_fijas_de_su_sesion(datos, patch):
    antes = _fila(datos, "sesiones", datos["sesion_id"])
    _exigir_permiso_denegado(
        lambda: datos["cliente"].table("sesiones").update(patch).eq("id", datos["sesion_id"]).execute()
    )
    assert _fila(datos, "sesiones", datos["sesion_id"]) == antes
