# Decisión 035 — PROPUESTA: suspender el veredicto del saque de perfil hasta que el orden coincida entre encuadres

**Fecha:** 12 de octubre de 2026
**Estado:** **PROPUESTA, sin aplicar** (a decidir por Valentín antes de la demo del 28–30/10; es el bloqueante de la decisión 031)
**Afecta a:** `backend/app/ensamblar_reporte.py` (`RESPALDO_POR_GRUPO`) · decisión 031 · `docs/resultados/paso-a-resumen.md` · Capítulo 7

---

## El problema

La decisión 031 dejó **un solo grupo con veredicto**: el saque de perfil (referencia del orden: Kovacs y Ellenbecker 2011; Fleisig et al. 2003; Criterio 1 cumplido). Su orden modal medido era **tronco antes
que cadera**, así que **todo saque de perfil sale "desvío leve"**. La 031 dejó la validación "bloqueante de la demo": confirmar si ese orden es real o un artefacto, con el Paso A y las grabaciones nuevas.

El Paso A (12/10, `docs/resultados/paso-a-resumen.md`) ya está hecho. Resultados que importan:

1. **Con tiempo real y la tolerancia unificada (8,33 ms), el saque de perfil sigue cumpliendo el Criterio 1** en las dos sesiones (1a 0,83 y 0,80; 1b 1,00; siempre `tp`). Por la regla escrita en la 031,
   el veredicto se mantiene.
2. **Pero el orden depende del encuadre.** El mismo gesto, del mismo jugador: en **perfil** 0 de 9 repeticiones ordenables tienen la cadera primero; en **tres cuartos** 6 de 9 (Fisher p = 0,009,
   exploratorio). Un movimiento físico no puede depender de dónde está la cámara: **al menos un encuadre mide mal**.
3. El "tronco primero" **no se explica** por el reloj (corregido en el Paso A), por el filtro (cortes de 4 a 12 Hz) ni por la definición de la velocidad (el giro axial da el mismo sentido). **Sí** coincide
   con el encuadre donde la cadera lejana queda tapada (decisión 013 documenta lo mismo para el codo).

## Alternativas

| | Efecto | A favor | En contra |
| --- | --- | --- | --- |
| **A — Mantener la 031 tal cual** | Todo saque de perfil: "desvío leve", con la fuente del saque | Cumple la regla escrita; el reporte "evalúa algo" | Es muy probable que el desvío sea del instrumento y no del jugador. Un dato equivocado presentado como bueno (R3/R4) y justo en el gesto que los profesores van a mirar |
| **B — Suspender el veredicto del saque de perfil** (propuesta) | El orden se muestra como **"solo registrado"** con el motivo: "el orden medido en este encuadre no coincide con el de tres cuartos" | Honesto con lo medido; no se afirma lo que el propio Paso A pone en duda; reversible | El reporte del saque de perfil queda sin juicio (sigue mostrando el orden y los instantes) |
| C — Quitar también la referencia del saque | Ningún grupo con veredicto | Máxima prudencia | Pierde la única referencia citable de la tesis; no hace falta |

## Propuesta

**B.** Se agrega una **tercera condición** a la 031: **(c) el orden observado no debe depender del encuadre**; un grupo tiene veredicto solo si, para ese gesto, el orden modal medido en perfil y en tres
cuartos coincide (o el otro encuadre no es ordenable en la medición). Para el saque hoy **no coincide** (`tp` en perfil, `pt` en tres cuartos). Implementación: `RespaldoGrupo.criterio1_cumplido` pasa a
`False` para `("saque", "perfil")` con el comentario de esta decisión (cambio de una línea); la observación explica el motivo en el detalle técnico. **Se revierte** el día que el Paso B (240 Hz regularizados)
o un golpe grabado a la vez desde los dos encuadres muestre que el orden coincide.

## Consecuencias

- **El reporte del saque de perfil deja de decir "desvío leve"** y dice lo medido: el orden y la advertencia. La demo muestra un sistema que sabe cuándo no tiene con qué afirmar, que es el punto de R3.
- **El Capítulo 7 gana un resultado**: un criterio de validez (coherencia entre encuadres) que el propio sistema usa para retirar un veredicto.
- **Ningún grupo queda con veredicto** hasta nueva medición: el valor del reporte descansa en (b) datos, (c) consistencia entre golpes y la comparación consigo mismo (plan §8).
- Si se prefiere **A**, la demo debe llevar la aclaración de que el "desvío leve" del saque de perfil está **sin validar** (decisión 031, "Validación pendiente").
