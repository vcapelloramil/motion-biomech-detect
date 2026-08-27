# Decisión 006 — La velocidad de inferencia real obliga a revisar 4.2.3 y 4.5.4

**Fecha:** 27 de agosto de 2026
**Estado:** vigente — **pendiente de redacción, no de código**
**Afecta a:** Capítulo 4 (apartados 4.2.3 y 4.5.4) · entrega final

---

## El hecho

La medición de la Etapa 2 (tarea 2.6, `docs/resultados/e2-velocidad-inferencia.json`)
dio **~3,6 fotogramas/segundo** para MediaPipe con `model_complexity=2`, 1080p, sobre
CPU (MediaPipe-Python no usa la GPU disponible).

En el apartado **4.2.3** del Capítulo 4 se usó una estimación de **~25 fps** para
justificar el procesamiento asincrónico y estimar tiempos de respuesta; el apartado
**4.5.4** apoyó la estimación de costos en ese mismo número.

La diferencia es de casi 7×. No invalida la decisión de fondo (el procesamiento
asincrónico se vuelve *más* necesario, no menos), pero los tiempos y costos que citan
esos apartados quedan desactualizados.

## Qué se hace

- **Ahora:** nada en el código. Se coincide en no optimizar hasta **después** del
  punto de decisión de la Etapa 4, no antes.
- **Si en algún momento hace falta optimizar, el orden de palancas a evaluar es:**
  1. `model_complexity` más bajo (2 → 1) — cambio de una línea, sin migración.
  2. Si no alcanza, migrar a la **Vía A sobre ONNX Runtime** (ya prevista en el
     Capítulo 4): ahí sí hay soporte real de GPU en Windows, mientras que la API de
     Python de MediaPipe corre solo por CPU.
  3. Menor resolución antes de inferir y/o `static_image_mode=False` (tracking)
     quedan como palancas secundarias.
- **Antes de la entrega final:** reescribir 4.2.3 y 4.5.4 con el número medido (o
  con el que resulte tras aplicar las palancas). El dato reproducible ya está
  versionado en `docs/resultados/`.

## Por qué queda registrado acá

El registro de decisiones "alimenta directamente la redacción de los capítulos
siguientes" (tarea 0.6 del plan). Este es exactamente ese caso: un número que el
desarrollo produjo y que contradice una estimación previa de la tesis.
