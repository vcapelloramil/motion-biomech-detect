"""Versión del motor biomecánico.

Este número se sella en cada reporte generado (campo ``trazabilidad.version_motor``
del contrato, regla R4 del CLAUDE.md). Sirve para saber con qué versión del motor
se produjo un resultado y poder reproducirlo.

Convención: se mantiene en "0.0.0" mientras el motor no calcule nada. La Etapa 1
lo lleva a "0.1.0" y cada etapa siguiente incrementa la minor, en línea con las
etiquetas de git del plan de desarrollo (v0.1.0-etapa1, v0.2.0-etapa2, ...).
"""

__version__ = "0.0.0"
