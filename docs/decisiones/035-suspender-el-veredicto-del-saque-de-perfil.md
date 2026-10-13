# Decisión 035 — El saque no emite veredicto del orden mientras el orden dependa del encuadre; y se contrasta el encuadre declarado con el que se ve

**Fecha:** 12–13 de octubre de 2026 (reescrita con el Paso B del saque completo)
**Estado:** **APLICADA el 13/10/2026 con el OK de Valentín: B y D** (motor 0.5.2). **C queda como trabajo futuro** (tres cuartos como encuadre evaluado, tras una validación independiente).
**Afecta a:** `backend/app/ensamblar_reporte.py` (`RESPALDO_POR_GRUPO` y el aviso de encuadre) · decisión 031 · `docs/resultados/paso-b-saque.md` · Capítulo 7

---

## El problema

La decisión 031 dejó **un solo grupo con veredicto**: el saque de perfil. Su orden medido es **tronco antes que cadera**, así que todo saque de perfil sale **"desvío leve"**. Quedó "bloqueante de la demo":
había que confirmar si ese orden es real o un artefacto (del corpus convertido, o del encuadre).

## Qué se sabe ahora (Paso A y Paso B del saque, `docs/resultados/paso-a-resumen.md` y `paso-b-saque.md`)

| | Perfil | Tres cuartos |
| --- | --- | --- |
| Corpus convertido (Paso A, 120,2 fps) | cadera primero 0, tronco primero 9 | cadera primero 6, tronco primero 3 |
| **Originales a tasa real (Paso B, 200 fps → 240 Hz)** | **cadera primero 0, tronco primero 8** (2 dentro) | **cadera primero 7, tronco primero 0** (11 dentro) |

1. **No es un efecto del corpus convertido:** con los originales el perfil sigue en "tronco primero" (8 de 8 ordenables).
2. **No es el reloj, el filtro ni la definición de la velocidad** (Paso A).
3. **Depende del encuadre:** 0 de 8 contra 7 de 7 (Fisher exacto, p = 0,0002; exploratorio). Un movimiento físico no depende de la cámara: **al menos un encuadre mide mal**, y con los datos de que se dispone **no se
   puede decir cuál** (elegir el que coincide con lo esperado sería elegir por el resultado).
4. **El golpe del celular que parecía contradecirlo** (cadera 13 ms antes, "correcto") **es un saque de tres cuartos subido como "perfil"**: el archivo es de la toma 02 de tres cuartos (`IMG_6391`) y su giro de
   hombros (59°) cae en el de tres cuartos del corpus (50–83°), no en el de perfil (26–42°). Confirma la dependencia del encuadre, y deja un problema aparte: el sistema **aplicó el veredicto de un grupo a un video
   que no era de ese grupo**, porque el encuadre es lo que declara el usuario.

## Alternativas

| | Qué hace | A favor | En contra |
| --- | --- | --- | --- |
| **A — Mantener la 031** | Todo saque de perfil: "desvío leve" con la fuente del saque | Cumple la regla escrita | Muy probablemente el desvío es del instrumento y no del jugador (R3/R4); justo en el gesto que van a mirar los profesores |
| **B — Suspender el veredicto del saque de perfil** (recomendada) | El orden se muestra "solo registrado", con el motivo, en los dos encuadres | Honesto con lo medido; reversible; **tres cuartos ya no tiene veredicto** (no cumple el Criterio 1: 1a 0,17 y 0,50), así que **ningún grupo emite veredicto** | El reporte del saque queda sin juicio (sigue mostrando el orden y los instantes) |
| **C — Tres cuartos como encuadre evaluado para el saque** | Veredicto "correcto" a las repeticiones ordenables de tres cuartos (7 de 7 con la cadera primero) y "no ordenable" al resto | Es el encuadre cuyo orden coincide con la referencia; 1b = 1,00 en las dos sesiones | **Elegiría el encuadre por el resultado.** 11 de 18 quedan "no ordenables" y no cumple el Criterio 1 (1a < 0,8); hace falta una regla nueva y una validación independiente. **No antes de la demo** |
| **D — Contrastar el encuadre declarado con el que se ve** (complemento de B, o de A) | Se mide el giro de la línea de hombros en la preparación y, si no coincide con el encuadre declarado, el veredicto **no se emite** y se avisa ("este video parece de tres cuartos") | Barata (se calcula de la pose ya extraída); en el corpus los grupos no se solapan (42° contra 50°); evita el caso real que acaba de pasar | Umbral calibrado con 22 repeticiones de un jugador: detecta una discrepancia **gruesa**, no mide el ángulo; hace falta una preparación de ≥ 0,8 s antes del pico |

## Propuesta

**B + D, en dos pasos independientes:**

1. **B:** `RESPALDO_POR_GRUPO[("saque", "perfil")].criterio1_cumplido = False` (cambio de una línea, con el motivo en el comentario). El texto para el jugador, sin literatura ni estadística: *"El orden entre tu cadera y tu
   tronco cambia según desde dónde se grabó el golpe, y todavía no podemos asegurar cuál es el correcto. Por eso lo registramos sin evaluarlo."* El detalle técnico lleva el fundamento (dependencia del encuadre).
2. **D:** una función pura `encuadre_visto(secuencia)` (giro de hombros en la preparación, umbral ~46°) y, si el encuadre declarado no coincide, una **observación en el reporte** ("el video parece de tres cuartos; lo
   declaraste como perfil") y **ningún veredicto**. Se prueba con los 22 casos del corpus y con el golpe del celular. ~0,5 sesión.

**Se revierte** (B) el día que el orden coincida entre encuadres con una medición independiente (cintas de color con un solo teléfono, `docs/protocolo-saques-tres-cuartos.md`) o con la grabación simultánea desde dos
ángulos, que queda como trabajo futuro.

## Consecuencias

- **La demo muestra un sistema que sabe cuándo no tiene con qué afirmar** y que detecta que el video no es del encuadre declarado: es el punto de R3.
- **Ningún grupo queda con veredicto** hasta nueva medición: el valor del reporte descansa en los datos articulares (ya en el reporte), la consistencia entre golpes y la comparación consigo mismo (plan §8).
- **El Capítulo 7 gana dos resultados:** la dependencia del encuadre del orden (con el contraste contra el corpus convertido y contra los originales) y el criterio de coherencia entre encuadres que el propio sistema usa.
- Si se prefiere **A**, la demo debe llevar la aclaración de que el "desvío leve" del saque de perfil está **sin validar** y el reporte del golpe del celular debería leerse como un saque de tres cuartos.

## Aplicación (13/10/2026)

- **B:** `RespaldoGrupo.depende_del_encuadre` (condición (c) de la 031): el saque, en perfil y en tres cuartos, **no emite veredicto**; la tarjeta dice *"El orden entre tu cadera y tu tronco cambia según desde dónde se grabó
  el golpe, y todavía no podemos asegurar cuál es el correcto. Por eso lo registramos sin evaluarlo."* y el detalle técnico lleva el fundamento (7 de 7 contra 8 de 8).
- **D:** `engine/encuadre.py` (giro de la línea de hombros en la preparación, de 0,8 a 0,3 s antes del pico del tronco; perfil ≤ 42°, tres cuartos ≥ 50°, entre los dos no se afirma nada) y, en el reporte, una
  observación gris *"El video parece grabado de tres cuartos, pero elegiste perfil. Revisá el encuadre antes de comparar tus resultados."* (o la inversa). **No bloquea la carga**: el análisis y el reporte salen
  completos; solo se retira el veredicto y se avisa. **Solo para el saque** (calibrado con 22 repeticiones); drive y revés se agregan con las cifras del Paso B.
- **Pruebas:** 505 pasan en el servidor (las de B y D y las del módulo puro). **Contra el corpus:** las 28 repeticiones válidas del saque se clasifican en el encuadre con que se grabaron (**0 avisos falsos, 0 sin
  afirmar**; la calibración es de la misma muestra, así que es una verificación de consistencia y no una validación independiente) y el caso real del 12/10 (59°) cae en tres cuartos.
- **Sin cambio de contrato** (1.3): el aviso es una observación `no_auditable` más.
