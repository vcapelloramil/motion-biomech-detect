"""Tolerancia de "ordenable": UNA sola constante para el producto y para el recálculo del corpus (decisión 032).

Dos picos (p. ej. cadera y tronco) son **ordenables** si sus instantes difieren en MÁS que la tolerancia. Con una diferencia menor o
igual, el orden no se puede establecer a esa resolución: no es un error del sistema ni un estado nuevo, es un motivo de "no auditable"
("a esta resolución no se puede saber cuál fue primero", decisión 015).

La tolerancia está en **tiempo**, no en fotogramas: un fotograma dura 8,3 ms a 120 fps, 5 ms a ~200 fps reales y 4,2 ms en la grilla de
240 Hz a la que se regulariza, así que "1 fotograma" no significa lo mismo en cada archivo (era el defecto de la regla anterior, que
contaba fotogramas de la grilla). El valor es el del pre-registro aprobado del recálculo (``docs/plan-recalculo-corpus-tasa-real.md``
§3): **1 fotograma a 120 Hz = 1/120 s = 8,33 ms** ("8,3 ms"), que es lo que la medición original de la decisión 014 (τ = 1 fotograma)
medía de verdad, porque el corpus horneado era de 120 fps efectivos (decisión 030).

Es la MISMA constante que debe importar el arnés del recálculo (Paso A/B) para clasificar "ordenable"; no se redefine allí.
"""

from __future__ import annotations

FPS_REFERENCIA_TOLERANCIA = 120.0

# Primaria (pre-registro, plan de recálculo §3): 1/120 s = 8,333 ms. Se informa como "8,3 ms".
TOLERANCIA_ORDEN_S = 1.0 / FPS_REFERENCIA_TOLERANCIA
TOLERANCIA_ORDEN_MS = 1000.0 * TOLERANCIA_ORDEN_S

# Sensibilidad declarada de antemano (4,2; 12,5 y 16,7 ms): 0,5, 1,5 y 2 fotogramas a 120 Hz. Solo el recálculo las usa.
TOLERANCIAS_SENSIBILIDAD_S = (0.5 / FPS_REFERENCIA_TOLERANCIA, 1.5 / FPS_REFERENCIA_TOLERANCIA, 2.0 / FPS_REFERENCIA_TOLERANCIA)

# Holgura numérica: dos fotogramas de la grilla de 240 Hz (2/240 s) son exactamente la tolerancia y NO deben quedar del lado
# "ordenable" por un error de redondeo de punto flotante.
_EPS_S = 1e-9


def es_ordenable(delta_s: float, tolerancia_s: float = TOLERANCIA_ORDEN_S) -> bool:
    """``True`` si la diferencia entre dos picos supera la tolerancia (estrictamente: igual a la tolerancia no es ordenable)."""
    return abs(delta_s) > tolerancia_s + _EPS_S
