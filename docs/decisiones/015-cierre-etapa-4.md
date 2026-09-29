# Decisión 015 — Cierre de la Etapa 4: punto de decisión

**Fecha:** 29 de septiembre de 2026
**Estado:** vigente (decisión de Valentín)
**Afecta a:** punto de decisión de la Etapa 4 (`docs/plan-desarrollo.md`) · contrato del reporte (Anexo A, consecuencia para Etapa 5) · Capítulos 6 y 7 · decisiones 011, 012, 013, 014

---

## El punto de decisión (plan de desarrollo, tabla de la Etapa 4)

| Resultado | Acción |
| --- | --- |
| Criterios 1 y 2 se cumplen | Continuar con la Etapa 5 |
| Criterio 1 falla | Replegarse a la fase de preparación |
| Criterio 2 falla | Replegarse a 2D con encuadre controlado |
| Ambos fallan | Reformular el alcance del MVP |

Con los tres criterios medidos (Criterio 1: decisión 014 y `criterio1-sesion-2.json`; Criterio 3 redefinido:
decisiones 012/014 y `criterio3.json`, con el override de la 014; Criterio 2: `criterio2.json`), el resultado
es **mixto por grupo**, no un cumple/no-cumple único. **Decisión de Valentín: sin repliegue de arquitectura.**
Se mantiene la cadena `pelvis → torso → brazo` y el resto del pipeline, con las cinco salvedades documentadas
abajo, que pasan a formar parte del alcance declarado del sistema.

## Salvedades documentadas

### 1. Tres cuartos: el orden pelvis-torso solo es auditable en revés

| grupo | ordenables (τ=1, par pelvis-torso) | 1a | orden modal |
| --- | --- | --- | --- |
| revés de tres cuartos | 6 de 6 | 1,00 | `tp` (torso primero) |
| saque de tres cuartos | 9 de 18 | 0,50 | `pt` en las ordenables, pero no llega al umbral |
| drive de tres cuartos | **0 de 6** | 0,00 | — |

En drive de tres cuartos ninguna repetición resultó ordenable; en saque de tres cuartos, la mitad. En ambos,
la separación entre los picos de pelvis y torso está al límite de la resolución de 240 fps (1 fotograma =
4,17 ms). **Se reportan como "no ordenable"**, no como fallo del sistema: es información, no un dato faltante
por error. Revés de tres cuartos es, de los tres, el único donde el orden pelvis-torso es auditable.

### 2. Perfil: orden repetible pero invertido, sin etiqueta de correcto/incorrecto

| grupo | 1a | 1b | orden modal | 1c (coincide con lo esperado) |
| --- | --- | --- | --- | --- |
| saque de perfil | 1,00 | 1,00 | `tp` | 0,00 |
| drive de perfil | 1,00 | 1,00 | `tp` | 0,00 |
| revés de perfil | 0,67 | 0,75 | `pt` | 0,75 |

En saque y drive de perfil el orden es repetible (cumple 1a y 1b) pero **invertido** respecto del esperado
por la literatura (torso antes que pelvis). En revés de perfil la repetibilidad no llega al umbral (4 de 6
ordenables). **Se reporta como orden observado, sin la etiqueta "correcto"/"incorrecto"** (R4: esa etiqueta
necesitaría una fuente bibliográfica para el sentido observado, que no existe).

### 3. Brazo: además de la decisión 011, advertencia de precisión del codo dominante

La decisión 011 ya establece que el "brazo" es un proxy de orientación espacial, no de rotación interna
(no comparable con Fleisig). A eso se suma un hallazgo del Criterio 2: las únicas 2 mediciones ciegas del
codo **dominante** (las únicas con cobertura suficiente para medirlo, ambas en revés de tres cuartos) dieron
un error medio de **27,2°** contra el sistema (11,9° y 42,5°), muy por encima del error agregado del codo
(12,5°, dominado por 16 mediciones del lado no dominante). **La causa no está separada**: puede ser el
sistema, la medición manual (escorzo, difícil de medir incluso a ojo — anotado así por Valentín en la
planilla) o ambas. Con n = 2 no hay conclusión formal. **Queda como trabajo futuro** ampliar esa validación
con más fotogramas del codo dominante.

### 4. Drive de perfil: orden estable, magnitud e instante no estables entre sesiones

- **Criterio 1:** 6 de 6 ordenables, cumple (orden `tp`).
- **Criterio 3:** el único grupo con señal de diferencia real entre sesiones en las dos métricas: separación
  cadera-hombro máxima (Δ = 6,03°, σ_w = 3,14°, p = 0,044) e instante del pico de torso desde la máxima
  separación (Δ = 156 ms, σ_w = 37 ms, p = 0,050), sin corrección por las 6 comparaciones.

El **orden** que reporta el sistema en este grupo es repetible; la **magnitud y el instante** no lo son entre
sesiones. Es el grupo de **menor confianza** de los seis, y se documenta así — no debe confundirse con el
drive de tres cuartos (salvedad 1), que es un grupo distinto con un problema distinto (no ordenable, no
"inestable entre sesiones"). *(Corrección de una atribución cruzada errónea entre ambos grupos, señalada por
Valentín el 29/9/2026; ver bitácora.)*

### 5. Criterio 2 del codo: el "cumple" es por la media; el p95 supera la meta

| | media | p95 | meta | veredicto |
| --- | --- | --- | --- | --- |
| codo | 12,5° | **36,4°** | < 20,6° | cumple (por la media) |
| rodilla | 8,5° | 19,2° | < 20,6° | cumple |

El p95 del codo (36,4°) **supera** la meta de 20,6°. El criterio del plan se define sobre el error medio, y
por esa definición el codo cumple; pero informar solo la media sin el p95 sería ocultar que 1 de cada 20
mediciones del codo se aleja bastante más de lo que la meta tolera. **Ambos números se informan siempre
juntos** en cualquier reporte o capítulo que cite este resultado.

## Consecuencia para el contrato del reporte (Etapa 5, no aplicado ahora)

**Corrección (29/9/2026, Valentín): "no ordenable" NO es un quinto estado.** R3 tiene cuatro estados —
correcto, desvío leve, alerta de carga, no auditable— y se quedan así. "No ordenable" es un **motivo** dentro
de la observación de secuenciación de una repetición, igual que los demás motivos que ya usa el motor
(`PicoSegmento.motivo`, `motivo_no_auditable`): cuando la separación entre pelvis y torso no supera el umbral
de resolución, esa repetición se muestra en **gris** (no auditable) con la explicación puntual —p. ej.
"simultaneidad al límite de resolución de 240 fps"—, sin inventar un color ni un estado nuevo. No hace falta
un campo nuevo en el contrato para esto.

Queda abierta, en cambio, una pregunta distinta para la Etapa 5: la salvedad 2 (perfil invertido) tiene picos
auditables **y** ordenables —el orden sí se determina— pero sin una referencia bibliográfica para juzgarlo
correcto o incorrecto. Ahí `correcto` no puede ser `null` por el motivo "no auditable" (R3 exige que `null`
signifique "no se pudo medir", y acá sí se midió), pero tampoco corresponde forzar `true` o `false` sin
fundamento (R4). Se deja para la Etapa 5 decidir cómo se representa un orden observado, auditable y
ordenable, sin veredicto de corrección por falta de referencia. No se modifica el contrato en esta decisión.

## Decisión final

**Sin repliegue de arquitectura.** Se continúa con la Etapa 5 sobre la cadena `pelvis → torso → brazo`
completa, con las cinco salvedades de arriba incorporadas al alcance declarado del sistema (CLAUDE.md,
Capítulos 3, 4, 6 y 7 — pendiente de redacción, igual que las decisiones 006, 010 y 011).

**Cierre administrativo:** merge de `etapa/4-cinematica` a `main`, etiqueta `v0.5.0-etapa4`, push.
