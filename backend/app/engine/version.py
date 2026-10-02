"""Versión del motor biomecánico.

Este número se sella en cada reporte generado (campo ``trazabilidad.version_motor``
del contrato, regla R4 del CLAUDE.md). Sirve para saber con qué versión del motor
se produjo un resultado y poder reproducirlo.

Convención: cada etapa que agrega capacidad al motor incrementa la minor, en
línea con las etiquetas de git del plan de desarrollo (v0.2.0-etapa1,
v0.3.0-etapa2, ...). Empezó en "0.0.0" (Etapa 0, sin cálculo).

**Ojo con el desfasaje a propósito entre esta constante y la etiqueta de git**: la
etiqueta que CIERRA la etapaN es "v0.(N+1).0-etapaN" (p. ej. "v0.5.0-etapa4" cierra la
Etapa 4), pero el __version__ que corresponde a esa misma etapa es "0.N.x" (etapa4 →
"0.4.x"), un minor menos — porque la Etapa 0 ya se etiqueta "v0.1.0" aunque el motor
siga en "0.0.0" (sin cálculo todavía). No es un desfasaje que haya que corregir ni una
constante que se haya quedado atrás: confirmado revisando las cinco etiquetas de etapa
cerradas hasta ahora (0/1/2/3/4), el patrón es el mismo en las cinco, no solo en esta
(revisado el 2/10/2026 a pedido de Valentín, sin encontrar ningún caso que lo rompa).
Lo que sí incrementa __version__ es si CAMBIÓ algo en engine/ desde el último bump —
0.4.1 se mantiene vigente mientras no se toque engine/ de nuevo, sin importar cuánto
tiempo pase entre etapas (ver el historial de commits de este archivo con
``git log --follow -- backend/app/engine/version.py``).

- 0.1.0 — Etapa 1: ingesta y validación de FPS.
- 0.2.0 — Etapa 2: estimación de pose (interfaz intercambiable + MediaPipe).
- 0.3.0 — Etapa 3: filtrado de fase cero (Butterworth + Winter).
- 0.3.1 — Fix: detector de inversión de profundidad (z) en la validación (decisión 009).
- 0.3.2 — Calibración del detector de inversión de z (confianza previa + retorno).
- 0.4.0 — Etapa 4 (en curso): cinemática y secuenciación, pasos 4.1–4.6.
- 0.4.1 — Fix E3: las series con huecos se filtran por segmentos continuos (antes se dejaban
  enteras sin filtrar; decisión 010). Cambia toda velocidad calculada con articulaciones con
  huecos (en la práctica, el brazo). Sigue vigente al cerrar la Etapa 4 (decisión 015, tag
  v0.5.0-etapa4): ningún commit posterior a este tocó engine/ (ver más arriba).
"""

__version__ = "0.4.1"
