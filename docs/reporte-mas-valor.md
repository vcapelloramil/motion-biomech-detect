# Que el reporte evalúe más, sin inventar — respuesta al punto 8 del 12/10/2026

**Estado:** análisis y propuesta (no cambia reglas). Lo único que ya se hizo es (d), el lenguaje. Lo demás espera tu decisión; el orden propuesto está en
`docs/plan-mvp-punta-a-punta.md` §8. Fuentes: `docs/tesis/capitulo-3-marco-teorico.md`, `capitulo-4-marco-tecnologico.md`, decisiones 011, 013, 014, 015 y 031, `backend/app/engine/kinematics.py`.

## El diagnóstico en una frase

Un reporte casi siempre gris no es un problema de lenguaje: es que **la tesis tiene una sola referencia citable del orden (el saque) y ninguna con rangos numéricos**. Lo que sí se
puede hacer sin inventar es (1) mostrar más datos medidos, con su confianza y como dato, y (2) evaluar **contra el propio jugador**, que es el eje del proyecto (CLAUDE.md §3) y no
necesita literatura.

## (a) ¿Respaldan Elliott (2006) o Kibler el orden cadera → tronco en drive y revés?

**No, con lo que hay en los textos del repositorio. No lo puedo afirmar y no lo agregué a `RESPALDO_POR_GRUPO`.**

| Fuente | Dónde aparece | Qué dice ahí | ¿Respalda el orden en golpes de fondo? |
| --- | --- | --- | --- |
| **Elliott (2006)** | **No aparece en los capítulos 3 ni 4.** Solo en la maqueta de Lovable (`frontend/src/lib/reporte-mock.ts`, `REFERENCIAS`, líneas ~205–210), con el comentario "confirmar cada entrada contra la bibliografía del Capítulo 2 antes de la entrega" | La maqueta le asigna "orden proximal-distal de los picos; flexión de rodilla en la carga" | **No verificable.** Es texto generado por la herramienta de la maqueta, no un pasaje de la tesis |
| **Kibler** | Capítulo 3, apartado 3.3.3.1 ("Definición"): *"Kibler: piernas y tronco generan 51–55 % de la energía que llega a la mano."* **Sin año** | Una fracción de energía en la cadena cinética del tenis en general | **No.** No habla del orden temporal ni de drive/revés. (La maqueta lo cita como "Kibler (1995)", otro año del que aparece en tu mensaje: hay que fijar cuál es) |
| Kovacs y Ellenbecker (2011); Fleisig et al. (2003) | Capítulo 4, apartado 4.3.3, tabla de alcance: "saque... con mayor respaldo bibliográfico"; Capítulo 3, 3.4.2.2 (velocidades) | Saque | Solo el saque. Para drive y revés la propia tabla dice "un conjunto reducido de reglas", sin cita |

**Para cerrarlo** necesito de vos el pasaje: abrir el artículo, buscar dónde describe la secuencia cadera → tronco → brazo en el **drive/revés** y pasarme **página y frase**. Con eso
es una línea en `RESPALDO_POR_GRUPO`. Sin eso, el reporte dice "todavía no tenemos un patrón de referencia" y es verdad.

**Antes de agregarlo, un aviso que importa más que la cita.** Si la referencia aparece, los grupos que pasarían a tener veredicto son **drive de perfil** y **revés de tres cuartos**
(los que cumplen el Criterio 1). En ambos el orden modal medido es `tp` (**tronco primero**, 6 de 6 y 5 de 6): casi todo drive de perfil saldría "desvío leve", igual que hoy el saque de
perfil (decisión 031). Es la misma pregunta abierta: ¿ese `tp` es real o un artefacto del perfil monocular y del corpus a 120 fps? **Conviene hacer el Paso A antes**: puede que la
respuesta cambie qué grupos tienen veredicto, y evita publicar tres "desvío leve" por una causa que no es el jugador.

## (b) Más mediciones: qué calcula el motor, qué tiene rango citable y qué se puede mostrar como dato

La tabla 4.7 pone como núcleo "ángulos articulares" y "separación cadera-hombro". El motor los **calcula** (`engine/kinematics.py`: `serie_angulo_articular`,
`serie_separacion_cadera_hombro`), pero el reporte hoy **solo trae velocidades pico y orden** (`metricas` = `velocidad_pico_*`). Las magnitudes que las maquetas muestran con estado
(42°, 118°, 27°) son **valores de ejemplo de la maqueta**: ninguna tiene un rango en el texto de la tesis.

| Magnitud | ¿La calcula el motor? | ¿Está en el reporte? | Validación propia | Referencia citable (texto de la tesis) | Qué se puede mostrar |
| --- | --- | --- | --- | --- | --- |
| Orden de picos cadera → tronco → brazo | Sí | Sí | Criterio 1, por grupo (1a/1b) | Saque: Kovacs y Ellenbecker (2011); Fleisig et al. (2003), **sin valores**. Drive/revés: ninguna | Veredicto en saque de perfil; dato en el resto |
| Velocidad angular pico por segmento (°/s) | Sí | Sí (detalle técnico) | La escala depende de la tasa real (ya leída); sin goniometría | Fleisig (2003), saque: cadera 440, torso 870 °/s — hoy se usan como **techo de plausibilidad**; el brazo **no es comparable** (decisión 011) | Dato; "sin evaluar" |
| **Separación cadera-hombro máxima (°)** | **Sí** | **No** | Criterio 3 (métrica i): consistente en la mayoría de los grupos | La tesis la llama "de las más confiables" (3.3.3.2; 3.3.4.2 fila 3) pero **no da un rango en grados** | **Dato con confianza**, sin estado de juicio |
| **Flexión de rodilla (°), mínimo de la ventana** | **Sí** (`rodilla`, por lado) | **No** | Criterio 2: error medio **8,5°**, p95 19,2° (< 20,6°) | Solo cualitativa (3.3.3.3): "poca flexión de rodilla implica 23–27 % más carga en hombro y codo". **Sin grados** | **Dato** con el error esperable declarado (±9°) |
| Ángulo de codo (°) | Sí | No | Criterio 2: error medio 12,5°, **p95 36,4°**; el codo dominante (n = 2) dio 27,2° | Ninguna | Dato con **advertencia** (cobertura del codo dominante baja, decisiones 013 y 015) |
| Tronco-muslo (hombro-cadera-rodilla) | Sí | No | Ninguna | Ninguna | No mostrar todavía |
| Rotación interna del hombro | **No** (no se mide con 17 puntos, 3.3.3.4) | — | — | — | Limitación declarada |
| Instante de impacto | **No** (frágil, 3.4.2.5) | — | — | — | Fuera: no se puede anclar "ángulo en el impacto" |

**Lectura.** Hay **cuatro magnitudes mostrables como dato hoy** (separación cadera-hombro máxima, flexión de rodilla mínima, ángulo de codo y, ya mostrada, la velocidad pico) y
**ninguna con rango de referencia citable**. Los umbrales poblacionales además figuran en la tesis como **funcionalidad simulada** ("valores de literatura de élite, con advertencia de
extrapolación", apartado 4.3.3). Mostrarlas con verde/ámbar sería inventar el umbral (R4). Mostrarlas como **dato con confianza y error esperable** es honesto, llena el reporte y
prepara la comparación consigo mismo (c), que es donde esos números adquieren sentido.

**Costo:** ~1 sesión. Calcular en el ensamblador los tres valores sobre la ventana del golpe (mismo espacio métrico que ya filtra E3), con su confianza y `auditable`, como
`metricas` del contrato (que ya admite cualquier nombre); una tabla en el nivel 3 y una línea en el nivel 1 solo si el dato es auditable. Las fotos clave ya muestran el esqueleto en el
pico, pero **sin ángulos dibujados**: dibujarlos es medio día más y se justifica recién con estos datos.

## (c) Comparación consigo mismo desde la primera sesión

**Qué se puede decir sin literatura con una sesión de varios golpes** (todo es *conteo o dispersión de lo medido*, nada importado):

1. **Repetibilidad del orden:** "en 5 de 6 golpes ordenables el orden fue el mismo". Es el **Criterio 1b del propio proyecto** (≥ 0,8 del mismo orden entre los ordenables): una regla ya
   pre-registrada, no una cifra nueva. Con ≥ 5 golpes ordenables puede llevar estado ("repetible" / "variable").
2. **Dispersión del instante del tronco y de la separación cadera-hombro:** "tu tronco llegó al pico entre 0,29 y 0,33 s; variaste 18 ms" (la dispersión ya está en el contrato:
   `resumen.dispersion_instante_pico_torso_ms`). **Va como dato**, junto al error de medición (~8 ms): lo que varía menos que eso no se distingue de la medición.
3. **Golpe que se aparta del resto:** el golpe cuyo instante se aleja de la mediana de la sesión más que la dispersión de los demás (regla robusta, con MAD, la de la decisión 014).

**Lo que no se puede todavía:** poner **verde/ámbar** a la dispersión. Para eso hace falta un umbral y el único que existe es la regla del Criterio 3 (Δ ≤ σ_w) entre **sesiones**,
que pide ≥ 2 sesiones comparables. Por eso la recomendación es: **desde la primera sesión, 1 y 2 y 3 como datos y la repetibilidad del orden con estado; el estado de la dispersión,
desde la segunda sesión**, con la regla que ya está congelada. No es una limitación de implementación: es no inventar un número.

**Costo estimado: 1,5 a 2 sesiones**, además de la carga de varios golpes (que el plan ya cuenta en el rediseño de Cargar):

| Pieza | Esfuerzo |
| --- | --- |
| Agregador puro por sesión (orden modal, 1b, dispersión, atípicos) + pruebas | 0,5 |
| Escribirlo en `reportes_sesion` (`componentes`/`observaciones`, tabla ya existente) al completarse cada golpe | 0,5 |
| Vista de sesión en la Biblioteca: tarjetas "Tus golpes entre sí" y lista de golpes | 0,5–1 |

Es lo que **más valor le da al reporte con menos esfuerzo** una vez que haya sesiones de varios golpes: un reporte de 6 golpes deja de ser "todo gris" y pasa a decir algo
verificable sobre el jugador.

## (d) Lenguaje del reporte simple (hecho el 12/10)

**Qué cambió:**

- Las tarjetas de "Lo más importante" muestran **solo el texto llano** y su estado. Se fueron de ahí "el orden descrito en la literatura", "Fuente: Kovacs y Ellenbecker (2011)…" y la línea
  de instantes (que además se repetía en las dos tarjetas). Todo eso está en **"Ver detalle técnico → Observaciones y su fundamento"**, con la fuente de cada una y sin repetirse.
- `texto` del contrato ya no nombra la literatura (hay una prueba que lo verifica en los seis grupos); `fundamento` y `referencia` siguen siendo los campos del nivel 3 y del PDF.
- Cuando no hay con qué evaluar: *"Todavía no tenemos un patrón de referencia para este golpe; lo registramos para que puedas compararte en tus próximas sesiones."* Cuando hay
  referencia pero la validación propia no alcanza (saque de tres cuartos): *"Todavía no podemos evaluar este orden con suficiente confianza en este encuadre; lo registramos para que
  puedas compararte en tus próximas sesiones."*

**Etiqueta, propuesta** (hoy "Sin evaluar", que dice lo que el sistema *no hizo* y no qué es el dato):

| Opción | Cómo se lee | Pro | Contra |
| --- | --- | --- | --- |
| **Solo registrado** (mi recomendación) | "Solo registrado" junto a un dato medido | Es verdad en los tres casos (sin patrón, sin validación, brazo); se distingue claramente de "No auditable" (no se pudo medir); cabe en la pastilla | Hay que explicar en una línea que es un dato sin juicio (el texto de la tarjeta ya lo hace) |
| Sin referencia todavía | explica el motivo | Muy claro cuando falta el patrón | **No es verdad** para el saque de tres cuartos (hay referencia, falta validación propia) |
| Para comparar después | orienta a la acción | Amable, le da sentido a "compararte" | Promete una comparación que hoy no existe hasta la 2.ª sesión |

En la **vista detallada** y en el PDF se conserva "Sin evaluar" (término técnico de la decisión 011). El cambio es de una línea (`SinEvaluarBadge` en `components/estado.tsx`); no lo
apliqué porque pediste una propuesta.

## Orden recomendado (valor / esfuerzo)

1. **(d) Lenguaje** — hecho (0,1 sesión).
2. **Paso A del recálculo** (0,5–1) — destraba el veredicto del saque de perfil, decide si (a) conviene y fija la tolerancia ya unificada. Es bloqueante de la demo de todos modos.
3. **(b) Datos: separación cadera-hombro, rodilla, codo** (1) — el reporte deja de ser solo "orden y velocidades".
4. **(c) Consistencia entre golpes** (1,5–2, sobre la carga de varios golpes) — el mayor valor: es lo único que evalúa de verdad sin literatura.
5. **(a)** — 0,1 sesión cuando haya pasaje y el Paso A confirme el sentido del orden; antes, no.
