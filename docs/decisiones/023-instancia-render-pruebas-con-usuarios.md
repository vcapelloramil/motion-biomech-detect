# Decisión 023 — Instancia de Render: Free y Starter descartados para las pruebas con usuarios; Standard solo durante el período de pruebas y defensa

**Fecha:** 6 de octubre de 2026
**Estado:** vigente — decisión de Valentín. El cambio de plan se hace hacia el **20/10/2026** y se revierte a Free
al terminar las pruebas con usuarios y la defensa.
**Afecta a:** decisión 017 (criterio de pase a Starter, superado; error "Standard = 2 vCPU" corregido ahí) ·
`render.yaml` (`plan: free` hasta el cambio) · Etapa 9 (pruebas de usabilidad) · modelo de costos del Capítulo 5 ·
apartado 4.5.4 de la tesis (pendiente de redacción)

---

## El problema

La decisión 017 dejó Render Free "durante el desarrollo" y Starter "antes de las pruebas de usabilidad", con
el criterio de pasar si la memoria pico superaba 460 MB o si había un corte por suspensión. Al preparar las pruebas
de punta a punta con usuarios (una sesión = hasta 6 golpes) se revisó ese criterio contra lo medido y contra la
documentación de planes de Render, y no se sostiene:

1. **Tiempo.** Una sesión de 6 golpes, uno por vez (un análisis a la vez por proceso, apartado 4.5.3), en Free son
   unos **41 minutos** (6 × 414 s medidos). Con el tope de 50 MB un clip llega a ~700 fotogramas, casi el doble.
2. **Memoria.** El único dato real de Render Free es **480,4 MB de RSS pico sobre 512 MB** (margen de 32 MB, ~6 %),
   medido con una sola corrida y antes de la corrección que suelta los bytes del clip (`del`, no re-medida en
   Render). Ya superaba el umbral de 460 MB de la decisión 017.
3. **Suspensión.** Free se duerme tras 15 minutos sin tráfico entrante. La corrida de 414 s duró menos que eso,
   así que "sin cortes por suspensión" no cubre una sesión de 41 minutos. No se verificó si una tarea de fondo en
   curso cuenta como tráfico.
4. **Starter no resuelve la memoria.** Tiene los **mismos 512 MB** que Free (0,5 CPU contra 0,1). El criterio de la
   017 ("memoria > 460 MB → Starter") apuntaba a un plan que no agrega memoria. Solo **Standard** (1 CPU / 2 GB)
   sube el techo de RAM.

## Planes de Render comparados

CPU y RAM: documentación de planes de Render, verificada el 6/10/2026. Precios: los de Starter y Standard son los
que maneja el proyecto (no figuran en esa página; confirmar en el panel de Render antes del cambio); el de Pro salió
de un resultado de búsqueda, **sin verificar**, y no interviene en la decisión.

| Plan | CPU | RAM | USD/mes | Tiempo por golpe (360 fotogramas) | Sesión de 6 golpes | Origen del tiempo |
| --- | --- | --- | --- | --- | --- | --- |
| Free | 0,1 | 512 MB | 0 | 414 s | ~41 min | **medido** en Render (1 corrida) |
| Starter | 0,5 | 512 MB | 7 | ~180 s | ~18 min | Docker, 0,5 vCPU simulado |
| **Standard** | **1** | **2 GB** | **25** | **~91 s** | **~9 min** | Docker, 1 vCPU simulado |
| Pro | 2 | 4 GB | 85 | — | — | no medido, no hace falta |

Los tiempos de Starter y Standard son **de Docker local, no de Render**: sirven para comparar entre sí, no como cota
absoluta (decisión 017). Escalar por cantidad de fotogramas supone relación lineal, sin verificar.

## Alternativas consideradas

- **Quedarse en Free.** Descartada: 41 min por sesión, 32 MB de margen de memoria y riesgo de suspensión a mitad de
  un análisis (el video quedaría `procesando`; la recuperación al arranque es la tarea 6.5, aún sin hacer).
- **Starter (USD 7).** Descartada: mismos 512 MB; arregla el tiempo (~18 min por sesión) pero no el margen de
  memoria. Podría volver a evaluarse con una medición real en Starter si, tras `model_complexity=1` (decisión 017,
  pendiente) o la corrección del `del`, el RSS quedara holgado por debajo de ~460 MB.
- **Pro (USD 85).** Descartada: no hay evidencia de que haga falta; 1 CPU ya es el 91 s medido y subir de 1 a 2 vCPU
  aporta poco (decisión 017).

## Decisión

1. **Standard (1 CPU, 2 GB, USD 25/mes) solo durante el período de pruebas con usuarios y la defensa.** El cambio se
   hace hacia el **20/10**, antes de la primera prueba de punta a punta con un video subido desde el celular.
2. **Después se vuelve a Free.** El cambio de plan lo hace Valentín en el panel de Render y, **en el mismo paso**, se
   actualiza `render.yaml` (`plan:`) y se anota en la bitácora. `render.yaml` **no se edita antes**: si el servicio
   está sincronizado con el blueprint, pushear un cambio de `plan` podría cambiar la facturación sin querer.
3. El **criterio de la decisión 017** ("RSS > 460 MB → Starter") queda **superado** por esta decisión, no se aplica.

## Consecuencias

- **Costo estimado del período:** de 1 a 2 meses de Standard, **USD 25–50** (estimación; Render factura según el
  plan y el tiempo, verificar en el panel). Entra en el modelo de costos del Capítulo 5 como costo de la etapa de
  validación, separado del costo de operación posterior.
- **Para el modelo de costos del Capítulo 5, producción:** no se decide acá. Cuando haya medición real sobre Standard
  se compara contra Starter con datos de Render, no de Docker.
- **A medir apenas se cambie a Standard** (reemplaza los números derivados de Docker por números de Render): RSS pico
  y tiempo por golpe de un clip real, y una **sesión de 6 golpes seguidos** de punta a punta. Con ese resultado se
  puede cerrar el modelo de costos del Capítulo 5.
- **Después del 20/10 con Free otra vez:** el servicio sigue funcionando pero con las limitaciones de arriba; es
  aceptable para una demostración de un solo golpe, no para sesiones completas.
- Las instancias de pago no se duermen por inactividad (comportamiento documentado de Render para el plan Free; no
  medido acá): con Standard desaparece el riesgo de suspensión, que sigue siendo la razón de existir de la tarea 6.5.
- No hacer el cambio de plan mientras haya análisis en curso: reinicia el servicio.
