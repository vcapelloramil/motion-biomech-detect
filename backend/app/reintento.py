"""¿Se puede encolar este video? — decisión 022.

Función pura, sin red: recibe lo que está en la base y devuelve si se encola o por qué no. El
router (``routers/analisis.py``) la usa y después aplica el cambio con un *compare-and-swap*; la
lógica vive acá aparte para poder probar cada celda de la tabla sin Supabase.

Principio: se reintenta solo desde ``fallido``, y solo si hay algo distinto que probar.

====================================  ==========================================================
Estado actual                         ¿Se encola?
====================================  ==========================================================
``pendiente``                         Sí (confirmación de carga)
``fallido`` + modo incompatible       Solo si la sesión ya no declara el modo con el que falló
``fallido`` + error inesperado        Sí, mientras ``intentos`` < tope
``fallido`` sin motivo                Igual que error inesperado (filas anteriores a la 022)
``encolado`` / ``procesando``         No (el doble clic no encola dos veces)
``completado`` / ``parcial``          No (nunca se reanaliza; ``parcial`` queda pendiente)
====================================  ==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

CODIGO_ESTADO_NO_REINTENTABLE = "estado_no_reintentable"
CODIGO_DECLARACION_SIN_CAMBIOS = "declaracion_sin_cambios"
CODIGO_INTENTOS_AGOTADOS = "intentos_agotados"

# Mismos valores que videos.motivo_fallo (migraciones 20261002000000 y 20261007000000).
MOTIVO_MODO_CAPTURA_INCOMPATIBLE = "modo_captura_incompatible"
MOTIVO_ERROR_INESPERADO = "error_inesperado"


@dataclass(frozen=True)
class DecisionReintento:
    permitido: bool
    codigo: str | None = None  # None si permitido; si no, uno de los CODIGO_* de arriba.


_PERMITIDO = DecisionReintento(True)


def decidir_reintento(
    estado: str,
    motivo_fallo: str | None,
    modo_intentado: str | None,
    modo_actual: str,
    intentos: int,
    max_intentos: int,
) -> DecisionReintento:
    if estado == "pendiente":
        return _PERMITIDO

    if estado != "fallido":
        return DecisionReintento(False, CODIGO_ESTADO_NO_REINTENTABLE)

    if motivo_fallo == MOTIVO_MODO_CAPTURA_INCOMPATIBLE:
        # modo_intentado en None: el fallo es anterior a la columna (decisión 022), no se sabe con
        # qué modo falló. Se deja reintentar: negarlo dejaría al usuario sin salida, y el peor
        # resultado es volver a fallar con el mismo código.
        if modo_intentado is not None and modo_intentado == modo_actual:
            return DecisionReintento(False, CODIGO_DECLARACION_SIN_CAMBIOS)
        return _PERMITIDO

    # error_inesperado, o fallido sin motivo (anterior a la 022: el único fallo con código era el
    # de modo de captura, así que un fallo sin código fue inesperado por definición).
    if intentos >= max_intentos:
        return DecisionReintento(False, CODIGO_INTENTOS_AGOTADOS)
    return _PERMITIDO
