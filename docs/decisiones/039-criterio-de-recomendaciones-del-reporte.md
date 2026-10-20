# Decisión 039 — Criterio de las recomendaciones del reporte: qué tipos se permiten, cuáles no, y por qué

**Fecha:** 19 de octubre de 2026
**Estado:** **APROBADA en lo esencial por Valentín el 20/10/2026**, con 10 ajustes de lenguaje (`docs/ux/textos-reporte-039-propuesta.md`, versión 2). Falta su revisión de la **matriz de casos** (9 escenarios, generada por el mismo código) antes de terminar las pantallas. Debe estar publicado antes de la limpieza del 25/10.
**Afecta a:** frontend (reporte del golpe, de la sesión, Evolución y PDF) · `CLAUDE.md` §3 (el nivel 1 pasa de «Lo más importante» a «Qué vimos») · R2 (derivación genérica a un profesional)
· Capítulo 4 (apartados de la interfaz del reporte). **No afecta** al motor (`engine/`, `ensamblar_reporte.py`), al contrato del reporte (1.4) ni a la versión del motor (0.5.5).

---

## El problema (revisión de un golpe y una sesión reales con ojos de usuario, 19/10)

1. **«Lo más importante» empieza por lo que no se midió** (dos tarjetas negativas), cuando lo medido es lo que sirve.
2. **Datos sin significado para quien no es técnico:** «0,296 s desde el inicio de la ventana analizada» (además es un artefacto: la ventana se ancla en el pico del tronco, que da 0,300 s en los
   seis golpes de la sesión) y «793 grados/s».
3. **Jerga interna visible:** puntos interpolados, escala temporal, cobertura auditable, MAD × 1,4826, `codo_der`, «medido en parte».
4. **Una contradicción aparente en la sesión:** «33° ± 4°» junto a «de 11° a 42°»; el golpe 6 se aparta y no se explica.
5. **Se calla lo más interesante:** en los 3 golpes ordenables la cadera llegó antes que el tronco (17, 42 y 17 ms). Decirlo es una observación, no un veredicto.
6. **No se luce el error medido del codo** contra goniometría manual (12,5° de media, p95 36,4°), que es lo que le permite a un profesional saber cuánto confiar.

## Decisión

**1. Estructura (golpe y sesión; el PDF con la misma lógica).** Qué vimos (2–3 líneas, primero lo medido; lo no medido después, con el porqué en una línea) → Fotos y video (con una
línea de qué mirar) → Qué podés hacer con esto → Para tu entrenador o profesional (preguntas, PDF, aviso, cuánto confiar en cada medición) → Detalle técnico (cerrado, cada término con una
línea de explicación, sin nombres internos; el procesamiento —tiempos, interpolación— solo acá). En la web, un ⓘ con la explicación corta al lado de cada dato.

**2. «Qué podés hacer con esto» admite SOLO cuatro tipos de recomendación:**

| Tipo | Qué es | Ejemplo |
| --- | --- | --- |
| **A. Cómo medir mejor** | Sobre la captura: lado de la cámara, encuadre, cantidad de golpes | «Con 5 o más golpes en que se distinga, KinetiQ puede decir cuántas veces se repitió el orden» |
| **B. Cómo usar los datos para entrenar** | Comparar sesiones desde el mismo lugar, mirar si un número se vuelve más parejo, la variación propia | «Mirá en Evolución si la torsión se vuelve más pareja de una sesión a otra» |
| **C. Contexto de la literatura** | En un **recuadro separado**, sin ningún dato del jugador adentro, con cita, y **sin «coincide» ni «está bien»**. **Solo frases generales**: una secuencia específica (el orden de los picos, valores, rangos) **requiere verificar antes el pasaje** de la fuente | «La literatura describe el saque como una cadena que transmite energía desde las piernas, a través de la cadera y el tronco, hacia el brazo y la raqueta (Kovacs y Ellenbecker, 2011). La forma exacta varía de un jugador a otro.» |
| **D. Preguntas para el entrenador** | Armadas con los datos del jugador (van en la sección «Para tu entrenador»), siempre abiertas | «En el golpe 6 la torsión fue de 11°: ¿qué ves en el video?» |

**3. Prohibido, en los cuatro tipos:** «deberías» y cualquier imperativo de técnica; «corregí»; «bien/mal», «correcto/incorrecto», «mejor/peor»; **riesgo de lesión** y toda predicción;
**comparar con profesionales** o con un «modelo ideal»; **prometer mejoras**; prescribir tratamiento, descanso o carga. Una **prueba automática** recorre todas las salidas del generador
(con los reportes reales de ejemplo) y falla si aparece alguna de esas palabras.

**4. Cómo se arman los textos.** **Reglas fijas** sobre los datos que el reporte ya tiene guardado; plantillas con huecos, **sin IA generativa**. Un solo módulo
(`frontend/src/lib/textos-reporte.ts`) lo usan la pantalla y el PDF: **los mismos textos en la web y en el papel**. Llevan **versión** (`VERSION_TEXTOS`, hoy «1»), impresa en el detalle técnico y
en el pie del PDF (R4): si se cambia una frase o una regla, sube la versión y la bitácora dice qué cambió. Como salen del JSON guardado, **valen también para los reportes viejos** y se
degradan con gracia cuando falta un campo (por ejemplo, `picos_no_medidos` en un reporte anterior al contrato 1.4).

**5. Aviso corto en toda sección para profesionales (sin «riesgo de lesión»; R2 sin excepción):** *«KinetiQ mide cómo te movés; no evalúa si tu técnica es correcta ni dice nada sobre lesiones. Si tenés dolor o una molestia, consultá a un profesional y llevale este informe.»*

**6. Todo ángulo de articulación lleva su referencia** en una línea («180° es la pierna —o el brazo— totalmente estirada»). En «Qué vimos» no va el codo del brazo que no golpea (el del lanzamiento): va al detalle técnico; en su lugar, la rodilla.

**7. Las preguntas para el entrenador van solo en la sección 4**, y una puede ser para el propio jugador («¿cuál de estos saques sentiste más cómodo o más potente?»): la valoración la hace el jugador, nunca el sistema.

## Por qué estos tipos (y no otros)

- **Es lo que el proyecto puede sostener con sus propias mediciones.** Las cuatro validaciones del motor (Criterios 1 a 3) dicen **cómo medir bien** (A), **cuánto se repite lo medido** (B) y **cuánto
  error tiene cada ángulo** (el bloque para profesionales). No dicen qué valor es bueno: la tesis no tiene ningún rango numérico citable para el tenis (`docs/reporte-mas-valor.md`).
- **R2 y la decisión 036.** Ningún grupo emite veredicto del orden con una sola cámara. Una recomendación de técnica («llegá con la cadera antes») sería un veredicto con otro nombre y, si el
  jugador la sigue, una prescripción. Las recomendaciones A y B son sobre **cómo medir y cómo comparar**, no sobre cómo golpear.
- **C va aparte y sin datos del jugador** porque pegar una cita junto a un número invita a leer «coincide» o «no coincide» aunque no se escriba. La literatura es contexto; el dato es del jugador.
  Solo hay una cita general para el **saque** (Kovacs y Ellenbecker, 2011; **sin Fleisig hasta verificar el pasaje**); para drive y revés el recuadro dice que todavía no hay una referencia incorporada al proyecto. Las velocidades de Fleisig
  (440 y 870 °/s) **no se muestran** junto a las del jugador: sería compararlo con profesionales, y la decisión 011 ya dice que el brazo no es comparable.
- **D (preguntas)** devuelve la interpretación a quien corresponde (el entrenador o el profesional): el sistema muestra el dato; la conclusión es del profesional (R2).
- **Se exige la salvedad de la cámara** cada vez que se menciona un orden (decisiones 035 y 036): el orden medido cambia con el encuadre, y con menos de 5 golpes ordenables no se habla de
  repetición (`MIN_ORDENABLES_REPETIBILIDAD`).

## Qué no cambia

El motor y su sello (0.5.5), el contrato (1.4), los cuatro estados de R3 (no se reintroduce puntaje ni color de estado), y el vocabulario de R2 (se observa / se midió / no se pudo medir).

## Costo y calendario

≈ 3,25 a 4 días de frontend (detalle en el documento de textos); sin tocar el motor ni el servidor, así que se publica solo el frontend (Cloudflare) y no redeploya Render.

## Consecuencias

- `CLAUDE.md` §3: el nivel 1 se llama «Qué vimos» (lo medido primero, 2–3 líneas); se actualiza al aprobar, no antes.
- `docs/tesis/correcciones-pendientes-capitulo-4.md`: se agrega la fila de la interfaz del reporte al programarlo (regla de §6).
- Queda pendiente (no se hace en este cambio): una frase equivalente del recuadro C para drive y revés cuando exista una cita verificada.

## Ajustes del 20/10 (segunda ronda, revisión de la matriz de casos)

- **La frase de la sesión dice el rango concreto y cuántos golpes fueron ordenables**, sin adjetivos: «En tus 6 saques te enroscaste entre 29° y 42°, salvo el golpe 6 (11°). En 3 de tus 6 saques se pudo distinguir el orden, y en los tres tu cadera aceleró antes que tu tronco.» «Parecidos entre sí» se eliminó. Un solo golpe ordenable: «…y en ese tu cadera aceleró…»; ninguno: «En ningún golpe se pudo distinguir cuál aceleró primero: quedaron casi a la vez.»
- **El gráfico «Cuándo giró cada parte» queda visible** (es el elemento central, CLAUDE.md §3) debajo de «Qué vimos», simplificado: todo relativo al tronco, con la franja de ± 8,3 ms rotulada «zona donde no se puede distinguir cuál fue primero». Los segundos desde el inicio de la ventana quedan en el detalle técnico. `CLAUDE.md` §3 actualizado.
- **Once casos de prueba** (matriz de la sección C del documento de textos): cadera antes, tronco antes, nada medido, drive, revés, cámara del lado de la mano dominante, zurdo, orden mezclado, 3 golpes, sin golpe que se aparte, un solo golpe ordenable y ninguno ordenable. El documento se **genera** con el mismo código que arma los textos.
- **Evolución** queda fuera de este cambio (se hace después, si queda tiempo).

## Ajustes del 20/10, tercera ronda (tras ver el reporte en producción) — `VERSION_TEXTOS` = «2»

- **«En una frase» (golpe, sesión y Evolución): una sola idea, SIN números** (ni grados, ni milisegundos, ni rangos, ni «salvo el golpe X»; los números se escriben con palabras) y un solo verbo, **«giró/giraron»**. Golpe: «Tu cadera y tu tronco giraron casi a la vez en este saque.» Sesión: «Medimos seis saques. Giraste parecido en casi todos y, cuando se pudo ver el orden, la cadera arrancó primero.» Los datos pasan a «Qué vimos». «Giraste parecido» solo se dice desde 5 golpes (cuando el servidor puede marcar el golpe que se aparta). **Prueba nueva: «En una frase» no puede contener dígitos.** Sigue valiendo la decisión 036 (sin «bien», «mal», «como se espera», «correcto»).
- **«¿Qué giró primero?» reemplaza al gráfico del cuerpo del reporte:** cajas de izquierda a derecha, sin eje ni números; dos partes a menos de 8,33 ms (decisión 032) van juntas en una caja «casi a la vez»; si se distingue, flecha con «antes»; parte no medida: caja punteada «Brazo · no se vio». El gráfico en milisegundos con la franja pasa al **detalle técnico** y **reemplaza** al de segundos desde el inicio de la ventana; sus etiquetas ya no las pisa la línea punteada. Igual en el PDF.
- **Textos:** título «Saque · golpe N de M»; rodilla y codo dichos en palabras («la pierna izquierda casi estirada», con el ángulo y «180° es…» entre paréntesis); «de su sesión» → «de tu sesión» (prueba de que no queda); sin la tarjeta vacía del brazo en «Fotos y video».
- **Pie del sitio y del PDF:** sin «Proyecto final de Ingeniería en Informática · Universidad del Salvador · 2026»; «KinetiQ documenta el movimiento. No diagnostica ni reemplaza la evaluación de un profesional.»; descripción: «Medí cómo gira tu cuerpo en cada golpe.»
- **Evolución** en el mismo lenguaje («En una frase» sin números + «Qué vimos» con ⓘ + texto simple con menos de 2 sesiones comparables), con las mismas pruebas de palabras prohibidas y de jerga. **Limitación conocida:** la serie se arma por jugador × golpe × encuadre; **el lado de la cámara todavía no forma parte de la clave** (es una consulta del servidor): si las sesiones se grabaron desde lados distintos se comparan igual y un aviso lo dice. Hacerlo estricto toca `/evolucion`, no el motor.

## Puntos abiertos

1. **Pasaje exacto de la cita** del recuadro C (Kovacs y Ellenbecker, 2011): no verificado; por eso la frase es general.
2. **Revisión de la matriz de casos** por Valentín (nueve escenarios, `docs/ux/textos-reporte-039-propuesta.md` sección C).
4. **El lado de la cámara en la clave de Evolución** (servidor).
