# Decisión 040 — Indicador de «Regularidad» de la torsión (BORRADOR: solo propuesta, nada implementado)

**Fecha:** 20 de octubre de 2026
**Estado:** **BORRADOR con su análisis hecho; recomienda NO implementar el 1–10.** Pedido de Valentín (20/10): análisis y propuesta, **sin implementar**. Si no está implementado, probado y aprobado el **23/10**, queda como **trabajo futuro**.
**Afecta a (si se aprueba):** solo frontend (`frontend/src/lib/textos-reporte.ts`, `textos-evolucion.ts`, pantallas de la sesión y de Evolución, PDF). **No toca** el motor (0.5.5), el contrato (1.4) ni el servidor: usa la «variación típica» que `/sesiones/{id}/consistencia` y `/evolucion` ya calculan.
**Relacionada con:** 014 (variación robusta), 035 a 037 (sin veredicto), 039 (lenguaje de los reportes; ningún corte más angosto que el error medido).

---

## Qué es (y qué no es)

La **«Regularidad»** es la traducción, a una escala de **1 a 10 y una palabra**, de la **variación típica de la torsión cadera-hombro entre los golpes de una sesión**: qué tan parecida fue tu torsión de un golpe a otro. Hoy la variación se muestra como «±4°» (sesión del 25/9: ±4,4°).

- **No compara contra ninguna referencia** (ni otros jugadores ni un modelo ideal) y **no dice si el movimiento es el que conviene**: un golpe muy regular puede no ser el buscado, y uno variable puede serlo a propósito.
- **Nunca se llama «técnica», «calidad» ni «puntaje»** (ni en la pantalla ni en el PDF). El nombre es «Regularidad»; el ⓘ aclara «regular no significa correcto».
- **Solo la torsión.** El orden cadera-tronco casi nunca llega a 5 golpes distinguibles en tres cuartos (en la sesión del 25/9, 3 de 6), así que su repetibilidad no se traduce.

## Cuándo se calcula

- **Mínimo 4 golpes con la torsión medida**, el mismo mínimo que la variación típica (`MIN_GOLPES_DISPERSION`). Con menos, **un texto simple** y ningún número: «Con menos de 4 golpes medidos no se puede decir cuán regular fue tu torsión.»
- Usa la variación típica que ya devuelve el servidor (desvío robusto: mediana de las diferencias con la mediana × 1,4826, decisión 014), **sin recalcular nada**.

## La escala — cortes FIJADOS ANTES de calcular nada con las sesiones reales

**Referencia: la repetibilidad de la torsión medida en el Capítulo 7** (Criterio 3, `docs/resultados/criterio3.json`, corpus propio, un jugador, n = 6 por grupo y sesión; `docs/tesis/insumos-capitulo-7.md` §2, tabla del Criterio 3):

| Dato del Capítulo 7 | Valor |
| --- | --- |
| Variación típica dentro de una sesión (σ_w), los 6 grupos | **2,84 a 3,14°** (≈ 3°); saque de tres cuartos, 2,98° |
| Diferencia entre las medianas de dos sesiones consecutivas (Δ), los 6 grupos | **0,93 a 6,03°**; mediana de los seis ≈ **2,3°**; saque de tres cuartos, 2,71° |

**Regla:** `valor = 10 − 9 × (σ − 1,5) / (9 − 1,5)`, redondeado al entero más cercano y acotado entre 1 y 10 (cada punto vale 0,83° de variación típica σ).

| Punto de la escala | σ (variación típica) | Justificación |
| --- | --- | --- |
| **10** | **1,5° o menos** | La **mitad** de la variación típica medida en el corpus (≈ 3°) y **menos** que la diferencia habitual entre dos sesiones consecutivas (≈ 2,3°): golpes tan parecidos que el instrumento apenas los distingue. |
| **1** | **9° o más** | El **triple** de la variación típica del corpus y **1,5 veces** la mayor diferencia entre sesiones que se midió (6,03°): golpes muy distintos entre sí. |
| Intermedios | lineal entre ambos | No hay un dato que justifique otra forma. |

**Qué da cada σ** (se fija ahora, por la regla): 10 si σ < 1,92°; 9 si < 2,75°; 8 si < 3,58°; 7 si < 4,42°; 6 si < 5,25°; 5 si < 6,08°; 4 si < 6,92°; 3 si < 7,75°; 2 si < 8,58°; 1 desde 8,58°. **Control de cordura:** el σ típico del corpus (2,84 a 3,14°) da **8**.

**Palabras (cuatro bandas, neutras, que no califican):**

| Valor | Palabra | σ |
| --- | --- | --- |
| 9 y 10 | **muy regular** | menos de 2,75° |
| 7 y 8 | **bastante regular** | de 2,75° a 4,42° |
| 4, 5 y 6 | **algo variable** | de 4,42° a 6,92° |
| 1, 2 y 3 | **muy variable** | 6,92° o más |

## El criterio de la 039 aplicado a la propia escala (fijado antes de calcular)

La decisión 039 dice que **ningún corte puede ser más angosto que el error medido**. Acá el «error» es la **incertidumbre de la propia variación típica**, que con pocos golpes es grande. Se verifica **antes de decidir** con dos cálculos: (1) una **simulación** (datos normales con σ verdadero = 3°, n = 6 y n = 12; intervalo del 95 % del σ estimado y de la escala que le corresponde), independiente de las sesiones reales; (2) un **bootstrap** de cada sesión real. **Criterio:** si el intervalo del 95 % de un σ típico abarca **más de una banda de palabra**, el 1–10 transmite una precisión que el dato no tiene, y se propone mostrar la palabra y no el número (o el número como «aproximadamente»).

## Texto para el usuario (propuesta)

- **Sesión, en «Qué vimos»** (una línea más, con su ⓘ): «La regularidad de tu torsión fue **7 de 10: bastante regular**. Es qué tan parecida fue de un golpe a otro.» ⓘ
- **Menos de 4 golpes:** «Con menos de 4 golpes medidos no se puede decir cuán regular fue tu torsión.»
- **Evolución, en «Qué vimos»:** «La regularidad de tu torsión pasó de **10** a **7**: en tu última sesión los golpes variaron más entre sí. Es lo que cambió, no un juicio sobre tu técnica.» (y «se mantuvo en 7» si es igual). **Nunca** «mejoró» ni «empeoró».
- **ⓘ «Regularidad»:** «Qué tan parecida fue tu torsión (el ángulo entre tus caderas y tus hombros) de un golpe a otro dentro de la sesión. **10** es muy parecida (variación de 1,5° o menos) y **1** es muy distinta (9° o más). **Regular no significa correcto:** un movimiento puede ser muy regular y no ser el que busca tu entrenador, o variar a propósito. No se compara con otros jugadores y no mide si el movimiento es el que buscás.»
- **No va en «En una frase»** (regla de la 039: sin números).

## Lo que cambiaría en el código (no se hace ahora)

- `regularidadDe(variacion: number | null, golpesMedidos: number)` → `{ valor, palabra } | null` en `textos-reporte.ts` (función pura, 15 líneas), con los cortes como constantes exportadas.
- Una línea en `textosDeSesion` y en `textosDeEvolucion`; una entrada del glosario.
- Pruebas: los cortes exactos (los 10 puntos y los 4 límites de palabra), el mínimo de 4 golpes, el texto de Evolución con «pasó de a» y «se mantuvo», la prueba de palabras prohibidas (que además prohíba «técnica», «calidad» y «puntaje» fuera de la negación del ⓘ) y el caso de las sesiones reales.
- **Esfuerzo:** ≈ 0,5 a 0,75 día. **Motor y servidor: no se tocan.**

## Riesgos de lectura

1. **Un número del 1 al 10 se lee como una nota** aunque se lo llame «regularidad»: el 10 parece «lo mejor». Mitigación: la palabra va primero, el ⓘ lo aclara y el texto nunca compara.
2. **Falsa precisión con pocos golpes** (ver el cálculo de abajo).
3. **Un jugador puede perseguir el 10** repitiendo siempre el mismo movimiento aunque no sea el que le conviene. El aviso del ⓘ lo dice, pero el riesgo existe.
4. **La variación mezcla al jugador con la medición** (el error de la propia torsión): no se puede separar.

## Alternativas

- **A (la pedida):** 1–10 + palabra.
- **B:** solo la palabra (cuatro bandas) con la variación en grados en el detalle. **Más honesta con pocos golpes y menos parecida a una nota.**
- **C:** no mostrar nada nuevo: la variación típica ya está en «Qué vimos» y en Evolución.

---

## Cálculo (hecho DESPUÉS de commitear los cortes: commit `9e270f8`)

Script de solo lectura sobre la base de producción (`resumen_de_sesion` del servidor y el desvío robusto de la decisión 014); semilla fija. Cortes y palabras: los de arriba, sin cambios.

**Control de cordura:** el σ típico del corpus (2,84; 2,98; 3,14°) da **8** en los tres casos.

### Las sesiones reales

| Sesión | Golpes con torsión | Variación típica σ | Valor (1–10) | Palabra | Si se saca el golpe más lejano |
| --- | --- | --- | --- | --- | --- |
| **24/9** · saque · tres cuartos (`e46264bf`) | 6 | **1,11°** | **10** | muy regular | — |
| **25/9** · saque · tres cuartos (`e807c36e`) | 6 | **4,37°** | **7** | bastante regular | sin el golpe 6 (11,2°): σ 3,11° → **8** |
| 24/9 · saque · tres cuartos (`3a101dd3`, 1 golpe) | 1 | — | — | *«Con menos de 4 golpes medidos…»* | — |
| 24/9 · revés · tres cuartos (`97ca033b`) | 1 | — | — | *«Con menos de 4 golpes medidos…»* | — |
| 24/9 y 25/9 · saque de perfil, 25/9 · revés (3 sesiones) | 0 | — | — | *«Con menos de 4 golpes medidos…»* | — |

Evolución diría, entre el 24/9 y el 25/9: «La regularidad de tu torsión pasó de **10** a **7**: en tu última sesión los golpes variaron más entre sí.»

### Qué tan firme es ese número (el criterio de la 039 aplicado a la escala)

**Simulación** (datos normales; 20 000 repeticiones por fila; el σ verdadero 3,7° es el que hace que el σ *estimado* típico con 6 golpes sea ≈ 3°, como en el corpus, porque el estimador robusto con pocos golpes subestima):

| Golpes por sesión | σ verdadero | Mediana del σ estimado | Intervalo del 95 % del σ estimado | Valores que abarca | Reparto de las palabras |
| --- | --- | --- | --- | --- | --- |
| 4 | 3,7° | 2,48° | 0,44 a 6,36° | **4 a 10** | muy regular 57 % · bastante regular 29 % · algo variable 13 % |
| **6** | 3,7° | 2,90° | 0,79 a 6,39° | **4 a 10** | muy regular **46 %** · bastante regular 36 % · algo variable 16 % |
| 12 | 3,7° | 3,34° | 1,45 a 5,97° | **5 a 10** | muy regular 30 % · bastante regular 51 % · algo variable 19 % |
| 6 | 5,0° | 3,97° | 1,06 a 8,73° | **1 a 10** | las cuatro palabras (10 % a 33 % cada una) |

El bootstrap de las dos sesiones reales (10 000 remuestreos) da intervalos que no sirven con 6 golpes: 24/9 de 0,00 a 3,11° (valores 8 a 10) y 25/9 de 0,00 a 15,34° (valores 1 a 10), porque con 6 datos el desvío robusto puede dar 0.

**Lectura:** **no se cumple el criterio.** Con 6 golpes (lo habitual), un jugador cuya variación verdadera es la típica del corpus recibiría, según la muestra, desde un «4 algo variable» hasta un «10 muy regular», y casi la mitad de las veces un 9 o 10. **Cada punto de la escala vale 0,83° de σ, pero el intervalo del 95 % del σ con 6 golpes mide unos 5,6°, o sea unos 7 puntos de la escala: el 1–10 es unas 7 veces más fino que el dato.** La diferencia entre el 24/9 (10) y el 25/9 (7) es, en gran parte, ruido de muestreo (un solo golpe, el 6, la mueve de 7 a 8) y **Evolución la contaría como «los golpes variaron más entre sí»** con una confianza que el dato no tiene. La misma incertidumbre afecta a la «variación típica ±4°» que ya se muestra; el indicador no agrega información, **le agrega aspecto de medida exacta**.

## Recomendación

1. **No implementar el 1–10 para el 23/10.** Queda como **trabajo futuro**, y no por falta de tiempo: por el resultado de arriba.
2. **Si se quiere algo para la demo, la alternativa B (solo la palabra), con dos cambios:** (a) **tres** bandas y no cuatro, con cortes que el dato pueda sostener (por ejemplo «bastante parecidos» por debajo de 3,6°, «algo variables» de 3,6° a 6,9° y «muy variables» desde 6,9°), y (b) **solo con 8 golpes o más**, no con 4. Aun así, con 12 golpes el intervalo del 95 % abarca dos o tres bandas: la palabra debería decir «aproximadamente» y **Evolución no debería comparar la palabra entre sesiones** (dos sesiones solo se comparan si la diferencia de σ supera la incertidumbre).
3. **Alternativa C (la que prefiero hoy):** dejar la variación típica en grados, con su ⓘ, y agregar en el ⓘ de la variación típica una línea: «Con 6 golpes esta cifra puede moverse varios grados si repetís la sesión.» Honesta y sin nota.
4. **Camino futuro con mérito:** una **«regularidad habitual»** que junte los golpes de varias sesiones (≥ 18 golpes, por ejemplo con las medianas de `variacion_habitual`), donde la incertidumbre baja a la mitad. Necesita decidir cuántas sesiones juntar; no es para esta entrega.

**Decisión pendiente de Valentín:** elegir A (implementar igual, sabiendo que el 1–10 es unas 7 veces más fino que el dato), B, C o dejar la 040 como trabajo futuro.
