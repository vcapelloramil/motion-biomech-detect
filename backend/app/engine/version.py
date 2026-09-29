"""Versión del motor biomecánico.

Este número se sella en cada reporte generado (campo ``trazabilidad.version_motor``
del contrato, regla R4 del CLAUDE.md). Sirve para saber con qué versión del motor
se produjo un resultado y poder reproducirlo.

Convención: cada etapa que agrega capacidad al motor incrementa la minor, en
línea con las etiquetas de git del plan de desarrollo (v0.2.0-etapa1,
v0.3.0-etapa2, ...). Empezó en "0.0.0" (Etapa 0, sin cálculo).

- 0.1.0 — Etapa 1: ingesta y validación de FPS.
- 0.2.0 — Etapa 2: estimación de pose (interfaz intercambiable + MediaPipe).
- 0.3.0 — Etapa 3: filtrado de fase cero (Butterworth + Winter).
- 0.3.1 — Fix: detector de inversión de profundidad (z) en la validación (decisión 009).
- 0.3.2 — Calibración del detector de inversión de z (confianza previa + retorno).
- 0.4.0 — Etapa 4 (en curso): cinemática y secuenciación, pasos 4.1–4.6.
- 0.4.1 — Fix E3: las series con huecos se filtran por segmentos continuos (antes se dejaban
  enteras sin filtrar; decisión 010). Cambia toda velocidad calculada con articulaciones con
  huecos (en la práctica, el brazo).
"""

__version__ = "0.4.1"
