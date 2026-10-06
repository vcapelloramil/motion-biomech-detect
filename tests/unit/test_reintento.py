"""``app.reintento.decidir_reintento`` — decisión 022. Prueba pura, sin red: una por celda de la tabla
de transiciones del docstring del módulo."""

from __future__ import annotations

import pytest

from app.reintento import (
    CODIGO_DECLARACION_SIN_CAMBIOS,
    CODIGO_ESTADO_NO_REINTENTABLE,
    CODIGO_INTENTOS_AGOTADOS,
    decidir_reintento,
)

_MAX = 3
_INCOMPATIBLE = "modo_captura_incompatible"
_INESPERADO = "error_inesperado"


def _decidir(estado, motivo=None, intentado=None, actual="camara_lenta_240", intentos=0, maximo=_MAX):
    return decidir_reintento(estado, motivo, intentado, actual, intentos, maximo)


def test_pendiente_se_encola():
    d = _decidir("pendiente")
    assert d.permitido and d.codigo is None


@pytest.mark.parametrize("estado", ["encolado", "procesando", "completado", "parcial"])
def test_los_demas_estados_no_se_reencolan(estado):
    d = _decidir(estado)
    assert not d.permitido and d.codigo == CODIGO_ESTADO_NO_REINTENTABLE


def test_estado_no_reintentable_gana_aunque_haya_un_motivo_viejo():
    """Un video 'completado' que arrastrara un motivo_fallo viejo no se vuelve reintentable."""
    d = _decidir("completado", motivo=_INCOMPATIBLE, intentado="normal")
    assert not d.permitido and d.codigo == CODIGO_ESTADO_NO_REINTENTABLE


def test_modo_incompatible_con_la_misma_declaracion_no_se_reintenta():
    d = _decidir("fallido", _INCOMPATIBLE, intentado="camara_lenta_240", actual="camara_lenta_240")
    assert not d.permitido and d.codigo == CODIGO_DECLARACION_SIN_CAMBIOS


def test_modo_incompatible_con_la_declaracion_corregida_se_reintenta():
    assert _decidir("fallido", _INCOMPATIBLE, intentado="normal", actual="camara_lenta_240").permitido


def test_modo_incompatible_anterior_a_la_columna_se_deja_reintentar():
    """modo_captura_intentado en null = fallo previo a la decisión 022: no se sabe con qué modo
    falló, y negarlo dejaría al usuario sin salida."""
    assert _decidir("fallido", _INCOMPATIBLE, intentado=None).permitido


def test_el_tope_de_intentos_no_aplica_al_modo_incompatible():
    """Corregir la declaración es una acción nueva del usuario cada vez: el tope es para los
    errores que el usuario no controla."""
    assert _decidir("fallido", _INCOMPATIBLE, intentado="normal", intentos=99).permitido


@pytest.mark.parametrize("motivo", [_INESPERADO, None], ids=["error_inesperado", "sin_motivo_anterior_a_022"])
@pytest.mark.parametrize("intentos,permitido", [(0, True), (1, True), (2, True), (3, False), (4, False)])
def test_error_inesperado_se_reintenta_hasta_el_tope(motivo, intentos, permitido):
    d = _decidir("fallido", motivo, intentos=intentos)
    assert d.permitido is permitido
    assert d.codigo == (None if permitido else CODIGO_INTENTOS_AGOTADOS)


def test_el_tope_es_un_parametro():
    assert not _decidir("fallido", _INESPERADO, intentos=3, maximo=3).permitido
    assert _decidir("fallido", _INESPERADO, intentos=3, maximo=5).permitido
