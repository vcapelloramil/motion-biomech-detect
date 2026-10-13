"""``app.recuperacion``: golpes que quedaron ``encolado``/``procesando`` por un reinicio. Cliente de Supabase falso, sin red."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.recuperacion import FALLAR, REENCOLAR, decidir, recuperar


def test_decide_por_estado_e_intentos():
    assert decidir("encolado", 0, 3) == REENCOLAR
    assert decidir("encolado", 99, 3) == REENCOLAR           # nunca empezó: no es el sospechoso
    assert decidir("procesando", 0, 3) == REENCOLAR
    assert decidir("procesando", 2, 3) == REENCOLAR
    assert decidir("procesando", 3, 3) == FALLAR             # ya agotó los intentos: no se reanuda en bucle


class _Consulta:
    def __init__(self, admin, filas=None, patch=None):
        self.admin, self.filas, self.patch, self.filtros = admin, filas, patch, {}

    def select(self, *_a, **_k):
        return self

    def in_(self, *_a, **_k):
        return self

    def order(self, *_a, **_k):
        return self

    def update(self, patch, *_a, **_k):
        return _Consulta(self.admin, None, patch)

    def eq(self, columna, valor):
        self.filtros[columna] = valor
        return self

    def execute(self):
        if self.patch is None:
            return SimpleNamespace(data=self.filas)
        fila = next((f for f in self.admin.filas if f["id"] == self.filtros["id"]), None)
        # compare-and-swap: solo cambia si sigue en el estado leído
        if fila is None or fila["estado"] != self.filtros.get("estado", fila["estado"]):
            return SimpleNamespace(data=[])
        fila.update(self.patch)
        return SimpleNamespace(data=[fila])


class _Admin:
    def __init__(self, filas):
        self.filas = filas

    def table(self, nombre):
        assert nombre == "videos"
        return _Consulta(self, self.filas)


def _fila(id_, estado, intentos=1):
    return {"id": id_, "estado": estado, "intentos": intentos, "encolado_en": "2026-10-13T10:00:00+00:00"}


def test_reencola_los_encolados_y_los_procesando_y_falla_los_agotados():
    admin = _Admin([_fila("a", "encolado", 1), _fila("b", "procesando", 1), _fila("c", "procesando", 3)])
    encolados: list[str] = []
    hecho = recuperar(admin, encolados.append, max_intentos=3)
    assert hecho["reencolados"] == ["a", "b"] and hecho["fallidos"] == ["c"]
    assert encolados == ["a", "b"]
    por_id = {f["id"]: f for f in admin.filas}
    assert por_id["a"]["estado"] == "encolado" and por_id["a"]["intentos"] == 1      # el encolado no suma intento
    assert por_id["b"]["estado"] == "encolado" and por_id["b"]["intentos"] == 2      # el que corría, sí
    assert por_id["b"]["inicio_procesamiento_en"] is None
    assert por_id["c"]["estado"] == "fallido" and por_id["c"]["motivo_fallo"] == "error_inesperado"


def test_no_toca_lo_que_ya_esta_en_este_proceso():
    admin = _Admin([_fila("a", "encolado"), _fila("b", "procesando")])
    encolados: list[str] = []
    hecho = recuperar(admin, encolados.append, 3, ya_en_este_proceso=lambda i: i == "a")
    assert hecho["omitidos"] == ["a"] and encolados == ["b"]


def test_sin_pendientes_no_hace_nada():
    assert recuperar(_Admin([]), lambda _i: pytest.fail("no debería encolar"), 3) == {"reencolados": [], "fallidos": [], "omitidos": []}
