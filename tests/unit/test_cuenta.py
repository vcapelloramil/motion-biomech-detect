"""``app.cuenta`` y ``DELETE /cuenta`` — eliminar la cuenta y todos sus datos (paso 5). Cliente de Supabase falso, sin red.

Lo que importa: los archivos van PRIMERO y la cuenta DESPUÉS; si un archivo no se puede borrar, la cuenta no se toca; el borrado es solo
de la cuenta del token; y sin la confirmación explícita no pasa nada."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.cuenta import eliminar_cuenta, rutas_del_usuario
from app.main import app
from app.security import UsuarioAutenticado, get_admin_client, usuario_autenticado

_USUARIO = "11111111-1111-4111-8111-111111111111"
_OTRO = "22222222-2222-4222-8222-222222222222"


class _Bucket:
    def __init__(self, storage, nombre):
        self.s, self.nombre = storage, nombre

    def list(self, carpeta, opciones=None):
        opciones = opciones or {}
        hijos = self.s.arbol[self.nombre].get(carpeta, [])
        o, n = opciones.get("offset", 0), opciones.get("limit", 100)
        return hijos[o : o + n]

    def remove(self, rutas):
        if self.s.falla_en == self.nombre:
            raise RuntimeError("Storage no respondió")
        self.s.eventos.append(("remove", self.nombre, list(rutas)))


class _Storage:
    def __init__(self, arbol, eventos, falla_en=None):
        self.arbol, self.eventos, self.falla_en = arbol, eventos, falla_en

    def from_(self, nombre):
        return _Bucket(self, nombre)


class _AuthAdmin:
    def __init__(self, eventos):
        self.eventos = eventos

    def delete_user(self, usuario_id):
        self.eventos.append(("delete_user", usuario_id))


class _Admin:
    def __init__(self, arbol, falla_en=None):
        self.eventos: list = []
        self.storage = _Storage(arbol, self.eventos, falla_en)
        self.auth = SimpleAuth(_AuthAdmin(self.eventos))


class SimpleAuth:
    def __init__(self, admin):
        self.admin = admin


def _carpeta(nombre):
    return {"name": nombre, "id": None}


def _archivo(nombre):
    return {"name": nombre, "id": "x", "metadata": {"size": 1}}


def _arbol():
    return {
        "videos": {
            _USUARIO: [_carpeta("v1"), _carpeta("v2")],
            f"{_USUARIO}/v1": [_archivo("golpe1.mov")],
            f"{_USUARIO}/v2": [_archivo("golpe2.mov")],
        },
        "artefactos": {
            _USUARIO: [_carpeta("v1")],
            f"{_USUARIO}/v1": [_archivo("pelvis.jpg"), _archivo("torso.jpg"), _archivo("overlay.mp4")],
        },
    }


def test_recorre_las_carpetas_y_pagina():
    muchos = [_archivo(f"f{i}.jpg") for i in range(250)]
    arbol = {"artefactos": {_USUARIO: [_carpeta("v1")], f"{_USUARIO}/v1": muchos}}
    rutas = rutas_del_usuario(_Storage(arbol, []), "artefactos", _USUARIO)
    assert len(rutas) == 250 and rutas[0].startswith(f"{_USUARIO}/v1/")


def test_borra_primero_los_archivos_y_despues_la_cuenta():
    admin = _Admin(_arbol())
    r = eliminar_cuenta(admin, _USUARIO)
    assert r == {"archivos_eliminados": 5}
    tipos = [e[0] for e in admin.eventos]
    assert tipos == ["remove", "remove", "delete_user"]
    assert admin.eventos[-1] == ("delete_user", _USUARIO)
    borradas = [r for e in admin.eventos if e[0] == "remove" for r in e[2]]
    assert all(ruta.startswith(f"{_USUARIO}/") for ruta in borradas)     # solo la carpeta del usuario


def test_si_falla_el_borrado_de_archivos_la_cuenta_no_se_toca():
    admin = _Admin(_arbol(), falla_en="artefactos")
    with pytest.raises(RuntimeError):
        eliminar_cuenta(admin, _USUARIO)
    assert ("delete_user", _USUARIO) not in admin.eventos


def test_una_cuenta_sin_archivos_se_elimina_igual():
    admin = _Admin({"videos": {}, "artefactos": {}})
    assert eliminar_cuenta(admin, _USUARIO) == {"archivos_eliminados": 0}
    assert admin.eventos == [("delete_user", _USUARIO)]


# --- el endpoint -------------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def cliente():
    def _armar(admin, usuario=_USUARIO):
        app.dependency_overrides[get_admin_client] = lambda: admin
        app.dependency_overrides[usuario_autenticado] = lambda: UsuarioAutenticado(id=usuario)
        return TestClient(app)

    yield _armar
    app.dependency_overrides.clear()


def test_el_endpoint_elimina_la_cuenta_del_token(cliente):
    admin = _Admin(_arbol())
    r = cliente(admin, usuario=_USUARIO).request("DELETE", "/cuenta", json={"confirmacion": "ELIMINAR"})
    assert r.status_code == 200 and r.json() == {"archivos_eliminados": 5}
    assert ("delete_user", _USUARIO) in admin.eventos and ("delete_user", _OTRO) not in admin.eventos


def test_sin_la_confirmacion_no_pasa_nada(cliente):
    admin = _Admin(_arbol())
    r = cliente(admin).request("DELETE", "/cuenta", json={"confirmacion": "eliminar"})
    assert r.status_code == 400 and r.json()["detail"]["codigo"] == "confirmacion_incorrecta"
    assert admin.eventos == []


def test_un_fallo_de_storage_es_502_y_deja_la_cuenta(cliente):
    admin = _Admin(_arbol(), falla_en="videos")
    r = cliente(admin).request("DELETE", "/cuenta", json={"confirmacion": "ELIMINAR"})
    assert r.status_code == 502 and r.json()["detail"]["codigo"] == "no_se_pudo_eliminar"
    assert not any(e[0] == "delete_user" for e in admin.eventos)


def test_sin_sesion_iniciada_es_401():
    app.dependency_overrides.clear()
    r = TestClient(app).request("DELETE", "/cuenta", json={"confirmacion": "ELIMINAR"})
    assert r.status_code == 401
