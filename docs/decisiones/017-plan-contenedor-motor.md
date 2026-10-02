# Decisión 017 — Plan de contenedor para el motor: Free durante el desarrollo, Starter antes de usabilidad

**Fecha:** 29 de septiembre de 2026 (medición local); **ampliada el 2 de octubre de 2026** con la medición
real contra Render.
**Estado:** vigente para el MVP, con el hallazgo colateral de `model_complexity` todavía **pendiente de
decisión** (ver abajo)
**Afecta a:** Etapa 4.5 (tarea 4.5.3/4.5.4/4.5.5) · apartado 4.5.4 de la tesis (estimación de costos) ·
Criterio 2 (decisión 015), si se decide bajar `model_complexity` · decisión 018 (plan gratuito de Render,
hallazgo de 0,1 vCPU) · decisión 019 (semilla de la API que hizo posible esta medición)

---

## Método

`Dockerfile` en `backend/` (Python 3.11-slim + librerías de sistema de opencv + modelo de MediaPipe
precalentado en tiempo de build, para que la medición de tiempo no incluya la descarga por red).
`app/medir_contenedor.py` corre el pipeline completo (ingesta → pose → E3 → E4) sobre un clip real de la
Fase B y mide tiempo total y memoria pico del proceso (`resource.getrusage`, RSS). Se simulan los planes de
contenedor con `docker run --memory=X --cpus=Y`. Resultados completos en
`docs/resultados/e4.5-contenedor-tiempo-memoria.json`. **Máquina de desarrollo, no el proveedor final:**
sirve para comparar configuraciones entre sí, no como cota absoluta de lo que dará en producción.

## Resultado: memoria y CPU (con `model_complexity=2`, el default actual del motor)

| configuración | tiempo total | RSS pico | ¿se cae? |
| --- | --- | --- | --- |
| **512 MB / 0,5 vCPU** (≈ Render Starter, USD 7/mes) | 176–185 s (3 corridas) | 426–427 MB | **no** |
| 1 GB / 1 vCPU | 91,3 s | 427,3 MB | no |
| 2 GB / 2 vCPU (≈ Render Standard, USD 25/mes) | 81,0 s | 441,1 MB | no |

**Ninguna configuración se cayó ni dio OOM, ni siquiera la más ajustada.** Esto contradice la primera
lectura apresurada de la corrida sin restricciones (516 MB de RSS, que hizo pensar que 512 MB no
alcanzaría): esa cifra resultó ser un artefacto de la descarga del modelo en caliente durante esa corrida
puntual: repetida tres veces con el modelo ya precalentado en la imagen, el pico de memoria es consistente
en 426–427 MB, con margen debajo de 512 MB. La memoria casi no cambia entre 512 MB y 2 GB (427 → 427 → 441):
el proceso no está memoria-limitado a este volumen, es prácticamente el mismo consumo con más o menos techo
disponible.

**El tiempo sí depende fuertemente de la CPU:** 0,5 vCPU es 2,2× más lento que 1 vCPU (180 s vs 91 s); subir
de 1 a 2 vCPU aporta poco más (91 s → 81 s, mediapipe en `static_image_mode` no paraleliza mucho más allá
de un núcleo para este patrón de uso, fotograma por fotograma).

## Decisión

**Para el MVP, Render Starter (USD 7/mes, 512 MB, 0,5 vCPU) alcanza.** Un clip real de una repetición
(25 MB, 360 fotogramas) tarda 3 minutos en un trabajador asincrónico de fondo, sin caerse. El apartado 4.2.5
de la tesis ya asume procesamiento en segundo plano, no una respuesta síncrona: 3 minutos es aceptable para
ese diseño. **No se paga el plan de USD 25/mes por este motivo.** Sujeto a confirmarse en la Etapa 4.5
completa (4.5.4: correr esto de verdad en Render, no solo en Docker local) y a que el volumen real de
análisis simultáneos siga siendo bajo (apartado 4.5.3 de la tesis: "un análisis a la vez por proceso
trabajador").

## Hallazgo colateral — PENDIENTE DE DECISIÓN, no aplicado

Se comparó también `model_complexity` (0/1/2) bajo el límite más ajustado (512 MB/0,5 vCPU), a pedido de
Valentín ("puede ser la diferencia entre pagar 7 o 25 dólares"):

| `model_complexity` | tiempo total | RSS pico | cobertura |
| --- | --- | --- | --- |
| **2 — heavy (default actual)** | 176 s | 426 MB | 100 % |
| **1 — full** | **91 s** | **324 MB** | 100 % |
| 1 + resolución reducida a 480 px | 95 s | 311 MB | 100 % |
| 0 — lite | 80 s | 309 MB | 100 % |

**Bajar de `model_complexity=2` a `1` corta el tiempo a la mitad y la memoria en ~100 MB, en el mismo plan
de USD 7.** Reducir la resolución del fotograma antes de la pose no aportó casi nada más sobre `complexity=1`
en este clip (95 s vs 91 s): la complejidad del modelo es la palanca que importa, no la resolución.

**Por qué esto NO se aplica ahora:** `cobertura` es binaria (¿se detectó a la persona?, sí/no) y en este
clip —de la Fase B, bien iluminado, encuadre controlado— da 100 % en los tres niveles: **no discrimina
precisión entre ellos**. El Criterio 2 (decisión 015, "cumple" con 8,5°/12,5° de error medio) se midió con
`model_complexity=2`. Cambiar el default de producción a `1` es una decisión que **afecta la precisión
angular ya validada** y necesitaría repetir esa medición (o al menos una parte) con el nuevo ajuste antes
de adoptarlo — no se decide por costo de contenedor solamente. Queda anotado como candidato fuerte a
evaluar, no aplicado en esta decisión.

## Ampliación (2/10/2026): medición real contra Render, plan Free

Antes de pagar Starter, Valentín pidió medir primero el plan **gratuito** de Render con datos reales (no con
la simulación de Docker local de más arriba). Hecho posible por la decisión 019 (semilla de la API,
`POST /analisis/{video_id}/procesar`), con el mismo clip de la Fase B usado en la medición de Docker local.

| | Docker local, 512 MB/0,5 vCPU (medición de arriba) | Render Free (medido) |
| --- | --- | --- |
| CPU | 0,5 vCPU (simulada) | **0,1 vCPU** (real — decisión 018) |
| RAM | 512 MB (límite simulado) | 512 MB (límite real del plan) |
| Tiempo | 176–185 s | **414,1 s** |
| RSS pico | 426–427 MB | **480,4 MB** |
| ¿Se cae / se corta? | No | **No** (sin cortes por suspensión por inactividad) |

El tiempo sube de forma consistente con la CPU 5 veces menor (176 s a 0,5 vCPU → 414 s a 0,1 vCPU no es un
5×, pero tampoco se esperaba lineal: `static_image_mode` de MediaPipe no escala simétricamente por debajo de
0,5 vCPU). La memoria sube **54 MB** (426→480); investigado por separado, ver la bitácora del 2/10 y el
comentario agregado en `app/procesar_video.py` (se soltaban los bytes del clip recién al final de la función,
superpuestos en memoria con los buffers de la inferencia — corregido con un `del` explícito apenas se escribe
el archivo temporal). Durante la misma corrida apareció el aviso `[aviso] pico de brazo no finito (nan)` —
no es un bug de esta medición: es el comportamiento ya conocido del motor con el codo dominante en perfil
(decisión 013), cuantificado aparte en `docs/resultados/diagnostico-brazo-corpus.json`.

### Decisión final

**Render Free durante el desarrollo** (Etapas 5–8, mientras el único tráfico es el propio Valentín probando).
**Pasar a Starter antes de las pruebas de usabilidad de la Etapa 9**, con este criterio explícito de
activación (decisión de Valentín, no depende de que alguien se acuerde de revisarlo):

- memoria pico por encima de 460 MB en cualquier clip real (margen de 52 MB debajo del límite de 512 MB,
  no los ~32 MB que dejaba la medición de Render), **o**
- cualquier corte por suspensión de inactividad (un análisis que quede "procesando" porque Render durmió el
  servicio a mitad de camino).

No se decide por tiempo de procesamiento solo (414 s para un trabajador de fondo sigue siendo aceptable
según el apartado 4.2.5 de la tesis, que ya asume asincronía) — el criterio es memoria y continuidad, los dos
riesgos reales de un plan con 5 veces menos CPU y el mismo techo de RAM.

## Consecuencias

- Task 4.5.4 (desplegar en Render de verdad) usa el plan **Free** para el desarrollo, con el criterio de
  arriba para pasar a Starter — no un "ya se verá".
- El apartado 4.5.4 de la tesis puede actualizarse con datos medidos en vez de la estimación de folleto
  (pendiente de redacción, igual que las decisiones 006/010/011), ahora con dos juegos de números: Docker
  local y Render real.
- Si en algún momento se decide bajar `model_complexity`, hay que volver a esta decisión y a la 015
  (Criterio 2) juntas, no por separado.
