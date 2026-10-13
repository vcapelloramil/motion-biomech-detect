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

**Qué sello llevan los reportes (RNF-02)** — la regla se rompió entre el 9 y el 12/10/2026: el motor cambió en cuatro
commits con el sello 0.4.1 puesto, y recién se subió el número al ajustar la tolerancia del orden (decisión 032). Para
distinguir un reporte viejo de uno nuevo, la tabla de commits está en ``docs/bitacora.md`` (entrada del 12/10, "Versiones
del motor"); el discriminador práctico es la ``version_contrato`` del propio reporte (1.0 · 1.1 · 1.2 · 1.3).

- 0.1.0 — Etapa 1: ingesta y validación de FPS.
- 0.2.0 — Etapa 2: estimación de pose (interfaz intercambiable + MediaPipe).
- 0.3.0 — Etapa 3: filtrado de fase cero (Butterworth + Winter).
- 0.3.1 — Fix: detector de inversión de profundidad (z) en la validación (decisión 009).
- 0.3.2 — Calibración del detector de inversión de z (confianza previa + retorno).
- 0.4.0 — Etapa 4 (en curso): cinemática y secuenciación, pasos 4.1–4.6.
- 0.4.1 — Fix E3: las series con huecos se filtran por segmentos continuos (antes se dejaban
  enteras sin filtrar; decisión 010). Cambia toda velocidad calculada con articulaciones con
  huecos (en la práctica, el brazo). Sigue vigente al cerrar la Etapa 4 (decisión 015, tag
  v0.5.0-etapa4).
- 0.5.0 — Etapas 4.5 y 5 mínima: el motor **lee la tasa real de las marcas de tiempo** del archivo y no la supone (decisiones
  029 y 030, RNF-01), corrige la orientación automática, **regulariza el tiempo** a una grilla uniforme antes de filtrar
  (con los puntos interpolados contados, R4), alinea con las marcas de los fotogramas realmente decodificados, marca
  "no auditable" la cadera y el tronco simultáneos, aplica la tolerancia del 5 % del piso de R1 (114 fps) y, desde la
  decisión 032, decide "ordenable" con **una sola tolerancia de 8,33 ms** (``engine/tolerancia_orden.py``) y genera los
  fotogramas clave y el video con esqueleto (``engine/render.py``). Los reportes del contrato 1.3 son de esta versión.
- 0.5.1 — Regla de cobertura de la ventana (12/10/2026): el pico de un segmento no se reporta si se midió menos del 75 % de la
  ventana (un máximo censurado no es el máximo); con el brazo sin medir y la cadera y el tronco ordenables, la repetición se informa
  con esos dos. Video con esqueleto a 720 px y CRF 20. Magnitudes articulares como dato (``engine/magnitudes.py``: separación
  cadera-hombro máxima y ángulos de rodilla y codo en el pico del tronco). Sin cambio de contrato.
- 0.5.2 — Decisión 035 (13/10/2026, con el OK de Valentín): el saque no emite veredicto del orden (depende del encuadre) y el reporte contrasta
  el encuadre declarado con el que se ve (``engine/encuadre.py``); si discrepa, avisa y no emite veredicto. Sin cambio de contrato.
- 0.5.3 — Decisión 036 (13/10/2026): ningún grupo emite veredicto del orden. El drive se suspende por encuadre (como el saque) y el revés
  por no ser confiable con una sola cámara; la suspensión decide aunque haya referencia y el Criterio 1 se cumpla. Cambia el texto de
  las observaciones del drive y del revés. Sin cambio de contrato.
- 0.5.4 — Decisión 037 (13/10/2026): un golpe con cadera y tronco empatados a la resolución del video está **medido** (no "no auditable"):
  la observación pasa a "sin diferencia medible" (contrato 1.4); un golpe está medido si los picos de cadera y tronco se midieron con
  confianza suficiente; los picos que no se pudieron medir (el brazo, sobre todo) llevan su motivo en palabras simples.
"""

__version__ = "0.5.4"
