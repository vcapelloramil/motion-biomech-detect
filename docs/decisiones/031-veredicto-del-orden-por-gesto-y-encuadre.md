# Decisión 031 — El veredicto del orden cadera → tronco solo existe donde hay referencia y Criterio 1 cumplido; el resto se documenta "sin evaluar"

**Fecha:** 9 de octubre de 2026
**Estado:** **aprobada por Valentín (9/10/2026)**. **Se revisa cuando se haga el recálculo del corpus con la tasa real (Paso A de `docs/plan-recalculo-corpus-tasa-real.md`)**: la condición (b) usa cifras que ese
recálculo puede cambiar. **Bloqueante para la demo a los profesores** (no para el flujo de punta a punta): ver "Validación pendiente".
**Afecta a:** `backend/app/ensamblar_reporte.py` (`RESPALDO_POR_GRUPO`) · contrato del reporte (v1.1 → **v1.2**, aditiva) · decisiones 011, 014, 015 y 024 · especificación de frontend §6 · Capítulo 7

---

## El problema

La decisión 015 dejó abierta para la Etapa 5 una pregunta: cómo representar un orden **medido y ordenable** pero **sin referencia** para juzgarlo correcto o incorrecto. Mi primera
propuesta (9/10) emitía veredicto solo en el revés y dejaba saque y drive en gris con el estado `no_auditable`. Valentín la rechazó por dos motivos:

1. **Contradecía la tesis.** El apartado 4.3.3 (tabla 4.8) sustenta el saque con Kovacs y Ellenbecker (2011) y Fleisig et al. (2003): es el gesto con respaldo bibliográfico, y yo
   lo había dejado sin veredicto.
2. **`no_auditable` significa "no se pudo medir"** (R3). El orden sí se midió; lo que falta es respaldo para evaluarlo.

## Decisión

**Un veredicto (`correcto` / `desvio_leve`) sobre el par cadera → tronco se emite solo si, para ese gesto y encuadre, se cumplen las dos condiciones:**

- **(a)** hay referencia bibliográfica del orden esperado (la que cita la tesis), y
- **(b)** el Criterio 1 se cumplió para ese grupo (decisión 014: 1a ≥ 0,8 y 1b ≥ 0,8, par pelvis-torso, tolerancia de 1 fotograma, sesión 2).

**Donde falta alguna, el orden se documenta como `sin_evaluar`**: la misma etiqueta que el balanceo del brazo (decisión 011). No es un quinto estado del semáforo (R3 sigue teniendo
cuatro, y `Severidad` sigue coincidiendo con `alertas.severidad`): es un valor más de `Observacion.severidad` (contrato v1.2) para un dato que se informa sin juicio.

El veredicto es **del par cadera → tronco**, el único comparable con la literatura (decisión 011). El brazo se informa siempre como `sin_evaluar`, con o sin veredicto en el par.
Si la cadera y el tronco quedan a **1 fotograma o menos** (decisión 014), no se ordenan y la observación es `no_auditable` con el motivo "simultaneidad al límite de resolución"
(decisión 015, corrección del 29/9): ahí sí es "no se pudo establecer".

## Qué grupos quedan con veredicto

Cifras: `docs/resultados/criterio1-resumen.md`, sesión 2, τ = 1 fotograma (primaria), par pelvis-torso.

| Gesto · encuadre | (a) referencia del orden | (b) Criterio 1 (1a · 1b) | Veredicto |
| --- | --- | --- | --- |
| **Saque · perfil** | sí: Kovacs y Ellenbecker (2011); Fleisig et al. (2003) | **cumple** (1,00 · 1,00) | **sí** |
| Saque · tres cuartos | sí | no cumple (0,50 · 1,00: ordenable en 9 de 18) | no: sin evaluar |
| Drive · perfil | no (tabla 4.8: "conjunto reducido de reglas", sin cita) | **cumple** (1,00 · 1,00) | no: sin evaluar |
| Drive · tres cuartos | no | no cumple (0,00: ninguna ordenable) | no: sin evaluar |
| Revés · perfil | no | no cumple (0,67 · 0,75) | no: sin evaluar |
| Revés · tres cuartos | no | **cumple** (1,00 · 0,83) | no: sin evaluar |

**Con la regla, el único grupo con veredicto es el saque de perfil.** Es el resultado de un cruce, no de una elección: el saque es el único con (a); el drive de perfil y el revés
de tres cuartos cumplen (b) pero no (a). Si Valentín dispone de una referencia del orden esperado para drive o revés, se agrega en `RESPALDO_POR_GRUPO` y esos grupos pasan a
tener veredicto sin tocar nada más.

> **Corrección de un dato del pedido:** según `criterio1-resumen.md` el Criterio 1 **no** lo cumplió solo el drive de perfil. A τ = 1 lo cumplen **tres** grupos (saque de
> perfil, drive de perfil y revés de tres cuartos); a τ = 2 y 3 quedan **dos** (saque de perfil y drive de perfil). La frase "el único grupo que cumple el Criterio 1 es `drive|perfil`"
> de la decisión 029 (con "1a = 0,83", que es la cifra de τ = 3) **no coincide con esa tabla**: a τ = 3 el saque de perfil también cumple (1,00). **No lo investigué** (regla
> de no abrir investigaciones nuevas); queda anotado para reconciliarlo al hacer el recálculo (Paso A). Esta decisión usa la tabla formal de la 014.

## Consecuencia que hay que tener presente

En el saque de perfil el orden modal medido es **tronco antes que cadera** (`tp`) en **6 de 6** repeticiones: la coincidencia con el orden esperado (1c) es **0,00**. Con esta regla
**todo saque de perfil con ese orden sale como `desvio_leve`** (nunca `alerta_de_carga`: no hay umbral con referencia, E5.1) y cita a Kovacs y Ellenbecker (2011) y Fleisig et al.
(2003). La decisión 015 (salvedad 2) había evitado esa etiqueta porque no existe fuente para el sentido observado; puede ser una característica del jugador, o un artefacto de la
vista de perfil monocular. **Es la regla que se pidió y se implementó; este es el efecto visible y queda anotado para el Capítulo 7.** Si al recalcular (Paso A) el orden de este
grupo cambia o deja de cumplir (b), el veredicto desaparece solo al actualizar la tabla.

## Validación pendiente — BLOQUEANTE para la demo a los profesores (decisión de Valentín, 9/10)

Que el único grupo con veredicto (saque de perfil) dé **tronco antes que cadera en 6 de 6** significa que **todo saque de perfil saldría "desvío leve"**. Antes de que lo vean los profesores hay que
confirmar si ese orden es **real o un artefacto**: (i) de la vista de perfil monocular, o (ii) de la escala ×2 y los fotogramas irregulares del corpus horneado (decisión 030).

- **Cómo:** hacer el **Paso A** del recálculo apenas pase la prueba de punta a punta, y compararlo con las **grabaciones nuevas** de Valentín (archivos "Actual", con tiempos reales y la regularización
  temporal de E0). Si con tiempos reales el orden deja de ser tronco → cadera, o el grupo deja de cumplir (b), se actualiza `RESPALDO_POR_GRUPO`.
- **Qué bloquea:** mostrar el reporte del saque de perfil en la demo. **No bloquea** el flujo de punta a punta (registro, carga, procesamiento, reporte), que puede probarse con el veredicto como está.
- **Mientras tanto** el texto del reporte ya dice qué se observó y cita la fuente; no promete que el desvío sea un hallazgo.

## Referencias

Las dos del saque, **verificadas por Valentín contra la lista de Referencias de la tesis** (9/10/2026):

- Kovacs, M., & Ellenbecker, T. (2011). An 8-stage model for evaluating the tennis serve: Implications for performance enhancement and injury prevention. *Sports Health, 3*(6), 504–513. https://doi.org/10.1177/1941738111414175
- Fleisig, G., Nicholls, R., Elliott, B., & Escamilla, R. (2003). Kinematics used by world-class tennis players to produce high-velocity serves. *Sports Biomechanics, 2*(1), 51–64. https://doi.org/10.1080/14763140308522807

(Yo no pude cotejar los DOI: no tengo la lista en el repositorio; tomo la verificación de Valentín.) Martin et al. (2014) figura en el texto de los capítulos 3 y 4 (apartado 3.3.4.3), pero
queda sin ficha completa y sin uso acá. No se citan capítulos en el reporte. **Martin et al. (2014)** (el tronco gira más tarde en los lesionados) **no** respalda "tronco antes que cadera", así que no se cita en estos veredictos; queda para la
alerta por giro tardío del tronco (E5.1), que necesita un umbral con referencia.

## Qué cambió en el código

- `RESPALDO_POR_GRUPO` y `respaldo_del_grupo()` en `ensamblar_reporte.py`: una fila por gesto y encuadre, con (a) y (b) y la cifra que la sustenta.
- Contrato **v1.2** (aditivo): `Observacion.severidad` admite `sin_evaluar`; `docs/contrato-reporte.ejemplo.json` incluye una observación así. Los reportes 1.0 y 1.1 siguen válidos.
- `secuencia_correcta` (columna) toma el mismo valor que el JSON: `null` donde no hay veredicto.
- Pruebas: la tabla completa (qué grupos tienen (a), (b) y veredicto), cada celda sin evaluar con su motivo, la tolerancia de 1 fotograma y el vocabulario de R2 sobre los seis grupos.
