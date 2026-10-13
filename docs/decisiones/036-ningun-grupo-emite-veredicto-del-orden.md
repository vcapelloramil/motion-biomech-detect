# Decisión 036 — Ningún grupo emite veredicto del orden con una sola cámara (extiende la 035 a drive y revés)

**Fecha:** 13 de octubre de 2026
**Estado:** **APLICADA el 13/10/2026 por indicación de Valentín** (motor 0.5.3). La columna (b) de `RESPALDO_POR_GRUPO` **no se revisó** con el Paso B (queda para después de la demo, ver "Qué no cambia").
**Afecta a:** `backend/app/ensamblar_reporte.py` (`Suspension`, `RESPALDO_POR_GRUPO`) · decisiones 031 y 035 · `docs/resultados/paso-b-resumen.md` · `docs/ux/especificacion-frontend.md` §1 y §6 · Capítulo 7

---

## El problema

La 035 suspendió el veredicto del orden **del saque**. El Paso B terminó después con drive y revés (`docs/resultados/paso-b-resumen.md`) y repitió el patrón en el drive:

| Gesto | Perfil: cadera / tronco primero | Tres cuartos: cadera / tronco primero | Fisher (exploratorio) | Criterio 1 en perfil (sesión 2) |
| --- | --- | --- | --- | --- |
| Saque | 0 / 8 | 7 / 0 | p < 0,001 | cumple (1a 0,83 · 1b 1,00) |
| **Drive** | **1 / 7** | **3 / 0** | **p = 0,024** | **cumple (1a 0,83 · 1b 1,00)** |
| Revés | 3 / 3 | 0 / 5 | p = 0,182 | no cumple (1a 0,80 · 1b 0,50) |

Lo que importa de esta tabla:

1. **El drive de perfil cumple el Criterio 1 con el tronco primero, y el mismo orden se invierte en tres cuartos.** Es el mismo caso que el saque de perfil: el grupo que "pasa" el criterio de repetibilidad es el
   sospechoso (la repetibilidad no distingue un movimiento real de un sesgo fijo del encuadre).
2. **Hoy lo único que impide un veredicto del drive de perfil es que falta la referencia (a)**: `RespaldoGrupo(None, ...)`. Es una protección accidental: la 031 dice que *"si aparece una referencia, se agrega
   y el grupo pasa a tener veredicto si además cumple (b)"*. Si Valentín encuentra un pasaje de Elliott (2006) y se agrega, **cada drive de perfil saldría "desvío leve"** por la misma causa que motivó la 035.
3. **El revés no sigue el patrón** (tres cuartos: tronco primero en 5 de 5; perfil 3 contra 3 y sensible al método): no se puede afirmar que dependa del encuadre, pero tampoco hay forma de decir cuál es
   correcto. No es un grupo con veredicto posible.

## Decisión

**Ningún grupo (gesto × encuadre) emite veredicto del orden cadera → tronco.** La garantía vive en la tabla y es independiente de (a) y (b):

- `Suspension` (nuevo, `ensamblar_reporte.py`): si un grupo tiene una suspensión, `con_veredicto` es `False` **aunque haya referencia y el Criterio 1 se cumpla**. Solo se levanta a propósito
  (`suspension=None` en esa fila), con una medición independiente.
- Los seis grupos quedan suspendidos: saque (perfil y tres cuartos) y drive (perfil y tres cuartos) **por encuadre** (el orden cambia con el encuadre); revés (perfil y tres cuartos) **por método** (el orden no es
  confiable con una sola cámara y no se puede separar el gesto del sesgo de la medición).
- La prueba que lo garantiza (`test_la_suspension_gana_aunque_haya_referencia_y_el_criterio_1_se_cumpla`) fuerza (a) y (b) en verdadero **en cada uno de los seis grupos** y verifica que no sale `correcto`,
  `desvio_leve` ni `alerta_de_carga`, y que solo levantar la suspensión lo habilita.

### Texto para el jugador (sin literatura ni estadística)

- Saque y drive (la misma de la 035): *"El orden entre tu cadera y tu tronco cambia según desde dónde se grabó el golpe, y todavía no podemos asegurar cuál es el correcto. Por eso lo registramos sin evaluarlo."*
- Revés: *"El orden entre tu cadera y tu tronco en este golpe todavía no se puede medir con suficiente confianza con una sola cámara, y no podemos asegurar cuál es el correcto. Por eso lo registramos sin evaluarlo."*
- El **detalle técnico** lleva las cifras de cada gesto (7 de 7 contra 8 de 8; 3 de 3 contra 7 de 8; 5 de 5 en tres cuartos y 3 contra 3 en perfil, con la sensibilidad al giro axial).

## Qué no cambia

- **`criterio1_cumplido` de drive y revés sigue con las cifras del Paso A.** Revisarlo con el Paso B es el pendiente (3) de abajo; no cambia ningún veredicto porque la suspensión gana.
- **D (contraste del encuadre declarado con el visto)** sigue calibrado solo para el saque. Para drive y revés, hacerlo es el pendiente (1); mientras no esté, el reporte no avisa si el video no es del encuadre
  declarado (en esos gestos eso ya no puede producir un veredicto equivocado, porque no hay veredicto).
- **El contrato no cambia** (la observación sigue siendo `sin_evaluar`); el motor pasa a **0.5.3** porque el texto de las observaciones del drive y del revés cambia.
- **Los estados `correcto`, `desvio_leve` y `alerta_de_carga` siguen existiendo en el contrato**, pero con el orden suspendido y sin umbrales con referencia (E5.1), **el reporte real hoy solo produce
  `sin_evaluar` y `no_auditable`**. Las pantallas y la landing que prometen "cuatro estados siempre con nombre" y "veredicto" hay que reescribirlas (ver `docs/ux/auditoria-pantallas-13-10.md`).

## Consecuencias

- **El valor del producto deja de ser un juicio y pasa a ser medición y seguimiento del jugador consigo mismo en el mismo encuadre** (el sesgo es fijo por encuadre, así que cancela al comparar contra uno
  mismo). Propuesta de cómo comunicarlo: `docs/ux/valor-sin-veredictos.md`.
- **El Capítulo 7 gana un resultado más:** la dependencia del encuadre del orden cadera-tronco en dos de tres gestos y la no confiabilidad del tercero con una sola cámara, y que **los grupos que cumplen el Criterio 1
  son justamente los sospechosos**. Es un límite declarado del instrumento, no un fallo.
- **La suspensión se levanta, grupo por grupo, con una medición independiente de la pelvis** (cintas de color con un solo teléfono, `docs/protocolo-saques-tres-cuartos.md`; o dos cámaras simultáneas). Ver el
  orden de trabajo posterior a la demo en `docs/plan-mvp-punta-a-punta.md` §8.

## Pendientes, en el orden de Valentín (13/10)

1. **Calibrar D para drive y revés** con las poses del Paso B (`backend/.cache/corpus-real-pose-b`). El revés agrega una pregunta: por qué el tronco primero en tres cuartos.
2. **Criterio 3 con el tiempo real** (la métrica (ii), el instante del pico desde la separación máxima, depende del tiempo; la (i), la separación, no).
3. **`RESPALDO_POR_GRUPO`** (columna (b)) con las cifras del Paso B.
4. **Al final, y solo si hay tiempo antes de la defensa:** validación con cintas de color. **Prueba tentativa, sin diseñar.**
