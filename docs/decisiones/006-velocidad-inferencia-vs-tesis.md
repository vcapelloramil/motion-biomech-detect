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

- **Ahora:** nada en el código. Se coincide en no optimizar hasta que el punto de
  decisión de la Etapa 4 diga si la velocidad es un problema real para el alcance
  del MVP.
- **Antes de la entrega final:** reescribir 4.2.3 y 4.5.4 con el número medido
  (o con el que resulte tras las palancas de la decisión 005: `model_complexity=1`,
  `static_image_mode=False`, o menor resolución). El dato reproducible ya está
  versionado en `docs/resultados/`.

## Por qué queda registrado acá

El registro de decisiones "alimenta directamente la redacción de los capítulos
siguientes" (tarea 0.6 del plan). Este es exactamente ese caso: un número que el
desarrollo produjo y que contradice una estimación previa de la tesis.
