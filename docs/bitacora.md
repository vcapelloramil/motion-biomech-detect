# Bitácora de desarrollo

Registro de cierre de cada sesión de trabajo con Claude Code. Una entrada por sesión, la
más reciente arriba. Cada entrada anota: **qué se hizo**, **qué quedó pendiente** y el
**siguiente paso concreto**.

---

## 2026-10-21 — Decisión 040 cerrada («evaluada; descartada para el MVP»), quinta ronda de la 039 (textos v4), puntaje de calidad y tiempo de la limpieza del 25/10

**Pedido de Valentín** tras leer la 040: no se implementa el 1–10; dejar planteado cuándo sí sería viable. Frontend y documentos; motor 0.5.5, contrato 1.4 y servidor sin cambios.

- **1 · ¿Cuándo sí?** Misma simulación (σ verdadero 3,7°, desvío robusto del servidor, 20 000 repeticiones; niveles de igual ancho entre 1,5° y 9°). **Intervalo del 95 % de la variación estimada, una sesión:** n = 6: 0,79 a 6,40° (5,6°); 12: 1,46 a 5,94°; 20: 1,89 a 5,52°; 30: 2,22 a 5,20°; 50: 2,52 a 4,86° (2,3°). **Niveles que abarca** (amplitud ÷ ancho de un nivel): con 3 niveles (3,75°) 1,5 / 1,2 / **1,0** / **0,8** / **0,6**; con 5 (1,88°) 3,0 / 2,4 / 1,9 / 1,6 / 1,2; con 10 (0,83°) 6,7 / 5,4 / 4,4 / 3,6 / 2,8. **Para que quepa en UN nivel: ≈ 20 a 30 golpes con 3 niveles, ≈ 80 con 5, ≈ 400 con 10** (inviable). **Juntando sesiones** (promedio de σ por sesión): 3 × 6 = 18 golpes → 1,0 (3 niveles) / 2,0 (5) / 4,6 (10); **4 × 6 = 24 → 0,9 / 1,8 / 4,0**; 4 × 12 = 48 → 0,7 / 1,4 / 3,1. Con el desvío estándar clásico, unas 3 veces menos golpes, pero sensible a un golpe lejano. Supuestos optimistas (datos normales, σ constante). Tablas completas en la 040.
- **2 · Cierre de la 040:** «evaluada; descartada para el MVP»; la variación queda en grados y **su ⓘ dice que con pocos golpes es una estimación gruesa** (textos v4). **Trabajo futuro:** regularidad en palabras (3 bandas) con ≥ 20 a 30 saques del mismo encuadre y lado en una sesión, o «regularidad habitual» juntando ≥ 4 sesiones de 6; nunca 10 niveles. **Celda de ≈ 20 saques** agregada al protocolo post-demo (`docs/protocolo-sesion-lado-derecho.md`, «Celda extra para la regularidad»), con lo que se va a mirar fijado antes de analizar.
- **3 · Capítulo 7:** `insumos-capitulo-7.md` **§2.11** (cortes fijados antes, commit `9e270f8`; tabla de las dos sesiones; tablas del punto 1; conclusión: ninguna escala más fina que la incertidumbre del dato, el mismo principio que los cortes de rodilla y codo) y fila en §7.3.
- **4 · Textos que comparan la variación:** corregidos los de «Para usar estos datos al entrenar» del golpe y de la sesión (ya no invitan a ver si «se vuelve más pareja»; dicen que con pocos golpes es una estimación gruesa y no conviene compararla entre sesiones; Evolución se usa para el valor típico); nota del gráfico y de la tabla de Evolución con la misma advertencia; **prueba nueva `CAMBIO_DE_VARIACION`**; `VERSION_TEXTOS` = 4 (quinta ronda de la 039). Documento de textos regenerado.
- **5 · Limpieza + nueva subida del guion §C (`docs/demo-guion.md`):** 14 golpes (6 + 6 + drive + revés), de a uno (1 CPU). Medido: saque de tres cuartos 193 s (24/9) y 246 s (25/9, máximo 280 s) por golpe; drive/revés 14 a 125 s (una vez 677 s). **Análisis ≈ 40 a 60 min (peor caso ≈ 80)**; el 13/10 los 12 golpes tardaron 43,7 min (la nota de «≈ 35 min» estaba corta). **Toda la limpieza ≈ 1 h 35 min a 2 h 40 min: arrancar el 25/10 a las 9:00** y no empujar nada mientras haya análisis en curso.
- **6 · Capítulo 7, §7.4 «Puntaje de calidad»:** por qué no es posible en el MVP (sin definición de calidad; sin referencia comparable en 2D —decisiones 011, 035 y 036—; límites de medición: encuadre, oclusión del brazo, error de rodilla y codo; R2) y caminos: A) resultado de la pelota, B) población de jugadores avanzados con el mismo protocolo (choca con R5: hay que revisarla), C) puntuación de entrenadores con acuerdo entre evaluadores; **recomendación A + C, idealmente multicámara o 3D**; **D) la lista de criterios de la literatura, descartada**. Diferencia explícita: **regularidad** (viable con más golpes, 040) ≠ **calidad** (necesita una referencia externa).

## 2026-10-20 (más tarde) — Cuarta ronda de la 039: cortes de rodilla/codo, lista de la sesión y Evolución; y borrador de la decisión 040 (Regularidad), solo propuesta

**Pedido de Valentín** tras revisar producción (sesión 25/9, golpes 3 y 4, y Evolución). `VERSION_TEXTOS` = 3; solo frontend, motor 0.5.5.

- **A · Cortes en palabras:** tres categorías, ninguna más angosta que el error medido (rodilla 8,5° de media y hasta 19,2°; codo 12,5° y hasta 36,4°): **165° o más «estirada o casi estirada»; 135°–165° «algo flexionada»; menos de 135° «flexionada»**. Nunca «totalmente estirada» (la referencia es «180° es la pierna recta, sin doblar»). Registrado en la 039 como regla general. **El lado en la clave de Evolución queda para después de la demo**: fila 42 de `correcciones-pendientes-capitulo-4.md`. *(Interpreté «nunca “totalmente estirada”» también para la referencia de 180°: pasó a «recta, sin doblar».)*
- **B · Sesión y Evolución:** la lista muestra solo «Golpe N» + torsión + estado + «casi a la vez» (etiqueta cambiada en toda la aplicación) + «se pareció menos»; «Ver reporte» y «Eliminar» juntos a la derecha (verificado a 390 px y en escritorio, sin saltos); nombre del archivo y tiempos de cola/procesamiento en el detalle técnico; un solo título de «Fotos y video» y «textos vN» una vez; en Evolución las sesiones del mismo día se llaman «24 sep · 1.ª» y «24 sep · 2.ª».
- **La sesión del 24/9 con 1 golpe** es `3a101dd3`: saque de tres cuartos, **un solo golpe** (`20260925_saque_trescuartos_toma02c_golpe1.mov`, un recorte de la toma del **25/9** cargado el 13/10 con la fecha **24/9** por error), medido con motor **0.5.4**. **La limpieza del guion §C la elimina** (paso 2: «24/9 saque tres cuartos de 0.5.4» entre las 6 sesiones de un golpe de prueba). Por eso Evolución dice «antes: 1 de 1» y tiene dos puntos del 24 sep; después de la limpieza quedan una sesión por fecha.
- **C · Regularidad (borrador de la decisión 040, `docs/decisiones/040-indicador-de-regularidad-propuesta.md`; nada implementado):** escala 1–10 y cuatro palabras fijadas **antes** de calcular (commit `9e270f8`) con la repetibilidad del Capítulo 7 (σ_w del corpus 2,84–3,14° → 8; Δ entre sesiones 0,93–6,03°): **10 = variación típica de 1,5° o menos; 1 = 9° o más**. Sesiones reales (mínimo 4 golpes): **24/9 → σ 1,11° → 10 «muy regular»; 25/9 → σ 4,37° → 7 «bastante regular»** (sin el golpe 6, 8); las otras sesiones tienen menos de 4 golpes. **Hallazgo: con 6 golpes el intervalo del 95 % del σ abarca unos 7 puntos de la escala (valores 4 a 10 para un jugador con la variación típica del corpus): el 1–10 es ≈ 7 veces más fino que el dato, y Evolución contaría como «variaron más» una diferencia (10 → 7) que es en gran parte ruido de muestreo.** Recomendación: **no implementar el 1–10 para el 23/10** (trabajo futuro); si se quiere algo, la palabra en tres bandas con 8 o más golpes, o dejar la variación en grados con una línea en el ⓘ; camino futuro: una «regularidad habitual» con ≥ 18 golpes de varias sesiones. Decide Valentín.

## 2026-10-20 (noche) — Tercera ronda de la decisión 039: «En una frase» sin números, «¿Qué giró primero?», Evolución en lenguaje simple (`VERSION_TEXTOS` = 2; solo frontend)

**Pedido de Valentín** tras ver el reporte del golpe 4 en producción (republicó el frontend del commit `b444c9a`).

- **«En una frase» (golpe, sesión, Evolución):** una sola idea, **sin dígitos**, verbo «giró». Golpe 4: «Tu cadera y tu tronco giraron casi a la vez en este saque.» Sesión: «Medimos seis saques. Giraste parecido en casi todos y, cuando se pudo ver el orden, la cadera arrancó primero.» Los datos (grados, ms, rango, «salvo el golpe 6») están en «Qué vimos». **Prueba nueva: sin dígitos, sin «aceleró», sin «bien/mal/correcto/como se espera».**
- **«¿Qué giró primero?»** (`secuencia-simple.tsx`) reemplaza al gráfico del cuerpo: cajas sin ejes ni números; a menos de 8,33 ms, UNA caja «casi a la vez»; si se distingue, «antes →»; parte no medida, caja punteada «Brazo · no se vio». El gráfico en ms con la franja pasó al **detalle técnico** y reemplaza al de segundos desde el inicio de la ventana (se borró `secuencia-real.tsx`); etiquetas con halo para que la línea punteada no las pise. Igual en el PDF del golpe.
- **Textos:** «Saque · golpe N de M» (también en el PDF; «golpe único» si es uno solo); rodilla/codo en palabras («tenías la pierna izquierda casi estirada (rodilla a 172°; 180° es la pierna totalmente estirada)»); «de tu sesión» (una prueba lo cuida); sin la tarjeta vacía del brazo en «Fotos y video» (pantalla y PDF); «de el brazo» corregido.
- **Pie:** sin «Proyecto final…»; descripción «Medí cómo gira tu cuerpo en cada golpe.»; el pie del PDF lleva «KinetiQ documenta el movimiento. No diagnostica ni reemplaza la evaluación de un profesional.»
- **Evolución** (`textos-evolucion.ts`): «En una frase» + «Qué vimos» con ⓘ + texto simple con menos de 2 sesiones + detalle técnico (tabla por sesión); mismas pruebas de palabras prohibidas y jerga. **Limitación (no cambia en esta tanda): el lado de la cámara no es parte de la clave de la serie**; con lados distintos se compara igual y un aviso lo dice (toca `/evolucion`, servidor).
- **Documento de textos regenerado** con los 12 casos + 6 de Evolución (`bun tests/generar-textos-doc.ts`).
- **Pruebas:** frontend **221 pasan**; `tsc` y `build` limpios. **Visto en pantalla** (servidor temporal con datos simulados desde fixtures, ya borrado): golpe 4 (empate) y golpe 3 (orden distinguible) a **390 px** y en escritorio (sin desplazamiento horizontal), Evolución a 390 px, PDF del golpe simulado en papel. **No visto:** fotos y video reales, celular físico, impresión real.

## 2026-10-20 — Reportes rediseñados (decisión 039): golpe, sesión y PDF; solo frontend, sin tocar el motor

**Pedido de Valentín (19 y 20/10):** el reporte no se entendía (arrancaba por lo no medido, jerga, datos sin significado). Aprobó los textos con 10 ajustes y, tras revisar la matriz de casos, con 5 más.

- **Qué quedó (frontend, sin cambios de motor 0.5.5, contrato 1.4 ni servidor):** `frontend/src/lib/textos-reporte.ts` arma **todas las frases con reglas fijas** (sin IA generativa) a partir del JSON ya guardado, con `VERSION_TEXTOS = "1"`; la pantalla y el PDF llaman a las mismas funciones. Estructura: **En una frase → Qué vimos → Cuándo giró cada parte (gráfico relativo al tronco con franja de ± 8,3 ms) → Fotos y video (una sola foto si cadera y tronco están dentro de la tolerancia) → Qué podés hacer con esto (solo cuatro tipos; literatura en recuadro aparte) → Para tu entrenador o profesional (preguntas, PDF, cuánto confiar, aviso) → Detalle técnico cerrado**, con un **ⓘ** (se abre con un toque) en cada dato y glosario. Valen también para los reportes viejos (0.5.3): no hay nada que re-subir.
- **Frases clave:** golpe 4: «Un saque típico de tu sesión: te enroscaste 34° y tu cadera y tu tronco aceleraron casi juntos.»; sesión: «En tus 6 saques te enroscaste entre 29° y 42°, salvo el golpe 6 (11°). En 3 de tus 6 saques se pudo distinguir el orden, y en los tres tu cadera aceleró antes que tu tronco.» Todo ángulo de articulación lleva su referencia («180° es la pierna totalmente estirada»); en «Qué vimos» va la rodilla y no el codo del brazo que no golpea; el aviso no dice «riesgo de lesión».
- **Pruebas:** frontend **194 pasan** (122 + 72 nuevas: el golpe 4 y la sesión **reales del 25/9** como fixtures, **matriz de 12 casos** —cadera antes, tronco antes, nada medido, drive, revés, cámara del lado de la mano dominante, zurdo, orden mezclado, 3 golpes, sin golpe que se aparte, un solo golpe ordenable, ninguno ordenable—, datos del gráfico, y una **prueba de palabras prohibidas y de jerga** sobre cada frase de cada caso). `tsc` y `build` limpios; `eslint` sin errores (la regla de formato de prettier ya fallaba en el árbol antes de este cambio: no se tocó).
- **Documento de textos** (`docs/ux/textos-reporte-039-propuesta.md`, el que se cita en la tesis): el golpe 4, la sesión y la matriz están **generados por el mismo código** (`bun tests/generar-textos-doc.ts`), así que no pueden diferir del sistema.
- **Visto en pantalla** con la sesión real (servidor de desarrollo temporal con datos simulados desde los fixtures, ya borrado; no se tocó la autenticación): golpe 4 y golpe 3 a **390 px** (sin desplazamiento horizontal de la página, ⓘ abierto con un toque, gráfico legible) y en escritorio; **PDF del golpe y de la sesión** simulados en papel A4 (el detalle técnico va abierto). **No visto:** las fotos reales (en la prueba eran imágenes simuladas), el video con esqueleto, un celular físico y la impresión real en papel.
- **Correcciones menores en el camino:** «de el brazo» (reporte-simple), ⓘ pegado al borde en el celular, tablas del PDF con columnas del mismo ancho en cada grupo, «camara lenta 240» → «cámara lenta de 240 fps».
- **Decisiones y documentos:** decisión 039 (con los ajustes de las dos rondas), `CLAUDE.md` §3 (nivel 1 = «Qué vimos»; el gráfico queda visible y relativo al tronco), `correcciones-pendientes-capitulo-4.md` fila 41.
- **Pendiente:** **Evolución** con el lenguaje nuevo (solo si queda tiempo); verificar el pasaje de la cita de Kovacs y Ellenbecker (2011); ver el reporte con las fotos y el video reales tras republicar.

## 2026-10-19 (tarde) — Correcciones de fechas, clave SMTP de Brevo y propuesta de textos de los reportes (decisión 039; solo documentos, nada programado)

- **Corrección del dominio (Valentín):** `kinetiqtennis.me` se registró el **12/10/2026**, no el 5/10; vence el **12 de octubre de 2027** (fecha exacta de Namecheap, confirmada por Valentín el 20/10). Corregido en `docs/tesis/insumos-capitulo-7.md` (tabla de despliegue y §10.7), en la decisión 034 (Consecuencias) y en las dos
  menciones de la entrada de arriba (marcadas como corregidas). El 19/10 el mensaje traía la fecha del panel sin completar y se anotó «≈ 12/10/2027»; el 20/10 Valentín confirmó **12 de octubre de 2027** y se quitó el «≈» de todos los documentos.
- **Clave SMTP de Brevo (nuevo, Valentín):** se creó el **15/10/2026** con **vencimiento de un año (≈ 15/10/2027)**. **Si vence, dejan de salir los correos de confirmación de cuenta y de recuperación de contraseña.** Hay que crear otra clave en Brevo y cargarla en Supabase
  (Authentication → Emails → SMTP Settings) antes de esa fecha. Registrado en la decisión 034 y en `insumos-capitulo-7.md` (fila nueva de la tabla de despliegue).
- **Pedido de Valentín (prioridad sobre la detección automática, antes del congelamiento del 24/10):** los reportes (golpe, sesión, Evolución y PDF) no se entienden. Revisó un golpe y una sesión reales y marcó seis problemas (arranca por lo no medido, datos sin significado, jerga interna,
  «33° ± 4°» contra «de 11° a 42°», se calla que la cadera llegó antes que el tronco, no se luce el error del codo). Estructura nueva en cinco bloques (Qué vimos · Fotos y video · Qué podés hacer con esto · Para tu entrenador · Detalle técnico) y un ⓘ en la web.
- **Hecho hoy:** **decisión 039** (`docs/decisiones/039-…`, propuesta: tipos de recomendación permitidos A–D y prohibidos, y el porqué) y **los textos concretos** del golpe 4 y de la sesión completa del saque de tres cuartos del 25/9, con datos reales leídos de la base en solo lectura
  (`docs/ux/textos-reporte-039-propuesta.md`). **No se programó nada.** Esfuerzo ≈ 3,25–4 días, **sin tocar el motor, el contrato ni el servidor** (solo frontend).
- **Hallazgos al leer los datos:** (1) el golpe 4 es el «golpe típico» de la sesión; (2) el instante absoluto del tronco da **0,300 s en los seis golpes** (la ventana se ancla en él): «0,296 s desde el inicio» no significa nada, lo útil es la diferencia cadera-tronco en ms;
  (3) cadera y tronco están a 4 ms en el golpe 4, así que las dos fotos «del pico» son casi el mismo fotograma (se propone una sola); (4) el golpe 6 se aparta también en la rodilla izquierda (101° contra 172°–178°), no solo en la torsión (11° contra 29°–42°); (5) «Medido en parte»
  de los golpes 2, 4 y 6 es un resto de la 0.5.3 (la decisión 037 ya cuenta el empate como medido).
- **Puntos que necesitan a Valentín:** OK del lenguaje; «riesgo de lesión» está en su aviso pero R2 lo prohíbe (alternativa propuesta); el pasaje exacto de las citas del recuadro de literatura (Kovacs y Ellenbecker 2011; Fleisig et al. 2003) no está verificado; la fecha exacta del vencimiento del dominio.
- **Sin push.** Los commits siguen locales (empujar redeploya Render).

## 2026-10-19 — Actualización de los insumos del Capítulo 7, insumos del Capítulo 8 y correcciones del Capítulo 4 (solo documentos; sin cambios en el producto)

Pedido de Valentín: poner al día `docs/tesis/insumos-capitulo-7.md` (corte 13/10 → 19/10), resolver sus pendientes y preparar material para el Capítulo 8 y la lista del Capítulo 4. **No hay registros posteriores al 16/10 02:56:** lo que se haya hecho del 17 al 19/10 (sesión de validación, revés raros) **no consta**.

- **Verificado hoy:** producción `/health` = 0.5.5 (3 veces), contrato 1.4, `main` = `origin/main` = `08ccec1`; suite rápida del servidor **620 passed**, frontend **122 pass**; base: 1 cuenta, 8 sesiones, 18 golpes, 17 reportes, 1 fallido, 0 filas sin dueño, 0 archivos huérfanos, nada en curso.
- **Hallazgos nuevos:** (1) **`IMG_6376`, subido como «saque de perfil», es un saque de tres cuartos** (marca de captura 24/9 14:58:43 = original del corpus; D = 52,9° sobre el archivo subido); `IMG_6395`, `IMG_6380` e `IMG_6391` son recortes de originales del corpus, no grabaciones nuevas. (2) La sesión `3a101dd3` tiene **fecha 24/9 con un golpe del 25/9**. (3) **Espera en cola medida:** sesión de 6 golpes 19,6 min (la estimación de ~12 min era baja); 12 golpes en cola 43,7 min. (4) RNF-03 (17 pruebas; fase cero 0 ms contra +70,8 ms del filtro de una pasada) y RNF-07 (28 pruebas contra el Supabase real) pasan; **no existen** Playwright ni la prueba de RNF-05. (5) Cloudflare Workers gratis: 100 000 solicitudes por día y 10 ms de CPU por solicitud (fuente oficial); renovación del dominio ≈ USD 19,18 por año (fuente de terceros).
- **Documentos:** `insumos-capitulo-7.md` (§9 delta con las cifras que cambiaron, §10 pendientes resueltos o declarados NO CONSTA / NO MEDIDO, correcciones en el cuerpo); **`insumos-capitulo-8.md`** (conclusiones, implicancias, 16 aportes técnicos con su evidencia, recomendaciones para usuarios, desarrollo e investigación, 26 mejoras con su estado); `correcciones-pendientes-capitulo-4.md` (filas 36 a 40, filas 2, 19 y 34 actualizadas, anotaciones 20 a 22 y nota 8 corregida); `criterio4-latencia.md` (fila 1).
- **Herramienta nueva (solo lectura):** `tools/respaldo/tiempos_y_origen_de_las_subidas.py`.
- **Respuestas de Valentín (19/10):** (1) **OE4** «análisis comparativo visual… contraste con modelos de referencia, permitiendo corregir errores y mejorar el rendimiento»: **no se construyó la comparación con modelos de referencia; se reemplazó por la comparación del jugador consigo mismo**; (2) motivo del cambio de alcance del 7/10: **plazo y no tener otros usuarios disponibles**; (3) del 17 al 19/10 **no hubo desarrollo** (el plan del 17/10 sigue pendiente); (4) **17/11 es la fecha final de entrega de documentación y sistema para regularizar la materia**. Incorporado en los insumos 7 (§10.3, §10.5, §8.2, §10.11 y una fila de desvíos) y 8. **Dominio registrado el 5/10/2026** (vence ≈ 5/10/2027) *[corregido el 19/10 (tarde): fue el 12/10/2026, vence el 12/10/2027; ver la entrada de arriba]*. No queda ninguna pregunta abierta.
- **Commit `7b61d86` y el siguiente quedan locales** por decisión de Valentín; si se empujan, que sea sin ningún análisis corriendo (Render redeploya).
- **Sin empujar:** los commits de esta entrada quedan en `main` local (empujar redeploya Render).

### Cierre de contexto del 19/10 (retomar desde acá)

**Estado:** producción = `origin/main` = `08ccec1`, **motor 0.5.5, contrato 1.4**, sin cambios desde el 16/10. En `main` local hay **3 commits de solo documentos sin empujar** (`7b61d86`, `7a13750`, `434add3`): **empujarlos redeploya Render**, así que hacerlo solo con la base sin análisis en curso (`tools/respaldo/estado_de_la_base.py` → «EN CURSO: ninguno»); Valentín dijo que por ahora quedan locales. Árbol de trabajo limpio. Pruebas del 19/10: servidor 620 pasan, frontend 122.

**Calendario vigente:** demo con la **carga declarada** (la detección automática, 038, no cumplió en la etapa 1 y solo se integra si valida antes del **23/10**) · **24/10** congelar el motor (`git tag motor-congelado-<versión>`) · **25–26/10** limpieza y nueva subida (corregir la sesión `3a101dd3`, fecha 24/9 con un golpe del 25/9; no volver a subir `IMG_6376` ni `IMG_6391` como «perfil») · 26–27/10 ensayo · 27/10 congelamiento total · **28–30/10 demo** · **17/11 fecha final de entrega de documentación y sistema** para regularizar la materia.

**Respuestas de Valentín (19/10), ya incorporadas en los insumos:** OE4 reemplazado por la comparación del jugador consigo mismo; motivo del cambio de alcance del 7/10 = plazo y falta de otros usuarios; del 17 al 19/10 no hubo desarrollo; dominio registrado el ~~5/10/2026~~ **12/10/2026** (vence el 12/10/2027, fecha exacta de Namecheap; corregido, ver la entrada de arriba).

**Pendiente, en orden:**
1. Plan del 17/10 (no se hizo): reglas exploratorias nuevas (brazo del lanzamiento para el saque, sentido de giro del tronco para drive contra revés, D por golpe), **revisar a mano los 5 revés de perfil** (`20260924_VCR_reves_perfil_240_01_rep01/02/03`, `20260925_VCR_reves_perfil_240_02_rep02/03`) y el **protocolo de una jornada** (tipo de golpe, encuadre y lado; un video largo por combinación) para datos nuevos de validación.
2. Congelar el motor el 24/10; limpieza y nueva subida; ensayo cronometrado; video y capturas de respaldo; PDF impreso en papel.
3. Respaldo fuera de la PC y `pg_dump` (necesita la contraseña de la base); correo con otro proveedor y alias de Privacidad; revisar `/privacidad`.
4. Después de la demo: Criterio 3 (ii) con el tiempo real, calibrar D, `RESPALDO_POR_GRUPO` (b), re-medir el Criterio 2 con el motor 0.5.x, sesión del lado derecho, cintas de color.
5. Redacción: Cap. 4 (40 filas en `correcciones-pendientes-capitulo-4.md`), Cap. 6 y 7 (`insumos-capitulo-7.md`, §9 delta y §10 pendientes resueltos), Cap. 8 (`insumos-capitulo-8.md`).

**Cómo retomar:**
```bash
cd C:\Users\valen\motion-biomech-detect
git fetch origin && git status -sb                       # main = origin/main + 3 commits de docs
cd backend
PYTHONPATH=. .venv/Scripts/python.exe ../tools/respaldo/estado_de_la_base.py                      # cuentas, sesiones, en curso, huérfanos
PYTHONPATH=. .venv/Scripts/python.exe ../tools/respaldo/tiempos_y_origen_de_las_subidas.py        # cola y origen de los archivos
PYTHONPATH=. .venv/Scripts/python.exe -m pytest ../tests -m "not slow" -q                         # 620 esperadas
cd ../frontend && bun test                                                                         # 122 esperadas
```
**Reglas que no hay que revertir:** ningún grupo emite veredicto del orden (035–037); no reintroducir puntaje ni color de estado; todo lo que contradiga el Capítulo 4 se registra en el momento (CLAUDE.md §6); avisar antes de cada push a `main`; todo el corpus es de un jugador diestro, dos sesiones, cámara a la izquierda.

---

## 2026-10-16 (tarde) — Navegación del celular publicada en main, 038 adelantada (etapa 1: NO cumple) y verificación de cuentas

**Cambio de calendario (pedido de Valentín el 16/10):** el tipo de golpe y el encuadre se **intentan antes de la demo** (el lado de la cámara, no), en **dos etapas con puerta** y **límite el 23/10** (lo que no esté validado e integrado ese día queda para después; el motor se congela el 24/10).
Reemplaza el punto 3 de la aprobación del 15/10 en `docs/decisiones/038-…` (actualizada, con el resultado) y en `demo-guion.md` y `plan-mvp-punta-a-punta.md`.

- **Verificación de las cuentas borradas (solo lectura, 16/10):** **1 cuenta** en `auth.users` (la de v.capelloramil); `usuarios` 1, `atletas` 1, `sesiones` 8, `videos` 18, `reportes_biomecanicos` 17, todas con dueño; **0 filas sin dueño**; `metricas` y `alertas` cuelgan de `reportes_biomecanicos` con
  `on delete cascade` (no se pudieron leer con el cliente de servicio, la integridad la da la clave foránea). Storage: `videos` 18 archivos (607 MB) y `artefactos` 47 (28 MB), **todos bajo la carpeta de la cuenta que existe: 0 archivos de cuentas inexistentes**; `estado_de_la_base.py`: 0 huérfanos, 0 en curso, 1 fallido. **Los 245 MB huérfanos ya no existen.**
- **Frontend, puntos 1 y 2 (`main` = `9415814`, empujado; sin análisis en curso al momento del push; solo frontend, el servidor sigue en 0.5.5):**
  - **Celular, con sesión:** arriba logo + inicial (menú con «Salir»); abajo barra fija **Biblioteca · Cargar · Perfil** con ícono y texto (56 px; la pestaña Biblioteca queda activa también en reporte, sesión y procesando). El botón «Subir y analizar» queda **sobre** la barra (medido a 390 px: 11 px de aire) y el pie no queda tapado (`--barra-inferior`).
  - **Celular, sin sesión:** logo + Ingresar + Crear cuenta; sin «Inicio»; Tecnología en un menú ☰ (**oculto bajo 360 px** por falta de lugar: queda en el pie). **Escritorio sin cambios.**
  - **Cargar:** sin el texto «iPhone · Android · Computadora» del título; en el esquema de tres cuartos «CÁMARA» ya no pisa la línea punteada, el «90°» pasó debajo de la línea y hay una **raqueta en la mano dominante** (espejada para zurdos; usa la mano del jugador elegido y, sin ella, la contraria al lado de la cámara).
  - **Pruebas:** frontend **122 pasan** (+4: rótulo sin cruzar la línea en los 4 casos, raqueta espejada y sobre el mango), `tsc` y `build` limpios. **Visto en pantalla:** encabezado sin sesión a 360 px y los esquemas (12 variantes); con sesión, la barra, el menú de la inicial y la posición del botón con una sesión simulada **solo para la vista local**
  (alias de Vite en una configuración temporal, ya borrada; no se tocó el código de autenticación). **No visto:** la pantalla de Cargar completa con una sesión real (pide ingresar) ni nada en un celular físico. Republicado por Valentín (ver el cierre al final de esta entrada).
- **038, etapa 1 (validación sin tocar el producto): NO cumple en ningún campo** (`docs/resultados/deteccion-038-etapa1.md`; arnés `backend/app/medicion_deteccion.py`; reglas fijadas y commiteadas **antes** de medir, `fee1003`; ajuste en una sesión y evaluación en la otra):

  | Campo | Determinados | Error (Wilson 95 %) | No determinado | ¿Cumple? |
  | --- | --- | --- | --- | --- |
  | Tipo de golpe | 1 de 76 | 100 % | **98,7 %** | No |
  | Encuadre, tipo verdadero | 35 de 76 | 14,3 % (6,3–29,4 %) | 53,9 % | No |
  | · saque / drive / revés | 18 / 13 / 4 | 0 % / 15,4 % / 75 % | 37,9 % / 45,8 % / 82,6 % | No |
  | Encuadre, tipo detectado | 6 de 76 | 66,7 % | 92,1 % | No |

  Causas: la posición de «trofeo» del saque no existe en la ventana de preparación de este jugador (muñeca 5–18 cm **bajo** la nariz; `s_saque` = 0 en los 8 saques con dato; 32 de 76 sin dato por el brazo lejano); drive contra revés, dos candidatas separan una sesión y ninguna la otra (un atípico por clase rompe los extremos); D **no distingue el encuadre del drive y va invertido en el revés**.
  Análisis **exploratorio posterior** (post hoc, optimista, no cuenta; `1eef8d7`): ~10 % de error para saque contra resto y drive contra revés, encuadre de saque 0/28; tampoco llega al 5 %. **Cinco revés de perfil** tienen la muñeca alta en el contacto: hay que **mirarlos a mano** (¿pose, técnica o etiqueta?).
  **La etapa 2 no se propone** (condición: que la etapa 1 cumpla). Camino posible: una sesión nueva con saque, drive y revés (≥ 12 por celda; se puede sumar a la del lado derecho) para validar reglas robustas fijadas de antemano; el segundo camino de la 038 («propone y el usuario confirma») no exige el 5 %.
- **Pruebas del servidor:** suite rápida **620 pasan** (597 + 23 del arnés de la 038).
- **Capítulo 7:** §2.10 y fila 24 en `docs/tesis/insumos-capitulo-7.md`.

### Cierre del 16/10 (informe de Valentín) y plan para mañana
- **Frontend republicado** y **navegación en celular verificada por Valentín, con y sin sesión** (lo que yo no había podido ver: Cargar completo con sesión real y un celular físico). Se reemplaza la nota «falta que Valentín republique» de arriba.
- **Resultado negativo de la etapa 1 de la 038** (ver arriba y `docs/resultados/deteccion-038-etapa1.md`): ningún campo cumple.
- **Plan para el 17/10 (no se empezó nada de esto):**
  1. **Reglas nuevas, exploratorias:** brazo del lanzamiento para el saque (la otra muñeca arriba al comienzo, cláusula que no se usó el 16/10), sentido de giro del tronco para drive contra revés, y recalibrar D **por tipo de golpe** (con la orientación invertida del revés). Todo exploratorio: lo que se elija mirando las dos sesiones del corpus no se puede validar con ellas.
  2. **Revisar a mano los 5 revés de perfil «raros»** (muñeca alta en el contacto): `20260924_VCR_reves_perfil_240_01_rep01/02/03` y `20260925_VCR_reves_perfil_240_02_rep02/03` (¿pose, técnica o etiqueta?).
  3. **Protocolo de una sola jornada** para datos nuevos de validación: tipo de golpe, encuadre y lado de la cámara en el mismo día; **un video largo por combinación** (a recortar después). Se integra con `docs/protocolo-sesion-lado-derecho.md`.
  4. **Calendario:** la **demo va con la carga declarada**; la detección se integra **solo si valida antes del 23/10**; el motor se congela el 24/10.
- **Push:** sin análisis en curso (verificado con `estado_de_la_base.py` al cerrar), se empujan a `main` los commits de docs y del arnés de la 038 (sin efecto en el motor; Render redeploya el mismo 0.5.5).

**Estado de commits:** `main` local está **por delante de `origin/main` (`9415814`)** (`git log origin/main..main`) (los de docs y arnés de la 038 **no están empujados**: empujar redeploya Render; se publican con el próximo push, sin efecto en el motor). Producción sigue en 0.5.5.

---

## 2026-10-16 — ESTADO DE CIERRE DE CONTEXTO (retomar desde acá)

**Nada nuevo se empezó en esta entrada:** es el resumen de lo que hay, lo que se probó y lo que viene. Verificado el 16/10 con las herramientas de solo lectura (`tools/respaldo/estado_de_la_base.py`) y contra producción.

### 1. Qué está en producción
| Qué | Estado | Cómo se verificó |
| --- | --- | --- |
| **Servidor (Render Standard)** | `main` = **`4f07ee7`**; motor **0.5.5**, contrato 1.4; `/health` = `{"estado":"ok","version_motor":"0.5.5"}` | `curl /health` (16/10) |
| **Frontend (Cloudflare, `kinetiqtennis.me`)** | el build de `4f07ee7` está publicado: el chunk `upload-DdiH1VuF.js` de producción es **idéntico** al del build local y trae el desplegable de Cargar | comparación del nombre y del texto del chunk (16/10) |
| **Base (Supabase)** | **sin migraciones nuevas** desde `20261012000000` (13 archivos en `supabase/migrations/`); 1 cuenta, 8 sesiones, 18 videos, 17 reportes | herramienta de estado |
| **Correo** | SMTP propio (Brevo) funcionando; registro, confirmación y "Olvidé mi contraseña" probados (informe de Valentín) | decisión 034 |
| **Pruebas** | servidor **597 pasan** (suite rápida), frontend **118 pasan**, `tsc` y `build` limpios | corridas del 15/10 antes del push |

`main` y `respaldo-13-10` están en el mismo commit. Los documentos de esta entrada son el único cambio posterior.

### 2. Qué se probó el 15/10 (en producción, con el frontend republicado)
- **Informe de Valentín:** **Perfil, Evolución, PDF (golpe y sesión), desplegable de Cargar y "Eliminar mi cuenta"** funcionan.
- **Verificado por mí:** "Eliminar mi cuenta" no dejó nada (**0 filas** sin dueño y **0 archivos** en carpetas de cuentas inexistentes, en Postgres y en los dos buckets). Del desplegable verifiqué que **el texto está en el chunk publicado**;
  no lo vi renderizado (la pantalla pide sesión).
- **Sigue sin verse:** Evolución con las sesiones del corpus **subidas con el motor congelado** (hoy tiene versiones mezcladas) y el PDF **impreso en papel**.

### 3. Cuentas y datos (16/10)
- **Una sola cuenta:** la principal ("Valentín", creada el 9/10, jugador): **8 sesiones, 18 videos, 65 archivos (635 MB)**, último ingreso el 16/10.
- **Eliminadas por Valentín** con "Eliminar mi cuenta": la de prueba del 15/10 (gmail), la de la página de prueba del iPhone (creada el 6/10) y la de rol entrenador (creada el 15/10). **Los 15 archivos huérfanos (245 MB) desaparecieron con la de prueba del iPhone.**
  Verificado: sin filas ni archivos sin dueño.
- **Datos de B (sin tocar todavía):** versiones del motor **mezcladas** (0.4.1 ×2, 0.5.0, 0.5.2, 0.5.3 ×12, 0.5.4) y **dos sesiones por fecha** (24 y 25/9) → Evolución mostraría puntos duplicados. **1 video fallido.** **Nada en curso.**

### 4. Decisiones aprobadas (15/10)
- **038 — detección automática** (`docs/decisiones/038-…`): **diseño A** (propone después, dentro del análisis); **criterio de aceptación ≤ 5 % de error entre los determinados y ≤ 20 % de "no determinado"** como **pre-registro**
  (fijado antes de ver datos); **tipo de golpe: lo asigna el sistema solo si es seguro, separa en sesiones distintas y lo informa ("5 saques y 1 drive"), pregunta solo si es "no determinado", el usuario corrige; si no se cumple el criterio,
  "propone y confirma"**; **el lado de la cámara entra en la clave de la serie de Evolución**. **La implementación va DESPUÉS de la demo.** Antes de la demo, **solo si el 24/10 el núcleo está completo: extender D a drive y revés.**
  Abiertas sin instrucción nueva: encuadre y lado siguen "detecta y propone, el usuario corrige".
- **013 — el lado de la cámara es una recomendación, no una restricción:** se recomienda el contrario a la mano dominante (el validado con el corpus); se aceptan los dos lados; nota neutra en el reporte si es el de la mano dominante (motor 0.5.5).
- **Sesión del lado derecho** (`docs/protocolo-sesion-lado-derecho.md`): la graba Valentín **cuando el clima lo permita** (avisa); variante aprobada de **girar al jugador** (perfil 180°, tres cuartos por delante 90° hacia su izquierda).

### 5. Calendario y congelamiento
| Fecha | Qué |
| --- | --- |
| **24/10** | **Congelar el motor** (`engine/` y `ensamblar_reporte.py` sin cambios pendientes; `git tag motor-congelado-<versión>`). Ese día, **si el núcleo está completo**, antes de congelar: extender D a drive y revés |
| **25–26/10** | **Limpieza y nueva subida** (plan paso a paso en `docs/demo-guion.md` §C): respaldo, eliminar las 8 sesiones de la cuenta, subir sesión 1 (24/09, 6 saques), sesión 2 (25/09, 6 saques), un drive de perfil y un revés de tres cuartos (`recortes-demo`), verificar con la herramienta, respaldo final |
| **26–27/10** | Ensayo cronometrado con los datos definitivos; video de pantalla y capturas de respaldo |
| **27/10 (D−1)** | Checklist (`demo-guion.md` §B) y **congelamiento total** (no se publica nada) |
| **28–30/10** | **Demo** |

**No se sube nada antes del congelamiento:** si el motor cambia después de subir, hay que repetir.

### 6. Pendiente (en orden)
1. **Congelar el motor el 24/10** y decidir D para drive y revés (0,5–1 sesión, solo si el núcleo está completo).
2. **Limpieza y nueva subida** el 25–26/10 (Valentín borra y sube; yo verifico después de cada paso).
3. **Ensayo** de la demo dos veces con cronómetro; **video de pantalla** y **capturas**; PDF impreso en papel.
4. **Copia del respaldo fuera de la PC** y copia completa con `pg_dump` (necesita la contraseña de la base; no la tengo): ver `docs/respaldo-y-restauracion.md`.
5. **Correo:** probar con una dirección de **otro proveedor** y el límite de envíos por hora; alias de contacto de Privacidad; revisar el texto de `/privacidad` (declaración de Valentín).
6. **Sesión del lado derecho** cuando el clima lo permita; después, decidir (c) de la 038.
7. Después de la demo: calibrar D drive/revés si no entró, Criterio 3 con el tiempo real, `RESPALDO_POR_GRUPO` (columna b), implementación de la 038, y solo si hay tiempo cintas de color.
8. Redacción: Cap. 4 (35 filas en `docs/tesis/correcciones-pendientes-capitulo-4.md`), Cap. 6 y 7 (`docs/tesis/insumos-capitulo-7.md`).

### 7. Reglas vigentes que no hay que revertir sin avisar
- **Ningún grupo emite veredicto del orden** (035 y 036); **"golpe medido"** y "sin diferencia medible" (037); brazo "no medido" con su motivo, sin máximo parcial.
- **Todo lo que contradiga el Capítulo 4 se registra en el momento** en `correcciones-pendientes-capitulo-4.md` (CLAUDE.md §6).
- **Vocabulario:** se documenta, no se diagnostica ni predice; etiqueta "Solo registrado".
- **Avisar antes de cada push a `main`** (redeploya Render); no publicar con análisis en curso; **el respaldo antes de publicar** (`docs/publicacion-y-vuelta-atras.md`).
- **Todo el corpus es de un jugador, dos sesiones y cámara a la izquierda:** toda cifra de orden vale para ese lado.

### 8. Dónde está cada cosa
`docs/demo-guion.md` (guion, checklist, limpieza, plan B) · `docs/publicacion-y-vuelta-atras.md` · `docs/respaldo-y-restauracion.md` y `tools/respaldo/` · `docs/decisiones/038-…` y `013-…` ·
`docs/protocolo-sesion-lado-derecho.md` · `docs/tesis/insumos-capitulo-7.md` y `correcciones-pendientes-capitulo-4.md` · `docs/resultados/` · respaldo local en `C:/Users/valen/kinetiq-data/respaldos/` (fuera del repositorio) ·
recortes en `Desktop/corpus-originales-reales/recortes-evolucion/` y `recortes-demo/` (fuera del repositorio).

### 9. Cómo retomar
```bash
cd C:\Users\valen\motion-biomech-detect
git fetch origin && git status -sb                       # main = origin/main = 4f07ee7 (más esta entrada)
cd backend
PYTHONPATH=. .venv/Scripts/python.exe ../tools/respaldo/estado_de_la_base.py   # cuentas, sesiones, versiones, en curso, huérfanos
PYTHONPATH=. .venv/Scripts/python.exe -m pytest ../tests -m "not slow" -q      # 597 esperadas
cd ../frontend && bun test && node_modules/.bin/tsc --noEmit                   # 118 esperadas
```

---

## 2026-10-15 (más tarde) — Probado en producción, cuentas, 038 (tipo de golpe automático), Cargar por dispositivo, Evolución y recortes de la demo

- **Probado en producción por Valentín** (frontend republicado): **Perfil, Evolución y PDF (golpe y sesión)** funcionan y se descargan. **"Eliminar mi cuenta" probado con una cuenta de prueba: funcionó.**
  **Verificado por mí (solo lectura):** la cuenta ya no está en `auth.users` (3 cuentas; estaba en el respaldo de las 21:49), **0 filas** de `usuarios`, `atletas`, `sesiones` ni `videos` sin dueño y **0 archivos** en carpetas de cuentas
  inexistentes en los dos buckets. Es la primera ejecución real de `DELETE /cuenta` (antes solo razonada del esquema).
- **Cuentas restantes:** A (6/10, sin sesiones, **15 archivos huérfanos de 245 MB** de la página de prueba del iPhone), B (principal: 8 sesiones, 18 videos, 65 archivos, 635 MB) y C (15/10, rol entrenador, sin sesiones ni archivos).
- **Decisión 038, segunda ronda:** (a) el **tipo de golpe** lo asigna el sistema solo cuando la detección es segura y, si una carga trae golpes de distinto tipo, los **separa en sesiones distintas y lo informa** ("5 saques y 1 drive");
  pregunta solo si es "no determinado"; el usuario corrige; si no se cumple el criterio (≤ 5 % de error), pasa a "propone y confirma". (b) **El lado de la cámara entra en la clave de Evolución: sí.**
- **Cargar:** las instrucciones son ahora un **desplegable cerrado con pestañas iPhone · Android · Computadora** (la del dispositivo detectado viene preseleccionada), cada una con el esquema del encuadre recomendado. Android: "Cámara lenta" (no
  "Súper cámara lenta"), recortar sin cambiar la velocidad, evitar WhatsApp y a veces Google Fotos, **no probado en todos los modelos** (el sistema avisa si no llega a 120 fps). Computadora: original sin compresión y recorte sin recodificar; se nombra
  **LosslessCut** porque su documentación dice que corta sin recodificar ("lossless trimming", copia directa de datos con FFmpeg), con la salvedad de que corta en fotogramas clave.
- **Evolución:** el gráfico "Golpes con el mismo orden" se **oculta** cuando ninguna sesión tiene 5 golpes ordenables y queda una frase que explica por qué (lo habitual en tres cuartos: 8,33 ms de tolerancia). La leyenda "KinetiQ documenta…" quedó **una sola vez**
  (en el pie) en Perfil, Privacidad, Reporte y Sesión.
- **Recortes de la demo** (fuera de git, `Desktop\corpus-originales-reales\recortes-demo\`): **12 recortes verificados** (6 drive de perfil y 6 revés de tres cuartos de la sesión 2); `recortar_evolucion.py --grupos demo`.
- **Guion de la demo, §C reescrito:** la limpieza y la nueva subida se ejecutan **después del congelamiento del motor (24/10)**, el 25–26/10, con paso a paso (qué borra Valentín, en qué orden, qué sube con qué fecha).

---

## 2026-10-15 (noche) — Push a main, 0.5.5 en producción, 038 aprobada y guion de la demo

- **`main` publicado:** `56a13c1..a377e71` (avance rápido; sin análisis en curso al momento del push). **`/health` = 0.5.5 verificado tres veces seguidas**; `GET /evolucion` y `DELETE /cuenta` responden 401 sin token (rutas nuevas vivas).
  Falta que Valentín **republique el frontend** (`bun run build` y `wrangler deploy`).
- **Decisión 038 aprobada por Valentín:** diseño **A**, criterio **≤ 5 % de error y ≤ 20 % de "no determinado"** como **pre-registro** (fijado antes de ver resultados de detección), implementación **después de la demo**; antes de
  la demo **solo si el 24/10 el núcleo está completo: extender D a drive y revés**. Abiertas: mover un golpe a pedido y el lado en la clave de Evolución. Protocolo del lado derecho: **variante de girar al jugador** en vez de mover la
  cámara (perfil 180°; tres cuartos por delante 90° hacia su izquierda, porque con 180° queda por detrás), con controles previos y sin contraluz.
- **Hallazgo de la base (solo lectura):** todas las sesiones están en la cuenta B; **A, C y D no tienen sesiones**; hay **15 archivos huérfanos (245 MB)** en `prueba-iphone` de la cuenta A (restos de la página de prueba del iPhone);
  versiones del motor mezcladas (0.4.1, 0.5.0, 0.5.2, 0.5.3 × 12, 0.5.4) y dos sesiones por fecha: hay que limpiar antes de la demo. `tools/respaldo/estado_de_la_base.py` (solo lectura) lo verifica.
- **`docs/demo-guion.md`** (paso 8, sin programar): guion de ~13 min con lo que hay que decir de los límites, preguntas esperables, checklist de D−1, plan de limpieza ordenado y plan B. **Falta:** cortar un drive y un revés del corpus,
  probar "Eliminar mi cuenta" con una cuenta descartable, ensayar con cronómetro y grabar el video de respaldo.

---

## 2026-10-15 — Publicación preparada (sin push a main), Perfil real, esquema de encuadre, nota del lado, correo funcionando, propuesta 038 y paso 7

**`main` y `origin/main` no se tocaron:** todo está en `respaldo-13-10`, a la espera del OK de Valentín para el push (cada push a `main` redeploya Render).

### Publicación de los pasos 5 y 6 — qué se comprobó antes
- **Migraciones: ninguna.** `git diff origin/main respaldo-13-10 -- supabase` está vacío; los pasos 5 y 6 y lo de hoy no tocan esquema ni políticas. No hay nada que aplicar ni deshacer en la base.
- **Pruebas en verde sobre la rama:** servidor, suite rápida **589 passed** (antes de los cambios de hoy; se corrió de nuevo al final); frontend `bun test` 106 → 114 con lo nuevo, `tsc` y `bun run build` limpios.
- **Respaldo antes de publicar** (porque `DELETE /cuenta` es irreversible): hecho (ver paso 7). **Volver atrás en Render y en Cloudflare:** `docs/publicacion-y-vuelta-atras.md`.

### Perfil sin nada de la maqueta
- Auditado todo `frontend/src`: la maqueta ya no estaba en la rama de respaldo (el Perfil real salió en el paso 5); no hay estadísticas inventadas, "Compartir con un profesional", "Notificaciones", "Métricas preferidas", planes ni
  precios. "Alerta de carga" solo queda como etiqueta del vocabulario de estados que ningún reporte emite.
- **Agregado:** tarjeta **"Tu actividad"** con datos reales: sesiones, golpes cargados y golpes medidos (misma definición que la Biblioteca), y cuántos no se pudieron medir o siguen en análisis. `resumirActividad` con pruebas.

### Esquema de encuadre en Cargar (decisión 013)
- La cámara se dibuja del lado **contrario a la mano dominante** (a la izquierda de un diestro; **espejo para zurdos** según la mano del jugador elegido o cargado) y, en tres cuartos, **por delante** del jugador en diagonal de 45°.
  Geometría en `lib/esquema-encuadre.ts` con pruebas. Protocolos corregidos ("por detrás" y "del lado de la raqueta").
- **Es una recomendación, no una restricción:** el esquema y el selector dicen "Recomendado" y por qué (la condición validada con el corpus); se acepta el otro lado. **Motor 0.5.5:** si la cámara estuvo del lado de la mano
  dominante, el reporte agrega una nota neutra ("Este lado de cámara todavía no está validado; el brazo puede verse mejor, pero cadera, tronco y encuadre se calibraron con el otro lado."). Sin cambio de contrato ni de números.
  Registrado en la decisión 013 como recomendación revisable tras la sesión del lado de la raqueta.

### Correo propio funcionando (informe de Valentín)
- Brevo generó la clave SMTP, Valentín la cargó en Supabase y probó **registro, confirmación y "Olvidé mi contraseña"** con una cuenta de prueba: funciona todo. Registrado en las decisiones 034 y 027. **Sin verificar:** entrega a otros
  proveedores y el límite de envíos por hora.

### Propuesta 038 (sin programar)
- `docs/decisiones/038-deteccion-automatica-en-la-carga-propuesta.md` y `docs/protocolo-sesion-lado-derecho.md` (28 saques, ≈ 1 h 30 min; recomendado 40 golpes). Dato que condiciona todo: **el corpus es de un solo lado**, así que el
  detector de lado no se puede validar sin esa sesión. Antes de la demo solo entraría el banco de validación y D para drive y revés, y solo si el 24/10 el núcleo está al 80 %.

### Paso 7 — respaldo con restauración probada
- `backend/app/respaldo.py` (exportar y verificar) y `tools/respaldo/restaurar_prueba.py` (Postgres local descartable). **Primer respaldo:** 3 cuentas, 8 sesiones, 18 videos, 17 reportes, 35 métricas, 33 + 47 archivos, **840 MB,
  íntegro**; en `C:/Users/valen/kinetiq-data/respaldos` (fuera del repositorio). **Restauración verificada: 16 de 16 comprobaciones** (`docs/resultados/respaldo-restauracion-2026-10-15.json`). Procedimiento y límites
  (contraseñas, configuración de Supabase y Render, probado en local y no en un proyecto Supabase real): `docs/respaldo-y-restauracion.md`.
- **Falta:** copiar la carpeta a un disco externo y la copia completa con `pg_dump` (necesita la contraseña de la base, que no tengo).

### Pendiente
1. **OK de Valentín para el push a `main`**; después: `/health` = 0.5.5 (tres veces) y republicar el frontend.
2. Probar en pantalla real los pasos 5 y 6 (eliminar cuenta con una cuenta descartable, Evolución con las dos sesiones, PDF impreso).
3. Decidir la 038 (A o B, criterio de aceptación) y si se graba la sesión del lado derecho el fin de semana.
4. Paso 8: ensayo de la demo.

---

## 2026-10-13 (después del cierre) — Lado de la cámara confirmado (izquierda, no dominante), insumos del Capítulo 7 y documentos corregidos

**Solo documentación y verificación de lectura; sin cambios de código ni de motor.** Rama `respaldo-13-10`.

- **Confirmado por Valentín:** en todos sus videos la cámara estuvo **a su izquierda (lado no dominante; es diestro)**. La decisión 013 era la correcta; el protocolo y las notas que decían "del lado de la
  raqueta" estaban mal.
- **Verificado en la base (solo lectura):** las **7 sesiones** subidas (24 y 25/9) tienen `lado_camara = izquierda` y el atleta `mano_dominante = derecha`. **Un lado mal declarado no cambia ningún cálculo:** el
  motor usa la mano dominante del atleta para elegir el brazo, no el lado de la cámara; `lado_camara` solo viaja al reporte de sesión y a Evolución, que avisa si dos sesiones de una serie tienen lados
  distintos. El contraste de encuadre (D) usa el valor absoluto del giro de hombros.
- **Documentos corregidos:** `protocolo-sesiones-evolucion.md` (lado = izquierda, también para las sesiones nuevas opcionales), `protocolo-saques-tres-cuartos.md`, `protocolo-grabacion.md` (ángulo A y ficha de
  la sesión), `resultados/brazo-por-golpe.md` ("Implicancia" y el hallazgo: condición del lado de grabación, trabajo futuro del lado de la raqueta con la salvedad de comparabilidad), decisión 013
  (actualización) y `tesis/correcciones-pendientes-capitulo-4.md` (nota 19, limitación para los Capítulos 6 y 7). `tesis/insumos-capitulo-7.md` ya lo trae.
- **Queda abierto (decisión de Valentín):** el esquema de encuadre de Cargar (`frontend/src/components/esquema-encuadre.tsx`) dibuja la cámara del lado de la raqueta de un jugador diestro, contrario al
  corpus. No se tocó. Además `protocolo-grabacion.md` describe tres cuartos "a unos 45° por delante del jugador" y los otros protocolos "por detrás": no se verificó cuál fue el del corpus.

---

## 2026-10-13 (cierre del día) — Estado, qué está solo en la rama de respaldo y cómo retomar

**Lo que no se hizo hoy a propósito:** nada nuevo después de esta entrada. El árbol de trabajo está limpio y todo lo terminado está commiteado.

### Dónde está cada cosa

| Qué | Dónde | Commit | En producción |
| --- | --- | --- | --- |
| Motor 0.5.4, contrato 1.4, decisión 037 (empate = golpe medido, "sin diferencia medible", picos no medidos con motivo), hallazgos a–e, PDF barato, `GET /sesiones/{id}/consistencia`, recuperación al arrancar, cupo de análisis, eliminar golpe/sesión, Privacidad | `main` | hasta `56a13c1` | **Sí** (servidor: `/health` = 0.5.4; el frontend lo republicó Valentín) |
| **Paso 5:** Perfil real mínimo, descargar mis datos, eliminar cuenta (`DELETE /cuenta`, archivos de ambos buckets primero) | **solo en la rama `respaldo-13-10`** | `5b1dc01` | **No** |
| **Paso 6:** Evolución mínima real (`GET /evolucion`, pantalla `/evolucion`, "Ver mi evolución" en la Biblioteca) y **PDF como documento A4** (golpe y sesión), especificación al día | **solo en la rama `respaldo-13-10`** | `0bbc1df` | **No** |
| Esta entrada | `respaldo-13-10` | el commit siguiente | No |

`main` y `origin/main` quedan en `56a13c1`: **Render no tiene nada nuevo que desplegar** (la rama de respaldo no se despliega). Lo de producción de hoy sigue funcionando sin los pasos 5 y 6.

### Pruebas al cierre (sobre la rama de respaldo)

- Servidor: suite rápida **589 passed** (`PYTHONPATH=. .venv/Scripts/python.exe -m pytest ../tests -m "not slow" -q`, desde `backend/`).
- Frontend: `bun test` **106 pass**, `tsc --noEmit` limpio, `eslint` sin errores (los avisos de `prettier` son anteriores y de todo el árbol), `bun run build` limpio.

### Qué falta probar (no se pudo hoy; nada de esto está verificado en pantalla real)

1. **Eliminar cuenta** (`DELETE /cuenta`): con una **cuenta descartable**, cuando funcione el correo propio (el registro pide confirmar por correo). Cargar un golpe, "Eliminar mi cuenta" y comprobar que Storage
   queda sin la carpeta del usuario en los dos buckets (`videos` y `artefactos`) y que la cuenta ya no entra. La cascada de claves foráneas y `auth.admin.delete_user` están razonadas del esquema, no ejecutadas.
2. **Evolución** en pantalla real con las dos sesiones del corpus (24/9 y 25/9, saque en tres cuartos, ya subidas y procesadas con 0.5.3): ver los dos puntos, la línea de variación, "se mantuvo" o "aumentó/disminuyó"
   y que el aviso de versiones del motor aparezca si mezcla 0.5.3 y 0.5.4. Los gráficos solo se miraron con una serie sintética.
3. **PDF** impreso de verdad (Archivo → Imprimir → Guardar como PDF) del reporte de un golpe y de una sesión: salto de página, imágenes cargadas y A4 vertical. Solo se miró el documento renderizado a 210 mm con
   datos sintéticos.
4. **Perfil** con una cuenta real (guardar nombre y rol, editar un jugador, "Descargar mis datos").
5. **Procesando en escritorio** (título, botón y etiqueta; arreglado el 13/10 pero sin ver con sesión real).
6. Antes de la demo: el **correo de contacto** `contacto@kinetiqtennis.me` (Valentín configuró el reenvío) y revisar el texto de `/privacidad` (declaración suya).

### Cómo retomar

```bash
cd C:\Users\valen\motion-biomech-detect
git fetch origin
git checkout main && git merge --ff-only origin/respaldo-13-10   # lleva 5b1dc01, 0bbc1df y esta entrada a main
# probar antes de publicar:
cd backend && PYTHONPATH=. .venv/Scripts/python.exe -m pytest ../tests -m "not slow" -q
cd ../frontend && bun test && node_modules/.bin/tsc --noEmit && bun run build
```

- **Publicar:** `git push origin main` (Render redeploya el servidor; sin análisis en curso, y de todos modos la recuperación al arrancar reencola lo que quede colgado) y después **republicar el frontend**
  (`bun run build` y `wrangler deploy` desde `frontend/`): hacen falta las dos cosas, porque la pantalla de Evolución y el Perfil llaman a `/evolucion` y `/cuenta`.
- **Sigue en el plan (§8):** paso 7 (respaldo con restauración probada, 0,75) y paso 8 (ensayo de la demo, 0,5). Núcleo restante ≈ 1,25 sesiones más las pruebas de arriba. Demo: 28–30/10.
- **Después de la demo (§9):** calibrar D para drive y revés, Criterio 3 con el tiempo real, `RESPALDO_POR_GRUPO` (columna (b)) y, solo si hay tiempo, cintas de color.
- **Decisiones vigentes que no hay que revertir sin avisar:** 035 y 036 (ningún grupo emite veredicto del orden), 037 (empate = medido; brazo "no medido" con su motivo, sin máximo parcial).

---

## 2026-10-14 (tarde) — Paso 6 (Evolución mínima real) y el PDF como documento, en local

**Sin push** (orden de Valentín; suite del servidor 589 passed, `bun test` 106). Las sesiones del corpus (24/9 y 25/9, saque en tres cuartos) ya están subidas y procesadas con 0.5.3.

### Paso 6 — Evolución

- **`GET /evolucion?atleta_id&gesto&encuadre`** (`routers/evolucion.py`, `serie_de_evolucion` en `app/consistencia.py`): la serie de sesiones del mismo jugador, golpe y encuadre, cada una resumida con la **misma**
  función que la vista de sesión (una sola definición de "medido" y de "mismo orden"). Calculada al leer. Devuelve por sesión: golpes medidos, separación cadera-hombro (mediana y dispersión robusta), repetibilidad
  del orden, lado de cámara y versiones del motor; y para la serie: la **variación habitual** (media de las dispersiones por sesión; desde 4 golpes), el **centro habitual** (con ≥ 3 sesiones) y el **cambio** entre
  las dos últimas sesiones con dato, con "dentro de lo habitual" (Δ ≤ variación, la lógica del Criterio 3).
- **Pantalla `/evolucion`** (desde "Ver mi evolución" en la Biblioteca): elegir jugador × golpe × encuadre; cuatro tarjetas (separación, mismo orden, golpes medidos, sesiones); panel de la separación por sesión
  (mediana, línea vertical = variación, banda de "tu variación habitual" desde 3 sesiones, **huecos "SIN DATO" sin interpolar**) y panel de "mismo orden" (k de m, con "SIN ORDEN"/"POCOS" cuando no alcanza).
  Vocabulario neutro (aumentó / disminuyó / se mantuvo; "no es mejor ni peor"), sin color de estado. Avisa lado de cámara distinto entre sesiones y mezcla de versiones.
- **Pruebas:** `test_evolucion.py` (12) y `evolucion.test.ts` (13). Salió el componente y los datos de ejemplo de abril/mayo (`evolucion-atleta`, `evolucion-mock`).
- **No lo vi con datos reales** (no inicié sesión): los gráficos sí los miré con una serie sintética en el navegador; falta verlo con las dos sesiones del corpus.

### El PDF como documento (decisión de Valentín: "no una copia de la pantalla")

- **Vista de impresión propia**, A4 vertical, 1 a 2 páginas, solo en el papel (la pantalla lleva `print:hidden`): `documento.tsx` (primitivas), `documento-golpe.tsx`, `documento-sesion.tsx`.
  **Golpe:** cabecera (KinetiQ, jugador, fecha, golpe, encuadre, fps reales, motor) · resumen en lenguaje llano · tres fotogramas chicos en una fila (o "no medido" con el motivo) · tabla de mediciones con
  confianza · trazabilidad · limitaciones. **Sesión:** lo mismo con las tarjetas de consistencia en texto, el golpe típico y la **tabla de golpes** (estado, separación, qué llegó primero y cuánto como dato observado,
  fps, procesamiento). Evolución imprime la pantalla con la hoja de estilos de impresión.
- **Por qué se cortaban las imágenes:** era la pantalla impresa (tres columnas de `aspect-[3/4]`, `max-height` y `object-fit`); en vertical el ancho no alcanzaba. Ahora cada fotograma es una caja de 44 mm de alto.
- **Lo miré** renderizando el documento con datos sintéticos a 210 mm de ancho (no la impresión real del navegador): se lee como documento y el reporte de un golpe cabe en poco más de una página.
  **Falta:** Archivo → Imprimir → Guardar como PDF con un reporte real (para ver el salto de página y las imágenes cargadas). Las imágenes se piden al abrir la pantalla (`loading="eager"`), así que ya
  están cuando se imprime.
- **Especificación:** §3 y §6 registran que **la web es el reporte simple con "Ver detalle técnico" y el PDF es la versión completa para compartir con un entrenador o un kinesiólogo**.
- **Costo:** ~0,7 sesión (dentro del tope de 1).

### Pendiente

- Valentín: avisar para el push (servidor: `/evolucion`, `/sesiones/.../consistencia` ya publicado; `/cuenta` y `/evolucion` nuevos) y republicar el frontend; probar eliminar la cuenta con una cuenta descartable cuando
  funcione el correo propio.
- Paso 7: respaldo con restauración probada. Paso 8: ensayo de la demo.

---

## 2026-10-14 (mañana) — Push (motor 0.5.4 en producción), hallazgo del brazo registrado y paso 5 (Perfil real + eliminar cuenta) en local

### Push

- **Pusheado `56a13c1`** (decisión 037, PDF, hallazgos a–e; antes `c9f0334`…`93a15aa` del paso 3: consistencia, eliminar, recuperación al arrancar). **`/health` muestra `0.5.4`** (verificado 3 veces seguidas
  tras el despliegue). Al arrancar, la recuperación reencola lo que haya quedado "encolado"/"procesando".
- **Falta (de Valentín):** republicar el frontend (`bun run build` y `wrangler deploy`): sin él, los reportes nuevos del servidor no se ven completos.

### Hallazgo para el capítulo de resultados: el brazo (decisión de Valentín: queda "no medido", sin máximo parcial)

- **Oclusión del codo dominante en tres cuartos:** **52 de 76 repeticiones del corpus (68 %) sin pico del brazo** con el motor actual; en el saque de tres cuartos, 18 de 18. El estimador reporta el codo como no
  visible en todo el armado del golpe (ningún fotograma de los 0,3 s anteriores al pico del tronco llega a 0,5; 82 % de los 0,3 s siguientes), con el hombro visto el 100 %.
- **El motor anterior (0.5.0) informaba un máximo parcial como si fuera del golpe completo** (pico del brazo en 69 de 76, el de la fase posterior al pico del tronco); la regla de cobertura del 75 % (0.5.1) lo retiró.
- **Registrado en** `docs/resultados/brazo-por-golpe.md` ("Decisión" y "Hallazgo para el Capítulo 7", redactado para pegar) y en `docs/resultados/README.md`. Datos: `brazo-por-golpe-13-10.json` y
  `codo-ventana-saque-trescuartos.json`.

### Paso 5 — Perfil real mínimo + eliminar cuenta (local, sin push; suite del servidor 578 passed, `bun test` 93)

- **Perfil** (`/profile`, ya sin datos inventados ni la foto de otra persona): nombre y rol editables (`usuarios`; el nombre también va a los metadatos de la sesión, de donde lo lee la cabecera);
  **jugadores** con nombre, mano dominante y nivel editables (con el aviso de que la mano vale para los análisis nuevos, no recalcula los hechos); **"Descargar mis datos"** (JSON con la cuenta, los jugadores
  y las sesiones con el reporte de cada golpe, sin los archivos); **"Eliminar mi cuenta"** con confirmación escrita ("ELIMINAR"). La cabecera muestra la inicial del nombre en lugar de una foto fija.
  "Vista por defecto" no está: el interruptor Simple/Detallado salió del núcleo y una opción que no hace nada es una promesa falsa. El texto del rol en Registro y Perfil lo dice ("hoy no cambia lo que ves").
- **Servidor:** `DELETE /cuenta` (`routers/cuenta.py`, `app/cuenta.py`) con el JWT del usuario y `{"confirmacion": "ELIMINAR"}`. **Borra primero los archivos** (recorre `<usuario>/` en los dos buckets, paginado)
  **y después la cuenta** (`auth.admin.delete_user`; el resto sale en cascada por las claves foráneas). **Si un archivo falla, no se borra la cuenta** (502) y se puede reintentar: lo contrario dejaría archivos
  con una persona identificable y sin fila que los referencie. Actúa solo sobre el `sub` del token. CORS ahora admite `DELETE`.
- **Pruebas:** `test_cuenta.py` (8: orden archivos→cuenta, fallo parcial, solo la carpeta propia, paginación, confirmación, 401, 502) y `perfil.test.ts` (9).
- **No probado contra la base real:** la cascada de claves foráneas y `delete_user` de Supabase están razonadas del esquema (`on delete cascade` en `usuarios`, `atletas`, `sesiones`, `videos`,
  `reportes_*`), no ejecutadas: no puedo crear cuentas en producción. **Probalo con una cuenta descartable** antes de la demo (cargar un golpe, "Eliminar mi cuenta", y mirar que Storage quede sin la carpeta).
- **`/privacidad`** actualizada: ahora dice que el acceso, la corrección y el borrado se hacen desde Perfil; `contacto@kinetiqtennis.me` queda para quien no puede entrar.

---

## 2026-10-14 (madrugada) — Hallazgos de producción (a–e), decisión 037 y PDF (paso 4), todo en local

**Sin pushear** (orden de Valentín: la cola de la sesión 2 del corpus sigue procesando; un reinicio de Render deja golpes "encolado" para siempre). Motor **0.5.4**, contrato **1.4**.
Pruebas: backend suite rápida **569 passed**, frontend `bun test` **84**, `tsc` y build limpios.

### a) y b) Empate de cadera y tronco = golpe medido (decisión 037)

- Un golpe con cadera 0,296 s y tronco 0,300 s salía "NO AUDITABLE". **Se midió:** pasa a la observación **`sin_diferencia_medible`** (contrato 1.4, aditivo; pastilla gris neutra *"Sin diferencia medible a esta
  resolución"*, con ícono). "No auditable" queda solo para datos no confiables (R3). Corrige la nota del 29/9 de la decisión 015. Los reportes ya guardados se leen igual sin recalcular.
- **"Golpe medido" = picos de cadera y tronco con confianza ≥ 0,5, aunque empaten**; aparte, **"orden distinguible"** (> 8,33 ms). Misma definición en `par_medido` (servidor), `consistencia.py`, el estado
  final del video ("completado") y el frontend (`golpeMedido`, `ordenDistinguible`). La Biblioteca dice "N golpes medidos · K con orden distinguible · M no medibles"; las tarjetas de la sesión, igual.

### c) El pico del brazo (`docs/resultados/brazo-por-golpe.md`)

- **Con el motor actual lo pierden 52 de 76 repeticiones del corpus (68 %); con el anterior, 7 (9 %).** Saque en tres cuartos: 18 de 18 contra 2 de 18; la sesión del 24/9, 6 de 6 contra 0.
- **Es oclusión real, no una regla demasiado estricta:** en la ventana de ±0,3 s del pico del tronco, el hombro dominante tiene confianza ≥ 0,5 el 100 % del tiempo y el **codo el 41 %**; **0 % en la primera
  mitad** (el armado del golpe; confianza cruda del estimador ≈ 0,06) y 82 % en la segunda. Ninguna repetición queda entre 60 y 75 % de cobertura: bajar el piso no recuperaría ninguna.
- **Hecho:** el pico que falta no desaparece: tarjeta **"Pico del brazo: no medido"** en "Tres momentos" con el motivo en palabras simples (`picos_no_medidos`, `motivo_pico_llano`), y el mismo motivo como
  fundamento de la observación del brazo.
- **Decide Valentín** (opciones en el documento): dejarlo así (recomendada), mostrar el máximo de la parte visible como dato parcial rotulado (0,5 sesión), o cambiar el encuadre de grabación del saque.

### d) Procesando en escritorio

- Título `text-3xl md:text-4xl lg:text-5xl` (antes 6xl); "← Volver a la biblioteca" en la fila de arriba, junto al "/ Procesando"; el nombre del archivo corta donde haga falta (`overflow-wrap:anywhere`) y la
  etiqueta "EN CURSO" ya no se sale de la tarjeta (la fila pasa a `flex-wrap`). **No lo vi en un navegador de escritorio con una sesión real** (no inicié sesión): a verificar por Valentín.

### e) Portada del video

- El `<video>` con esqueleto lleva como `poster` el fotograma clave del pico del tronco (el primero que haya): ya no se ve negro antes de reproducir.

### Paso 4 — PDF barato, sin interruptor

- Botón **"Descargar PDF"** en el reporte del golpe y en la vista de sesión: abre el detalle técnico y llama a `window.print()` (también con Ctrl+P, por `beforeprint`). Hoja de impresión en `styles.css`:
  fondo blanco y texto oscuro (la interfaz es oscura), sin cabecera, pie ni botones, sin el video, sin saltos de página dentro de una tarjeta. Solo en el papel: **sello** (título del reporte, versión del motor,
  fecha de generación) y **limitaciones** (R2 y R5: no diagnostica; el orden depende del encuadre; resolución del instrumento; "no medido" no es "normal"; no compara con otros).
- **No lo vi impreso:** se prueba con Archivo → Imprimir → Guardar como PDF sobre un reporte real. Pendiente de Valentín.

### Pendiente / siguiente

- Valentín: avisar cuando la cola termine → push (reinicia Render con el motor 0.5.4, el contrato 1.4, la recuperación al arrancar y el cupo) y republicar el frontend. **Hace falta las dos cosas:** un frontend
  nuevo contra un servidor viejo no ve `picos_no_medidos` ni `sin_diferencia_medible` en reportes nuevos (los viejos los lee igual).
- Paso 5: Perfil real mínimo + eliminar cuenta y datos.

---

## 2026-10-13 (madrugada del 14) — Paso 3: vista de sesión, consistencia entre golpes, eliminar, miniatura, tiempos de cola y recuperación al arrancar

**Sin pushear** (orden de Valentín: un reinicio de Render deja golpes "encolado" para siempre hasta que termine de subir las sesiones del corpus). Esta entrada es del trabajo local.
Pruebas: backend suite rápida **558 passed**, frontend `bun test` 79, `tsc` y build limpios.

### Recuperación al arrancar (tarea 6.5 adelantada; costó ~0,4 sesión)

- `backend/app/recuperacion.py` + arranque en `main.py`: al iniciar el servicio, tras una pausa de 60 s (`KINETIQ_RECUPERACION_PAUSA_S`, para no pisar al proceso anterior en un despliegue), reencola los videos
  `encolado` y `procesando`. **Regla:** el `encolado` nunca empezó (no suma intento); el `procesando` era el que corría cuando murió el proceso (sospechoso de haber agotado la memoria): **suma un intento** y,
  con el tope agotado, pasa a `fallido` (`error_inesperado`) en vez de reanudarse en bucle. Compare-and-swap sobre el estado leído; los que ya están en este proceso no se tocan.
- **Qué no cubre:** un servicio con **dos** instancias a la vez (no es el caso, Standard es una) ni un golpe "procesando" que el proceso anterior sigue completando durante un despliegue más largo que la pausa
  (el segundo resultado pisaría al primero con el mismo contenido). Pruebas: `test_recuperacion.py` (4).
- Con esto, **los golpes que hoy están "encolado" para siempre en producción se recuperan solos en el próximo arranque** (el del push de este paso).

### Tiempos: cola y procesamiento por separado (Criterio 4)

- `tiemposDe` en el frontend: **espera en la cola** (`inicio − encolado`) y **procesamiento** (`fin − inicio`); el detalle técnico del reporte, Procesando y la lista de golpes de la sesión muestran los dos. El
  Criterio 4 mide solo el procesamiento. Registro y lectura de las filas anteriores: `docs/resultados/criterio4-latencia.md` ("Cómo se registra").

### Vista de sesión y consistencia

- **`GET /sesiones/{id}/consistencia`** (`routers/sesiones.py`, `app/consistencia.py`): se **calcula al leer, no se guarda** (nunca queda desactualizada si se elimina o termina un golpe; el frontend no calcula
  nada biomecánico). Devuelve golpes medidos / no medibles / en análisis, separación cadera-hombro (mediana y dispersión robusta desde 4 golpes), repetibilidad del orden (**si fue el mismo, no cuál es el
  correcto**; desde 5 ordenables), golpe típico (el más cercano a la mediana) y golpes que se apartan (> 3 desviaciones robustas, desde 5 golpes, con piso de 1°), y declara la mezcla de versiones del motor.
  Pruebas: `test_consistencia.py` (11), `test_api_sesiones.py` (4: 401, 404 ajena e inexistente).
- **Pantalla `/sesion/{id}`:** "Tus golpes entre sí" (tres tarjetas que dicen por qué falta lo que falta), golpe típico con **selector de golpe** y "Tres momentos", lista de golpes con estado, separación y
  tiempos, y aviso "se pareció menos a los demás" (sin decir que esté mal). Se actualiza sola mientras haya golpes en análisis. La tarjeta de la Biblioteca lleva ahí.
- **Miniatura real** en la Biblioteca (el fotograma del pico del tronco del primer golpe medido; si no hay, un panel neutro). **Procesando** dice "Golpe 2 de 6" y cuántos van listos.

### Eliminar (derecho de supresión, Ley 25.326)

- **Un golpe** (en la vista de sesión) o **una sesión** (en la Biblioteca y en la vista de sesión), con confirmación. Borra los **archivos de los dos buckets** (original y artefactos) y después las filas (el
  reporte se va en cascada); el último golpe de una sesión se lleva también la sesión vacía. Se puede eliminar un golpe `encolado` que quedó trabado.

### Limitaciones

- El borrado de archivos es de mejor esfuerzo: si Storage falla, la fila igual se borra y puede quedar un archivo huérfano (no se ve ni se puede leer desde la interfaz).
- La vista de sesión y el borrado no se probaron contra producción (no inicié sesión): solo contra el tipo de dato real, con pruebas unitarias y build.

---

## 2026-10-13 (noche) — Higiene 2, paso 2 (cargar con varios golpes) y recortes del corpus para Evolución

Pedido de Valentín tras revisar producción con capturas de cada pantalla. Servidor: **sin cambio de motor** (0.5.3); cambia la API (cupo de análisis simultáneos).

### Higiene 2 (frontend)

- **a) Reportes de motor < 0.5.2:** `observacionesDe` no muestra el veredicto (correcto / desvío leve / alerta): pasa a **"Solo registrado"**, sin la frase de "orden esperado" ni la cita, con la nota
  *"Calculado con una versión anterior del motor"*; el reporte guardado no se toca. La Biblioteca ya no cuenta veredictos (cuenta golpes medidos) y marca "Incluye reportes calculados con una versión anterior".
  Pruebas: 4 nuevas (comparación de versiones, versión ilegible, reporte viejo y reporte actual).
- **b) Tecnología:** el sello "v0.1.0" se sacó (cada reporte lleva el suyo, en el detalle técnico); "YOLOv8-Pose" ahora dice que está **prevista, no implementada**; la caja E5 "Estados y alertas" pasó a
  "Observaciones y trazabilidad" (no hay alertas con umbral); "el filtrado va después de la elevación" (la elevación 3D no está implementada) se corrigió; la frecuencia de corte no es fija (se elige por clip).
- **c) Landing:** sin "Veredicto" (ya estaba); "ángulos articulares" pasó a "ángulos de rodilla y codo" (lo que el reporte muestra); "ángulo de tronco" (no se mide) salió; "comparación entre sesiones" lleva
  "(en preparación)" hasta la Evolución; "unos 160 ms" (número sin fuente) pasó a "una fracción de segundo"; "se avisa cuando el reporte está listo" (no hay avisos) pasó a "podés cerrar la página y volver";
  **la foto del kinesiólogo con el paciente se reemplazó por la del saque** y se borró del repositorio; para visitantes, **"Cargar un video" lleva a Crear cuenta**.
- **d) Pie de página:** salieron "Sobre nosotros", "Investigación", "Contacto", "Términos", "Carga y verificación", "Reporte" y "Evolución del atleta" (texto sin enlace). Quedan Tecnología, Alcance del sistema
  y **Privacidad (`/privacidad`, nueva)**: qué datos se guardan, para qué, dónde, cuánto tiempo y cómo pedir el borrado (Ley 25.326).
- **e) Perfil:** sin planes, precios, "PLAYER" ni "Plan Player renovado". El resto (datos inventados, con la marca "Datos de ejemplo") sigue para el paso 5.

### Paso 2 — Cargar con varios golpes

- **Cargar:** selector de archivos **múltiple** (o arrastrar), hasta **12 golpes por sesión**; una fila por golpe con estado (listo / subiendo con progreso / enviando / en análisis / error y el motivo) y botón
  para quitarlo; los que no cumplen (formato, 50 MB) quedan marcados "No se va a subir". Una sola sesión por carga; si un golpe falla, **los demás siguen** y se puede **reintentar solo los que fallaron**
  (los datos de la sesión quedan fijos). Botón fijo abajo ("Subir y analizar N golpes"). **El mínimo de 6 no se recorta** (se recomienda, no se exige).
- **Ayuda para elegir el encuadre:** dos tarjetas con un **esquema visto desde arriba** (cámara a 90° del golpe / en diagonal por detrás, a ~45°) y una frase; aclaración de que "lado de la cámara" es el lado del
  jugador, no el tuyo, y de que el encuadre se mantiene en todas las sesiones para poder comparar.
- **Servidor:** `KINETIQ_MAX_ANALISIS_SIMULTANEOS` (1 por defecto) en `workers/procesamiento.py`. Sin cupo, 6 golpes mandados a la vez habrían corrido en paralelo (~750 MB cada uno en 2 GB). Los que esperan
  siguen en "encolado". Pruebas: `test_workers_procesamiento.py` (4).
- **Limitación conocida:** un reinicio del servicio con golpes en cola los deja "encolado" para siempre (la recuperación al arranque es el paso 7). "Tardó en procesarse" de un golpe en cola incluye la espera.
- **Falta (paso 3):** Procesando "golpe 2 de 6" y la vista de sesión (hoy la tarjeta de la Biblioteca abre el primer golpe).

### Recortes del corpus para la Evolución de la demo (sin grabar)

- **18 recortes** de los originales del 24/9 (IMG_6376, 6 golpes) y del 25/9 (IMG_6392 = toma 02b y IMG_6393 = toma 02c, 6 y 6), saque en tres cuartos: `ffmpeg -c copy` con las ventanas del Paso B.
  Carpeta **fuera del repositorio**: `Desktop\corpus-originales-reales\recortes-evolucion\`. Script reproducible: `backend/app/recortar_evolucion.py`.
- **Verificado, 18 de 18:** misma marca de tiempo de cada fotograma que el original (aritmética entera), ninguno de la ventana falta, tasa real 199,3–201,1 fps, decodifica sin errores y menos de 50 MiB
  (el máximo 49,2 MB). El motor los lee como captura real (probado con 2). **Funciona: esa es la Evolución de la demo.** Qué subir y con qué fecha: `docs/protocolo-sesiones-evolucion.md` §A.

### Para Valentín

1. **Republicar el frontend** (`bun run build` y `wrangler deploy` en `frontend/`) y **pushear** (Render se reinicia con el cupo).
2. **Correo de contacto de Privacidad:** la página dice `contacto@kinetiqtennis.me` (el alias que prevé la guía del dominio). **Hay que crear ese reenvío** (Cloudflare → Email Routing) o decirme otro correo.
   **Revisá el texto de `/privacidad`**: es una declaración tuya (no se usa para publicidad ni se vende; no hay borrado automático).
3. Confirmar el **lado de la cámara** de las sesiones del corpus mirando un golpe (el protocolo era del lado de la raqueta: "a la derecha del jugador").

---

## 2026-10-13 (tarde) — Paso 1 del orden vigente: higiene de contenido (frontend) · plan §8 reordenado

**Orden aprobado por Valentín:** 1) higiene, 2) cargar con varios golpes, 3) vista de sesión, 4) PDF sin interruptor, 5) perfil + eliminar cuenta, 6) Evolución mínima real, 7) respaldo, 8) ensayo. Plan §8 actualizado
(núcleo 10,75 sesiones; el interruptor Simple/Detallado sale del núcleo). Push del commit anterior (decisión 036, motor 0.5.3) hecho.

### Qué se hizo (solo frontend; el servidor no cambia)

- **"Ver un reporte de ejemplo": se sacó el botón** (los tres) y `/reporte` ya no muestra nada: redirige a la Biblioteca. **Por qué esa y no un "Ejemplo real" público:** el ejemplo real pide una ruta pública
  nueva, una copia congelada del reporte con sus fotogramas y su video (hoy en un bucket privado, que se tendría que sacar a un lugar público), y un segundo camino de dibujo del reporte; las imágenes son del
  cuerpo de Valentín en un video real (no se puede asegurar "sin datos personales"); y una copia congelada envejece con el motor y el contrato. Cuesta ≥ 0,5–1 sesión y deja una superficie pública para
  mantener. Sacar el botón cuesta cero y no puede equivocarse. En su lugar: **"Cómo se calcula cada número"** (`/tecnologia`, pública). El ejemplo real queda como opción posterior a la demo.
- **Landing:** sin "Veredicto" ni "✓ Coincide / Orden esperado" (la tarjeta del hero dice "Ilustración" y "Solo registrado"); sin "4 estados" (pasa a "Sin juicio" y "No auditable: si no se pudo medir, se dice");
  agrega la frase de valor y la limitación "no te dice si tu orden de cadera y tronco es el correcto".
- **Biblioteca:** en vez del conteo por veredicto, **"N golpes medidos" y "M no medibles"** (`contarGolpes`, con pruebas). Un reporte viejo con veredicto cuenta como medido, no como "correcto".
- **Código huérfano retirado:** el reporte falso y sus dos componentes (`reporte-mock.ts`, `grafico-secuenciacion.tsx`, `reproductor-sincronizado.tsx`; quedan en el historial de git). `evolucion-atleta` y su mock
  quedan para el paso 6.
- **Pruebas:** `bun test` **62 pass** (3 nuevas), `tsc` limpio, build limpio, `eslint` sin errores (los 6000 avisos de `prettier` son anteriores y de todo el árbol).

### Para Valentín

- **Hay que republicar el frontend** (`bun run build` y `wrangler deploy` en `frontend/`): la landing y la Biblioteca cambian. Render no cambia con este commit.
- **Los reportes que ya están en la base generados antes de la 0.5.2** conservan el veredicto que tenían (es el registro de lo que dijo el motor de esa versión); en la Biblioteca ya no se ven, pero al abrir el
  reporte sí. Si va a mostrar uno en la demo, conviene volver a subir ese golpe.

---

## 2026-10-13 (sesión nueva) — Decisión 036 (ningún grupo emite veredicto), auditoría de pantallas y valor sin veredictos

Retomada desde la bitácora. **No se tocó nada de Brevo ni del correo.** Sin commit ni push todavía (reinicia Render): lo decide Valentín.

### 1. Decisión 036 — hecho (código, pruebas y documentos)

- **Qué:** la suspensión de la 035 se extiende a **drive** (por encuadre: perfil tronco primero 7 de 8, tres cuartos cadera primero 3 de 3; Fisher p = 0,024) y a **revés** (por método: no sigue el patrón y
  el orden de perfil cambia con el giro axial). **Los seis grupos quedan suspendidos.**
- **Por qué hizo falta código:** el drive de perfil estaba sin veredicto **solo porque faltaba la referencia (a)**; con el Criterio 1 cumplido en el Paso B (1a 0,83) y una referencia agregada, habría emitido
  "desvío leve" por la misma causa que la 035. Ahora la garantía es de la tabla: `Suspension` en `RespaldoGrupo`; `con_veredicto` es falso mientras haya suspensión, **sean cuales sean (a) y (b)**.
- **Código:** `backend/app/ensamblar_reporte.py` (`Suspension`, texto y fundamento por gesto), motor **0.5.3** (`engine/version.py`; cambia el texto de las observaciones de drive y revés, sin cambio de contrato).
  Pruebas: nueva `test_la_suspension_gana_aunque_haya_referencia_y_el_criterio_1_se_cumpla` (los seis grupos con (a) y (b) forzados en verdadero); suite rápida **535 passed**.
- **No cambia:** `criterio1_cumplido` de drive y revés (queda con las cifras del Paso A; su revisión es el pendiente 3 de la lista de abajo) ni D para drive y revés.
- **Documentos:** `docs/decisiones/036-…` (nueva) + índice, `especificacion-frontend.md` §1 (el "hoy solo el saque de perfil tiene veredicto" ya no vale), `CLAUDE.md` (motor 0.5.3).

### 2. Auditoría pantalla por pantalla — hecho, sin programar (`docs/ux/auditoria-pantallas-13-10.md`)

- **Lo que no esperaba:** (a) la **landing de producción promete "Veredicto"** y muestra "✓ Coincide / Orden esperado"; (b) **"Ver un reporte de ejemplo" manda a Ingreso** a un visitante (verificado), y detrás
  del login hay un **reporte falso con "5 de 6 correctos"**; (c) **Evolución no existe como pantalla** (hay un componente huérfano con datos de abril); (d) **Perfil sigue siendo la maqueta** (otra persona,
  planes y precios); (e) el reporte real es de **un solo golpe**: lo que la maqueta muestra de "6 golpes" depende de Cargar con varios golpes.
- **Limitación declarada:** las pantallas con sesión las leí del código de `main`, no en producción (no inicié sesión ni creé cuentas); no verifiqué qué commit del frontend está desplegado.
- **Orden propuesto** (núcleo ≈ 11,25 sesiones, mismo margen corto del plan): higiene de contenido 0,75 → Cargar con varios golpes 2,25 → vista de sesión 1,5 → Evolución mínima 1 → PDF e interruptor 1,5 →
  Perfil y eliminar 2,5 → respaldo 1,25 → ensayo 0,5. **Se elimina del plan el puntaje (§8 #15) y la Evolución "de ejemplo" (#13).**

### 3. Valor sin veredictos — propuesta (`docs/ux/valor-sin-veredictos.md`)

- El sesgo es fijo por encuadre, así que **comparar contra uno mismo en el mismo encuadre lo cancela**. Se destaca: variación entre golpes, repetibilidad del orden (**si es el mismo, no cuál es el correcto**),
  golpes medidos completos, magnitudes con su error y cambio entre sesiones **contra la variación propia**; vocabulario neutro y sin color de estado. Sin esto el reporte "parece vacío": el valor visible es la
  cadena fotos reales → datos con confianza → Evolución con sesiones reales.

### 4. Para después de la demo (en el orden de Valentín; `plan-mvp-punta-a-punta.md` §9)

1. Calibrar D para drive y revés. 2. Criterio 3 con el tiempo real. 3. `RESPALDO_POR_GRUPO` (columna (b)). 4. **Al final y solo si hay tiempo antes de la defensa: validación con cintas de color — prueba
tentativa, registrada, sin diseñar.**

### Pendiente / siguiente

- **Decide Valentín:** (a) si commitea y pushea (reinicia Render con el motor 0.5.3); (b) el orden de pantallas de la auditoría §3; (c) **grabar o recortar de los originales dos sesiones reales** de un gesto y un
  encuadre para que Evolución muestre algo real; (d) mirar él las pantallas con sesión en producción una vez.
- **Primer paso de código, con su OK:** higiene de contenido (landing sin veredicto, retirar `/reporte` falso, conteo de Biblioteca) ≈ 0,75 sesión.

---

## 2026-10-13 (00:00) — PASO B COMPLETO (76 repeticiones) · cierre de la sesión

**Estado final:** repositorio limpio y pusheado; nada en curso. Resumen completo en `docs/resultados/paso-b-resumen.md` (y `paso-b-saque.md` para el saque). Corrida: 131,9 min, commit `7c9535c`, motor 0.5.1.

**Resultados (originales a tasa real, regularizados a 240 Hz; tolerancia 8,33 ms):**

| Grupo | Válidas | Cadera primero | Tronco primero | Dentro |
| --- | --- | --- | --- | --- |
| Saque · perfil | 10 | 0 | 8 | 2 |
| Saque · tres cuartos | 18 | 7 | 0 | 11 |
| Drive · perfil | 12 | 1 | 7 | 4 |
| Drive · tres cuartos | 12 | 3 | 0 | 9 |
| Revés · perfil | 11 | 3 | 3 | 5 |
| Revés · tres cuartos | 12 | 0 | 5 | 7 |

- **Saque y drive: el orden depende del encuadre en el mismo sentido** (perfil tronco primero; tres cuartos cadera primero o dentro de la tolerancia; drive p = 0,024, exploratorio). **El revés no sigue el patrón**
  (tres cuartos: tronco primero 5 de 5 ordenables; perfil 3 contra 3 y sensible al método).
- **Criterio 1 (sesión de medición):** cumplen solo el **saque de perfil (1a 0,83)** y el **drive de perfil (1a 0,83)**, los dos con el tronco primero; en la réplica no cumple ninguno; ningún grupo de tres cuartos cumple
  (resolución: más de la mitad dentro de 8,33 ms, con 1b = 1,00).
- **Lectura:** el orden cadera-tronco con una sola cámara no es confiable como veredicto en este material; los grupos que cumplen el Criterio 1 son justamente los sospechosos. Es un resultado para el Capítulo 7.

**Lo que NO se hizo (por orden de Valentín: "no empieces nada más"):**
1. **`RESPALDO_POR_GRUPO` no se revisó con estas cifras:** `drive|perfil` pasaría a cumplir (b) con 1a 0,83; ningún veredicto cambia porque falta la referencia (a).
2. **D (contraste de encuadre) no está calibrado para drive y revés** (hoy solo saque): se puede calibrar con las poses guardadas en `backend/.cache/corpus-real-pose-b`.
3. **Criterio 3 con el tiempo real** (la métrica (ii) depende del tiempo) y el capítulo de resultados.
4. **Mañana:** el resto del plan §8 (punto 1: registro real con correo propio, depende de Brevo/Resend; cargar con varios golpes; consistencia entre golpes; reporte detallado; PDF; perfil; eliminar cuenta; respaldo).

---

## 2026-10-13 (madrugada) — Novedades de Valentín (solo registro): dominio en producción y Brevo

- **Dominio hecho (Valentín):** pasos 1 a 5 de la guía. Deploy con **`kinetiqtennis.me` como dominio personalizado** (el `workers.dev` sigue activo); Supabase **Site URL y Redirect URLs** actualizadas;
  `KINETIQ_CORS_ORIGINS` en Render con los tres orígenes; **prueba en ventana de incógnito OK**; repositorio **`vcapelloramil.github.io` eliminado**. Pendiente de verificar en una próxima prueba: registro con correo real
  (depende de SMTP) y "Olvidé mi contraseña".
- **Brevo:** **sigue sin generar la clave SMTP**; Valentín **abrió un ticket a soporte**. **Si no hay respuesta, se pasa a Resend** (plan B de la decisión 034); el cambio es solo de los datos de SMTP en Supabase y el
  DNS del dominio en Cloudflare (los registros que pida Resend, como "solo DNS").
- **Orden de Valentín:** cuando termine el Paso B de drive y revés, resumir en `docs/resultados`, bitácora al día, commit y push. **No empezar nada más**; sigue mañana en una sesión nueva.

---

## 2026-10-12, 23:45 — Decisión 035 APLICADA (B y D, motor 0.5.2) · lista para publicar

- **B:** el saque no emite veredicto del orden en ningún encuadre (`depende_del_encuadre` en `RESPALDO_POR_GRUPO`); la tarjeta lo explica sin literatura ni estadística y el detalle lleva el fundamento.
- **D:** `engine/encuadre.py`: giro de la línea de hombros en la preparación; si el encuadre declarado discrepa con claridad del visto (perfil ≤ 42°, tres cuartos ≥ 50°), el reporte agrega *"El video parece grabado de tres
  cuartos, pero elegiste perfil. Revisá el encuadre antes de comparar tus resultados."* y no emite veredicto. **No bloquea la carga.** Solo saque (calibrado con 28 repeticiones: 0 avisos falsos).
- **Pruebas:** servidor **505 passed**, `bun test` **59 passed**. Sin cambio de contrato ni de frontend.
- **Falta (de Valentín):** republicar el frontend (cambios del 12/10 y `wrangler.jsonc` con el dominio) y los pasos de la guía (E.1 a E.4). **Paso B de drive y revés sigue corriendo** (`paso_b_resto.log`).
- **Trabajo futuro registrado:** C (tres cuartos como encuadre evaluado) y D para drive y revés (hace falta calibrar con el Paso B).

---

## 2026-10-12, 23:00 — OK de Valentín a la decisión 035 (B y D); C queda como trabajo futuro

- **OK de Valentín:** aplicar **B** (suspender el veredicto del saque de perfil) y **D** (contrastar el encuadre declarado con el visto). **C (tres cuartos como encuadre evaluado) queda como trabajo futuro.**
- **D, requisitos de Valentín:** el aviso se entiende sin tecnicismos (*"El video parece grabado de tres cuartos, pero elegiste perfil. Revisá el encuadre antes de comparar tus resultados."*); **no bloquea la carga**: solo
  no se emite veredicto y se avisa.
- **Registro del origen del golpe de prueba (por pedido de Valentín):** el video de la prueba de producción del 12/10 era **`IMG_6391` (saque de TRES CUARTOS, toma 02)** y se **declaró como perfil por error de Valentín**,
  no del sistema. El reporte aplicó el veredicto del grupo declarado. Es el caso que motiva D.
- **Estado:** Paso B de drive y revés **corriendo** (`backend/.cache/paso_b_resto.log`, ~2 h, commit `7c9535c`). Antes de esto: push a `7c9535c` hecho; falta republicar el frontend (cambios de hoy).
- **Siguiente:** implementar B y D con pruebas (motor 0.5.2), commit, push y avisar a Valentín para republicar.

---

## 2026-10-12, 22:30 — SAQUE DEL PASO B TERMINADO · decisión 035 propuesta · drive y revés en cola

- **Paso B del saque completo** (29 repeticiones, commit `33dd7d9`, motor 0.5.1): perfil **0 cadera primero / 8 tronco primero / 2 dentro**; tres cuartos **7 / 0 / 11**. Fisher p = 0,0002 (exploratorio). Detalle en
  `docs/resultados/paso-b-saque.md`.
- **"Contradicción" resuelta:** el golpe del celular es de `IMG_6391` (saque de **tres cuartos**, toma 02) subido como "perfil" (fecha de captura 25/9 15:23:05 y giro de hombros 59°, dentro de los 50–83° de tres cuartos y
  fuera de los 26–42° del perfil). El reporte le aplicó el veredicto del grupo equivocado.
- **Decisión 035 reescrita como propuesta** (B: suspender el veredicto del saque de perfil + D: contrastar el encuadre declarado con el visto). **Sin aplicar, a la espera del OK de Valentín.**
- **Dominio:** `wrangler.jsonc` con `kinetiqtennis.me` (commit `67c1024`) y la parte de Valentín paso a paso en la guía (sección E). **Brevo:** dominio autenticado, sin poder generar la clave SMTP (Valentín reintenta).
- **En curso:** Paso B de drive y revés (~2 h 10 min), lanzado al final de la sesión. Retomar con el mismo comando de la entrada de parada si se corta; guarda al terminar cada original.

---

## 2026-10-12, tarde — ESTADO DE TRABAJO (retomar desde acá si se compacta la conversación)

Pedido de Valentín: (1) terminar el SAQUE del Paso B (toma 02c incluida), drive y revés al final; (2) analizar la "contradicción" del golpe del celular; (3) proponer la 035 **sin aplicarla**; (4) pushear las 2 notas de
documentación y hacer mi parte del dominio, dejando `workers.dev` funcionando, y darle su parte paso a paso; (5) registrar que Brevo no deja generar la clave SMTP.

**Hecho:**
- Paso B del saque **lanzado** (commit `33dd7d9`, `--grupos "saque|perfil,saque|trescuartos"`, 29 repeticiones; las 23 ya guardadas se re-miden con el motor 0.5.1 y solo se infiere el original IMG_6393). Log:
  `backend/.cache/paso_b_saque.log`. **No mirarlo seguido**: espera de 10–15 min entre controles. Cuando termine escribe `docs/resultados/paso-b-sesion-1.json` y `-2.json`.
- El Paso B ahora fija el commit al arrancar (no al HEAD del momento de escribir).
- **Pusheado** a origin (`33dd7d9`): bitácora y resultados parciales.
- **Dominio, mi parte** (commit `67c1024`, **sin pushear**): `frontend/wrangler.jsonc` con `kinetiqtennis.me` (`custom_domain`) y `workers_dev: true`; verificado en el build. La guía
  (`docs/guia-dominio-correo-y-hosting.md`, sección E) tiene la parte de Valentín paso a paso (deploy, Supabase Site URL y Redirect URLs, `KINETIQ_CORS_ORIGINS` en Render).
- **Brevo (13/10):** el dominio figura **autenticado**; Valentín **no pudo generar la clave SMTP** y lo reintenta él. Si no sale: respaldo Gmail con contraseña de aplicación (decisión 027, B) o Resend. Anotado en la
  decisión 034 y en la guía.
- **Análisis de la "contradicción"** (golpe de producción `cbaf328d`, cadera 13 ms antes que el tronco, contra el tronco primero del Paso B en el perfil):
  - **El video es del corpus: `com.apple.quicktime.creationdate = 2026-09-25T15:23:05-0300` = el original `IMG_6391` (saque de TRES CUARTOS, toma 02)**, recortado. Se subió declarado como "perfil".
    El reporte de producción aplicó entonces el veredicto del grupo `saque|perfil` a un video de tres cuartos: ese "correcto" no corresponde.
  - Se reprocesó el mismo video por el camino del Paso B: **reproduce Δ = +12,5 ms** (cadera 1,658 s, tronco 1,671 s); con cortes de 4 a 12 Hz da +16,7 a +4,2 ms y el giro axial +16,7 ms: **cadera primero o dentro de la
    tolerancia, nunca tronco primero**, como el saque de tres cuartos del corpus (4 de 4 ordenables con la cadera primero). No contradice al Paso B: lo confirma.
  - La apertura de hombros / largo del tronco **no separa** perfil de tres cuartos en el corpus (medianas 0,23 y 0,15; el golpe nuevo, 0,11): no sirve para verificar el encuadre declarado.

**Pendiente (en este orden):**
1. Esperar el saque del Paso B (IMG_6393, ~27 min + re-medición ~5 min) y mirar el resultado **una vez**.
2. Escribir `docs/decisiones/035-...` como propuesta con el saque completo y el análisis de arriba (**no aplicar sin el OK de Valentín**).
3. Escribir el análisis de la contradicción en `docs/resultados/` (causas posibles y cómo comprobarlas sin grabar de nuevo).
4. Pushear `67c1024` y lo que siga (reinicia Render; sin análisis en curso).
5. Drive y revés del Paso B **al final de la sesión** (`--grupos` omitido retoma todo).

---

## 2026-10-12, 19:10 — PARADA ORDENADA (se apaga la PC) · qué quedó a medias y cómo retomar

**No se empezó nada nuevo.** El Paso B estaba corriendo y se detuvo a mano (pid 10196) antes de apagar; lo que ya estaba guardado queda guardado. **Nada de esta entrada está pusheado.**

### Estado del repositorio

- **Rama `main` = rama `ajustes-13-10`**, árbol limpio, con todo lo terminado y probado commiteado.
- **Origin está en `01e8ad4`** (lo publicado y en Render: motor 0.5.1). **Quedan commits locales sin pushear:** la bitácora del 13/10 y este commit (resultados parciales del Paso B + esta entrada). Pushear
  reinicia Render; hacerlo cuando no haya un análisis en curso.
- Pruebas al momento de parar: suite rápida del servidor **486 passed** (en el directorio principal; `test_api_analisis` necesita `backend/.env`), `bun test` **59 passed**, `tsc` y build limpios.
- Limpieza opcional (no hecha, no importa): `backend/.cache/corpus-real-pose/` tiene 3 archivos de una prueba de humo del Paso B **sin la validación de alineación**; no se usan (el Paso B usa `corpus-real-pose-b`).

### Los 7 puntos del último mensaje de Valentín (13/10)

| # | Punto | Estado |
| --- | --- | --- |
| 1 | Registrar la prueba del celular en `criterio4-latencia.md` | **Hecho** (fila 4: 146,7 s, RSS pico 748,4 MB, artefactos 10,2 s) |
| 2a | Video con esqueleto: más resolución y calidad, medir | **Hecho y publicado**: 720 px, CRF 20, ~1,6 MB para 12 s; verificado en producción (1,2 MB, 120 s) |
| 2b | Etiqueta única "Solo registrado" | **Hecho y publicado** |
| 2c | Confianza y ubicación del pico del brazo | **Hecho y publicado**: la confianza estaba bien, eran dos referencias de tiempo distintas sin rotular; y había un máximo censurado (57 % de la ventana sin datos) → regla de cobertura del 75 % (motor 0.5.1) |
| 2d | Fotogramas perdidos = interpolados | **Explicado y con una línea en la trazabilidad (publicado).** **No hecho:** marcar por pico si es medido o reconstruido (propuesta, 0,5 sesión, contrato 1.4) |
| 2e | Coma decimal en todo el reporte | **Hecho y publicado** |
| 3 | Pushear | **Hecho hasta `01e8ad4`**; los commits de bitácora y resultados quedan **sin pushear** |
| 4 | Guía del dominio y decisión 034 | **Guía y decisión hechas** (verificado: DNS ya en Cloudflare, zona vacía; NC.me creó el repositorio `vcapelloramil.github.io`, se puede eliminar). **No hecho (mío):** `wrangler.jsonc` con el dominio, `KINETIQ_CORS_ORIGINS`, prueba de registro real. **No hecho (de Valentín):** borrar el repositorio, registros de Brevo, SMTP en Supabase, URLs permitidas |
| 5 | Paso B y decisión 035 | **Arnés hecho y corrida PARCIAL (abajo). Decisión 035 SIN tomar.** |
| 6 | Reestimar el plan; registrar la grabación doble como trabajo futuro; protocolo opcional | **Hecho** (plan §8 reestimado; `docs/protocolo-saques-tres-cuartos.md`) |
| 7 | Seguir con el punto 3 del plan | **Hecho** (separación cadera-hombro y ángulos de rodilla y codo, `engine/magnitudes.py`; publicado) |

### Paso B: qué se procesó y qué no

Corrida iniciada a las 17:30 sobre el commit `f94aa56` (motor 0.5.0), de 13 originales y 76 repeticiones. **Se paró a los 99 min con 4 originales completos (23 de 76 repeticiones) guardados.**

| Original | Contenido | Estado |
| --- | --- | --- |
| IMG_6374 | sesión 1, saque de perfil (5 rep.) | **hecho** |
| IMG_6396 | sesión 2, saque de perfil (6 rep.) | **hecho** |
| IMG_6376 | sesión 1, saque de tres cuartos (6 rep.) | **hecho** |
| IMG_6392 | sesión 2, saque de tres cuartos toma 02b (6 rep.) | **hecho** |
| IMG_6393 | sesión 2, saque de tres cuartos toma 02c (6 rep.) | **interrumpido sin guardar** (había empezado a las 19:05; se pierde ese original entero, ~27 min) |
| IMG_6377 · IMG_6397 | drive de perfil, sesión 1 · 2 | pendiente |
| IMG_6379 · IMG_6398 | revés de perfil, sesión 1 · 2 (5 rep.) | pendiente |
| IMG_6378 · IMG_6394 | drive de tres cuartos, sesión 1 · 2 | pendiente |
| IMG_6380 · IMG_6395 | revés de tres cuartos, sesión 1 · 2 | pendiente |

**Qué quedó guardado:** las poses de las 23 repeticiones en `backend/.cache/corpus-real-pose-b` (3 archivos por repetición; no versionado) y los resultados en `docs/resultados/paso-b-sesion-1.json` y `paso-b-sesion-2.json`
(commiteados, con `commit: f94aa56`, `version_motor: 0.5.0`, `repeticiones_medidas` 11/35 y 12/41). **Faltan ~35.700 fotogramas ≈ 2 h 40 min** de cómputo.

**Excluidas por diseño:** `saque_perfil_240_01_rep01` y `reves_perfil_240_02_rep01` (empiezan en la rampa) y las 6 repeticiones de `IMG_6391` (original incompleto).

**Resultado parcial** (originales a tasa real, regularizados a 240 Hz; Δ = t_tronco − t_cadera en ms, negativo = el tronco llegó primero; tolerancia 8,33 ms):

| Grupo | Δ por repetición (ms) | Cadera primero · tronco primero · dentro de la tolerancia |
| --- | --- | --- |
| Saque · perfil · sesión 1 | −16,7 · −20,8 · −33,3 · −4,2 (una repetición no válida) | 0 · 3 · 1 |
| Saque · perfil · sesión 2 | −170,8 · −25,0 · −237,5 · −154,2 · −4,2 · −250,0 | 0 · 5 · 1 |
| Saque · tres cuartos · sesión 1 | −4,2 · +20,8 · −4,2 · +4,2 · +4,2 · +4,2 | 1 · 0 · 5 |
| Saque · tres cuartos · 02b (sesión 2) | +16,7 · +8,3 · +41,7 · +4,2 · +12,5 · +8,3 | 3 · 0 · 3 |

**Lectura provisoria:** el "tronco primero" del saque de perfil **se reproduce con los originales** (8 de 8 ordenables, ninguna con la cadera primero): **no viene del corpus convertido**. En tres cuartos, con los originales,
**nunca** sale el tronco primero entre las ordenables (4 de 4 con la cadera primero) y la mayoría queda dentro de la tolerancia. **La dependencia del encuadre del saque se sostiene.** Falta la toma 02c para cerrar el
saque de tres cuartos. Es **un jugador**; el golpe nuevo del celular (cadera 13 ms antes) es una repetición. Esto es lo que respalda la propuesta de la decisión 035, pero **la 035 sigue sin decidirse**.

### Cómo retomar

1. **Encender, abrir el repositorio** (`C:\Users\valen\motion-biomech-detect`, rama `main`) y comprobar el árbol limpio con `git status`.
2. **Reanudar el Paso B** (salta lo que ya está en la caché; **vuelve a medir las 23 ya hechas** con el motor actual, ~5 min, y reescribe los dos JSON; desde acá el `version_motor` de los JSON será 0.5.1):

   ```bash
   cd backend
   PYTHONPATH=. .venv/Scripts/python.exe -u -m app.medicion_paso_b --reales "C:/Users/valen/Desktop/corpus-originales-reales" --salida ../docs/resultados/paso-b
   ```

   Se niega a correr con el árbol sucio (decisión 014). Puede pararse y reanudarse de nuevo: guarda al terminar **cada original**. Para el saque solamente: agregar `--grupos "saque|perfil,saque|trescuartos"`
   (termina en ~35 min).
3. **Con el saque de tres cuartos completo (toma 02c), decidir la 035** (`docs/decisiones/035-suspender-el-veredicto-del-saque-de-perfil.md`): el resultado parcial la respalda. Aplicarla es una línea en
   `RESPALDO_POR_GRUPO` (`("saque", "perfil")` → `criterio1_cumplido=False`).
4. **Pushear** los commits locales cuando no haya un análisis en curso (reinicia Render). **Republicar el frontend:** los cambios de hoy (etiqueta única, comas, tiempos del video y de la ventana, magnitudes, nota de
   interpolación; commit `8a83a30`) **ya están en origin pero NO en Cloudflare** hasta que se corra `bun run build` y `.
ode_modules\.bin\wrangler.exe deploy` en `frontend/` desde la PowerShell.
5. **Valentín:** guía del dominio (partes B a D) y eliminar `vcapelloramil.github.io`; después me pasa un "listo" para hacer el punto 1 del plan (mi parte).
6. Cuando el Paso B termine: `docs/resultados/paso-b-resumen.md` (como `paso-a-resumen.md`) y revisar `RESPALDO_POR_GRUPO` otra vez con las cifras de los originales.

---

## 2026-10-13 (madrugada) — Correcciones del reporte tras la prueba del celular, datos en el reporte y Paso B en curso

Pedido de Valentín tras probar el saque de perfil desde el celular (2 min 28 s; tres fotogramas y video bien de posición; "Olvidé mi contraseña" visible). Suite rápida del servidor **486 passed**; `bun test` **59 passed**;
`tsc` y build limpios. **Publicado** (`01e8ad4`, Render Live con motor 0.5.1) y **verificado en producción** con un usuario de prueba (borrado): 120,3 s de punta a punta, video de 1,2 MB, magnitudes en el reporte.

### Hecho

1. **Criterio 4, fila 4** (`criterio4-latencia.md`): 146,7 s, **RSS pico 748,4 MB** en Standard, artefactos en 10,2 s. En Free ese golpe no habría entrado (512 MB).
2. **Video con esqueleto a 720 px y CRF 20** (antes 360 px / CRF 30 = 160 KB, "se veía muy mal"): ~1,6 MB para 12 s; `ffmpeg` de un hilo, 76 MB; +~7 s por golpe. Medido de nuevo (decisión 033, actualizada).
3. **Etiqueta única "Solo registrado"** en la vista simple, el detalle técnico y el PDF.
4. **Pico del brazo (0,521 s) y confianza 0,99:** revisado sobre el reporte real (`cbaf328d`).
   - **La confianza estaba bien y el pico no cae en el tramo no auditable**: `instante_s` se cuenta desde el inicio de la ventana (que empieza en 1,371 s del video) y los tramos desde el inicio del video; el pico está en
     1,892 s, 180 ms **después** de que termina el tramo del codo (0,333–1,712 s). Eran dos referencias distintas sin rotular. **Ahora la tabla muestra las dos columnas** y los tramos dicen "desde el inicio del video".
   - **Pero había un problema real, distinto:** el codo derecho no tenía datos en el **57 % de la ventana** (1,371–1,712 s), así que el "pico del brazo" era el máximo del último 43 % (la deceleración), no el de la
     ventana. Un máximo censurado presentado como dato (R3). **Regla nueva (motor 0.5.1): si se midió menos del 75 % de la ventana, el pico del segmento no se reporta.** Con el brazo sin medir y la cadera y el tronco
     ordenables, la repetición se informa con esos dos ("el brazo no se pudo medir"), en lugar de perder todo el orden.
   - **El pico, cuando se reporta, está donde corresponde por definición**: es el máximo de la velocidad angular del vector hombro→codo, que no es la velocidad de la raqueta y suele ser más tardío (decisión 011).
5. **"Fotogramas perdidos" e "interpolados" iguales (16,3 %): es lo esperado y no un error.** El iPhone graba sobre un reloj de 240 Hz y entrega ~200,8 fotogramas por segundo: los 240 − 200,8 que faltan son los puntos de la grilla
   que se interpolan, así que las dos cifras coinciden **por construcción** (156 de 959 puntos, huecos de hasta 12,5 ms). Se regulariza a la grilla **nominal** (la del reloj de la cámara) y no a 200,8: los fotogramas que sí
   llegaron quedan en su instante real y solo se rellenan los que faltan; regularizar a la tasa media movería **todos** los puntos. Impacto: un instante que cae en un punto interpolado es una reconstrucción (error acotado por
   el hueco, ≤ 6 ms), comparable a la tolerancia de 8,33 ms. **Corrección hecha:** una línea de explicación en la trazabilidad. **Propuesta (0,5 sesión):** marcar por pico si su instante es medido o reconstruido y
   sumar la incertidumbre del hueco a la decisión de "ordenable".
6. **Coma decimal en todo el reporte** (un solo helper, `frontend/src/lib/formato.ts`), incluidas la tabla de velocidades y la trazabilidad.
7. **Punto 3 del plan (datos en el reporte):** separación cadera-hombro máxima y ángulos de rodilla y codo en el pico del tronco, con su confianza y el error medido contra goniometría (8,5° y 12,5° de media). Mismas
   definiciones que se validaron (Criterios 2 y 3). Sin estado de juicio. `engine/magnitudes.py`.
8. **Dominio** (`kinetiqtennis.me`): **verificado desde afuera** que los servidores de nombres ya apuntan a Cloudflare y que la zona está vacía (ni `A`, `AAAA`, `CNAME`, `TXT` ni `MX`). NC.me creó el repositorio
   **`vcapelloramil.github.io`** (con un `CNAME`); **se puede eliminar** y conviene, después de borrar los registros de GitHub Pages si aparecieran (la guía los lista). Guía y decisión 034 actualizadas.
9. **Paso B** (`backend/app/medicion_paso_b.py`, commit `f94aa56`): originales a tasa real, regularizados a 240 Hz, con las poses reanudables y la alineación validada (la duración de cada ventana contra el decodificador).
   **En curso** (~3–4 h de cómputo; el saque primero).
10. **Plan reestimado** (§8) y **protocolo opcional** de saques con un solo teléfono (`docs/protocolo-saques-tres-cuartos.md`). La grabación simultánea desde dos ángulos queda como trabajo futuro.

### Paso B — primer resultado (saque de perfil, originales a tasa real)

11 repeticiones medidas (sesión 1: 5 de las 6, la sexta empieza en la rampa y se excluyó; sesión 2: 6), regularizadas a 240 Hz con el 16,2 a 16,7 % de puntos interpolados. Diez son válidas: **tronco primero en 8, ninguna con la
cadera primero** y 2 dentro de la tolerancia (4,2 ms). **El "tronco primero" del saque de perfil no es un efecto del corpus convertido**: se reproduce con los originales. El golpe nuevo del celular (cadera 13 ms antes) es
una excepción de una repetición. Detalle y las otras agrupaciones, cuando termine la corrida.

### Pendiente

1. **Decisión 035** con el resultado del saque de tres cuartos del Paso B (en curso).
2. **Push** de la bitácora y de los resultados del Paso B cuando terminen.
3. Valentín: partes B (registros), C (Brevo) y D (Supabase) de la guía; eliminar el repositorio `vcapelloramil.github.io`; republicar el frontend.

---

## 2026-10-12 (madrugada del 13) — Standard y artefactos en producción, guía del dominio, "Olvidé mi contraseña" y Paso A

Continuación del punto anterior, con las decisiones de Valentín (migración aplicada, Standard, OK de push, orden del §8 aprobado, demo 28–30/10, etiqueta, Elliott confirmada en la lista de Referencias del Word).
Suite rápida del servidor **467 passed**; `bun test` **55 passed**; `tsc` y build limpios.

### Hecho

1. **Render en Standard y publicado** (`e35fc6f`, push a `main`): `render.yaml` y decisión 023 actualizados; `/health` devolvió `0.5.0` ~3 min después del push.
2. **Prueba en producción** (usuario de prueba, luego borrado; recorte real de 3,1 s, 626 fotogramas): **117,4 s de punta a punta (116,0 s de cómputo)**, 5,8 veces más rápido que Free; `completado`; reporte 1.3 con
   `tolerancia_orden_ms = 8,333`, tres fotogramas clave y video con esqueleto en el bucket `artefactos`; columnas `ruta_fotograma_*` y `ruta_overlay` escritas; **firmado y descargado con la sesión del propio
   usuario** (115 KB por fotograma, 127 KB el video); **otro usuario no puede firmar esas rutas** (aislamiento por carpeta verificado). `criterio4-latencia.md`, fila 3. Falta el RSS pico en Linux (solo está en
   el log de Render).
3. **Etiqueta de la vista simple:** "Solo registrado / Para seguimiento" en las tarjetas, Procesando y Biblioteca; "Sin evaluar" queda en el detalle técnico. (Una constante en `components/estado.tsx`.)
4. **Dominio y correo** (decisión 034 y `docs/guia-dominio-correo-y-hosting.md`): guía paso a paso (Namecheap → Cloudflare → Brevo → Supabase → la aplicación en el dominio), con el criterio de por qué **el DNS va a
   Cloudflare** (un Worker solo acepta un dominio propio si la zona está activa ahí). Verificado contra la documentación de Cloudflare, Supabase y Brevo; los datos del SMTP de Brevo vienen de la decisión 027
   y hay que confirmarlos en pantalla (el sitio de ayuda de Brevo bloquea las lecturas automáticas).
5. **"Olvidé mi contraseña"** (adelantado, no depende del dominio): `/recuperar` pide el enlace sin revelar si el correo existe; `/restablecer` elige la contraseña nueva; enlace desde Ingreso; plantilla
   `supabase/templates/restablecer-contrasena.html`. Falta probarlo con el correo propio (parte D de la guía).
6. **Plan §8 reordenado** con las pantallas que faltaban: reporte detallado con interruptor y vista por rol, PDF barato (impresión), Perfil real con "descargar mis datos" y eliminar, Evolución con la marca.
   **La demo del 28–30/10 no se mueve**, pero el margen es corto si el ritmo cae a 1 sesión por día.
7. **Paso A del recálculo** (`docs/resultados/paso-a-resumen.md`, `backend/app/medicion_paso_a.py`, commit `3d88f89`, árbol limpio, 84 repeticiones, ambas sesiones):
   - **Solo el saque de perfil cumple el Criterio 1** con el tiempo real y la tolerancia unificada (1a 0,83; réplica 0,80; 1b 1,00; `tp`). **Drive de perfil y revés de tres cuartos dejan de cumplir** (1a 1,00 → 0,50).
   - **El "tronco primero" no es el reloj, ni el filtro (cortes de 4 a 12 Hz), ni la definición de la velocidad (giro axial)**. **Sí depende del encuadre**: en el saque, 0 de 9 repeticiones ordenables
     con la cadera primero en perfil contra 6 de 9 en tres cuartos (Fisher p = 0,009, exploratorio). Al menos un encuadre mide mal; el sospechoso es el perfil (cadera lejana tapada).
   - En tres cuartos el material está en su límite: 34 de 48 repeticiones a 8,33 ms o menos de diferencia.
   - `RESPALDO_POR_GRUPO` actualizado con estas cifras (ningún veredicto cambia). **Decisión 035 (propuesta): suspender el veredicto del saque de perfil.** No se aplicó.
   - Un control quedó descartado (2D en el espacio de la imagen: E3 lo excluye porque sus umbrales están en metros) y se reemplazó por el giro axial.

### Pendiente

1. **Valentín:** partes A a D de la guía (dominio, DNS en Cloudflare, Brevo, Supabase) y pasarme el nombre del dominio; **republicar el frontend** (trae Recuperar/Restablecer y los cambios del reporte);
   **decidir la 035**.
2. **Push:** quedan commits **locales** (`3d88f89` y siguientes). Cada push reinicia Render: se hace cuando no haya un análisis en curso.
3. **Punto 1 del plan** (parte mía): `wrangler.jsonc`, `KINETIQ_CORS_ORIGINS` y prueba de registro real, cuando llegue el nombre.
4. **Punto 3 (datos en el reporte)**, luego Cargar con varios golpes (4) y la consistencia entre golpes (5).

---

## 2026-10-12 (noche) — Ajustes del primer reporte real: tolerancia única, esqueleto en el reporte, motor 0.5.0 y el reporte que evalúa más

Pedido de Valentín tras la prueba del 12/10 (puntos 1 a 8). **Nada pusheado ni desplegado**; tres commits en `main` local (`875b2cf` motor, `3624418` frontend, `e6839ce` docs). Suite rápida del servidor **454 passed** (431 antes), `bun test` **53 passed**, `tsc` y eslint
(sin la regla de formato, que ya fallaba en el resto del repositorio) limpios.

### Hecho

1. **Tolerancia única de "ordenable": 1/120 s = 8,33 ms, estricta** (decisión 032). `engine/tolerancia_orden.py` es la constante compartida; el ensamblador la usa y el arnés del recálculo debe importarla. Con Δ ≤ 8,33 ms
   el reporte dice "a esta resolución no se puede saber cuál fue primero". **El golpe del 12/10 (8,3 ms) pasa a no ordenable**: la nota 11 del Capítulo 7 está corregida. Es la regla del pre-registro del recálculo
   (plan §3); lo que cambia respecto de la regla anterior es que se contaban fotogramas de la grilla de 240 Hz (4,17 ms) y no milisegundos.
2. **Resolución real, no la de la grilla:** el gráfico dice "1 fotograma ≈ 5 ms a 200 fps reales"; la frase de simultaneidad y el detalle técnico también, con la tolerancia ("a menos de 8,3 ms uno del otro").
3. **Motor 0.5.0** y **contrato 1.3** (aditivo: `trazabilidad.tolerancia_orden_ms`, `artefactos.overlay_info`). Tabla de versiones más abajo.
4. **Cargar:** la instrucción completa va antes de elegir el archivo: recortar en Fotos → Editar → barra de rayitas, todo el tramo a velocidad normal → Opciones → Formato: Actual, y por qué (un recorte que
   mantiene la cámara lenta llega a ~50 fps aunque se elija "Actual").
5. **Esqueleto en el reporte** (decisión 033): tres fotogramas clave (picos de cadera, tronco y brazo) y un video corto con el esqueleto, acercados al jugador, en un bucket nuevo `artefactos`, y mostrados en el reporte
   ("Tres momentos de tu golpe" + `<video>`). Generación opcional: si falla, el reporte sale igual. **Costo medido localmente: +9 s sobre 134 s (+7 %), el pico de memoria no sube; `ffmpeg` +56 MB aparte.**
   Estimación Render: +47 s en Free (11 min 18 s → ~12 min), +11 s en Standard. **Recomendación: pasar a Standard antes de publicar esto** (margen de memoria de 32 MB en Free; ver 033).
6. **Menores:** el encabezado ya no es "pegajoso" en el celular (ocupaba el 28 % de la pantalla y tapaba el comienzo de las secciones al hacer scroll); las dos tarjetas ya no repiten la línea de instantes
   (las tarjetas muestran solo texto; el fundamento y la fuente están en el detalle, sin repetirse).
7. **Criterio 4:** el dato de 11 min 18 s (677,8 s; cómputo 676,6 s) ya estaba en `criterio4-latencia.md` (fila 2, medido por la base); se agregó la estimación del costo de los artefactos.
8. **El reporte que evalúa más — análisis en `docs/reporte-mas-valor.md`:** (a) **ni Elliott (2006) ni Kibler respaldan el orden en drive y revés en los textos del repositorio** (Elliott solo está en la maqueta
   de Lovable; Kibler aparece sin año y habla de energía): no se agregó nada a `RESPALDO_POR_GRUPO`; hace falta página y pasaje de tu lectura; (b) tabla de qué calcula el motor / qué tiene rango citable / qué se
   puede mostrar como dato (ninguna magnitud tiene rango en grados en la tesis); (c) consistencia entre golpes: costo 1,5–2 sesiones sobre la carga de varios golpes; (d) lenguaje simple hecho, etiqueta propuesta.
   El orden de todo hasta la demo está en `docs/plan-mvp-punta-a-punta.md` §8.

### Versiones del motor (RNF-02): desde qué commit rige cada sello

El motor cambió entre el 9 y el 12/10 con el sello `0.4.1` puesto. Discriminadores prácticos: `version_contrato` del reporte y la fecha.

| Sello | Estado del motor | Desde el commit | Qué lo distingue en un reporte |
| --- | --- | --- | --- |
| 0.4.1 | Original: E3 por segmentos, ingesta con la tasa del contenedor y la declaración del usuario | `661cb5e` (25/9) | contrato 1.0 · sin `fps_nominal` ni `regularizacion` |
| 0.4.1 | + lectura de la tasa real por marcas de tiempo (decisión 029) | `c80a4a1` (9/10) | — (no se persistían reportes JSON todavía) |
| 0.4.1 | + fotogramas visibles, rotación automática y regularización (decisión 030) | `18942d5` (9/10) | contrato 1.1 · `regularizacion` presente |
| 0.4.1 | + reporte persistido, motivo `archivo_convertido`, veredicto por grupo (031), piso de R1 con 5 % | `43fc159` (9/10) | contrato 1.2 |
| 0.4.1 | + alineación por fotogramas decodificados, "no ordenable a un fotograma de la grilla" | `6ab2b18` (9/10) | contrato 1.2 · tolerancia de 4,17 ms (sin `tolerancia_orden_ms`) |
| **0.5.0** | + tolerancia única de 8,33 ms, artefactos, textos sin literatura en el nivel 1 | **`875b2cf`** (12/10) | contrato 1.3 · `tolerancia_orden_ms` presente |

Los reportes anteriores **no se recalculan**: conservan su sello y su contrato.

### Acciones de Valentín (en este orden)

1. **Aplicar** `supabase/migrations/20261012000000_bucket_artefactos.sql` (panel de Supabase → SQL). Sin ella la subida de artefactos falla y el reporte sale sin ellos (falla suave).
2. **Pasar Render a Standard** (decisión 023) y avisarme en el mismo paso para actualizar `render.yaml` (`plan: standard`). Recomendado antes del push (decisión 033).
3. **Dar el OK para pushear** (Render redespliega) y **republicar el frontend** desde tu PowerShell (`bun run build` y `wrangler deploy` en `frontend/`).
4. **Subir un golpe** (el recorte sin cámara lenta): tiene que aparecer "Tres momentos de tu golpe". Del log de Render: "artefactos en X s" y el RSS pico (es la medición que falta en Linux).
5. **Decidir:** la etiqueta de la vista simple ("Solo registrado", propuesta); si seguís con el pasaje de Elliott/Kibler (pasame página y frase; yo recomiendo después del Paso A); el orden de §8 del plan.

### Qué no se hizo y por qué

- **Reproductor sincronizado, PDF, puntaje, comparación con la sesión anterior:** diferidos (plan §5). Los tres momentos y el video no los reemplazan.
- **Ángulos dibujados sobre el esqueleto y ángulos en el reporte:** son el punto (b); necesitan una sesión propia (plan §8).
- **Medición real de memoria en el contenedor Linux:** Docker no estaba en marcha; se mide con el primer golpe real en Render.

---

## 2026-10-12 — NOTA DE TRASPASO (antes de /clear) · estado, pruebas del día y pendientes

**Rama:** `main`; el commit de esta nota es el último y queda pusheado. Árbol limpio. Suite rápida del servidor **455 passed**, `-m requiere_supabase` **84 passed**, `-m requiere_render` en verde (9/10), frontend `bun test` **48 passed**.

### Qué está publicado

- **Servidor (Render, plan Free):** motor con la regularización por fotogramas decodificados, "no auditable" por simultaneidad y tiempos de procesamiento; API con JWT por JWKS y chequeo de propiedad (404);
  `KINETIQ_API_TOKEN` borrado y `KINETIQ_CORS_ORIGINS` cargado. **Migraciones aplicadas hasta `20261010000000`.**
- **Frontend (Cloudflare Workers): https://kinetiq.v-capelloramil.workers.dev**, republicado por Valentín el 9/10: Registro, Ingreso, Cargar, **Procesando, Biblioteca y Reporte simple reales**, con el diseño nuevo
  en los tokens y en las pantallas nuevas. Sigue simulado, con la marca "Datos de ejemplo": Perfil. Landing y Tecnología son estáticas. La maqueta vieja del reporte vive en `/reporte/` y no está enlazada.
- Para republicar: desde la PowerShell de Valentín, `cd frontend; bun run build; .\node_modules\.bin\wrangler.exe deploy` (necesita `frontend/.env`, no versionado).

### Resultado de las pruebas de hoy (12/10, desde el celular, `IMG_6395.mov`, revés de tres cuartos, las tres declaradas `camara_lenta_240`)

1. **El recorte con cámara lenta llegó convertido y se rechazó bien.** Dos envíos (15:54 y 16:00 UTC): 12,0 s, 604 fotogramas = **50 fps** → `fallido` con `archivo_convertido` en **15 y 18 s**, `fps_real = 50`.
   El motor midió la tasa del archivo y no culpó a la declaración; Procesando muestra el camino "Opciones → Formato: Actual / Archivos".
2. **El recorte sin cámara lenta dio análisis completo a 199,9 fps.** 3,0 s, 599 fotogramas, 1920×1080 → `completado`. **Latencia de punta a punta: 11 min 18 s** (677,8 s; cómputo 676,6 s) en Render Free:
   **primer dato de latencia medido por la base** (`docs/resultados/criterio4-latencia.md`). Regularizado: 16,7 % de fotogramas perdidos y 16,7 % de puntos interpolados (hueco máximo 12,5 ms), escala conocida,
   cobertura auditable 100 %, repetición auditable, `version_contrato` 1.2.
   **Orden:** tronco 0,300 s, cadera 0,308 s (8,3 ms = **2 fotogramas**, ordenable), brazo 0,488 s → tronco, cadera, brazo. **Coincide con el orden modal del corpus para revés de tres cuartos (`tp`).**
   Sin veredicto, por la decisión 031 (no hay referencia del orden para el revés): dos observaciones "sin evaluar". n = 1; va a las notas del Capítulo 7 (ítem 11).

### Pendiente, en este orden

1. **Latencia:** 11 min por un golpe de 3 s es lo que más pesa. Decisión de Valentín (023): pasar a Standard (USD 25/mes, 1 CPU, 2 GB) y medir de nuevo; el cambio se hace en el panel y en el mismo paso se actualiza `render.yaml`.
2. **Adaptar al diseño nuevo** Registro e Ingreso, Cargar (con varios golpes por sesión), Landing y Perfil: ~2,5 días, antes de la demo a los profesores.
3. **"Olvidé mi contraseña"** (se prueba con dominio y correo propio, decisión 027; hoy solo sale el SMTP de Supabase a miembros del equipo, 2 por hora).
4. **Validar el veredicto del saque de perfil** con el Paso A del recálculo y las grabaciones nuevas (decisión 031): **bloqueante de la demo, no del flujo**. El Paso A va ahora que la prueba de punta a punta pasó.
5. `corte_hz` fuera de `versiones_motor` (anotado el 9/10, para después de la prueba de punta a punta); semana 3 (sesión de varios golpes, eliminar cuenta y datos, respaldo con restauración probada, recuperación al arranque).
6. Todavía sin generar: miniaturas, los tres fotogramas clave con esqueleto, video con esqueleto, PDF, puntaje y comparación con la sesión anterior.

### Para retomar sin perder tiempo

- Python del proyecto: `backend/.venv/Scripts/python.exe`, con `PYTHONPATH=backend:tests`. `ffmpeg` y `ffprobe` en el PATH. Frontend: `bun` (`bun test` en `frontend/`).
- Los videos nunca van al repositorio; antes de cada commit, `git ls-files | grep -i -E "\.(mov|mp4|npy|npz)$"` debe dar vacío.
- Pruebas contra Supabase: `pytest -m requiere_supabase` (~9 min); contra producción: `pytest -m requiere_render`.
- Las decisiones están en `docs/decisiones/` (hasta la 031); el resumen de lo hecho el 9/10 está en las entradas de abajo.

---

## 2026-10-09 (noche, 8) — Migración de tiempos aplicada, push y despliegue verificados; pieza 8: Reporte simple real

### Verificado y publicado (decisiones de Valentín, 9/10)

- **Migración `20261010000000` aplicada** por Valentín. `-m requiere_supabase` completo: **84 passed**, sin fallas ni saltadas (incluye `test_procesar_video_e2e.py`, que ahora exige el reporte válido y los tiempos de procesamiento).
- **Push de `6ab2b18`, `434427c` y `06d10d7`** a `main`. **Render sirvió el código nuevo en menos de un minuto:** un video sintético mínimo (1 s a 30 fps, declarado normal, `parcial` por R1) pasado por la API de producción
  dejó escritos `encolado_en`, `inicio_procesamiento_en` y `fin_procesamiento_en` (6 s de punta a punta; no es un dato de latencia representativo, solo prueba que el servicio los registra).
- **Aprobado por Valentín:** la alineación por fotogramas decodificados y el "no auditable" por simultaneidad. El dato de la cadera y el tronco a un fotograma quedó en las notas del Capítulo 7
  (`docs/tesis/correcciones-pendientes-capitulo-4.md`, ítems 8 a 10), con los cuidados para citarlo (n = 1, límite de resolución, no es evidencia a favor ni en contra del corpus).
- **Plan de diseño aprobado** (~2,5 días, antes de la demo): Registro e Ingreso, Cargar, Landing y Perfil, en "Antes de la demo a los profesores" del plan.
- **`corte_hz` en `versiones_motor`:** queda para después de la prueba de punta a punta.

### Pieza 8 — Reporte simple real (`/reporte/$videoId`, con el diseño nuevo; sin push)

- **Nivel 1:** "Lo más importante" con **a lo sumo tres observaciones**, por importancia (alerta de carga, desvío leve, correcto, no auditable, sin evaluar), cada una con su estado en ícono y texto y su fundamento y fuente;
  las que no entran quedan en el detalle técnico.
- **Elemento central:** gráfico de secuenciación real (un eje temporal único con los instantes de cadera, tronco y brazo, colores de segmento de la especificación). Dibuja solo lo medido; con la escala sin confirmar no muestra
  segundos; marca un fotograma de la **grilla del reporte** (4,2 ms a 240 Hz) para que un empate se vea como empate. Debajo, la frase en el vocabulario de R2: el orden observado, o "a N fps no se puede saber cuál fue primero,
  así que no lo evaluamos", o "no se pudo medir".
- **Nivel 3 plegado ("Ver detalle técnico"):** otras observaciones, trazabilidad (tasa real y nominal, fotogramas perdidos, puntos interpolados, escala, cobertura auditable, modo declarado, motor, latencia), velocidad máxima
  por segmento con su confianza (o "no auditable" si la escala no está confirmada) y tramos no auditables.
- **Lo que NO está y no se inventa:** puntaje de rendimiento, comparación con la sesión anterior, los "tres momentos" con fotogramas del video (todavía no se generan) y el PDF. Diferidos; la pantalla no los simula.
- **Rutas:** la maqueta vieja pasó a `/reporte/` (índice) para que `/reporte/$videoId` sea ruta hermana; la Biblioteca y Procesando abren el reporte real.
- **Verificado:** `bun test` 48 pasan (priorización a tres, frases, lectura defensiva del JSON, vocabulario de R2), `tsc` y eslint limpios, build OK; revisión visual en escritorio y celular con datos simulados
  (reporte regularizado con cadera y tronco simultáneos, y uno con orden establecido). **No verificado:** con tus datos reales desde el navegador (necesita tu sesión).

### Acciones de Valentín

1. **Republicar el frontend** desde tu PowerShell (`bun run build` y `wrangler deploy` en `frontend/`): el sitio en vivo todavía no tiene Procesando, Biblioteca ni este reporte.
2. **Subir un golpe nuevo** (o de nuevo `IMG_6376.mov`) con el motor nuevo: da el reporte regularizado, la latencia registrada y las pantallas reales.
3. Con tu OK pusheo la pieza 8.

### Siguiente

Reporte detallado (nivel 2: reproductor y curvas, con el video con esqueleto que todavía no existe) queda para después; lo que sigue según el plan es el registro de tiempos ya hecho, la sesión de varios golpes y la
Biblioteca con vista de sesión (semana 3), y la adaptación de las pantallas ya hechas al diseño nuevo.

---

## 2026-10-09 (noche, 7) — Revisión de la prueba de punta a punta; pieza 7: Procesando y Biblioteca reales con el diseño nuevo

### Revisión de tu prueba (video `06abd72b…`, `IMG_6376.mov`, saque de perfil, `camara_lenta_240`, `completado`)

**Lo que cerraba:** el reporte guardado **valida contra el contrato v1.2**; la tasa real leída fue **199,63 fps** (nominal 239,98, 16,8 % de fotogramas perdidos, `origen_factor = marcas_de_tiempo`, `factor = 1`);
el filtro fue Butterworth de fase cero de 4.º orden con corte de 7 Hz; 3 observaciones y el veredicto de la decisión 031 aplicado (saque de perfil tiene veredicto).

**Lo que NO cerraba (y corregí):**

1. **No se regularizó (`regularizacion: null`) y la escala quedó sin confirmar.** Causa exacta: `probe()` contó **501** fotogramas visibles (por paquetes del contenedor) y el decodificador entregó **499**
   (los dos últimos paquetes no producen fotograma). La comprobación de igualdad falló, y el motor —correctamente— no asignó tiempo "adivinando". Consecuencia: las velocidades salieron `null` y el orden se calculó con un eje de
   tiempo que tomaba el archivo como uniforme.
   **Arreglo:** `alinear_marcas` (función pura): si las cantidades no coinciden se leen las marcas de los fotogramas realmente decodificados (`ffprobe -show_frames`) y **solo** se usan si son exactamente N y cada una es una marca
   de algún paquete visible. Nada se supone. Con el mismo archivo ahora: 499 fuente → 597 puntos de grilla, **98 interpolados (16,4 %)**, 0 sin dato, **escala conocida**, velocidades auditables.
2. **El orden cadera/tronco dependía del eje de tiempo mal asignado.** Sin regularizar daba cadera 10 ms antes que el tronco (2 fotogramas, "correcto"). **Regularizado, el tronco queda en 0,300 s y la cadera en 0,304 s: 4,2 ms,
   un fotograma, dentro de la tolerancia** (decisión 014): no ordenable. Es lo que la decisión 015 anticipaba (picos de pelvis y torso "casi siempre a 0–3 fotogramas"). **No confirma ni refuta** el orden `tp` del corpus: n = 1 y
   justo en el límite de resolución. Coincide en el sentido (tronco ≤ cadera) pero no es evidencia.
3. **El reporte se contradecía:** marcaba la repetición `auditable: true` con un `orden_observado`, y a la vez la observación decía que el orden no se puede establecer. Ahora, con cadera y tronco a un fotograma o menos,
   la repetición sale **no auditable, sin orden, con motivo "simultaneidad al límite de resolución"** (decisión 015), conserva los picos medidos y el video queda `parcial`.
4. **Menor, sin cambiar:** `versiones_motor.parametros_dsp.corte_hz` quedó en 6,0 (de la primera corrida que creó la fila) y esta fue de 7,0. Esa fila es por versión del motor, no por análisis; el valor correcto está en el reporte.
   Conviene sacar `corte_hz` de ahí (anotado, no urgente).

**Criterio 4 (latencia):** el tiempo **no se guardaba en ningún lado** (solo en el log de Render). Datos que sí hay: ~9 min que mediste vos, y el reporte creado 16 min después del alta del video (incluye el intento fallido por CORS).
**Migración nueva `20261010000000_tiempos_de_procesamiento.sql`** (`encolado_en`, `inicio_procesamiento_en`, `fin_procesamiento_en`); la API y el procesamiento ya las escriben. Primer dato manual registrado en
`docs/resultados/criterio4-latencia.md`. **Hay que aplicar la migración ANTES de desplegar este código**: sin ella, la API falla al encolar.

### Diseño

- **Antes de esta entrada:** el frontend publicado era el diseño viejo de Lovable (Space Grotesk / Inter, paleta oklch, grilla de 56 px).
- **Ahora los tokens globales son los de la especificación §2** (Sora, DM Sans, JetBrains Mono; `#081015`, tarjetas `#0d181e` con borde `#1c2a32` de 20 px, grilla de 72 px, verde `#4ade80 → #10b981`, turquesa `#22d3ee`, los cuatro
  estados con su fondo propio y "sin evaluar" con borde punteado). Todas las pantallas lo heredan sin tocarlas.
- **Construidas desde las maquetas:** Procesando y Biblioteca, y el menú por sesión (§3: Biblioteca · Cargar · Perfil). **Con tokens nuevos pero diseño viejo:** Registro, Ingreso, Cargar, Landing, Tecnología, Perfil y el reporte
  simulado. Estimación para adaptarlas en el plan ("Antes de la demo a los profesores").

### Pieza 7 (sin push: depende de la migración)

- **Procesando** (`/procesando/$videoId`): consulta el estado cada 5 s y se detiene al terminar; pasos Subido · En cola · Analizando · Listo; tiempo transcurrido; descripción de lo que hace el análisis **sin marcar etapas como
  hechas** (el servidor no informa la etapa: R3); mensajes por `motivo_fallo` (`archivo_convertido` con el camino "Opciones → Formato: Actual" y la tasa medida; `modo_captura_incompatible` con corrección de la declaración;
  `error_inesperado` con contador y reintento) y resultado con observaciones (cuatro estados + "sin evaluar") y trazabilidad. Aviso de que se puede cerrar la página.
- **Biblioteca** (`/videos`, real): sesiones del usuario con estado, fps, conteo de observaciones por estado, filtros por golpe y búsqueda; se actualiza sola mientras hay análisis en curso. Sin puntaje de rendimiento ni miniatura
  (diferidos / no generadas): no se inventan.
- **Cargar** ahora lleva a Procesando al enviar.
- **Verificado:** `bun test` 37 pasan, `tsc` y eslint limpios, build OK; suite rápida del servidor **455 passed**. Revisión visual en el navegador con la sesión y las respuestas **simuladas** (con el reporte real de tu prueba):
  Biblioteca, Procesando (completado, en curso, fallido por archivo convertido) en escritorio y en celular (375 px). El encabezado se apretaba en celular y se corrigió.
- **No verificado:** el flujo con datos reales desde el navegador (necesita tu sesión), y las pruebas de integración que usan las columnas de tiempo (fallan hasta aplicar la migración).

### Acciones de Valentín

1. **Aplicar `supabase/migrations/20261010000000_tiempos_de_procesamiento.sql`** y avisar. Después corro `test_procesar_video_e2e.py` y `-m requiere_supabase`.
2. Con tu OK pusheo y Render redespliega; **después** republicás el frontend desde tu PowerShell.
3. Subir de nuevo `IMG_6376.mov` (o un golpe nuevo) con el código nuevo para ver el resultado regularizado y la latencia registrada.

---

## 2026-10-09 (noche, 6) — Frontend publicado en Cloudflare Workers; pieza 6: Cargar real y marca "Datos de ejemplo"

### Publicación (decisión 026, mecanismo definido)

- **URL: https://kinetiq.v-capelloramil.workers.dev** (Worker `kinetiq`, `wrangler deploy` desde `frontend/`, build con las variables públicas). Verificado: `/`, `/registro`, `/ingreso` y `/tecnologia` dan 200,
  una ruta inexistente 404, los assets cargan y el bundle lleva la URL pública de Supabase y ningún secreto.
- **Workers y no Pages:** el build de TanStack Start es un Worker con assets estáticos; Pages exigía convertirlo (decisión de Valentín, 9/10).
- **Particularidad del login de Wrangler:** `wrangler login` con scopes de Workers dijo "Successfully logged in" pero el archivo de credenciales visible desde esta sesión no cambió; el deploy lo hizo Valentín desde su
  PowerShell. Para volver a publicar: `cd frontend; bun run build; .\node_modules\.bin\wrangler.exe deploy` **desde su PowerShell** (el build necesita `frontend/.env`, que no se versiona).
- **Valores que carga Valentín** (origen = `https://kinetiq.v-capelloramil.workers.dev`):
  Supabase → Authentication → URL Configuration: *Site URL* = el origen; *Redirect URLs* = `<origen>/**` y `http://localhost:8080/**`.
  Render → `KINETIQ_CORS_ORIGINS` = `https://kinetiq.v-capelloramil.workers.dev,http://localhost:8080`.

### Pieza 6 — Cargar real (sin commit pusheado)

- **`/upload` deja de ser una maqueta.** Flujo: jugador (existente o nuevo: nombre, mano dominante, nivel) → golpe, encuadre, lado de la cámara, fecha → **"¿Cómo lo grabaste?"** sin opción marcada y con la ayuda
  "elegí cómo grabaste, no cómo se ve" → archivo. La **instrucción "Opciones → Formato: Actual / app Archivos" va antes de elegir el archivo.** Con "Grabación normal" aparece la pregunta
  "¿Lo grabaste en cámara lenta?" con la opción de cambiar la respuesta.
- **Validación en el navegador (cortesía; la definitiva es del motor):** MP4 o MOV, máximo 50 MB, aviso si dura más de 8 s. No se lee la tasa de fotogramas en el navegador (no es confiable); la mide el motor.
- **Subida directa a Storage** con la sesión del usuario y progreso real (XHR), en `<usuario_id>/<video_id>/<nombre seguro>` (solo letras ASCII, números, `-`, `_` y `.`: lo medido con la página del iPhone).
  Después: alta de `atletas`, `sesiones` y `videos` (las cuatro columnas permitidas) y `POST /analisis/{id}/procesar` con el JWT. Si falla antes de guardar, se deshace la carga; si falla solo el envío,
  el video queda guardado y se ofrece **"Enviar a analizar de nuevo"**. 409 `estado_no_reintentable` cuenta como éxito (ya estaba en cola o analizado).
- **Marca "Datos de ejemplo"** (ícono + texto, no solo color) en `/videos`, `/reporte` y `/profile`, que siguen simuladas (plan §5; piezas 7 y 8).
- **Verificado:** `bun test` 25 pasan (validación, clave de Storage con entradas hostiles, vocabulario contra los CHECK de la base, interpretación de la API), `tsc --noEmit` y eslint limpios, build OK sin secretos.
  **Contrato de red contra el Supabase real** con un usuario temporal (ya borrado): alta de atleta y sesión con la sesión del usuario, subida con los mismos headers que la pantalla (200), subida a una carpeta
  ajena rechazada (400), alta del video en `pendiente` y descarte completo en cascada.
- **No verificado:** el flujo completo en el navegador (necesita una sesión real, no manejo contraseñas) ni el envío a la API desde el navegador (falta `KINETIQ_CORS_ORIGINS` en Render).

### Acciones de Valentín

1. **Volver a publicar** (pieza 5 y 6 están en el código, el sitio en vivo tiene solo la 5): `cd frontend`, `bun run build`, `.\node_modules\.bin\wrangler.exe deploy`.
2. Cargar los valores de Supabase y Render de arriba.
3. Probar desde el celular: registrarse (o ingresar), **Cargar**, subir un golpe con Opciones → Formato: Actual.

### Siguiente

Pieza 7: **Procesando real** (polling del estado, mensajes por estado y por `motivo_fallo` —incluido `archivo_convertido`—, reintento) y Biblioteca real; después el Reporte simple real (pieza 8).

---

## 2026-10-09 (noche, 5) — Publicación del frontend en Cloudflare Workers: build listo, falta el permiso de Wrangler

- **Push de `9488ffc` hecho** (`1b62091..9488ffc`).
- **Decisión de Valentín: Workers, no Pages** (el build de TanStack Start es un Worker con assets: `dist/server/index.js` + `dist/client`; Pages exigiría convertirlo). Nombre del Worker: **`kinetiq`**
  (`frontend/wrangler.jsonc`), URL `https://kinetiq.<subdominio-de-la-cuenta>.workers.dev`.
- **Build verificado:** con `frontend/.env` (valores públicos), `bun run build` OK; el bundle del cliente **no contiene** la `service_role` (buscada por valor y por texto) y sí la URL pública de Supabase.
- **Bloqueado el deploy:** `wrangler deploy` falla con "No access to the specified resource". El token de Wrangler tiene solo `pages:write` (más `account:read` y `user:read`); desplegar un Worker pide
  `workers:write` y `workers_scripts:write`. **Corrección mía:** el listado largo que mostré de `wrangler whoami` eran los scopes que *faltan*, no los concedidos.
  **Acción de Valentín** (abre el consentimiento de Cloudflare en el navegador; el 7/10 el login con todos los scopes dio `request_forbidden`, por eso se piden solo los necesarios):
  `frontend\node_modules\.bin\wrangler.exe login --scopes account:read user:read workers:write workers_scripts:write`
- **Pendiente para antes de la demo a los profesores (decisión de Valentín): "Olvidé mi contraseña"** en `/ingreso` (recuperación por correo de Supabase). Se prueba cuando haya dominio y correo propio:
  con el SMTP por defecto no se puede (solo miembros del equipo, 2 por hora, decisión 027).

---

## 2026-10-09 (noche, 4) — Producción verificada con JWT; pieza 5 (frontend): sesión, Registro e Ingreso

**Producción:** `1b62091` ya está en `main`; Render sirvió el código nuevo a las 18:53:49 (un Bearer inválido pasó de "Token inválido o ausente." a 401 con `WWW-Authenticate: Bearer`). **`-m requiere_render` con JWT pasó**
(incluye el 404 del usuario ajeno contra el servicio desplegado). Valentín borra `KINETIQ_API_TOKEN` del panel después del aviso.

### Pieza 5 — qué se hizo (sin commit todavía)

- **`@supabase/supabase-js`** agregado al frontend. Cliente único y solo en el navegador (`src/lib/supabase.ts`): URL y clave **anon** desde `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY`; nunca la `service_role`.
  Variables en `frontend/.env.example` (el `.env` real está ignorado por git). `VITE_API_URL` queda lista para la pieza 6.
- **Sesión** (`src/lib/sesion.tsx`): `SesionProvider` y `useSesion()` (lee la sesión guardada y escucha los cambios). Mientras carga, el servidor y el primer render del cliente muestran lo mismo.
- **`/registro`:** nombre, correo, contraseña (8 caracteres con letras y números), rol sin opción marcada y consentimiento de la Ley 25.326 con fecha en los metadatos de la cuenta. Al enviar muestra
  "Te enviamos un correo… **Revisá también la carpeta de spam**" con el correo al que se envió y **Reenviar**. El trigger de alta toma `nombre` y `rol` de esos metadatos.
- **`/ingreso`:** sin confirmar el correo dice **"Confirmá tu correo para entrar"** (con reenvío), no un error genérico; con sesión va a `/videos`. `?confirmado=1` (lo agrega el enlace del correo) muestra el aviso.
- **Rutas protegidas** (`RutaProtegida`): `/upload`, `/videos`, `/reporte` y `/profile` redirigen a `/ingreso` sin sesión. Es comodidad de la interfaz; la barrera real es RLS y la API.
- **Encabezado** con sesión real: "Ingresar / Crear cuenta" o nombre + "Salir" (antes mostraba "Marco R." fijo).
- **Mensajes de error en lenguaje llano** (`src/lib/auth-errores.ts`, función pura): sin texto técnico del proveedor.
- **Verificado:** `bun test` 10 pasan (`frontend/tests/auth-errores.test.ts`: incluye que los roles coinciden con los de `usuarios.rol`), `tsc --noEmit` sin errores, `bun run build` OK y revisión en el navegador:
  `/registro` renderiza, valida del lado del cliente y `/upload` sin sesión redirige a `/ingreso`. **No se envió ningún formulario contra Supabase** (no se crean cuentas de prueba desde el navegador): el
  alta, la confirmación y el login reales los cubren las pruebas de integración del servidor; falta que Valentín los pruebe desde la página.
- **Datos de ejemplo:** `/videos`, `/reporte`, `/profile` y `/upload` siguen mostrando datos simulados (piezas 6 a 8). Falta ponerles la marca visible "Datos de ejemplo" (regla R3/R4 del plan §5).

### Acciones que son de Valentín

1. **Supabase → Authentication → URL Configuration:** *Site URL* y *Redirect URLs* con el dominio publicado del frontend (el enlace del correo vuelve a `/ingreso?confirmado=1`). Mientras se prueba en local, agregar `http://localhost:8080/**`.
2. **Probar el alta** desde la página con un correo real (revisar spam) o, si el correo todavía no sale, crear un usuario ya confirmado desde el panel y probar **Ingresar**.
3. Cargar `KINETIQ_CORS_ORIGINS` en Render cuando haya dominio del frontend (el dev local usa `http://localhost:8080`).

### Siguiente

Pieza 6: **Cargar real** (formulario de la sesión, instrucción "Opciones → Formato: Actual" antes de elegir el archivo, subida directa a Storage, alta de `sesión` y `video`, llamada a la API con el JWT).

---

## 2026-10-09 (noche, 3) — `usuarios` endurecido y verificado; push de la pieza 4; validación del veredicto como bloqueante de la demo

- **Migración `20261009130000_endurecer_usuarios.sql` aplicada y verificada por Valentín.** El alta de la fila la hace el trigger `al_registrarse` (`AFTER INSERT` sobre `auth.users`, `SECURITY DEFINER`),
  que no depende de los permisos de `authenticated`. Verificado: registro → confirmación → login, trigger de alta y `test_usuarios_columnas_protegidas.py`: **10 passed**.
- **Veredicto (decisión 031): aprobado.** Queda **anotado como bloqueante de la demo a los profesores, no del flujo**: confirmar si "tronco antes que cadera en 6/6" en el saque de perfil es real o un artefacto (vista de perfil,
  escala ×2, fotogramas irregulares) con el **Paso A** (apenas pase la prueba de punta a punta) y las grabaciones nuevas con tiempos reales. Referencias con DOI en la decisión 031.
- **R1:** la tolerancia en los pisos de 120 y 60 queda como está (confirmado).
- **Orden del despliegue:** push → Render termina → Valentín borra `KINETIQ_API_TOKEN` del panel (si se borra antes, el código viejo podría fallar al reiniciar) → `-m requiere_render` con JWT.

---

## 2026-10-09 (noche, 2) — Pieza 4 (tarea 7.4): la API autentica con el JWT de Supabase

**Commit anterior, ya en `main`: `43fc159`** (piezas 1 a 3 + decisión 031 + tolerancia de R1). Esta pieza está **commiteada en local, sin pushear** (espera a que Valentín aplique la migración de `usuarios` para subir todo junto).

- **JWT por JWKS** (`backend/app/security.py`, PyJWT): ES256 fijado por el servidor, exige `exp`, `sub`, `iss` y `aud = authenticated`; caché de claves y recarga ante un `kid` desconocido. 401 sin Bearer, inválido o vencido
  (el vencido lo dice); 503 si no se pudo pedir el JWKS. La identidad es el `sub`: una prueba manda otro `usuario_id` por query, cuerpo y header y no cambia nada.
- **Propiedad del video:** `POST /analisis/{id}/procesar` compara `videos.usuario_id` con el `sub`; **404** igual que un video inexistente (un id que no es uuid también). La API usa `service_role`, que ignora RLS.
- **CORS acotado:** `KINETIQ_CORS_ORIGINS` (lista; sin valor = ningún origen; un `*` es `ConfigError`); `allow_credentials=False`.
- **Token compartido retirado:** `verificar_token`, `KINETIQ_API_TOKEN` y `get_kinetiq_api_token` ya no existen; `render.yaml` y `.env.example` actualizados.
- **`usuarios` endurecido** (migración `20261009130000_endurecer_usuarios.sql`, **sin aplicar**): INSERT retirado y UPDATE solo de `nombre`, `rol` y `vista_por_defecto`; prueba en rojo hasta aplicarla.
- **Verificado:** suite rápida **447 passed**; `test_api_analisis_e2e`, `test_reintento_supabase` y `test_registro_confirmacion_login` (18 pruebas, contra el JWKS real y con el usuario ajeno recibiendo 404) en verde.
  `test_render_modo_captura` (contra el despliegue) quedó migrada pero **no se corrió**: hace falta desplegar.

### Acciones que son de Valentín

1. **Aplicar** `supabase/migrations/20261009130000_endurecer_usuarios.sql` y avisar (después `pytest tests/integration/test_usuarios_columnas_protegidas.py`).
2. En el panel de Render: **borrar `KINETIQ_API_TOKEN`** y, al publicar el frontend, **cargar `KINETIQ_CORS_ORIGINS`** con su dominio (sin barra final).
3. Confirmar que se pushea (el push dispara un despliegue en Render si el servicio tiene despliegue automático).

### Siguiente

Pieza 5 (frontend: cliente de Supabase, sesión, Registro con aviso de spam y Login). Lo que necesita el frontend de la API: `Authorization: Bearer <session.access_token>` (especificación §5).

---

## 2026-10-09 (noche) — Migración aplicada y corridas en verde; decisión 031 (veredicto por gesto y encuadre); tolerancia del 5 % en R1

**Corridas (con la migración `20261009120000` ya aplicada por Valentín): `test_procesar_video_e2e.py` pasó (2 min) y `pytest -m requiere_supabase` completo dio 79 passed, 0 failed (8 min 55 s), sin restos.
Suite rápida: 419 passed.** El e2e ahora verifica que el `reporte` guardado valida contra el contrato y que cada métrica trae `confianza_media`.

### Decisiones de Valentín (9/10, a continuación del cierre de arriba)

1. **Veredicto de la secuencia → decisión 031.** Mi propuesta (veredicto solo en revés, el resto `no_auditable`) fue rechazada: contradecía la tesis (§4.3.3, tabla 4.8: el saque tiene el respaldo bibliográfico) y
   `no_auditable` significa "no se pudo medir". **Regla:** veredicto del par cadera → tronco solo donde hay **(a)** referencia del orden esperado y **(b)** Criterio 1 cumplido para ese gesto y encuadre; donde falta una,
   el orden se documenta como **`sin_evaluar`** (la etiqueta del brazo, decisión 011). Contrato **v1.2** (aditivo: `Observacion.severidad` admite `sin_evaluar`; los cuatro estados de R3 no cambian).
2. **Escala desconocida → velocidades `null`:** aprobado, implementado.
3. **Citas:** Kovacs y Ellenbecker (2011), Fleisig et al. (2003) y Martin et al. (2014), sin capítulos. Verificadas contra el **texto** de los capítulos 3 y 4; **la lista formal de Referencias no está en el repositorio**
   (queda cotejar autores, título y revista contra ella). Martin (2014) no se usa en estos veredictos: no respalda "tronco antes que cadera".
4. **R1 con fotogramas perdidos:** tolerancia del 5 %: **114 fps** para la secuenciación completa y **57** para la preparación; el umbral de 240 no tiene tolerancia. Documentado en la decisión 029 (actualización) y en
   CLAUDE.md R1. Con eso el clip de 60 fps (59,26 reales por un hueco de 3 fotogramas) vuelve a ser `solo_preparacion`.

### Qué grupos quedan con veredicto (cifras de `criterio1-resumen.md`, sesión 2, τ = 1, par pelvis-torso)

| Gesto · encuadre | (a) referencia | (b) Criterio 1 | Veredicto |
| --- | --- | --- | --- |
| **Saque · perfil** | Kovacs y Ellenbecker (2011); Fleisig et al. (2003) | cumple (1a 1,00 · 1b 1,00) | **sí** |
| Saque · tres cuartos | sí | no (1a 0,50) | sin evaluar |
| Drive · perfil | no | cumple (1,00 · 1,00) | sin evaluar |
| Drive · tres cuartos | no | no (0,00) | sin evaluar |
| Revés · perfil | no | no (0,67) | sin evaluar |
| Revés · tres cuartos | no | cumple (1,00 · 0,83) | sin evaluar |

**Se revisa cuando se haga el recálculo (Paso A):** anotado en la decisión 031 y en `docs/plan-recalculo-corpus-tasa-real.md`.

### Hallazgos que quedan anotados (sin investigar)

- **El Criterio 1 no lo cumplió solo el drive de perfil:** a τ = 1 lo cumplen tres grupos (saque perfil, drive perfil, revés tres cuartos); a τ = 2 y 3, dos (saque perfil y drive perfil). La frase de la decisión 029
  ("el único grupo que cumple es `drive|perfil`, 1a = 0,83") no coincide con `criterio1-resumen.md`: reconciliar al recalcular.
- **Efecto visible de la regla:** en el saque de perfil el orden modal medido es tronco antes que cadera (6 de 6; coincidencia con lo esperado 0,00). Con la regla, **todo saque de perfil con ese orden sale como
  `desvío leve`** (nunca alerta de carga). Puede ser una característica del jugador o un artefacto de la vista de perfil monocular: la 015 (salvedad 2) lo había evitado por falta de fuente. Anotado para el Capítulo 7.
- Mi reproche a una prueba vieja: `test_normal_60fps_queda_parcial_solo_preparacion` estaba desactualizada respecto de la 029 (tasa medida, no la del contenedor); ahora cubre la tolerancia.

---

## 2026-10-09 (tarde) — `requiere_supabase` corrido; piezas 1 a 3 del flujo listas, **falta aplicar una migración**

**Corrida real contra el proyecto Supabase (primera desde el 6/10): 78 passed, 1 failed** (9 min 21 s, sin restos). La falla era una prueba vieja, no un fallo del producto:
`test_normal_60fps_queda_parcial_solo_preparacion` pedía `fps_real == 60` y la aptitud "solo_preparacion". Desde la decisión 029 la tasa es la **medida**: ese clip es nominal 60 fps pero trae **un hueco de 3 fotogramas
(66,7 ms) en 4,3 s**, así que la media real es **59,26** (1,2 % bajo 60) y la aptitud sale "rechazado". Para el producto da lo mismo (queda `parcial`, sin reporte, en los dos casos), pero la etiqueta cambió. Actualicé la prueba
a la semántica de la 029 (`fps_real` entre 59 y 60,1; `R1` en el motivo) y volvió a pasar.
**Anotado, no investigado:** los umbrales de 60 y 120 fps sobre la media medida son frágiles con pocas pérdidas (un 120 fps legítimo con un par de fotogramas perdidos da 118,6 → `parcial`). Decisión tuya si conviene
una tolerancia o evaluar sobre la grilla nominal; hoy se aplica la 029 tal cual.

### Qué se hizo (piezas 1, 2 y 3 del plan; sin commit, sin push)

- **Migración única `20261009120000_reporte_json_y_motivo_archivo_convertido.sql`:** `reportes_biomecanicos.reporte jsonb` (nullable, debe ser un objeto) y el código `archivo_convertido` en `videos.motivo_fallo`.
  **Sin aplicar.** El código nuevo depende de ella: hasta aplicarla, `procesar_video` falla al guardar el reporte (no desplegar ni pushear antes).
- **Ensamblador del reporte** `backend/app/ensamblar_reporte.py` (E5.4 mínimo): arma el JSON v1.1 y lo **valida contra el contrato antes de guardarlo**. Confianza por pico = media de la confianza de las articulaciones del
  segmento en el fotograma del pico (como pidió la 024); tramos no auditables en segundos; cobertura auditable = unión de los tramos excluidos de la cadena; observaciones en el vocabulario de R2 con **prueba automática del
  vocabulario** (E5.7). `procesar_video` guarda el JSON, el mismo `secuencia_correcta` y las métricas **desde esa única fuente**, y ahora escribe `confianza_media` en cada métrica.
- **Motivo `archivo_convertido`:** `fallido` con `fps_real` medido, cuando se declaró cámara lenta, el archivo llegó en tiempo real y **la grilla nominal de sus marcas ya está bajo 120 fps** (100 o 60 fps convertidos). No aplica con
  "normal" (60 fps genuinos → `parcial` por R1) ni a una captura de 120 con fotogramas perdidos. Reintento: solo si cambia la declaración (igual que `modo_captura_incompatible`); el arreglo real es subir otro archivo.
  Texto y botón "Subir otro archivo" en la especificación de frontend §5.
- **Pruebas:** 34 nuevas (21 del ensamblador, 13 de archivo convertido con cliente falso y vocabulario de la migración); suite rápida **400 passed**. `test_procesar_video_e2e` ahora exige el `reporte` válido y `confianza_media`.
- **Corrida en seco** de `procesar_video` con un clip real de Fase B y un cliente falso (96 s, sin tocar la base): el JSON sale válido y serializable. Ahí apareció un defecto mío (cobertura 100 % junto a tramos no
  auditables) que quedó corregido y con prueba.

### Decisiones mías que necesitan tu confirmación (están aisladas, se cambian en un solo lugar)

1. **Veredicto de la secuencia (la 015 lo dejó abierto "para la Etapa 5").** Solo el **revés** emite `correcto` / `desvío leve`. En **saque y drive** el orden se documenta (`orden_observado`, instantes) pero `correcto = null` y la
   observación va en gris (`no_auditable`) con el texto "se documenta el orden pero no se clasifica como correcto o incorrecto". Razón: perfil invertido sin fuente (salvedad 2) y tres cuartos no ordenable (salvedad 1).
   Constante `GESTOS_CON_VEREDICTO` en `ensamblar_reporte.py`. **Consecuencia visible:** en el MVP, saque y drive nunca salen en verde ni en ámbar. El gris para "medido pero sin veredicto" es el estado más cercano de los cuatro de R3.
2. **Escala desconocida** (`escala_temporal_conocida = false`): las velocidades pasan a `valor = null`, `auditable = false` y se agrega una observación; el orden sí se documenta. Antes quedaban como auditables (R3).
3. **Referencia del orden:** "Capítulo 3, apartado 3.3.3", no una cita con año; no inventé una.

### Siguiente paso concreto

1. **Valentín aplica la migración** `supabase/migrations/20261009120000_reporte_json_y_motivo_archivo_convertido.sql` en el SQL Editor y avisa.
2. Correr `pytest tests/integration/test_procesar_video_e2e.py` y después `pytest -m requiere_supabase` (el e2e tarda ~1,5 min).
3. Pieza 4 (7.4: JWT por JWKS, propiedad del video, CORS, retiro del token compartido) y recién después el frontend.

---

## 2026-10-09 (cierre) — NOTA DE TRASPASO (antes de /clear) · decisiones de Valentín y estado

**Rama:** `main`. **Último commit de código: `18942d5`** (E0 lee fotogramas visibles y tasa real, rotación, regularización, contrato v1.1); `68df5ff` es el de documentación (decisión 030, plan de recálculo). El commit
de esta nota es el siguiente. Árbol limpio. **Suite rápida: 366 passed.** `pytest -m requiere_supabase` **no se volvió a correr** desde el 6/10 (77 passed): el motor cambió desde entonces (`probe`, `procesar_video`); correrlo antes
de confiar en el camino real.

### Reglas de trabajo fijadas por Valentín (9/10)

1. **PRIORIDAD ABSOLUTA: el flujo de punta a punta** — registro, carga desde el celular, procesamiento en Render, reporte simple. **Todo lo demás va a la lista "Después del MVP" (abajo). Nada de investigaciones nuevas:
   si aparece algo, se anota y se sigue.**
2. **Fechas:** se trabaja cualquier día, no solo hábiles. **Objetivo: martes 20/10. Compromiso: viernes 23/10.** El **MVP completo, funcionando antes del 2/11**, para que los profesores lo vean con semanas de anticipación.
3. **`IMG_6391` no está incompleto:** es un video corto en el iPhone (2503 fotogramas, 12,5 s). **No se vuelve a bajar.** Las **6 repeticiones de la toma 02** (`saque|trescuartos|toma 02`, sesión 2) **quedan afuera** del recálculo. *(Anotado, no investigado: el
   horneado de esa toma tiene 7011 fotogramas, que a la razón de los otros 15 pares corresponderían a ~15 200 reales; la fecha de creación coincide. Se deja como está por decisión de Valentín.)*
4. **Recálculo del corpus:** **pre-registro aprobado tal cual** — umbral 0,8, mismos grupos, tolerancia en ms (**primaria 8,3; sensibilidad 4,2; 12,5; 16,7**). **Solo el Paso A, y después de la prueba de punta a punta.** El **Paso B es opcional y
   queda después del MVP.** El **Capítulo 7 tiene que anotar el ×2 y su corrección** (ya anotado en `docs/tesis/correcciones-pendientes-capitulo-4.md`).
5. **Entran al flujo** (no son "después"): el **motivo de fallo propio para archivos convertidos** (con migración) y la **integración en el reporte persistido**.

### Qué está hecho (resumen; detalle en las entradas de abajo y en las decisiones 021–030)

- **Servidor:** keep-alive, reintento y permisos por columna aplicados y verificados (77 passed el 6/10); contrato del reporte **v1.1**; E0 lee la tasa real de las marcas de tiempo y los fotogramas visibles; rotación de videos verticales;
  regularización temporal con trazabilidad de puntos interpolados; `procesar_video` toma la tasa del archivo (`origen_factor = marcas_de_tiempo`).
- **Subida desde el iPhone:** el camino que funciona es **Opciones → Formato: Actual** o la app **Archivos** (HEVC con marcas reales, ~200 fps medios). El formato por defecto de Fotos convierte a H.264 y baja a 100 fps o menos.
  Página de prueba publicada: https://kinetiq-prueba-iphone.pages.dev/ (usuario de prueba ya confirmado en Supabase).
- **Corpus:** el horneado es un remuestreo a **~120 fps con rampas**, no 240 (decisión 030): velocidades ×2 sobreestimadas, ms ×0,5 subestimados, ángulos sin cambio. Los 16 originales reales están emparejados (15 pares alineados, 88 repeticiones ubicadas).
- **Frontend:** sigue siendo la maqueta de Lovable con datos simulados; **no hay cliente de Supabase ni de la API todavía.**

### Lo que FALTA para el flujo de punta a punta, en orden (≈ 11 sesiones de ~medio día)

| # | Pieza | Sesiones | Depende de |
| --- | --- | --- | --- |
| 1 | **Migración única** (columna `jsonb` del reporte + código de motivo de fallo para archivo convertido) y su aplicación | 0,5 | Valentín aplica la migración |
| 2 | **Ensamblador del reporte** (E5.4 mínimo): JSON v1.1 validado, confianza por pico, vocabulario R2 (prueba automática), persistencia con la trazabilidad de la regularización | 2 | 1 |
| 3 | **Motivo de fallo propio** en `procesar_video` y mensaje en la especificación | 0,5 | 1 |
| 4 | **7.4:** JWT de Supabase por JWKS, chequeo de propiedad del video (404), CORS acotado, retiro del token compartido, endurecer `usuarios` | 1,5 | — |
| 5 | **Frontend:** cliente de Supabase, sesión, Registro (con aviso de spam) y Login | 1,5 | SMTP o usuario ya confirmado |
| 6 | **Cargar real:** formulario, **instrucción "Opciones → Actual" / Archivos antes de elegir el archivo**, subida directa, alta de sesión y video, llamada a la API | 2 | 4 |
| 7 | **Procesando real** + reintento | 1 | 6 |
| 8 | **Reporte simple real** | 1,5 | 2 y 7 |
| 9 | Publicación en Cloudflare, variables, CORS en Render, **prueba con el celular** | 1 | todo |

Con trabajo todos los días son **11 días hasta el martes 20/10** (vie 9 a lun 19): ~1 sesión por día, **sin colchón**; el compromiso del vie 23/10 da 3 días de margen.

### Siguiente paso concreto

**Pieza 1+2+3:** escribir **una sola migración** (columna `jsonb` en `reportes_biomecanicos` y el código de `motivo_fallo` para archivo convertido), avisar a Valentín para aplicarla, y construir el ensamblador del reporte y el motivo de fallo.
Después 7.4, y recién entonces el frontend. **No tocar el corpus ni el recálculo hasta que la prueba de punta a punta pase.**

### Acciones que son de Valentín (paneles y dispositivos)

- Aplicar la migración de la pieza 1 en el SQL Editor y avisar.
- **Correo:** esperar el Student Pack (opción A: dominio `.me` + Brevo); si no sale antes del 20/10, usar la B (Gmail dedicado) o crear los usuarios de prueba ya confirmados desde el panel. Confirmar el *Site URL* en Supabase al publicar el frontend.
- Render: Free primero; pasar a Standard si la espera o los cortes molestan (decisión 023), y avisar para actualizar `render.yaml` en el mismo paso.
- Probar desde el iPhone con **Opciones → Formato: Actual** cuando esté Cargar.

### Después del MVP (no se toca hasta pasar la prueba de punta a punta y tener el MVP)

- **Paso B del recálculo** (pose desde los originales reales, ~8 h) y la **decisión 031** con los resultados.
- Reetiquetar `escala_temporal` en `catalogo.csv` (fuera del repositorio) y marcar el factor 8 como supuesto.
- PDF y video con esqueleto (E5.5/E5.6) y el reproductor sincronizado (8.7); fotogramas clave con esqueleto **si no entran** en el flujo.
- Puntaje de rendimiento, comparación con la sesión anterior y Evolución real; reintento desde `parcial`; control contra historial (decisión 020).
- Biblioteca real; sesión de varios golpes y estado agregado; **eliminar cuenta y datos** (Ley 25.326) y sus objetos de Storage; recuperación al arranque (6.5); **respaldo manual con restauración probada** (7.7);
  retención de siete días (7.6).
- Probar "cámara lenta sin recortar" con Opciones → Actual; la rampa real que no se probó; la prueba manual de entrega del correo.
- Capítulos 4, 6 y 7 (redacción) con `docs/tesis/correcciones-pendientes-capitulo-4.md`; autovalidación de la semana 4 (Criterios 1 a 4 con grabaciones desde el celular).
- Los reportes de prueba ya guardados en Supabase tienen `fps_real = 240` (supuesto): sin impacto, no hay datos de usuarios; se borran con las pruebas.

### Para retomar sin perder tiempo

- Python del proyecto: `backend/.venv/Scripts/python.exe`, con `PYTHONPATH=backend:tests` para pytest. `ffmpeg`/`ffprobe` están en el PATH.
- `wrangler` (Cloudflare) tiene la sesión abierta con permisos mínimos; se publica con `frontend/node_modules/.bin/wrangler.exe pages deploy …`. **`armar.py` hay que correrlo con el Python del proyecto**, o se publica la versión vieja.
- La caché local `backend/.cache` (818 MB: miniaturas del corpus real, poses, energías) está **ignorada por git**; se puede borrar.
- **Los videos nunca van al repositorio** (`*.mov`, `*.MOV`, `*.mp4`, `.cache/` están ignorados): antes de cada commit, `git ls-files | grep -i -E "\.(mov|mp4|npy|npz)$"` tiene que dar vacío.
- Los originales reales están en `C:\Users\valen\Desktop\corpus-originales-reales`; no se copian.
- Convención: decisiones en `docs/decisiones/` (no se reescriben: las correcciones se marcan con nota visible); resultados en `docs/resultados/`.

---

## 2026-10-09 (noche) — Los 16 originales reales: el corpus horneado es 120 fps con rampas (decisión 030)

- **Inventario de `corpus-originales-reales`:** son **16 archivos** (no 18). HEVC 1920×1080, marcas de tiempo reales, tasa real media **199,9–201,0 fps**, ninguno horneado, sin rotación. **`IMG_6391` está incompleto** (2503 fotogramas, ~15 200 esperados): hay que volver a bajarlo.
- **Emparejamiento:** 16 de 16 por fecha y hora de creación. Los 2 horneados sin par son los controles de velocidad normal (030 y 060): no entran.
- **Los fotogramas NO corresponden uno a uno.** El horneado trae el 46 % de los fotogramas del real: es un **remuestreo a 120,2 fps en tiempo real** (1,665–1,675 reales por horneado en los 15 pares; ~7 % repetidos) con **rampas a velocidad normal** en los extremos.
  Hay una asignación monótona horneado→real (99,1–99,9 %). 88 repeticiones ubicadas: 86 en la meseta, 2 empiezan en una rampa (`saque_perfil_240_01_rep01`, `reves_perfil_240_02_rep01`).
- **Corrección de magnitud:** las velocidades del corpus están **×2,0** sobreestimadas y los ms **×0,5** subestimados (la 029 decía ×1,2). Los ángulos no cambian. **Mi simulación de la 029 suponía fotogramas consecutivos reales: la suposición era falsa.**
- **Error mío anterior (7–9/10):** había dicho "el corpus no tiene rampas": **sí las tiene** (en los extremos de los originales, a velocidad normal). Lo que vi al final del original era manejo de la cámara *dentro* de un tramo a velocidad normal.
- **Motor (obligatorio, aprobado):** `probe()` lee fotogramas visibles y tasa real media; `evaluar()` la usa; rotación automática de videos verticales; `_tasa_del_archivo` (factor 1 con marcas reales, `origen_factor = marcas_de_tiempo`);
  **regularización temporal** con trazabilidad de puntos interpolados; contrato **v1.1**. Humo de punta a punta sobre un recorte real (398 fotogramas, 82 interpolados = 17,1 %). La tarea de la rotación ofrecida queda cumplida.
- **Plan de recálculo escrito, NO ejecutado:** `docs/plan-recalculo-corpus-tasa-real.md` (Paso A rápido sobre poses cacheadas a 120,2 fps; Paso B definitivo desde los originales reales, ~8 h de pose; pre-registro de la tolerancia en ms).
- **Calendario:** el 20/10 cae **martes**. Sigue en pie solo con recortes y margen cero (~40–50 %); recomendación: **viernes 23/10** como fecha de la prueba de punta a punta. MVP completo del 2/11 intacto.
- **Anotaciones para el Capítulo 7** en `docs/tesis/correcciones-pendientes-capitulo-4.md` (RNF-01, fragilidad del Criterio 1, escala, tasa por grabación).

---

## 2026-10-09 (más tarde) — Resultado de las pruebas de Archivos / cámara lenta / Opciones; la tasa real varía (decisión 029)

- **Archivos y "Opciones → Formato: Actual" entregan el MISMO archivo** (42 bytes de metadatos de diferencia): **HEVC 1920×1080, 398 fotogramas visibles, 2,005 s, marcas de tiempo reales**, nominal 239,98 fps y **real media 198,9 fps** (17,1 % de fotogramas perdidos, con un patrón casi periódico:
  cada ~12 fotogramas faltan dos). Coincide con los ~200 fps de Fotos (ⓘ). El camino por defecto de Fotos reexporta a H.264 y **descarta** fotogramas (100 fps en el recorte; 60 nominales y **43 reales** en la cámara lenta de 9,5 s, que además trae **rotación −90°**).
- **`probe()` lee mal el archivo "Actual":** 169,28 fps y 479 fotogramas (cuentan 81 de pre-roll ocultos); hoy `camara_lenta_240` falla y `normal` lo analiza con 169,28 fps. `uniformidad_temporal.marcas_de_tiempo` ahora lee solo los **fotogramas visibles** y mide tasa nominal, **real media**, intervalos y pre-roll; el inspector los informa.
- **Diagnóstico del corpus (sin recalcular), decisión 029.** Simulación de sensibilidad con la huella real de pérdidas sobre las 84 repeticiones (1008 corridas, `docs/resultados/tasa-real-sensibilidad.json`; el arnés reproduce 48/48 picos guardados): velocidades **×1,12–1,16** (hasta ×1,38 en el brazo; teórico ×1,21), ms **×0,83**; el pico se corre ~4 ms (1 fotograma);
  **el orden estimado cambia en ~11–14 %** de las corridas (los picos de pelvis y torso están casi siempre a 0–3 fotogramas: mediana 2); el único grupo que cumple el Criterio 1 (`drive|perfil`) es **frágil** (10/12 y 6/12 mundos) y las conclusiones negativas son robustas (19 de 25 nunca cumplen). Los ángulos no cambian. **Mi lectura inicial ("el orden no cambiaría") valía para el orden real, no para el estimado.**
- **Catálogo:** `escala_temporal: conocida` en los 97 clips propios no tiene base (la huella de fotogramas únicos no detecta fotogramas perdidos); a reetiquetar como nominal.
- **No se recalcula** el corpus: lo más útil es la autovalidación de la semana 4 con archivos de marcas reales. Si Valentín re-exporta las 17 grabaciones originales con "Actual", se puede rehacer el eje de tiempo y recalcular Criterios 1 y 3.
- **Propuesta de producto (a aprobar):** aceptar como auditable completo solo archivos con marcas reales; regularización temporal antes de E3; R1 sobre la tasa real media; horneado (b) solo degradado (orden y ángulos; velocidades y ms no auditables); `modo_captura` como trazabilidad; motivo de fallo propio; contrato v1.1.
- **Pendiente (Valentín):** subir una **cámara lenta sin recortar con Opciones → Actual**. **Pendiente (técnico, separado):** aplicar la rotación de videos verticales en E0 (tarea ofrecida).

---

## 2026-10-09 — Página del iPhone: corregido el "Invalid key" del campo Nota

- **Causa (confirmada contra el Storage real):** la clave del objeto llevaba `~` como separador de la nota (`A-video-todos~recortado-...`) y Supabase Storage la rechaza con `InvalidKey` (400). **Error mío**, de la versión que agregó el campo "Nota".
- **Arreglo:** la nota y el separador ahora solo usan letras ASCII, números, guion y guion bajo (separador `_`); las tildes pasan a su letra base y todo lo demás a guion; la página valida la clave antes de subir y muestra el error si no es válida. Probado con entradas hostiles (tildes, `~`, `/`, emoji, textos largos) y contra el Storage real (la clave con `~` falla, la nueva sube). Republicada.
- **Dato de Valentín, sin subir todavía:** el mismo recorte guardado en **Archivos** pesa **16,47 MB** (contra 8,21 MB desde Fotos), dura 2,005 s, 1920×1080 y conserva la fecha original (24/09): sugiere que Archivos entrega el original sin convertir. **Falta subirlo y medirlo con el inspector.**

---

## 2026-10-07 (noche) — Resultado de la prueba del iPhone: el recorte llegó a 100 fps (decisión 028)

- **Valentín subió el mismo recorte (2 s, se reproduce a velocidad normal) con los cuatro selectores.** Los cuatro archivos son **el mismo video** (15 bytes de metadatos distintos): **H.264 a 100 fps, 201 fotogramas, 2,01 s, 8,2 MB, con audio**, sin
  etiqueta de cámara lenta. **La hipótesis "el recorte conserva los 240 fps" no se cumple por este camino.** Un saque entero entra en esos 201 fotogramas (en el corpus un saque dura 436–656 a 240 fps): se infiere tiempo real a 100 fps, no medido.
- **El sistema no lo analizaría con ninguna declaración** (calculado con las funciones de producción): `camara_lenta_240`/`120` → `fallido` por `modo_captura_incompatible` (240/100 = 2,4); `normal` → `parcial` por R1 (100 < 120). **Riesgo grave para el 20/10.**
- **Error mío corregido:** el primer informe del inspector clasificó los archivos como (c) por un umbral mal elegido (100 fps justo en el límite); ahora cualquier archivo con marcas ≥ 45 fps es "tiempo real" y se informa su aptitud (R1). El inspector además calcula qué haría el sistema según la declaración.
- **Página republicada** con un campo "nota" para distinguir cada prueba. **Pendiente (Valentín):** (1) el mismo recorte guardado en **Archivos** y subido con "Elegir archivos"; (2) una cámara lenta **sin recortar** (≤ ~3 s reales); (3) anotar si el selector de Fotos muestra "Opciones" y qué ofrece.
- **Especificación §5 corregida:** se retiró la afirmación de que el recorte conserva los 240 fps. El mensaje `modo_captura_incompatible` ("revisá el modo de captura") es **engañoso** para este caso (la declaración está bien, cambió el archivo): hace falta un motivo propio o tratarlo como `parcial` por R1; no se implementa hasta conocer los caminos alternativos.

---

## 2026-10-07 (más tarde) — Página del iPhone publicada; casos a/b/c; Student Pack (decisiones 027 y 028)

- **Página de prueba del iPhone PUBLICADA:** https://kinetiq-prueba-iphone.pages.dev/ (Cloudflare Pages, proyecto `kinetiq-prueba-iphone`). Se publicó con `wrangler`. El primer `wrangler login` falló con `request_forbidden`; el
  reintento con permisos mínimos (`--scopes account:read user:read pages:write`) funcionó. Valentín creó el usuario de prueba (confirmado) en Supabase. **Pendiente: que grabe, recorte un golpe del medio y suba con los cuatro selectores.**
- **Decisión 028 — tres casos de llegada de un golpe a 240 fps:** (a) 240 fps en tiempo real, (b) cámara lenta horneada a 30, (c) 30 fps con fotogramas descartados (el único inválido). Las marcas de tiempo distinguen (a) de (b)/(c),
  **no (b) de (c)**: hace falta la duración real del gesto. Implementado `engine/uniformidad_temporal.py` (17 pruebas) y el inspector informa el caso por selector. `_factor_y_motivo` con 240 fps en tiempo real declarado
  `camara_lenta_240`: factor 1, 240 efectivos (8 pruebas nuevas). (c) **no se puede detectar con `_factor_y_motivo`** (30 × 8 = 240 cierra igual): solo lo cubren, de forma condicional, los techos de plausibilidad (decisión 020).
- **Rampas de velocidad: error mío corregido.** Primero interpreté que los saltos de movimiento al principio y al final de los originales eran rampas; **era manejo de la cámara** (el final del original muestra a la persona agarrando el teléfono), y
  los dos originales de velocidad normal dan el mismo patrón. **El corpus no tiene ninguna rampa real.** Medido en los 115 clips (`docs/resultados/uniformidad-temporal-corpus.json`, reproducible): el detector marca los 18 originales, los 2 clips
  completos de velocidad normal y 5 de 95 recortes de golpe válidos (5,3 %; 0 con 8×). **Decisión: E0 no rechaza por velocidad no uniforme**; queda como diagnóstico experimental. Para calibrar uno hace falta una rampa real (pedido a Valentín).
- **Decisión 027 actualizada:** opción **A en curso** (dominio `.me` gratis del GitHub Student Developer Pack con Namecheap —1 año, verificado en la página del Pack— + Brevo) y **B de respaldo** (Gmail dedicado). Procedimientos de las dos documentados.
- **Decisión 026:** Lovable desconectado de GitHub por Valentín (hecho). **Especificación de frontend §5:** explica qué elegir en "¿Cómo lo grabaste?" (cómo se grabó, no cómo se ve ni llega el archivo).

---

## 2026-10-07 — Plan de punta a punta aprobado; contrato v1.0; decisiones 024 a 027

**Rama:** `main`. Valentín aprobó el plan de punta a punta (`docs/plan-mvp-punta-a-punta.md`) con ajustes (puntaje y comparación diferidos; fotogramas clave a la
semana 3 si hay atraso; respaldo con restauración probada antes de la semana 4; **autovalidación** en la semana 4, sin pruebas con otros usuarios; el sistema igual
tiene que funcionar para cualquier usuario nuevo).

- **Decisión 024 — contrato del reporte v1.0, IMPLEMENTADO:** `schemas/reporte.py` + `contrato-reporte.ejemplo.json` + 18 pruebas (`test_contrato_reporte.py`). Severidad de 4 estados;
  `modo_captura`/`factor_ralentizacion`/`origen_factor` en la trazabilidad; `version_contrato`; `dispersion` opcional; artefactos opcionales **por ruta, no URL** (refinamiento mío sobre lo aprobado:
  una URL firmada vence) y `fotogramas_clave`. Dos pruebas mantienen alineados el contrato y las migraciones. El Anexo A queda superado.
- **Decisión 025 — carga directa a Storage, estado por lectura directa, API autenticada con JWT por JWKS + chequeo de propiedad (404).** Desvío de §4.2.3/§4.2.5. Verificado contra el proyecto
  real: el JWKS es público y publica una clave ES256; los tokens de usuario se validan contra él (prueba automática).
- **Decisión 026 — frontend en Cloudflare; el repositorio es la única fuente (Lovable deja de editar).** `CLAUDE.md` §5 actualizado. Correcciones del Capítulo 4 en
  `docs/tesis/correcciones-pendientes-capitulo-4.md` (nueve ítems).
- **Decisión 027 — correo de confirmación: PROPUESTA, pendiente de que Valentín elija.** **Hallazgo:** la propuesta "Brevo sin dominio propio" no es confiable: Brevo exige dominio propio
  (no deja autenticar `gmail.com`, reemplaza el remitente por `t-sender-sib.com`/`brevosend.com`, y hay reportes de correos a Gmail que no llegan sin error). Supabase: el SMTP integrado entrega 2
  por hora y solo a miembros del equipo. Opciones: **A** dominio propio + Brevo (recomendada) o **B** cuenta Gmail dedicada (puente; límites sin verificar). Plantilla en español en
  `supabase/templates/confirmar-registro.html`.
- **Prueba automática de registro → confirmación → login** (`test_registro_confirmacion_login.py`): un usuario nuevo no entra sin confirmar, confirma con el enlace y entra; el token se valida por JWKS.
  Confirma que **la confirmación por correo está activa en el proyecto**. No prueba la entrega del correo (el enlace sale de la API de administración, sin enviar nada).
- **Decisión 023 actualizada:** Free primero (sesiones de 2–3 golpes), Standard si la espera o los cortes molestan y siempre para la defensa; precios verificados por Valentín en render.com/pricing.
  El cambio lo hace Valentín y en el mismo paso se actualiza `render.yaml` (hoy `plan: free`).
- **Prueba de riesgo del iPhone, lista para publicar:** `tools/prueba-iphone/` (página con cuatro selectores) + `armar.py` (genera `publicar/` con URL y clave **anon**, nunca la `service_role`) +
  `backend/app/inspeccionar_subidas.py` (mide cada archivo subido: códec, fps, fotogramas, duración). Probado el inspector con un archivo real; la página, solo su sintaxis (no se la ejercitó con un
  login real). **Pendiente: que Valentín la publique, grabe y suba.**
- Con "como si fuera público" aparece trabajo nuevo, ahora en el plan (semana 3): **eliminar cuenta y datos funcional** (incluye objetos de Storage), a confirmar por Valentín.

---

## 2026-10-06 (al final del día) — Reintento `fallido → encolado`, permisos por columna y plan de Render (decisiones 022 y 023)

**Rama:** `main`. Diseño aprobado por Valentín y registrado como **decisión 022**. Orden de trabajo: (a) migración de
seguridad + prueba → (b) migración del reintento → (c) `procesar_video` y API → (d) pruebas → (e) especificación de
frontend. Regla: no se pushea código que dependa de una migración sin aplicar; se avisa a Valentín cuando cada
migración está lista.

- **Hallazgo:** `authenticated` podía escribir cualquier columna de `videos` (`estado`, `motivo_fallo`, `fps_real`…).
  Comprobado contra el proyecto real: la prueba nueva dio 20 fallas / 3 pasadas antes de la migración.
- **(a) HECHO, aplicado y pusheado:** `20261006130000_columnas_protegidas_videos_sesiones.sql` +
  `tests/integration/test_columnas_protegidas.py` (commit `4a666f0`). Valentín aplicó la migración;
  `pytest -m requiere_supabase` dio 62 passed (39 anteriores + 23 nuevos), sin restos (0 usuarios Auth, 0 objetos
  Storage, 1 `versiones_motor`). Se restringió también el INSERT de `videos` (aprobado por Valentín).
- **(b)–(e) HECHOS, aplicados y pusheados:** (b) `20261007000000_reintento_fallido.sql`, aplicada por Valentín; (c)
  `app/reintento.py`, `routers/analisis.py`, `procesar_video.py` (escribe `modo_captura_intentado`, reemplaza el
  reporte previo, marca `error_inesperado`), `config.get_max_intentos` (`KINETIQ_MAX_INTENTOS`, 3 por defecto); (d)
  `tests/unit/test_reintento.py`, `test_api_analisis.py` ampliado, `tests/integration/test_reintento_supabase.py` y
  un reporte previo sembrado en `test_procesar_video_e2e.py`; (e) especificación de frontend §5. Verificado:
  suite rápida 284 passed; `pytest -m requiere_supabase` **77 passed** (8 min 42 s), sin restos. El trigger cubre
  también `atleta_id` (aprobado por Valentín). **Frente del servidor cerrado.**
- **Decisión 023 registrada:** instancia de Render. Free y Starter descartados para las pruebas con usuarios;
  **Standard (1 CPU, 2 GB, USD 25/mes) solo durante pruebas y defensa, cambio hacia el 20/10**, después vuelve a
  Free; `render.yaml` se actualiza en el mismo paso del cambio, no antes. Corregido en la 017 el error "Standard =
  2 vCPU". Resuelve el pendiente "criterio de instancia" que figuraba acá.
- **Siguiente:** plan de punta a punta en `docs/plan-mvp-punta-a-punta.md` (propuesta, a aprobar por Valentín).
- **PENDIENTE (anotado a pedido de Valentín): procedimiento de respaldo manual de la base antes de las pruebas
  con usuarios.** Supabase se queda en el plan Free (el keep-alive de la decisión 021 resuelve la pausa; el límite
  de 50 MB por archivo coincide con la decisión 016), y **Free no incluye respaldos**: un error propio (migración
  mal aplicada, `delete` sin filtro) o una pérdida del proyecto no tendría vuelta atrás. Hay que definir y probar
  UNA restauración real de punta a punta (volcado de las tablas del esquema `public` y de los usuarios de Auth, con
  qué herramienta, dónde se guarda —nunca en el repo, son datos de salud—, cada cuánto y cómo se restaura) antes
  de que entre el primer usuario real (Etapa 9).
- **Decisiones de Valentín:** `error_inesperado` reintentable con tope 3 (parámetro); `parcial` queda fuera
  (anotado como pendiente: reintento desde `parcial` cuando se declaró "normal" un slow-mo); el aviso de "<120 fps"
  del frontend pregunta "¿Lo grabaste en cámara lenta?" antes de subir; trigger en `sesiones` sí.

---

## 2026-10-06 (más tarde) — Keep-alive de Supabase (pendiente 1 de la nota de traspaso)

**Rama:** `main`. Workflow `.github/workflows/supabase-keepalive.yml` (cron cada 3 días + `workflow_dispatch`,
`POST /rest/v1/rpc/keepalive` con la clave anon desde los secrets `SUPABASE_URL` y `SUPABASE_ANON_KEY`; falla si
no hay 2xx) y migración `20261006120000_keepalive_rpc.sql` (aplicada por Valentín; `select public.keepalive()`
devuelve la hora). **Decisión 021:** con `anon` no se podía consultar ninguna tabla (401, comprobado), así que se
aprobó una excepción acotada: una función que solo devuelve `now()`; alternativa descartada, `service_role` como
secret de GitHub.

Verificado: el script exacto del YAML corrido en local contra el proyecto real dio HTTP 200; falla con exit 1 en
secretos vacíos, clave service_role/`sb_secret_`, URL inalcanzable y función inexistente (404). **Falta** la
corrida manual en GitHub (Actions → Supabase keep-alive → Run workflow) y confirmar en el panel, pasado el 13/10,
que el proyecto sigue activo. Quedan los pendientes 2 y 3 de la nota de traspaso.

---

## 2026-10-06 — Trazabilidad del modo y el factor en el reporte · NOTA DE TRASPASO (antes de /clear)

**Rama:** `main`. **Último commit de código: `36a60fd`** ("feat: trazabilidad del modo de captura y del factor de
ralentizacion en el reporte"), pusheado. La nota de traspaso va en el commit siguiente (solo documentación).

### Qué se hizo

- **Control contra historial: DIFERIDO** (decisión 020, propuesta no implementada; requiere datos del
  Criterio 3 para calibrar). Sumada a las limitaciones de la tesis: la detección del error inverso (normal
  declarado como cámara lenta) por techos de plausibilidad es **condicional** — un factor ×2 o golpes lentos
  pueden pasar sin ser detectados.
- **Trazabilidad (R4):** migración `20261006000000` (aplicada y verificada por Valentín): `modo_captura` y
  `factor_ralentizacion`, ambas NOT NULL sin default, en `reportes_biomecanicos`. Se congelan en el reporte
  (la declaración de la sesión es editable después). `procesar_video` las escribe; el e2e las verifica.
  Especificación de frontend: el nivel 3 muestra modo, factor y origen.
- **Prueba contra Render** con marcador propio `requiere_render`: no corre en la suite normal ni con
  `-m requiere_supabase`; solo con `-m requiere_render` (la corrida real pasó en 74 s).
- **Tropiezo propio, ya corregido:** al hacer NOT NULL las columnas nuevas, la primera corrida de
  `requiere_supabase` dio 1 failed + 24 errors: dos pruebas (`test_rls_aislamiento`, `test_cascada_borrado_usuario`)
  insertaban reportes a mano sin esas columnas. Corregidas; el esquema NO se aflojó (sin default a propósito).

### Estado verificado (6/10)

| Suite | Comando | Resultado |
| --- | --- | --- |
| Rápida | `pytest -m "not slow"` | 253 passed |
| Supabase real | `pytest -m requiere_supabase` | 39 passed (~7 min); sin restos: 0 usuarios Auth, 0 objetos Storage, 1 `versiones_motor` |
| Render real | `pytest -m requiere_render` | a demanda, no corre sola |

### PENDIENTES, EN ORDEN

1. **URGENTE — keep-alive de Supabase con GitHub Actions.** El plan gratuito **pausa el proyecto tras 7 días
   sin actividad**; última actividad conocida: hoy 6/10 (pruebas) → vence ~13/10 si no se hace nada. Ya existe
   `.github/workflows/` pero está **vacío**. Idea: workflow con `schedule` (cron cada ~3 días) +
   `workflow_dispatch`, que haga una consulta barata vía PostgREST con la clave guardada como *secret* del repo
   (nunca en el repo). Valentín tiene que cargar los secrets en GitHub (Settings → Secrets); el workflow no
   puede crearlos. Verificar con una corrida manual.
2. **Reintento `fallido → encolado`.** Hoy `POST /analisis/{id}/procesar` pone `encolado` sin validar el estado
   previo. Falta definir las transiciones permitidas, limpiar `videos.motivo_fallo`, y resolver la restricción
   única `reportes_biomecanicos.video_id` (~~hoy `procesar_video` borra el reporte previo~~ — **dato FALSO,
   corregido el 6/10 más tarde:** `procesar_video` NO borra nada; no hay `delete` ni `upsert`, así que un segundo
   análisis falla en el `insert` por la restricción única y marca `fallido` un video que ya tenía reporte válido).
   ~~Valentín quiere ver el diseño y aprobarlo antes de implementar.~~ **Diseño aprobado el 6/10: decisión 022.**
3. **Control contra historial** (decisión 020): diferido; recién con datos del Criterio 3.

### Otros pendientes, sin orden de urgencia

- **Primer paso de la Etapa 5:** alinear `schemas/reporte.py` — `severidad` de 4 estados (decisión 018) y
  los campos de `Trazabilidad` `modo_captura`, `factor_ralentizacion`, `origen_factor` (decisión 020) —
  antes de generar cualquier JSON real. Un solo cambio de contrato, registrado.
- Render Free → Starter por criterio (RSS > 460 MB o corte por suspensión), antes de la Etapa 9.
- Captura del editor de tablas de Supabase (apartado 4.4.6) pendiente.
- Borrado de objetos de Storage al eliminar la cuenta (Etapa 7; la cascada de Postgres no los toca).
- Frontend: campo "¿Cómo lo grabaste?" (especificación §5).
- Redacción del Capítulo 4 y de los Capítulos 6 y 7 (lista en `CLAUDE.md` §5; incluye las limitaciones de la 020).

### Siguiente paso concreto

Pendiente 1 (keep-alive): escribir el workflow y pedirle a Valentín que cargue los secrets; después presentar el
diseño del reintento (pendiente 2) para aprobación; recién después la Etapa 5.

---

## 2026-10-02 (más tarde) — El arreglo del bug de fps no servía para producción: diseño final con declaración del usuario

**Rama:** `main`. Continuación directa de la entrada anterior. Valentín objetó el primer arreglo del bug de
fps (decisión 020) antes de que llegara a aplicarse: buscar el factor en `catalogo.csv` por nombre de archivo
solo funciona con clips del corpus de prueba — un usuario real sube `IMG_4012.MOV` sin fila de catálogo, y
confirmó con sus propios clips que los slow-mo de iPhone declaran 30 fps aunque se hayan capturado a 240, se
recorten donde se recorten. Pidió diseño nuevo, lo presenté, lo aprobó con dos correcciones, e implementé.

**Diseño:** el usuario declara el modo de captura al cargar, una vez por sesión (`sesiones.modo_captura`:
`normal` | `camara_lenta_120` | `camara_lenta_240`). El motor combina esa declaración con el fps real del
contenedor (`_factor_y_motivo`, reemplaza a `_factor_de_catalogo`); si no cierra con un factor entero, el
video queda `fallido` con un código cerrado (`videos.motivo_fallo`), nunca se adivina en silencio.

**Las dos correcciones de Valentín sobre mi primera propuesta, las dos reales, no cosméticas:**

1. **"`normal` nunca falla por fps altos."** Mi primera versión hacía fallar `normal` si el contenedor
   declaraba ≥ 120 fps, razonando que era "una combinación inusual". Valentín: equivocado — `normal` significa
   "sin cámara lenta", no "fps bajo"; hay teléfonos que graban 120+ fps en modo normal, y eso es válido.
   Saqué esa rama de fallo por completo: `normal` usa el fps del contenedor tal cual, sea cual sea, y R1
   decide después si alcanza para el análisis completo.
2. **`motivo_fallo` como código cerrado, no texto libre.** Mi primera versión iba a guardar el texto técnico
   directo en la columna. Valentín: el texto en lenguaje llano para el jugador lo resuelve el frontend (R2);
   el detalle técnico (fps del contenedor, factor calculado) va al log, no a lo que ve el usuario ni a la
   base. `videos.motivo_fallo` queda con un `check` de vocabulario cerrado (hoy un solo código,
   `modo_captura_incompatible`; motivos nuevos se agregan cuando existan de verdad, no se anticipan).

**Esquema (migración `20261002000000_modo_captura_y_trazabilidad_escala.sql`, nueva, no toca las ya
aplicadas — no aplicada todavía, queda para que Valentín la corra):**
- `sesiones.modo_captura` (`not null`, sin default — fuerza a declarar).
- `videos.motivo_fallo` (código cerrado).
- `reportes_biomecanicos.escala_temporal_conocida` + `.origen_factor`: el contrato JSON congelado
  (`schemas/reporte.py: Trazabilidad.escala_temporal_conocida`) nunca se persistía en la base — se cierra ese
  hueco de trazabilidad (R4) de paso, ya que se estaba tocando la escala temporal por el mismo motivo.

**Pruebas:**
- `tests/unit/test_procesar_video_factor.py` (15 casos, sin red, nuevo): `normal` nunca falla en ningún fps
  probado (23,976 a 480), los factores de cámara lenta dan el entero esperado incluida la normalización
  NTSC, las combinaciones inconsistentes fallan con el código cerrado.
- `tests/integration/test_procesar_video_modo_captura_fallido.py` (nuevo): un clip real de 25 fps del corpus
  público declarado `camara_lenta_240` (240/25 = 9,6, no cierra) deja el video `fallido` de verdad contra
  Supabase real, con `fps_real`/`apto_fase_rapida` en `null` (no se guesea un valor ya demostrado no
  confiable) y sin `reportes_biomecanicos`.
- **No hay en el corpus ningún clip de un solo golpe grabado en modo normal** (todos los recortes de la Fase
  B son cámara lenta) para probar de punta a punta "normal con fps alto → análisis completo" contra un
  archivo real — se prueba con la unidad pura en vez de forzar un archivo que no existe; anotado así en el
  test, no silenciado.
- `test_procesar_video_e2e.py` y `test_api_analisis_e2e.py` actualizados: declaran `camara_lenta_240` (los
  clips reales de la Fase B lo son) en vez de depender del catálogo.
- Las otras dos pruebas que insertan `sesiones` (aislamiento, cascada) actualizadas con `modo_captura:
  'normal'` — no procesan video de verdad, cualquier valor válido alcanza.
- Suite rápida: ver más abajo si terminó antes del commit. Las pruebas que dependen de Supabase no se
  pueden correr todavía — necesitan la columna `sesiones.modo_captura`, que no existe hasta que se aplique
  la migración.

**Especificación de frontend (`docs/ux/especificacion-frontend.md` §5):** campo nuevo "¿Cómo lo grabaste?",
una vez por sesión, sin opción marcada por defecto; nota de que el aviso de "< 120 fps" del navegador usa el
fps crudo del archivo (sin corregir por cámara lenta, eso lo hace el motor) y no debería asustar al usuario
si ya eligió cámara lenta más arriba; y que una combinación que no cierra se muestra como error en lenguaje
llano, nunca procesada adivinando.

**Decisión 020 ampliada** con el diseño final, las dos correcciones de Valentín documentadas explícitamente
(para que quede el razonamiento, no solo el resultado), y la verificación completa.

### Pendiente

1. Valentín aplica `supabase/migrations/20261002000000_modo_captura_y_trazabilidad_escala.sql` desde el
   editor SQL.
2. Con la migración aplicada: correr `pytest -m requiere_supabase` completo (ahora con 2 archivos nuevos) y
   confirmar limpieza, como siempre.

### Siguiente paso concreto

Avisarle a Valentín que la migración está lista; cuando la aplique, correr la suite completa y commitear.

---

## 2026-10-02 — Tarea 4.5.4 cerrada: medición real en Render, bug de fps corregido, Etapa 4.5 completa

**Rama:** `main`. Continuación directa de la entrada anterior (semilla de la API lista, 1/10 noche). Valentín
conectó el repo a Render (plan Free) y corrió el análisis real; esta entrada cubre las seis tareas que pidió
al traer el resultado.

### 1. Números de Render registrados (decisión 017 ampliada)

Free: 414,1 s, RSS pico 480,4 MB, sin cortes por suspensión, sobre el mismo video de prueba. Comparado contra
Docker local (0,5 vCPU simulado): 176–185 s / 426–427 MB. **Decisión de Valentín: Render Free durante el
desarrollo; pasar a Starter antes de las pruebas de usabilidad de la Etapa 9**, con criterio explícito (no
"ya se verá"): memoria pico > 460 MB en cualquier clip real, o cualquier corte por suspensión.

### 2. Investigado el salto de memoria (426→480 MB) — parcialmente explicado, con dato limpio

Con Docker Desktop recuperado (mismo bug del "Inference manager" de sockets huérfanos que ya documentó la
bitácora el 29/9 — mismo arreglo, renombrar las carpetas y desactivar `EnableDockerAI`), medido DENTRO del
contenedor real, sin contaminar con nada más:

- Solo motor (numpy + mediapipe + engine/*, igual que `medir_contenedor.py`): **89,2 MB** tras los imports.
- Motor + FastAPI + uvicorn + supabase (igual que `app.main`, lo que corre en Render): **127,8 MB** tras los
  imports, antes de procesar nada.

**38,6 MB de los ~54 MB de diferencia salen de tener FastAPI/uvicorn/supabase en el mismo proceso que el
motor — confirmado, no una sospecha.** El resto queda sin explicación limpia: una corrida completa dentro de
Docker dio 485,4 MB, pero compitiendo por CPU con el diagnóstico del corpus (tarea 3) corriendo al mismo
tiempo — no es una medición limpia, se dice así en vez de maquillarla. Se aplicó igual una corrección real y
justificada en `app/procesar_video.py`: los bytes del clip descargado quedaban vivos en memoria durante toda
la inferencia (se liberan con un `del` explícito apenas se escribe el archivo temporal) — reduce la
superposición de memoria en principio, no remedida limpia todavía. La medición que importa de verdad es la
próxima vez que Valentín corra esto en Render.

### 3. Frecuencia del brazo no auditable — tabla hecha, y un hallazgo más importante en el camino

`app/diagnostico_brazo_corpus.py` (nuevo, de solo lectura, sobre la pose ya cacheada de los 84 clips
propios de perfil/tres cuartos a 240 fps, sesiones 1 y 2 — mismo método que `medicion_criterio1.py`):

| gesto | encuadre | lado cámara | n | no auditable | oclusión | cálculo | señal plana |
| --- | --- | --- | --- | --- | --- | --- | --- |
| drive | perfil | opuesto al dominante | 12 | 8,3% | 0 | 0 | 1 |
| drive | tres cuartos | opuesto al dominante | 12 | 0,0% | 0 | 0 | 0 |
| revés | perfil | opuesto al dominante | 12 | 0,0% | 0 | 0 | 0 |
| revés | tres cuartos | opuesto al dominante | 12 | 0,0% | 0 | 0 | 0 |
| saque | perfil | opuesto al dominante | 12 | 8,3% | 0 | 1 | 0 |
| saque | tres cuartos | opuesto al dominante | 24 | 4,2% | 0 | 0 | 1 |

**El lado de cámara no discrimina nada: es "opuesto al dominante" en las 84 repeticiones**, porque la
decisión 013 ya fijó "no se graba del lado derecho" como protocolo para toda la Fase B — no hay variación
que medir en este corpus sobre ese eje, no es un error del script.

**Cero casos de oclusión** dentro de la ventana anclada al torso (±300 ms) — la oclusión del brazo que
documentan las decisiones 011/013 existe en el clip completo, pero en la ventana angosta del pico el codo
dominante suele estar justo arriba del umbral de confianza. Solo 3 de 84 golpes (3,6%) no auditables: 2
"señal plana" (hay serie pero ningún pico se destaca) y 1 "velocidad implausible... probable error de
detección" (saque de perfil, rep03) — la única que calza con "problema de cálculo" tal como lo pidió
Valentín, y es un caso aislado, no un patrón. Resultado completo en
`docs/resultados/diagnostico-brazo-corpus.json`.

**Al cruzar este resultado contra lo que procesaba `procesar_video.py` en vivo apareció un bug real y más
serio, no solo el que se estaba buscando** — ver el punto siguiente.

### Bug encontrado y corregido: `procesar_video.py` ignoraba la cámara lenta (decisión 020)

El clip que disparó el aviso "pico de brazo no finito" en las dos pruebas anteriores
(`..._drive_perfil_240_01_rep01.mov`) daba auditable en el diagnóstico del corpus (pose cacheada) pero NaN en
`procesar_video.py` (extracción en vivo). Comparando landmark por landmark: **idénticos, diferencia 0** — no
es un problema de determinismo de MediaPipe. La diferencia real: `fps_efectivos` cacheado = 240,0; en vivo =
30,0. Es una captura Apple en cámara lenta (contenedor declara 30 fps, captura real 240, factor 8, confirmado
en `catalogo.csv`). `procesar_video.py` (escrito en la tarea 4.5.3) tomaba `fps_declarados` directo, con un
comentario ("los clips de la Fase B ya vienen a la frecuencia real") que resultó **falso**, nunca verificado
contra el catálogo. Con el valor sin corregir, toda velocidad salía calculada 8 veces mal — no solo el brazo,
cualquier resultado de ese clip.

**No es un bug del motor** (`engine/sequencing.py` hizo lo correcto con el fps que le dieron); es un bug de
`procesar_video.py`, que no llamaba a la detección de cámara lenta que `engine/ingest.py::evaluar` ya tenía
desde la Etapa 1. Corregido: `_factor_de_catalogo()` busca el factor real en `catalogo.csv` cuando el archivo
tiene fila (todo lo que se prueba hoy); sin catálogo (un upload real futuro, Etapa 8) usa `factor=1.0` sin
inventar nada, y **R1 ahora se aplica de verdad**: por debajo de 120 fps efectivos no se corre la
secuenciación completa, el video queda `parcial` en vez de un resultado inválido presentado como bueno. Las
pruebas de integración tenían el mismo problema (subían el clip con nombre aleatorio, impidiendo la búsqueda
en el catálogo) — corregidas para conservar el nombre real. Verificado: con la corrección, las pruebas de
punta a punta vuelven a pasar y **ya no aparece el aviso de pico no finito** en ese clip. Detalle completo en
la decisión 020.

### 4. Aviso de MediaPipe confirmado también en local

`Using NORM_RECT without IMAGE_DIMENSIONS is only supported for the square ROI` aparece igual corriendo
`medir_contenedor.py` en Windows que en Render — no es un resultado distinto por el entorno, es el
comportamiento normal de MediaPipe con esta configuración.

### 5. Versión del motor — no está desactualizada

Revisadas las cinco etiquetas de etapa cerradas (`v0.1.0-etapa0` … `v0.5.0-etapa4`): el `__version__` del
motor en cada una es siempre un minor menos que la etiqueta (etapa4 → tag `v0.5.0`, motor `0.4.1`) — patrón
consistente en las cinco, no una excepción de la Etapa 4. Ningún commit tocó `engine/` entre el último bump
(`0.4.1`, decisión 010) y el cierre de la Etapa 4 (decisión 015) salvo un comentario sin cambio numérico
(decisión 011). `engine/version.py` ahora documenta el desfasaje a propósito para que no vuelva a generar la
duda.

### 6. Datos de prueba borrados, Docker reparado

Usuario/atleta/sesión/video de prueba de Render borrados (cascada). Docker Desktop, que volvió a chocar con
el bug conocido del "Inference manager", reparado con el mismo procedimiento documentado el 29/9.

**Confirmado en carne propia el límite que ya anotaba la decisión 018:** borrar el usuario no se llevó el
clip de Storage (26 MB, `f16a8b3f-.../00e1efba....mov`) — son dos sistemas distintos, la cascada de Postgres
no toca `storage.objects`. Encontrado al verificar la limpieza final, no asumido; borrado a mano. Sigue
pendiente de la Etapa 7 (el flujo real de "eliminar mi cuenta" tiene que borrar Storage aparte).

### Pendiente

- La medición limpia de RSS en Docker local (sin contención con otro proceso), si hace falta más precisión
  que la medición real de Render — no bloquea nada, Render es la fuente de verdad de todos modos.
- Detección automática de cámara lenta para un upload SIN fila de catálogo: declarado como límite conocido,
  no resuelto, depende del diseño de la pantalla de carga real (Etapa 8).

### Siguiente paso concreto

Commit y push de todo lo de esta entrada. Con eso, **la Etapa 4.5 completa queda cerrada** (4.5.1 a 4.5.5):
siguiente paso del plan es la Etapa 5 (auditoría y reporte) — y lo primero ahí, por pedido explícito de
Valentín en la decisión 018, es resolver la desalineación entre `alertas.severidad` en la base (cuatro
estados de R3) y el `Literal` de tres valores todavía congelado en `reporte.py`, antes de generar cualquier
JSON real.

---

## 2026-10-01 (noche, aún más tarde) — Tarea 4.5.4: semilla de la API lista, falta conectar Render

**Rama:** `main`. Continuación directa de la entrada anterior (4.5.3 cerrada y pusheada, commit `aa8d0ee`).

**Pedido de Valentín:** antes de pagar el plan Starter, probar primero el plan gratuito de Render con datos
reales. Con cuatro condiciones explícitas: endpoint protegido por token (401 sin él, `/health` público
aparte), responde 202 y procesa en segundo plano (para medir de verdad si la suspensión del plan gratis
corta un análisis en curso), ningún secreto en el repo, y que sea la semilla real de la API de la Etapa 6
(estructura `routers/`), no código descartable.

**Hecho — decisión 019, detalle completo ahí:**

- **`backend/app/{main.py, security.py, routers/, workers/}`:** la estructura que la decisión 003 reservó
  para la Etapa 6 desde la Etapa 0 (hasta ahora solo `.gitkeep`), llenada por primera vez. `GET /health`
  (público, estado + versión del motor) y `POST /analisis/{video_id}/procesar` (protegido por
  `X-Kinetiq-Token` contra `KINETIQ_API_TOKEN`, `secrets.compare_digest`; 202 inmediato,
  `BackgroundTasks` de FastAPI llama a `procesar_video` de la tarea 4.5.3 — decisión de MVP del apartado
  4.4.2, sin cola externa). `backend/app/schemas/api.py` con los esquemas Pydantic de entrada/salida.
- **`render.yaml`** en la raíz: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `KINETIQ_API_TOKEN` con
  `sync: false` — Render los pide al aplicar el blueprint, no quedan en el repo.
- **`backend/Dockerfile`:** `CMD` pasa de `["bash"]` (abierto desde la 4.5.3) a
  `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` — el comando de producción real.
- **`app/procesar_video.py`** ahora mide tiempo total y RSS pico desde adentro del proceso (mismo método que
  `medir_contenedor.py`, decisión 017) y lo imprime en el log — para leer los números reales del log de
  Render directamente, sin depender de una lectura aparte del panel de métricas.
- **8 pruebas nuevas:** `tests/unit/test_api_salud.py` y `test_api_analisis.py` (rápidas, con un cliente de
  Supabase falso y el worker de fondo espiado — sin red: 401 sin token, 401 con token incorrecto, 404 si no
  existe el video, 202 si todo está bien, 500 si el servidor no tiene el token configurado) y
  `tests/integration/test_api_analisis_e2e.py` (dispara un análisis real a través de la API, contra Supabase
  real, con inferencia de MediaPipe completa — confirma que el cableado nuevo funciona con el stack real,
  no solo con falsos).
- **Suite completa confirmada en verde** tras los cambios: 238 pasan en la rápida, 37 en
  `pytest -m requiere_supabase` (después, 1 más al re-correr solo la de 4.5.3 tras agregar la instrumentación
  de tiempo/memoria). Limpieza confirmada de nuevo: 0 usuarios, 0 objetos, una sola fila real de
  `versiones_motor`.
- **No verificado en Docker local:** Docker Desktop no estaba corriendo en esta sesión; no se insistió en
  levantarlo porque el propio build de Render es la verificación real (y reporta cualquier error del
  `Dockerfile` en su log), no hace falta duplicarla en local.

### Pendiente — lo que le toca a Valentín

1. Generar `KINETIQ_API_TOKEN` (comando en la decisión 019).
2. Conectar el repo a Render con `render.yaml` (plan Free).
3. Cargar a mano, en el panel → Environment del servicio: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`,
   `KINETIQ_API_TOKEN`.
4. Probar `GET /health` y disparar un análisis real con `POST /analisis/<video_id>/procesar`.
5. Leer el log del servicio para tiempo/RSS pico y observar si la suspensión por inactividad corta un
   análisis en curso. Con esos números: Free alcanza, o se pasa a Starter (actualiza `render.yaml` y la
   decisión 017).

### Siguiente paso concreto

Commit y push de 4.5.4. Pasos exactos de conexión a Render, para Valentín, en el mensaje de cierre de esta
tarea (no se repiten acá para no desincronizarse si cambian).

---

## 2026-10-01 (noche, más tarde) — Tarea 4.5.3: el contenedor habla con Storage y la base

**Rama:** `main`. Continuación directa de la entrada anterior (4.5.2 cerrada y pusheada, commit `e1c2604`).

**Hecho:**

- **`backend/app/procesar_video.py`** (nuevo, `python -m app.procesar_video <video_id>`): baja un video de
  Storage por su `video_id`, resuelve el lado dominante (`sesiones` → `atletas.mano_dominante`), corre el
  pipeline existente sin tocarlo (ingesta → pose → E3 → secuenciación) y escribe `reportes_biomecanicos` +
  `metricas` + los campos reales de `videos` (fps, fotogramas, duración, resolución, `apto_fase_rapida`). Es
  el primer código que cierra el círculo completo de la arquitectura del apartado 4.5 (Storage → motor →
  base) con datos reales. **No es la Etapa 5:** no calcula alertas ni el puntaje de sesión a propósito, esos
  módulos no existen todavía.
- **`versiones_motor` se reutiliza, no se duplica por análisis:** `_version_motor_id()` busca por
  `version_motor` + `backend_pose` antes de insertar — confirmado con la prueba real, sigue habiendo una sola
  fila tras varias corridas.
- **Hallazgo real al correr contra un clip real, no anticipado:** un pico de velocidad del brazo salió `NaN`
  en un clip de perfil (consistente con las limitaciones del brazo en esa vista ya documentadas en las
  decisiones 011/013/015) — `json`/Postgres no aceptan un valor no finito, y al principio tiró la prueba
  abajo (`ValueError: Out of range float values are not JSON compliant`). Corregido: un pico no finito se
  trata igual que un pico ausente (se omite la métrica, con aviso en el log), no se escribe un dato inventado
  — mismo principio R3 aplicado a un caso que no estaba cubierto todavía.
- **`tests/integration/test_procesar_video_e2e.py`:** sube un clip real de la Fase B, registra la
  sesión/atleta/video que le correspondería, corre `procesar_video` de verdad (inferencia de MediaPipe
  completa, no simulada) y confirma el reporte, las métricas y los campos de `videos`. Limpia usuario de
  prueba y objeto de Storage al terminar; **no borra la fila de `versiones_motor`** a propósito — es un dato
  real, no sintético (se reutiliza entre corridas de prueba y reales por igual).
- **36 pruebas en verde** con `pytest -m requiere_supabase` (la de este archivo tarda ~100 s: es inferencia
  real de MediaPipe, no una medición simulada). Limpieza confirmada de nuevo con `list_users()` y
  `storage.from_("videos").list()` en 0, y una sola fila de `versiones_motor` (la real, no una de prueba).

### Pendiente

**No verificado todavía dentro de un contenedor Docker real** — Docker Desktop no estaba corriendo en esta
sesión y no se insistió en levantarlo, porque la tarea 4.5.4 (despliegue real en Render) de todos modos
necesita correr esto dentro de un contenedor de verdad para desplegarlo; no tiene sentido duplicar ese paso
acá. Si al llegar a 4.5.4 conviene primero una prueba en Docker local antes del despliegue en la nube, se
decide ahí, no se da por hecho ahora.

### Siguiente paso concreto

Commit y push de 4.5.3, y arrancar la tarea 4.5.4 (desplegar el contenedor en Render Starter, correrlo de
punta a punta contra el proyecto real, y medir el plan gratuito como pidió Valentín antes de pagar nada).

---

## 2026-10-01 (noche) — Tarea 4.5.2: bucket de Storage, cerrada

**Rama:** `main`. Continuación directa de la entrada anterior (4.5.1 cerrada y pusheada, commit `030cd84`).

**Hecho:**

- **`supabase/migrations/20261001090300_bucket_videos.sql`** (aplicada por Valentín desde el editor SQL):
  bucket privado `videos`, con `file_size_limit` (52428800 bytes = 50 MB, decisión 016) y
  `allowed_mime_types` (`video/mp4`, `video/quicktime`) — un segundo cerco del lado del servidor, no solo la
  validación del navegador de la especificación de frontend §5. RLS de `storage.objects` con la misma
  convención de ruta `<usuario_id>/...` que ya usan las tablas de `public/`.
- **Tres archivos de prueba nuevos**, los dos últimos a pedido explícito de Valentín:
  - `tests/integration/test_storage_bucket.py`: sube un clip real de la Fase B (lo resuelve solo vía
    `KINETIQ_DATA_DIR`, cualquier recorte de una repetición sirve) y confirma la descarga byte a byte, tanto
    con `service_role` como por URL firmada sin ninguna credencial — lo que haría el frontend.
  - Sumado al mismo archivo: rechazo del servidor para un archivo de 50 MB + 1 byte y para un tipo no
    permitido (`text/plain`) — confirma que `file_size_limit`/`allowed_mime_types` del bucket se aplican de
    verdad, no solo están declarados.
  - `tests/integration/test_storage_aislamiento.py`: mismo principio RNF-07 de `test_rls_aislamiento.py`
    (Etapa 4.5.1) aplicado a objetos en vez de a filas — un usuario no puede leer ni subir archivos en la
    carpeta de otro, y un cliente sin sesión no lee nada.
- **Hallazgo distinto al de la 4.5.1:** acá `service_role` sí tuvo acceso completo a Storage sin necesitar un
  `GRANT` aparte — confirmado corriendo la prueba real, no asumido. La Storage API de Supabase es un servicio
  separado de PostgREST (no pasa por los `GRANT` de tabla que hubo que agregar en 4.5.1 para `public/`), así
  que la lección de la decisión 018 (RLS y privilegios de tabla son capas independientes) no se repite acá de
  la misma forma — documentado en la propia migración para que quede donde se vuelve a leer.
- **Limpieza confirmada, no asumida** (pedido explícito de Valentín): `auth.admin.list_users()` en 0 y
  `storage.from_("videos").list()` en 0 después de la corrida completa.
- **35 pruebas en verde** con `pytest -m requiere_supabase` contra el proyecto real (las 28 de la 4.5.1 más
  las 7 nuevas de Storage).

### Pendiente

Nada bloqueante para 4.5.2. Sigue abierta la captura del editor de tablas del apartado 4.4.6 (heredada de la
4.5.1, no bloquea).

### Siguiente paso concreto

Commit y push de 4.5.2, y arrancar la tarea 4.5.3 (completar el contenedor: que descargue el clip de Storage
y escriba el resultado mínimo en la base — ya tiene la medición de tiempo/memoria hecha desde el 29/9, ahora
existen el esquema y el bucket que le faltaban).

---

## 2026-10-01 (tarde) — Esquema de datos rediseñado (decisión 018) y migraciones escritas

**Rama:** `main`. Continuación de la tarea 4.5.1 desde el checkpoint de esta misma mañana.

**Lo pedido por Valentín al retomar:** antes de escribir las migraciones, revisar que el esquema del apartado
4.4.6 contemplara lo que ya muestra `docs/ux/especificacion-frontend.md` §9 (sesión como grupo de videos, rol
y vista por defecto del usuario, reporte a nivel de sesión con puntaje) — para no tener que rehacer las
migraciones en la Etapa 5. Presentar el esquema propuesto y esperar el OK antes de aplicarlo.

**Hecho:**

- **Decisión 018:** esquema de nueve tablas, no siete. Se agregan `sesiones` (agrupa videos del mismo
  atleta/gesto/encuadre/lado de cámara) y `reportes_sesion` (puntaje, componentes, observaciones agregadas);
  se modifican `usuarios` (`vista_por_defecto`) y `videos` (`sesion_id`, pierde `gesto`/`atleta_id`, gana
  rutas de miniatura y de los tres fotogramas clave). Tres puntos de diseño confirmados por Valentín, cada
  uno con su razón documentada en la decisión:
  1. `estado_agregado` de la sesión es una vista (`sesiones_resumen`), no una columna — evita un trigger de
     sincronización que el volumen actual no justifica.
  2. `alertas.severidad` usa los cuatro estados de R3 (`correcto`/`desvio_leve`/`alerta_de_carga`/
     `no_auditable`), no los tres que trae congelados `reporte.py` desde la Etapa 0. **Desalineación
     conocida entre la base y el contrato del motor, dejada a propósito**: Valentín pidió que sea
     explícitamente **lo primero que se resuelve al arrancar la Etapa 5**, antes de generar cualquier JSON
     real — no se toca `reporte.py` ahora.
  3. RLS completo en las nueve tablas ahora (no solo una de prueba, aunque el plan lo permitía diferir a la
     Etapa 7), con una prueba automática de aislamiento pedida por Valentín (verifica RNF-07: un usuario no
     lee/modifica/borra datos de otro, y un cliente sin sesión no lee nada).
  - Además, a pedido de Valentín: el puntaje total de `reportes_sesion` sale del jsonb y queda en columnas
    tipadas (`puntaje`, `estado_puntaje`, `version_formula`) — la pantalla de Evolución lo consulta a
    través de varias sesiones, y la versión de la fórmula es trazabilidad (R4). `componentes` y
    `observaciones` siguen en jsonb: su forma recién se congela en una decisión de la Etapa 5.
- **Migraciones escritas, no aplicadas todavía:** `supabase/migrations/20261001090000_esquema_inicial.sql`
  (extensión, nueve tablas, restricciones, índices, la vista `sesiones_resumen` con
  `security_invoker = true` — sin eso, una vista ignora la RLS de quien consulta) y
  `supabase/migrations/20261001090100_rls_policies.sql` (RLS + políticas + `GRANT` explícito a
  `authenticated` por tabla, nunca a `anon`). *(Corrección más abajo: lo que decía acá sobre
  `service_role` resultó estar mal — sí necesita su propio GRANT.)*
- **Prueba de aislamiento:** `tests/integration/test_rls_aislamiento.py`. Crea dos usuarios de prueba y datos
  de ejemplo del usuario A contra el proyecto Supabase real (vía `service_role`), verifica que el usuario B y
  un cliente sin sesión no pueden leer/modificar/borrar nada ajeno (incluida la vista `sesiones_resumen`, que
  es justo donde se notaría si `security_invoker` se hubiera olvidado), y limpia todo al terminar. Se salta
  sin `SUPABASE_URL`/`SUPABASE_ANON_KEY`/`SUPABASE_SERVICE_ROLE_KEY`. Agregado `supabase==2.31.0` a
  `backend/requirements.txt` (lo va a necesitar también el contenedor en la tarea 4.5.3) y helpers
  `get_supabase_*()` en `backend/app/config.py`, mismo patrón que `get_data_dir()`.
- **`backend/.env.example`:** se agrega `SUPABASE_ANON_KEY` (antes decía "no hace falta hasta la Etapa 6-8";
  hace falta ahora porque la prueba de aislamiento se autentica como los usuarios de prueba). No es secreta,
  pero sigue sin versionarse.
- **Render, plan gratuito — verificado contra la documentación oficial (no folletos), a pedido de Valentín:**
  misma RAM que Starter (512 MB), pero **0,1 vCPU contra 0,5 de Starter** (5 veces menos) y **el tipo de
  servicio "Background Worker" no existe en el plan gratuito** (solo Web Service, Postgres, Key Value,
  estático). Para probarlo gratis, el contenedor se va a tener que desplegar como Web Service (responde a
  HTTP), no como worker. Con la CPU 5 veces menor, es esperable que el mismo clip de la decisión 017 tarde
  bastante más que los 176–185 s medidos a 0,5 vCPU — posiblemente cerca o por encima de los 10 minutos que
  Valentín marcó como aceptable, pero **no se proyectó, queda para medir de verdad en la tarea 4.5.4**, con el
  mismo clip, cuando se despliegue. Fuentes: render.com/docs/free, render.com/docs/compute-plans,
  render.com/docs/background-workers.

**Tres ajustes de Valentín al esquema, mismo día, antes de aplicar nada** (migraciones editadas directamente,
no aplicadas todavía — no hay regla de "nunca editar" que violar):

1. **`estado_puntaje` reemplaza a `puntaje_auditable`.** Un booleano no distinguía "no auditable" de "Desde tu
   2.ª sesión de este golpe" (sin referencia previa), y la especificación de frontend §7 los muestra distinto.
   Ahora `estado_puntaje check in ('calculado', 'no_auditable', 'sin_referencia')`, `not null` sin default;
   `puntaje` no nulo solo si `estado_puntaje = 'calculado'`.
2. **Borrado en cascada: confirmado, no corregido.** Las FK ya estaban bien encadenadas desde
   `auth.users` hasta las siete tablas de datos de usuario; lo que faltaba era demostrarlo. Prueba nueva:
   `tests/integration/test_cascada_borrado_usuario.py`. Anotado lo que la cascada NO hace: no borra los
   archivos en Storage (son `storage.objects`, no filas de estas tablas) — pendiente de la Etapa 7.
3. **Trigger de alta de usuario.** `public.manejar_alta_usuario()` + trigger `al_registrarse` sobre
   `auth.users` (`after insert`): crea la fila de `usuarios` sola al registrarse, `rol` desde los metadatos
   del registro o `'jugador'` por defecto. Un rol inválido en los metadatos hace fallar el alta completa (la
   restricción CHECK corre en la misma transacción) — comportamiento buscado, no un bug. Prueba nueva:
   `tests/integration/test_trigger_alta_usuario.py`.

Con el trigger de alta, la prueba de aislamiento ya no inserta la fila de `usuarios` a mano: la crea el
trigger. Decisión 018 actualizada con los tres ajustes.

**Render:** confirmado por Valentín — se mide una sola vez en la tarea 4.5.4, con el mismo clip de la
decisión 017; si no entra en el plan gratis (10 minutos o suspensión que corta un análisis), se pasa directo
a Starter sin iterar buscando que entre gratis.

### Aplicación real contra Supabase (mismo día, más tarde) — falló una vez, dos hallazgos reales

Valentín aplicó las dos migraciones desde el editor SQL y agregó `SUPABASE_ANON_KEY`. Al instalar las
dependencias nuevas en el venv hizo falta subir `pydantic` de `2.10.3` a `2.11.7` (piso que exige
`realtime`, dependencia de `supabase==2.31.0`; no se tocó nada más, la suite completa se re-corrió para
confirmarlo — sigue en verde, 232 en verde).

**`pytest -m requiere_supabase` falló la primera vez**, con `permission denied for table usuarios` sobre
`service_role`. El comentario de `20261001090100_rls_policies.sql` ("service_role no necesita nada de
esto, ya tiene BYPASSRLS") estaba mal: `BYPASSRLS` exime de las políticas de fila, pero el `GRANT` de tabla
es una capa de permisos de Postgres **aparte**, y hace falta igual. Con "exponer automáticamente"
desactivado y las tablas creadas por SQL crudo (no desde el panel), Supabase no se lo dio solo a
`service_role` — **la misma razón por la que `authenticated` ya necesitaba `GRANT` explícito, aplicada
también al rol que no tiene RLS.** Corregido con una migración nueva (las dos primeras ya estaban
aplicadas, no se editan): `supabase/migrations/20261001090200_grants_service_role.sql`. Comentario de la
migración de RLS corregido a pedido de Valentín, para que la lección quede donde se vuelve a leer.

**Esa primera corrida fallida dejó 3 usuarios de Auth de prueba sin borrar** (`kinetiq-rls-a-*`,
`kinetiq-rls-b-*`, `kinetiq-cascada-*`) — confirmado con `auth.admin.list_users()`, a pedido explícito de
Valentín de verificar que las pruebas no dejaran cuentas sueltas. Causa: el `try/finally` que borra el
usuario de prueba envolvía solo una parte del cuerpo de la prueba; cuando el insert siguiente fallaba por
el permiso faltante, la excepción saltaba por encima del borrado sin ejecutarlo. Se borraron las 3 cuentas a
mano y se corrigió la causa en `test_rls_aislamiento.py` y `test_cascada_borrado_usuario.py`: el
`try/finally` ahora envuelve todo lo que pasa después de crear los usuarios de Auth, no solo la parte que se
esperaba que fallara (`test_trigger_alta_usuario.py` ya estaba bien escrito desde el principio). Con la
corrección: 28 pruebas en verde, `list_users()` en 0 antes y después — limpieza confirmada.

**Decisión 018 ampliada** con esta sección (la lección para tablas futuras: RLS y privilegios de tabla son
dos sistemas independientes, hay que otorgar los dos siempre).

### Pendiente

Captura del editor de tablas de Supabase con el esquema aplicado (pendiente del apartado 4.4.6; no bloquea
seguir). **Tarea 4.5.1 cerrada.**

### Siguiente paso concreto

Commit y push de todo lo de 4.5.1, y arrancar la tarea 4.5.2 (bucket de Storage).

---

## 2026-10-01 — Checkpoint de la Etapa 4.5 antes de limpiar contexto

**Rama:** `main`. Punto de situación exacto para retomar, sin trabajo nuevo esta entrada (pedido explícito
de Valentín: solo documentar y commitear).

### Qué está HECHO de la Etapa 4.5

- **Decisión 016 (tentativa):** el MVP parte de un video por golpe, hasta 50 MB; la pantalla de carga
  rechaza archivos más grandes pidiendo recortar. Subida por partes queda fuera del MVP. Protocolo de
  grabación actualizado. Se confirma o se revierte recién probando el flujo completo con clips reales — no
  antes.
- **Decisión 017:** proveedor y plan de contenedor del motor decididos con datos reales, no con folletos:
  **Render Starter, USD 7/mes** (512 MB, 0,5 vCPU) procesa un clip real de una repetición en 176–185 s sin
  caerse (426–427 MB de pico, 3 corridas). No se paga el plan de USD 25.
- **`model_complexity` queda en `2` hasta nuevo aviso** (instrucción explícita de Valentín, 1/10/2026). El
  hallazgo de que `complexity=1` corta tiempo y memoria a la mitad en el mismo plan de 7 dólares sigue
  anotado en la decisión 017 como candidato, **no aplicado**: cambiarlo exige repetir el Criterio 2
  (se midió con `complexity=2`) y eso no se hace por iniciativa propia.
- **Dockerfile + `app/medir_contenedor.py`** (`backend/`): corren el pipeline completo dentro de un
  contenedor Linux real y miden tiempo/RSS por etapa, con el modelo de MediaPipe precalentado en el build.
  Soportan `--model-complexity` y `--reducir-resolucion` para comparar, no para cambiar el default.
- **Docker Desktop**, que no arrancaba (bug del "Inference manager"/IA integrada con sockets huérfanos de un
  apagado anterior sucio), quedó resuelto: carpetas renombradas, `EnableDockerAI` desactivado. Documentado
  por si vuelve a pasar tras otro apagado sucio.
- **Supabase:** proyecto creado por Valentín (São Paulo, sin integración GitHub, Data API activa, "exponer
  tablas nuevas automáticamente" desactivado, RLS automático activado). `backend/.env.example` documenta
  `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`; `.env` sigue ignorado por git.
- **`docs/ux/`** agregado (especificación del frontend + maquetas: HTML y capturas de Biblioteca, Cargar,
  Evolución, Perfil, Procesando, Registro, Reporte en sus variantes). **Contenido de Valentín, commiteado sin
  que Claude lo modifique.**

### Qué FALTA de la Etapa 4.5 (en orden)

1. **4.5.1 — Migraciones SQL.** No empezadas. Esquema del apartado 4.4.6: siete tablas, restricciones,
   políticas RLS. Con "exponer automáticamente" desactivado en Supabase, cada tabla nueva va a necesitar
   `GRANT` explícitos además de sus políticas — tenerlo presente al escribirlas.
2. **4.5.2 — Bucket de Storage.** No empezado.
3. **4.5.3 — Completar el contenedor.** Hoy corre sobre un archivo montado a mano; falta que descargue el
   clip de Storage y escriba el resultado mínimo en la base (espera a 4.5.1 y 4.5.2).
4. **4.5.4 — Despliegue real en Render Starter.** Hoy la medición es con Docker local; falta desplegarlo de
   punta a punta contra el proyecto Supabase real.
5. Recién con eso cerrada, el criterio de aceptación completo de la Etapa 4.5 y pasar a la Etapa 5.

### Siguiente paso concreto

Retomar por la tarea 4.5.1 (migraciones SQL del esquema del apartado 4.4.6), con los `GRANT` explícitos que
pide la configuración de Supabase ya creada.

---

## 2026-09-29 (tarde) — Etapa 4.5 en marcha: medición real en contenedor, decisión 016 y 017

**Rama:** `main`. Continuación de la entrada de esta misma fecha (cierre de la Etapa 4).

**Correcciones a lo ya escrito hoy** (Valentín):
- La decisión 015 decía que el contrato necesitaba "un tercer estado" para "auditable pero no ordenable" —
  **mal formulado**. "No ordenable" **no es un quinto estado de R3** (que se queda en sus cuatro: correcto,
  desvío leve, alerta de carga, no auditable): es un **motivo** dentro de la observación de secuenciación,
  mostrado en gris con una explicación, igual que los demás motivos que ya usa el motor. Corregido en la
  decisión 015 y en la entrada anterior de esta bitácora.

**Decisión 016 (tentativa):** para el MVP, se sube un video por golpe, hasta 50 MB; la pantalla de carga
rechaza archivos más grandes pidiendo recortar. Subida por partes queda fuera del MVP. Se confirma o se
revierte probando el flujo completo (subida → procesamiento → reporte) con clips reales — no antes.
Protocolo de grabación actualizado (`docs/protocolo-grabacion.md`, §7) con la indicación de recortar a un
solo golpe.

**Docker Desktop no arrancaba** (bug conocido del "Inference manager" / IA integrada de Docker, sockets
huérfanos de un apagado anterior sucio en `%LOCALAPPDATA%\Docker\run\` y `%LOCALAPPDATA%\docker-secrets-engine\`).
Solucionado: se renombraron ambas carpetas para que Docker las recree limpias y se desactivó
`EnableDockerAI` en `settings-store.json` (la función de IA no la necesita este proyecto). Reproducible si
vuelve a pasar tras un apagado sucio.

**Medición real en contenedor** (`backend/Dockerfile`, `app/medir_contenedor.py`, resultados en
`docs/resultados/e4.5-contenedor-tiempo-memoria.json`, decisión **017**):
- **512 MB/0,5 vCPU (Render Starter, USD 7/mes) alcanza:** procesa un clip real de una repetición en
  176–185 s (3 corridas) sin caerse, 426–427 MB de pico. La lectura inicial de 516 MB sin restricciones
  (sesión de la mañana) era un artefacto de la descarga del modelo en caliente, no reproducible con el
  modelo precalentado en la imagen. **No se paga el plan de USD 25/mes.**
- **Hallazgo colateral, pendiente de decisión:** `model_complexity=1` en vez de `2` (el default del motor)
  corta el tiempo a la mitad (91 s) y la memoria ~100 MB, en el mismo plan de 7 dólares. **No se aplica
  ahora:** la cobertura (100 % en los tres niveles) no discrimina precisión en este clip fácil, y el
  Criterio 2 (decisión 015, "cumple") se midió con `complexity=2` — bajarlo necesitaría repetir esa
  medición. Reducir la resolución del fotograma no aportó nada más sobre `complexity=1`.

**Supabase:** proyecto creado por Valentín (región São Paulo, sin integración GitHub, Data API activada,
"exponer tablas nuevas automáticamente" desactivado, RLS automático activado). Variables nuevas documentadas
en `backend/.env.example` (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`); confirmado que `.env` sigue
ignorado por git. Con "exponer automáticamente" desactivado, cada tabla nueva va a necesitar `GRANT`
explícitos además de sus políticas RLS — anotado para cuando se escriban las migraciones (tarea 4.5.1, no
hecha todavía).

### Pendiente

- **Tarea 4.5.1** (migraciones SQL) y **4.5.2** (bucket de Storage): no empezadas.
- **Tarea 4.5.3:** falta que el contenedor descargue el clip desde Storage y escriba en la base (hoy usa un
  archivo montado localmente).
- **Tarea 4.5.4:** desplegar de verdad en Render Starter (hoy la medición es con Docker local).
- **Valentín:** decidir sobre `model_complexity` (decisión 017) cuando corresponda. El Criterio 2 ya se
  midió (goniometría manual completa, ver la entrada de esta misma fecha más abajo): no está pendiente.

---

## 2026-09-29 — Cierre de la Etapa 4 (decisión 015): sin repliegue, cinco salvedades

**Rama:** `etapa/4-cinematica` → merge a `main`, tag `v0.5.0-etapa4`, push. Con los tres criterios medidos
(Criterio 1: decisión 014; Criterio 3 redefinido con override: decisiones 012/014; Criterio 2: goniometría
manual ciega), Valentín decidió **sin repliegue de arquitectura**: se mantiene `pelvis → torso → brazo`
completo, con cinco salvedades documentadas en la **decisión 015**:

1. Tres cuartos: el par pelvis-torso solo es auditable en revés (6/6); en drive es 0/6 y en saque 9/18 —
   se reportan "no ordenables", no como fallo.
2. Perfil: saque y drive dan el orden repetible pero invertido (sin etiqueta correcto/incorrecto, falta
   fundamento bibliográfico); revés de perfil no llega al umbral de repetibilidad (4/6).
3. Brazo: a lo ya dicho en la decisión 011, se suma que las únicas 2 mediciones ciegas del codo dominante
   dieron 27,2° de error medio (11,9° y 42,5°) — causa no separada entre sistema, medición manual o
   escorzo; trabajo futuro.
4. **Drive de perfil** (no drive de tres cuartos — ver la corrección de atribución de esta misma fecha,
   más abajo): orden estable (Criterio 1, 6/6) pero magnitud e instante NO estables entre sesiones
   (Criterio 3, p = 0,044 y p = 0,050): grupo de menor confianza.
5. Criterio 2 del codo: cumple por la media (12,5°), pero el p95 (36,4°) supera la meta — se informan
   siempre juntos.

**Corrección (mismo día, Valentín):** "no ordenable" **no es un quinto estado** — R3 se queda en sus cuatro.
Es un motivo dentro de la observación de secuenciación, mostrado en gris (no auditable) con una explicación,
igual que los demás motivos que ya usa el motor. Lo que sí queda abierto para la Etapa 5 es distinto: cómo
representar un orden auditable Y ordenable (perfil invertido, salvedad 2) sin veredicto de correcto/incorrecto
por falta de referencia bibliográfica — ver decisión 015, corregida.

**Siguiente paso concreto:** Etapa 5 — Auditoría y reporte, sobre `main` desde la etiqueta `v0.5.0-etapa4`.

---

## 2026-09-26 — Medición formal: Criterio 1, Criterio 3 (métrica i) y paquete ciego del Criterio 2

**Rama:** `etapa/4-cinematica`. Motor `0.4.1`. Diseño y reglas: decisión **014**, vigente desde el commit de
congelamiento `cefadb6` (Criterio 3 con lectura calibrada: `c970bf6`). Cada resultado registra su commit y que
el árbol estaba limpio. **Sesión 2 = medición; sesión 1 = réplica exploratoria.** Resumen legible y reproducible:
`docs/resultados/criterio1-resumen.md` (`python -m app.resumen_criterio1`).

### Criterio 1 (τ = 1 fotograma, primaria; sesión 2)

Dos mediciones separadas (1 = repetibilidad del orden, regla del criterio; 1c = coincidencia con el orden esperado,
aparte y sin umbral). n = 6 por grupo salvo el saque de tres cuartos (18, tres tomas).

| Grupo (sesión 2) | Ordenables / n (1a) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | --- | --- | --- |
| drive · perfil (par) | 6/6 | 1,00 `tp` | 0,00 | **cumple** (repetible pero invertido) |
| saque · perfil (par) | 6/6 | 1,00 `tp` | 0,00 | **cumple** (repetible pero invertido) |
| revés · tres cuartos (par / cadena) | 6/6 | 0,83 `tp` / 0,83 `tpb` | 0,17 / 0,17 | **cumple** (orden invertido) |
| revés · perfil (par) | 4/6 | 0,75 `pt` | 0,75 | no cumple |
| saque · tres cuartos (par / cadena) | 9/18 y 9/18 | 1,00 `pt` / 0,89 `ptb` | 1,00 / 0,89 | no cumple (1a = 0,50) |
| drive · tres cuartos (par / cadena) | **0/6** | — | — | no cumple |

- **Sensibilidad (τ = 2 y 3, declarada de antemano):** solo cumplen el saque y el drive de perfil (par pelvis-torso);
  el revés de tres cuartos deja de cumplir (1a 0,33).
- **Réplica exploratoria (sesión 1, no independiente):** **ningún grupo cumple** con τ = 1 (1a entre 0,33 y 0,67).
  Donde el orden es ordenable, coincide con la sesión 2 (perfil: torso primero; tres cuartos: saque `pt`).
- **Complemento DESCRIPTIVO (no pre-registrado), sesión 2:** el eslabón que limita a la cadena es **pelvis-torso**,
  no el brazo. En tres cuartos |pelvis − torso| tiene mediana de 1,0–2,0 fotogramas (en el drive, los 6 picos caen
  a 0 o ±1 fotograma: no es un artefacto, todos son válidos y auditables), mientras que torso→brazo se separa
  22–28,5 fotogramas (≈ 92–119 ms) con el brazo después en 6/6, 6/6 y 16/17 (la sesión 1: 5/6, 6/6, 6/6).
- **Con n = 6 por grupo** el intervalo de Wilson de "6 de 6" es [0,61–1,00]: "cumple" no establece estadísticamente
  la meta de 0,8. Se informa en el JSON y en el resumen.
- **No se decide nada sobre el punto de decisión de la Etapa 4** (tabla del plan: Criterio 1 falla → replegarse a
  la fase de preparación). Lo que se observa es que, a 240 fps, **pelvis y torso en tres cuartos no se separan más
  de 1–2 fotogramas**, un límite de resolución; y que perfil los separa de forma repetible pero invertida.

### Criterio 3, métrica (i): separación cadera-hombro máxima (parcial)

Sesión 1 contra sesión 2, saque de tres cuartos solo con la toma `02` (pedido de Valentín). **5 de 6** combinaciones
con Δ ≤ σ_w (83 %, umbral 75 %); 5 de 6 sin evidencia de diferencia (p de permutación > 0,05). El grupo que no
cumple es el **drive de perfil**: Δ = 6,03° contra σ_w = 3,14° (medianas 30,65° y 24,62°; p = 0,044, **sin corrección
por 6 comparaciones**). El revés de tres cuartos queda al borde (p = 0,074) y es donde el encuadre difiere más
entre sesiones (torso en píxeles 17 %, por debajo del 20 % de señalamiento). **Falta la métrica (ii); no hay
veredicto del Criterio 3.** Corrección previa a medir: con n = 6 por sesión y ningún cambio real la regla
Δ ≤ σ_w da "consistente" solo 75,6 % de las veces (igual al umbral); por eso se agregó el p de permutación (014).

### Criterio 2: paquete ciego listo

`C:\Users\valen\kinetiq-data\fase-b\criterio2\`: 18 recortes sin esqueleto (`ciego/C2-01.png` … `C2-18.png`),
`planilla-manual.csv` (36 mediciones: rodilla y codo), `LEEME.md`; la clave está en `.clave-NO-ABRIR/` y **no se abre
hasta terminar**. Selección con semilla `26092026`, 3 fotogramas por estrato (gesto × encuadre), solo donde el sistema
reporta confianza ≥ 0,6; 5 fotogramas marcados para repetir la medición. Al completar la planilla:
`python -m app.criterio2 analizar <carpeta>`.

### Pendiente (al cierre de esta entrada)

- **Valentín:** goniometría manual del Criterio 2; y confirmar la **definición del "instante de pico"** del
  Criterio 3 (la propuesta es el instante del pico de torso desde el instante de máxima separación cadera-hombro;
  la métrica (ii) queda detrás de un flag y no se mide hasta entonces).
- Veredictos del Criterio 2 y del Criterio 3 completo; punto de decisión de la Etapa 4 (Valentín).

---

## 2026-09-29 — Criterio 3 completo (ambas métricas) y hallazgo de censura en la métrica (ii)

**Rama:** `etapa/4-cinematica`. Motor `0.4.1`, sin cambios de motor. Decisión 014 confirmada por Valentín
(instante de pico = desde la máxima separación cadera-hombro: "la única de las tres opciones que corresponde
a un evento medido, no a una decisión de diseño o de edición") y **queda vigente sin excepciones** desde el
commit `260d03c`. Resultado: `docs/resultados/criterio3.json` (reemplaza a `criterio3-parcial-metrica-i.json`,
que queda como registro histórico de la corrida parcial del 26/9 — mismos números en la métrica (i)).

**Resultado combinado (ambas métricas, 6 grupos × 2 = 12 combinaciones):**

- **Regla original (Δ ≤ σ_w): 10/12 = 83 %** (umbral 75 %).
- **Lectura calibrada (sin evidencia de diferencia, p de permutación > 0,05): 11/12 = 92 %.**
- **El único grupo con señal de diferencia real en las DOS métricas es drive · perfil:** separación
  cadera-hombro Δ = 6,03° (σ_w = 3,14°, p = 0,044) e instante de pico Δ = 156 ms (σ_w = 37 ms, p = 0,050),
  sin corrección por las 6 comparaciones. Sesión 1: mediana −166,7 ms (el pico de torso antecede a la máxima
  separación); sesión 2: mediana −10,4 ms (casi simultáneos).
  **CORRECCIÓN (29/9/2026, Valentín):** el párrafo original decía acá que este era "el mismo grupo que en el
  Criterio 1 tuvo 0 de 6 repeticiones ordenables" — **es un error**. El drive de perfil dio **6 de 6**
  ordenables en el Criterio 1 (cumple, orden `tp` invertido); el que dio 0 de 6 es el **drive de tres
  cuartos**, un grupo distinto. Son dos hallazgos separados, en dos grupos distintos: el drive de perfil
  tiene el orden estable pero la magnitud/instante inestables entre sesiones (este hallazgo, Criterio 3); el
  drive de tres cuartos no llega a ser ordenable en ninguna repetición (Criterio 1). No hay convergencia
  entre ambos criterios sobre un mismo grupo: cada uno señala un problema distinto en un grupo distinto.
- Revés de tres cuartos queda al borde en la métrica (i) (p = 0,074) y es donde el encuadre difiere más entre
  sesiones (torso en píxeles, 17 %, señalado pero bajo el 20 %).

**Hallazgo metodológico, encontrado ANTES de aceptar el resultado, no buscado a propósito:** la máxima
separación cadera-hombro se busca dentro de la misma ventana de ±300 ms de todo lo demás. Se agregó un
diagnóstico de censura (`max_sep_dist_borde_ms`, umbral `CERCA_DEL_BORDE_MS = 50`, commit `699778d`, antes de
volver a correr la medición) que muestra:

| grupo | en el borde exacto (de 12) | cerca del borde (< 50 ms) |
| --- | --- | --- |
| revés · perfil | **5** | **9** |
| revés · tres cuartos | 0 | 4 |
| resto (4 grupos) | 0 | 0–1 |

**La métrica (ii) del revés de perfil no es confiable:** en 9 de 12 repeticiones el "máximo" encontrado está
pegado al borde de la ventana, así que el verdadero instante de máxima separación probablemente cae fuera de
ella. Que ese grupo saliera "consistente" (Δ = 6,25 ms, p = 0,868) podía ser solo el artefacto de que las dos
sesiones chocan contra el mismo límite, no evidencia real de consistencia. **No se ensanchó la ventana**
(afectaría también la métrica (i), ya aceptada, y el Criterio 1, ya medido y commiteado): queda como
limitación a declarar en los Capítulos 6 y 7, no como corrección aplicada.

### Override aplicado y resultado final (mismo día, commit `6773ffd`)

Decisión de Valentín: revés de perfil, métrica (ii), se reporta **NO AUDITABLE** (motivo: censura de ventana),
no "consistente" — "reportar Δ=6,25ms/p=0,868 ahí sería presentar un artefacto de censura como dato bueno".
Override manual y puntual (`GRUPOS_NO_AUDITABLES` en `medicion_criterio3.py`), no una regla automática de
umbral; el cálculo bruto queda en el JSON (`bruto_censurado`) para trazabilidad y se excluye de las
combinaciones de cumplimiento. La métrica (i) de ese grupo no se tocó. Candidato de trabajo futuro (no
aplicado): ventana específica por gesto, pre-registrada antes de volver a medir.

**Resultado final del Criterio 3 (11 combinaciones evaluables, no 12):**

- **Regla original (Δ ≤ σ_w): 9/11 = 82 %** (antes 10/12 = 83 %; el grupo excluido contaba como consistente,
  así que numerador y denominador bajan juntos).
- **Lectura calibrada (p de permutación > 0,05): 10/11 = 91 %** (antes 11/12 = 92 %).
- Ambos siguen por encima del umbral de 75 %. El único grupo con señal de diferencia real en las dos métricas
  sigue siendo **drive de perfil**.

**Paquete ciego del Criterio 2 — confirmado sin cambios.** Valentín preguntó si la estratificación incluía
codo derecho (dominante) del revés de tres cuartos, el único caso de cobertura alta durante el golpe
(decisión 013). Se verificó contra los metadatos de la clave (solo `estrato`/`clip`/`lado`, sin abrir los
valores del sistema): **2 de los 3 fotogramas de ese estrato (`C2-10`, `C2-15`) ya usan el codo derecho** por
tener mayor confianza que el izquierdo. No hizo falta regenerar el paquete; Valentín puede medir sobre el que
ya tiene.

**Decisión 013 ampliada:** el revés de tres cuartos (brazo dominante cercano a la cámara, cobertura alta
incluso durante el golpe) se documenta como evidencia más fuerte a favor de la hipótesis geométrica sobre la
de desenfoque puro — sin ser concluyente con un solo jugador. Una sesión con encuadre invertido queda como
trabajo futuro candidato, explícitamente no programada ahora.

### Criterio 2 medido — cumple en agregado; el codo dominante (n=2) queda sin validar bien

Planilla completa (36 mediciones). `python -m app.criterio2 analizar` →
`docs/resultados/criterio2.json` (commit del paquete: `cefadb6`).

| articulación | n | media | mediana | p95 | sesgo | veredicto (< 20,6°) |
| --- | --- | --- | --- | --- | --- | --- |
| rodilla | 18 | 8,5° | 5,9° | 19,2° | −1,5° | **cumple** |
| codo | 18 | 12,5° | 10,5° | 36,4° | +2,1° | **cumple** |

Error intra-observador (5 fotogramas repetidos, 10 mediciones): 4,1°.

**Hallazgo al abrir la clave (Claude, no pedido por Valentín):** el codo agregado "cumple" está dominado por
16 mediciones del lado **no dominante** (media 10,7°). Las únicas **2 mediciones del codo dominante**
(las que decisión 013 identificó como el único caso de cobertura alta durante el golpe: `C2-10` y `C2-15`,
ambas revés · tres cuartos) dan **27,2° de media (11,9° y 42,5°)** — el 42,5° es el error máximo de todo el
conjunto. Valentín comentó en la planilla, sobre `C2-10`, dificultad para medir "por posición del brazo (otro
frame estaría mejor tal vez para codo derecho)", pese a calificar la imagen como nítida (calidad 1): apunta a
escorzo (el codo gira hacia/desde la cámara) más que a desenfoque. Dato adicional, no decisivo: el ángulo 3D
filtrado (secundario, no validado por esta vía) de `C2-10` está más cerca del valor manual (129,8° vs
manual 118,5°, diferencia 11,3°) que el 2D (160,9°, diferencia 42,5°), compatible con que el problema sea
específico de la proyección 2D en esa vista.

**Con n = 2 no se puede concluir nada formal**, pero es una alerta a tener presente: la confianza de MediaPipe
(0,81 y 0,89, ambas por encima del umbral 0,6) mide si el punto se detectó, no si el ángulo derivado es
preciso — "cobertura alta" (decisión 013) no implica "ángulo preciso". El único caso de validación directa
del brazo dominante salió mal en 1 de 2. No se tocó código ni se recalculó nada: se deja documentado tal cual
para que Valentín lo pondere en el punto de decisión.

### Pendiente

- **Valentín toma el punto de decisión de la Etapa 4** con los tres criterios ya medidos (resumen consolidado
  en la conversación de la sesión, no volcado aparte a un documento de decisión: es una decisión de Valentín,
  no de Claude).

---

## 2026-09-26 — Sesión 2 completa, Criterio 3 redefinido y diseño de la medición formal (propuesta)

**Rama:** `etapa/4-cinematica`. Motor `0.4.1` (sin cambios). Sesión 2 catalogada: 48 repeticiones
(saque: 6 de perfil y 18 de tres cuartos en tres tomas `02`/`02b`/`02c`; drive 12; revés 12), 240 fps;
catálogo de 110 clips sin errores.

**Decisiones de Valentín:**
1. **No se graba del lado derecho** (el piloto no se justifica). Razón dada: la evidencia sugiere que el
   límite es el desenfoque durante el golpe y no el lado de la cámara. *Nota de Claude:* la evidencia
   (en reposo el brazo se ve mejor en la sesión 2, la ventana del gesto no mejora) es compatible con
   desenfoque **o** autooclusión y no las separa; y "grabar del lado dominante mejora la cobertura" queda
   **sin probar, no refutada** (el revés de tres cuartos, con el brazo de cara a la cámara, sí se ve
   bien). Va a la decisión 013.
2. **Extraer las 35 poses restantes** de la sesión 2 (en curso al escribir esto) y **documentar la
   cobertura del brazo tal como está, como limitación física conocida** (decisión 013, a escribir con las
   cifras de la sesión 2 completa).
3. **Criterio 3 redefinido, sin esperar una semana** (decisión 012): mide la repetibilidad del método
   aplicado por el mismo jugador en dos sesiones distintas, con variación natural y sin intervención
   deliberada. **Demuestra consistencia del sistema entre tomas del mismo jugador; NO permite afirmar que
   detectaría un cambio real de técnica** (fuera de alcance con este diseño, sin importar los días entre
   sesiones). Consecuencias anotadas en la 012: no restablece el criterio original (la base clínica de
   "comparar consigo mismo" queda sin validación de sensibilidad); el encuadre no es idéntico entre
   sesiones; el espaciado se aparta del plan.

**Hecho:** pose extraída para los **110 clips** (110/110 cachés). Diagnóstico de oclusión con la sesión 2
completa (n = 18 perfil y 30 tres cuartos) y **decisión 013** con la cobertura del brazo dominante por
sesión, encuadre y gesto: cámara del lado no dominante (izquierdo cercano en 74 de 84 clips; saque 36/36 y
drive 24/24); codo dominante con cobertura 0,03–0,53 en la ventana del saque y el drive y 0,87–0,99 en el
revés; en la sesión 2 de tres cuartos el codo se ve bien en reposo (0,79–0,84) pero vuelve a caer en la
ventana (0,30–0,46). Causa (desenfoque o autooclusión) no separada.

**Herramientas:** `--sesion` en `explorar_fase_b` y en los diagnósticos por grupo (`corte-brazo`,
`ventana-brazo`, `fleisig-brazo`), para no mezclar sesiones.

**Sesión 2 = conjunto de medición reservado.** Una tanda automática llegó a ejecutar `explorar_fase_b` sobre
la sesión 2 **sin leer los resultados**; se detuvo el resto y se **descartaron** los archivos generados,
porque la propuesta 014 exige fijar las definiciones antes de mirar órdenes y tiempos de esa sesión. De la
sesión 2 solo se leyeron confianza y cobertura de pose. Se regenera tras confirmar la 014.

**Propuesta, NO vigente:** decisión 014, diseño de la medición formal de los Criterios 1, 2 y 3
(definiciones, umbrales y reglas de cumplimiento a fijar **antes** de mirar la sesión 2; la sesión 1 =
exploratoria, la sesión 2 = medición). Tiene cinco grupos de preguntas para Valentín. **El Criterio 2
requiere goniometría manual sobre fotogramas y no puede hacerla Claude.**

**Siguiente paso:** Valentín confirma o corrige la **decisión 014** (τ del Criterio 1 y reglas de
cumplimiento; qué sesión es la de medición; grupos del Criterio 1; Criterio 2: ángulos, cantidad de
fotogramas y quién mide; Criterio 3: métricas, regla y las tres tomas del saque de tres cuartos). Se
commitea la 014 como vigente (congelamiento, con el hash del motor `0.4.1`) y **recién entonces** se
corren `explorar_fase_b --sesion 2` y los diagnósticos sobre la sesión 2, y la medición formal. El
Criterio 2 espera además la goniometría manual de Valentín.

---

## 2026-09-25 — Diagnóstico de oclusión del lado dominante (sesiones 1 y 2 de la Fase B)

**Rama:** `etapa/4-cinematica`. Sin cambios en el motor. Pedido de Valentín: en ambas sesiones la cámara
quedó del mismo lado y es diestro; ¿oclusión sistemática del brazo dominante? Decidir si hace falta una
tercera sesión con la cámara del otro lado **antes** de extraer pose del resto y medir formalmente.

**Herramienta:** `python -m app.diagnosticos_e3 oclusion-lado` (`docs/resultados/pose-oclusion-lado-dominante.json`;
7 pruebas en `tests/unit/test_oclusion_lado.py`). Solo lee la caché de pose.
**Muestra:** sesión 1 completa (36 clips de perfil y tres cuartos a 240 fps) y de la sesión 2 **solo 13 de 48**
(2 por grupo y 1 por cada toma `02`/`02b`/`02c` del saque de tres cuartos); las otras 35 no tienen pose
(no se extrajeron a propósito). n de la sesión 2 = 6 (perfil) y 7 (tres cuartos).
**Método:** por clip y pareado, confianza media (`visibility`) y cobertura (fracción de fotogramas con
confianza ≥ 0,5, la definición del motor) de hombro, codo, muñeca y cadera del lado dominante (der) contra
el no dominante (izq), en tres tramos: **reposo** (a más de 0,6 s del pico crudo del torso: sin desenfoque
posible), **ventana del gesto** (± 0,3 s) y clip completo. Criterio declarado antes de mirar (juicio de
Claude, ajustable): mediana de Δcobertura ≤ −0,10, Δ < 0 en ≥ 75 % de los clips y p del signo < 0,05.

**Resultados:**
- **La cámara ve el lado izquierdo (no dominante):** es el más cercano en 43 de 49 clips; los 6 restantes son
  todos revés (1 de perfil, 5 de tres cuartos), o sea que ese "lado cercano" está **confundido con el gesto**
  (en el revés el giro del cuerpo expone el brazo derecho).
- **Hombro y cadera: 1,00 en ambos lados en todos los grupos y sesiones.** Ojo: `visibility` satura en 1,0
  para estos puntos; no prueba que estén bien ubicados (no descarta un error de profundidad de la cadera o
  el hombro lejanos en perfil).
- **Codo y muñeca dominantes en reposo (sin desenfoque):** perfil, codo 0,10 (s1) y 0,14 (s2) contra 0,99 del
  izquierdo, cobertura 0,02 y 0,05; muñeca 0,29 y 0,37 contra 0,97–0,98; Δ < 0 en el 100 % de los clips
  → **oclusión geométrica confirmada en perfil, en ambas sesiones** (p = 0,031 con n = 6, el mínimo posible).
  Tres cuartos sesión 1: codo 0,21 (cobertura 0,16), muñeca 0,61 → marcado. Tres cuartos sesión 2 (n = 7):
  codo 0,82, muñeca 0,95 → **no** marcado.
- **En la ventana del gesto** el codo dominante ronda 0,45–0,53 de confianza y 0,46–0,54 de cobertura en todos
  los grupos (no dominante 0,94–0,96 y 1,00); muñeca 0,71–0,81. Con mi criterio no se marca (Δ < 0 en 67–83 %
  de los clips, p 0,02–0,45, porque los revés dejan ver el brazo y diluyen el signo), pero el efecto es grande
  (Δ mediana de cobertura del codo −0,47 a −0,54).
- **Revés de tres cuartos:** brazo dominante bien visible (confianza 0,84–0,89, cobertura 0,97–1,00 en la
  ventana). Explica por qué fue el único grupo con la serie del brazo completa (y por eso ya estaba filtrado
  antes del arreglo de E3, decisión 010).
- **Sesión 2, saque y drive de tres cuartos:** en reposo se ve mucho mejor que en la sesión 1 (0,59–0,92 contra
  0,03–0,27), pero **la ventana del gesto no mejora** (0,27–0,58). Es decir: aun con el brazo visible en reposo,
  durante el golpe el codo se pierde (desenfoque o autooclusión), no solo por la posición de la cámara.

**Lectura (para decidir; no se decidió):** la oclusión geométrica del brazo dominante está confirmada en perfil
y en el saque/drive de tres cuartos de la sesión 1. Pero mover la cámara al lado dominante no garantiza
resolver la cobertura durante el golpe: la mejora de reposo de la sesión 2 no se trasladó a la ventana. El
único caso "brazo que golpea de cara a la cámara" es el revés de tres cuartos (cobertura ~1,0), que es un gesto
más lento que el saque. Recomendación de Claude: **piloto corto** (p. ej. 6 saques y 6 drives de tres cuartos con
la cámara del lado dominante) antes de una tercera sesión completa, comparando la cobertura en la ventana.
**No se extrajeron las otras 35 poses de la sesión 2** a la espera de esa decisión.

**A tener presente:** las dos sesiones son de fechas consecutivas (24 y 25/9), y el plan pide al menos una
semana entre sesiones para el Criterio 3.

---

## 2026-09-25 — Fase B: extracción de pose, ventana anclada y corrección de E3 (motor 0.4.1)

Sesión larga: primera pasada de la Fase B, corrección de E3, y tres correcciones de rumbo de lo
que se había concluido (ver "CORRECCIÓN" y las decisiones 010 y 011).

### Estado al cierre de la sesión

**Rama/motor/tests:** `etapa/4-cinematica`, motor `0.4.1`, `pytest -m "not slow"` → **194 en verde**
(los 5 tests lentos que usan E3 sobre pose real también pasan). Sin merge ni tag de la Etapa 4.

**Decisiones de Valentín en esta sesión:**
1. `recortes/` es la única carpeta de unidades de análisis de la Fase B; el catalogador,
   `extraer_pose` y `analizar` recorren `fase-a/` y `fase-b/` y saltean `originales/`.
2. Arreglo de E3 (series con huecos, decisión 010, motor 0.4.1); se mantiene **un corte de Winter
   por clip** (sin cambio de contrato).
3. Codo vs muñeca: la decisión anatómica se mantiene; la justificación empírica de la 008 queda
   invalidada y es **pendiente de redacción del Capítulo 4**.
4. Referencia de Fleisig del brazo: error conceptual (decisión 011). El techo del brazo no se
   reancló a 1510 °/s; queda 7104 °/s como cota provisional sin respaldo en la literatura.
5. **El orden del brazo en perfil se declara NO CONCLUYENTE; las afirmaciones que dependen del
   brazo se apoyan en tres cuartos.** No se implementó ventana acotada del brazo.
6. El marcador de fase independiente queda como **trabajo futuro** (no implementar ahora).

**Lo medido (E3 0.4.1; 36 repeticiones propias, un jugador, una sesión):**
- Pelvis y torso no se vieron afectados por el defecto de E3 (diferencia 0,0000 °/s); pelvis más
  rápida que el torso en el saque (1,15–1,46×); gradiente saque > drive > revés en ambos encuadres.
- Brazo (orientación del segmento, p99 de ω a k=1): 790–2165 °/s por grupo, caída k1→k8 de 1–10 %.
  No hay referencia de Fleisig equivalente (decisión 011).
- **Por encuadre** (ancla de torso): **torso → balanceo del brazo** con el brazo después en **17 de 18**
  en tres cuartos (estable con el corte entre 6 y 15 Hz —a 20 Hz, 16 de 18— y con la ventana) y en **5 de 16** en perfil (no
  concluyente). **Pelvis vs torso:** perfil con el torso primero en 11 de 15 (saque 3/3, drive 6/6);
  tres cuartos 9 pelvis primero / 7 torso primero, |Δ| ≤ 3 fotogramas en 16 de 18.

**Lo que NO queda establecido:**
- **La cadena completa `pelvis → torso → brazo` no queda establecida en ningún encuadre**; tres
  cuartos sostiene su segunda mitad (torso→brazo). Perfil no sostiene pelvis→torso (lo invierte
  sistemáticamente), contra la formulación inicial; corregido en la decisión 011.
- Etiquetar "correcto/incorrecto" cuando interviene el brazo no tiene fuente (R4).
- Criterio 1 no medido formalmente; exploratoriamente, solo el saque de tres cuartos repite un mismo
  orden completo en 5 de 6.

**Pendientes (todos requieren decisión de Valentín salvo indicación):**
- Redacción: Cap. 3 (tabla 3.3.2.8 y cadena cinética), Cap. 4 (hipótesis I1, Criterio 1, gráfico de
  secuenciación; justificación de hombro→codo), CLAUDE.md §1 y §3, interfaz (R2/R3), y la
  terminología "balanceo del brazo" vs "rotación interna" (lista completa en la decisión 011).
- Propuesta: mapear el orden del brazo en perfil al estado gris "no auditable" (R3), y el orden que
  incluye al brazo como "orden observado" sin juicio de correcto/incorrecto. No implementado.
- Protocolo: recomendar tres cuartos para todo lo que involucre al brazo.
- Umbral de salto imposible en unidades físicas (punto 2); opcional: Winter sobre el tramo continuo
  más largo. Ambos con datos de ajuste y de medición separados.
- 4.7 / 4.8 y el punto de decisión de la Etapa 4; segunda sesión de la Fase B (Criterio 3).
- **Trabajo futuro (NO implementar ahora):** marcador de fase independiente (p. ej. punto más bajo
  de la muñeca como inicio del golpe hacia adelante), validado con fotogramas; depende de la
  cobertura de la muñeca (25–57 % en el saque; baja justo en el impacto).

**Siguiente paso concreto — ETAPA 4 EN PAUSA (indicación de Valentín, 25/9):** no se toca más código
de la Etapa 4 ni se decide nada sobre el **Criterio 1** ni el **punto de decisión** hasta que Valentín
vuelva con material nuevo: la **segunda sesión de la Fase B** (necesaria para el Criterio 3) y más
repeticiones de **tres cuartos**, el encuadre con la señal más clara. Al volver: catalogar
(`python -m app.catalogador`), extraer pose, correr `python -m app.explorar_fase_b` y
`python -m app.diagnosticos_e3` sobre lo nuevo, y recién entonces la medición formal (4.7 / 4.8) con
umbrales congelados y datos de ajuste separados de los de medición. La decisión 011 se deja como está.
Hallazgo a retomar: la inversión sistemática pelvis/torso en perfil (torso primero en 11 de 15).

### Referencia de Fleisig del brazo (2026-09-25, decisión 011)

- Prueba `test_omega_vector_vs_angulo.py` (geometrías de resultado conocido): el vector hombro→codo
  mide el balanceo del brazo (ω real), da **0** ante extensión de codo y **0** ante rotación axial;
  el ángulo de tres puntos ve la extensión y también da 0 ante rotación axial.
- Comparación equivalente (`diagnosticos_e3 fleisig-brazo`, saque, E3 0.4.1): ángulo del codo vs
  1510 °/s = **0,88×** en perfil y **0,50×** en tres cuartos, con baja cobertura (25–57 % de
  fotogramas con los tres puntos). ω del vector = 1315/1379 °/s: 0,56–0,58× de 2368 (referencia
  equivocada) y 0,87–0,91× de 1510 (coincidencia numérica, no comparación equivalente).
- La "subestimación" que veníamos arrastrando desaparece **como argumento** (no había comparación
  válida), y NO se reemplaza por "medido correctamente": no hay referencia equivalente.
- **Techo del brazo:** sin cambios numéricos (7104 °/s), ahora rotulado como cota provisional sin
  respaldo en la literatura. Reanclarlo a 1510 (×3 = 4530) da el mismo resultado práctico en la
  Fase B pero repetiría el error con otro valor; **pendiente de decisión de Valentín**.

**Alcance ampliado (decisión 011):** el "brazo" de `pelvis → torso → brazo` es un proxy de la
**orientación espacial del segmento superior** (balanceo del brazo), no de la rotación interna del
hombro que describe la literatura. Son dos eventos distintos que pueden no coincidir en el tiempo.
Se sostiene "el sistema documenta el orden de los picos de pelvis, torso y balanceo del brazo" y el
Criterio 1 (repetibilidad); NO se sostiene "el orden descripto en la literatura" ni etiquetar
correcto/incorrecto cuando interviene el brazo (R4: sin fuente). Pendiente de decisión y de
redacción: CLAUDE.md §1 y §3, Cap. 3 (3.3.2.8 y cadena cinética), Cap. 4 (I1, Criterio 1, gráfico de
secuenciación), arquitectura, plan (Anexo A), interfaz. Lista completa en la decisión 011.

### Ventana del brazo: barrido del adelanto (2026-09-25) — NO se implementó en el motor

`python -m app.diagnosticos_e3 ventana-brazo` (`docs/resultados/e3-ventana-brazo-fase-b.json`).
Se permite buscar el pico del brazo desde `torso − adelanto` hasta `torso + 300 ms` (adelanto 300,
200, 150, 100, 50, 0 ms) y se mide cuántos picos CAMBIAN respecto de la ventana de ±300 (lo que la
acotación enmascara). Con adelanto 0, "brazo antes que torso" es imposible por construcción.

- **Tres cuartos (saque, drive y revés): la ventana es irrelevante.** El pico del brazo no cambia
  al acotar (0 desplazados de 6 en casi todos los adelantos), y llega después del torso: +110 ms
  (saque), +115–121 (drive), +79 (revés) de mediana.
- **Drive de perfil:** brazo antes del torso en 4/5 con adelanto ≥ 150 ms (mediana −50 ms) y 3/4 a
  100 ms; con adelanto ≤ 50 ms el brazo queda **no auditable** en 5 de 6 (1/6 auditable): no hay un
  pico posterior identificable. Es decir, acotar no "arregla" el drive, lo vuelve no medible. Los
  picos se ubican 50–100 ms antes del torso.
- **Revés de perfil:** con ±300 el brazo va primero en 5/6 (mediana −19 ms), pero 2 de esos picos
  están 200–300 ms antes del torso; con adelanto ≤ 200 la mediana pasa a 0 ms (3/6 antes, los tres con
  −12 a −21 ms, prácticamente simultáneos) y con adelanto 0 los 4 auditables pasan a +165 ms
  (4/4 desplazados). Coherente con que esos 2 picos tempranos sean la preparación.
- **Saque de perfil:** 2/5 con el brazo antes (≥ 100 ms antes); con adelanto ≤ 50 esos 2 se
  desplazan a picos posteriores (dt +67). Confirma la fragilidad de ese grupo (n = 3–5).

**Lectura:** el patrón "brazo antes en perfil, después en tres cuartos" se sostiene con claridad
solo en el **drive de perfil** (y en los tres grupos de tres cuartos como "después"); en el revés
de perfil el brazo es casi simultáneo con el torso salvo dos picos de preparación; el saque de
perfil depende de la ventana. **Ninguna ventana por sí sola discrimina golpe de preparación:**
haría falta un marcador de fase independiente (p. ej. el punto más bajo de la muñeca como inicio del
golpe hacia adelante), validado con fotogramas. Pendiente de decisión de Valentín.

### Corte de Winter para el brazo (2026-09-25)

Pregunta de Valentín: ¿un solo corte por clip sigue siendo válido para el brazo? **No se tocó
código ni contrato** (`trazabilidad.filtro.corte_hz`). Datos: `docs/resultados/e3-corte-brazo-fase-b.json`,
`python -m app.diagnosticos_e3 corte-brazo`.

- **El corte del clip ya lo fija el brazo:** `elegir_corte` toma el MÁXIMO entre los cortes de las
  series de codo y muñeca (ambos lados). No sale de pelvis/torso.
- **Los cortes por articulación son parecidos:** codo 4–11 Hz (casi todos 7–9), muñeca 7–9,
  pelvis 5–9, torso 6–9; el corte del clip es 8–11 (mayoría 8–9). Diferencia por articulación
  ≲ 2 Hz: **no hay evidencia de que el brazo necesite un corte propio.**
- **No es el corte lo que hace ver "bajo" al brazo:** barriendo solo el corte del codo, el p99
  varía entre −2 % y +28 % entre 6 y 10 Hz (más al ir a 20 Hz), y a la vez la caída k1→k8 crece (p. ej. drive
  tres cuartos 10 % → 28 %, revés perfil 4 % → 25 %): más corte mete ruido, no revela movimiento.
- **Debilidades reales de la implementación (no del criterio "un corte por clip"):**
  (a) Winter concatena los valores válidos saltando los huecos: las uniones son discontinuidades;
  usando el tramo continuo más largo el corte del clip cambia en 19 de 36 clips (de −1 a +3 Hz,
  mediana 0, media +0,4);
  (b) el corte de una serie individual es inestable (codo 4 Hz en un clip); el máximo entre ~12
  series lo vuelve conservador; (c) el corte tiene efecto sobre el orden del saque de perfil
  (arriba): conviene registrar la sensibilidad en la trazabilidad.
- Recomendación: **mantener un corte por clip y el contrato**; si se quiere tocar algo, arreglar
  (a) sin cambiar el contrato. No hecho: espera la decisión de Valentín.

### Qué se hizo

- `extraer_pose` y `analizar` recorren `fase-a/` y `fase-b/` (mismas `CARPETAS_EXCLUIDAS` y
  `FASES_POR_DEFECTO` que el catalogador) y saltean `originales/`.
- `analizar` deducía `corpus_publico=True` siempre; ahora sale de la columna `fuente` del
  catálogo (`propio` → sin caveat; sin dato → caveat, el error seguro).
- Extracción de pose de fase-b (~2 min por clip, CPU).

### Primera lectura: saque de perfil (6 repeticiones, 240 fps reales)

Cualitativa, sin umbrales tocados. Ver la tabla completa en la conversación de la sesión.

- **Pelvis-torso:** las 3 repeticiones auditables dan `torso → pelvis` (4, 12 y 13 ms):
  mismo rango invertido que el corpus público. No se estabilizó con condiciones controladas.
- **Brazo (codo):** 4 de 6 bajo el techo (4000–6100 °/s, 1,7–2,6× Fleisig); una en 37 124.
- **Inversiones de z:** 8–28 por clip (público: 16–45 / 3): **no bajaron** con `z` métrica.
- **Pelvis 1000–1400 °/s (2,3–3,2× Fleisig 440)** y ~1,4× más rápida que el torso
  (Fleisig: al revés). Revisado el cálculo: **no hay error** (fórmula y `fps_efectivos`
  correctos; el pico casi no cambia con el paso k=1,2,4,8; ~todo en el plano x–z; curva de
  ángulo suave; caderas bien ubicadas en los fotogramas). No se puede distinguir "gira así"
  de "cadera lejana mal estimada por la oclusión del perfil" sin una medición independiente.

### Comparación entre gestos y encuadres (36 repeticiones, 1 jugador, 1 sesión)

Medianas por grupo (pico p99 de ω sobre el clip completo, `puntos_mundo` filtrados, °/s;
6 clips por grupo; **exploratorio**, umbrales sin tocar). Referencia de Fleisig: **solo saque**.

| grupo | pelvis | torso | pelvis/torso | caída pelvis k=1→8 | inv. z por clip (mediana) | orden pelvis-torso |
| --- | --- | --- | --- | --- | --- | --- |
| saque perfil | 1174 | 791 | 1,46 | 4 % | 14,5 | 3 auditables: 3 invertidas (−4/−12/−13 ms) |
| saque tres cuartos | 975 | 837 | 1,15 | 4 % | 5 | 6 auditables: 4 pelvis primero (0–13 ms), 1 empate 0 ms, 1 invertida (−13 ms) |
| drive perfil | 702 | 628 | 1,12 | 3 % | 9,5 | — |
| drive tres cuartos | 814 | 680 | 1,19 | 3 % | 7,5 | — |
| revés perfil | 324 | 435 | 0,72 | 3 % | 5,5 | — |
| revés tres cuartos | 257 | 507 | 0,46 | 3 % | 5 | — |

- **Sensibilidad al paso (pregunta 3):** la pelvis cae 3–4 % entre k=1 y k=8 en los seis
  grupos: no es un artefacto del saque; es una señal suave en todos los gestos.
- **Hipótesis del salto: resultado mixto, no confirmada.** El revés (sin vuelo) no muestra
  exceso (pelvis 257–324 °/s, pelvis/torso < 1, como en Fleisig). El drive (sin vuelo)
  mantiene pelvis ≥ torso y 700–800 °/s. El orden de gestos saque > drive > revés se repite
  en ambos encuadres; el encuadre mueve la magnitud (±20 %) sin cambiar ese orden.
- **Tres cuartos vs perfil (saque):** mejora el orden auditable (6/6 vs 3/6) y baja las
  inversiones de z (5 vs 14,5). Pero de los 5 "pelvis primero/empate", 3 quedan a ≤ 1
  fotograma (4,17 ms): en el límite de resolución.
- **Segmentación automática:** parte en 2–3 ventanas clips que contienen 1 repetición
  (revés perfil rep02, revés tres cuartos rep04/rep05, etc.). Para el Criterio 1 la unidad
  debe ser el clip (1 repetición), no las ventanas.
- **Drive:** varios clips dan el orden `brazo > torso > pelvis` (invertido); no reproduce la
  cadena que sí dio `drive_lateral_01` del corpus público. Sin analizar aún.
- **Revés tres cuartos, brazo:** ω ~850–980 °/s y casi constante con k (2 % de caída), muy
  distinto del resto (2000–5000 °/s, ~65–80 % de caída). Sospechoso; sin analizar aún.
- Límites: n = 6 por grupo, un jugador, una sesión; detector de vuelo aproximado (tobillos
  en imagen); p99 sobre el clip completo, no sobre la ventana del gesto.

### Segmentación: `clip completo` vs `auto` (2026-09-25, mismo día)

Hipótesis de Valentín: la segmentación automática elegía ventanas parciales y era la causa
común del drive invertido y del brazo anómalo del revés de tres cuartos. Se agregó el modo
explícito **`clip_completo`** (`segmentar`/`secuenciar`, `analizar --clip-completo`; excluyente
con `manual`) y se comparó con el automático (`docs/resultados/e4-fase-b-exploratorio-*.json`).

- **No era la causa.** Drive perfil: el pico del brazo cae 200–500 ms **antes** que los de
  torso y pelvis en las 4 repeticiones auditables, con ventana automática y con clip completo.
  Revés tres cuartos, brazo: los picos son los mismos valores (1001,7 / 917,6 / 855,0 /
  803,7 °/s) en ambos modos; solo cambia el instante (relativo a la ventana).
- **El clip completo tampoco es neutro:** el pico de cada segmento es el máximo global del
  clip y puede ser otro evento. Saque de perfil: brazo primero en 2 de 3 auditables (0 con
  auto); saque tres cuartos: pelvis→torso→brazo correcto 5 → 4 de 6; drive perfil 1 → 0; en el
  revés aparecen desfases pelvis→torso de −842, −142 y +208 ms (picos de eventos distintos).
- **Sí resuelve** el sobre-particionado (7, 7, 8 y 12 ventanas → 6 por grupo): para el
  Criterio 1 la unidad es el clip.
- Conclusión: las dos anomalías siguen abiertas y no son de ventana. La medición del orden
  es sensible a la ventana en ambos sentidos; falta una ventana anclada al gesto (p. ej.
  alrededor del pico de pelvis/torso, o marcas manuales).

### Ventana anclada al gesto (2026-09-25)

Se implementó `secuenciar(..., ancla="torso"|"pelvis", margen_ancla_s=0.3)` (`instante_ancla`,
`ventana_anclada`; `analizar --ancla`; excluyente con `manual` y `clip_completo`): UNA
repetición por clip, ventana centrada en el pico global del segmento ancla ± 300 ms. Si el
ancla no es auditable (tramo excluido o techo de plausibilidad) no se inventa una ventana
(R3). Salidas en `docs/resultados/e4-fase-b-exploratorio-ancla-{torso,pelvis}.json`.

**Sesgo a tener presente:** restringir la búsqueda a la vecindad del tronco excluye por
construcción los picos tempranos del brazo. Por eso cada repetición registra
`brazo_global_fuera_de_ventana`. Y anclar en un segmento no vuelve circular el orden
pelvis→torso solo si se compara contra el otro segmento (el ancla queda en el centro).

- **Las dos anclas coinciden:** torso vs pelvis difieren ≤ 75 ms en 30 de los 33 clips con
  ambas auditables (mediana 8–21 ms por grupo). Excepciones: 142 y 208 ms (revés perfil) y
  842 ms (revés tres cuartos rep05). En saque de perfil solo 3 de 6 clips tienen ambas auditables.
- **Saque tres cuartos (ancla torso):** el brazo llega DESPUÉS del torso en 6/6 (+12 a
  +138 ms) y pelvis→torso→brazo sale en 5/6 (igual que `auto`).
- **Drive de perfil: la inversión PERSISTE.** En las 4 repeticiones con brazo auditable el
  pico del brazo llega 133–288 ms ANTES del torso, con la ventana anclada y con las dos anclas.
  En rep03 y rep06 el máximo dentro de la ventana queda a ≤ 21 ms del borde: el pico real
  está aún más atrás. (Drive tres cuartos: brazo después del torso en 2/2 auditables.)
- **Revés tres cuartos, brazo: la anomalía PERSISTE.** Los picos son idénticos a los del clip
  completo (0 fuera de ventana): 4 de 6 en 800–1000 °/s, casi constantes con k; los otros 2 en
  2590–2830. El brazo queda último en 5/6: lo anómalo es la magnitud, no el orden.
- Criterio de Valentín cumplido: ambas anomalías persisten con la ventana bien anclada, así
  que se tratan como hallazgos a investigar, no como artefactos de ventana.

### CORRECCIÓN (2026-09-25, misma sesión): las "anomalías del brazo" vienen de E3 y de la validación

La serie fotograma a fotograma del codo (drive perfil rep04) y una revisión de `procesar_e3`
**invalidan la lectura anterior** ("ambas anomalías persisten → hallazgos"). Lo que se vio:

- **No es un salto de un fotograma.** Entre 0,196 y 0,242 s (fotogramas 47–58) el codo derecho
  se mueve 5,0 cm/fotograma (mediana; máx. 11,9 cm = 28 m/s), con confianza 0,65–0,98 y `z`
  alternando (0,168 → 0,225 → 0,172). Es una ráfaga de jitter, no un salto ni una inversión.
- **Por qué la validación no lo atrapó:** (1) la confianza está por encima de 0,5; (2) el
  umbral de salto imposible es 0,5 torsos = 25,7 cm/fotograma = **62 m/s** (torso 0,514 m): el
  máximo de todo el clip es 24,4 cm (0,47 torsos) y el de la ráfaga 11,9 cm (0,23); un codo
  real no supera ~10 m/s (≈ 4 cm/fotograma) y 79 de 299 fotogramas válidos lo superan;
  (3) no hay cambio de signo de `z`. El umbral detecta teletransportes, no jitter.
- **Hueco en E3 (`pipeline.py`, "Simplificación"):** toda serie con algún NaN (tramo largo
  excluido, > 5 fotogramas) **se deja SIN filtrar completa**. En rep04 el codo tiene 223 de 368
  fotogramas en NaN (60 %). Resultado: el codo crudo (ruidoso) entra a E4 contra un hombro ya
  filtrado. Sobre las 36 repeticiones: **pelvis 0 % y torso 0 % sin filtrar; hombro/codo
  derecho sin filtrar en 6/6 clips de cinco grupos** y en 2/6 del revés de tres cuartos.
- **Lo que explica todo:** en el revés de tres cuartos, los 4 clips donde el brazo SÍ se filtra
  dan 800–1000 °/s, planos con k (2 % de caída); los 2 sin filtrar dan 2590–2830 °/s y caen
  ~58 %, igual que el resto de los grupos (58–81 %). La "anomalía" era el único grupo bien
  filtrado; lo anómalo son los demás.
- Diagnóstico (interpolando y filtrando el codo a 8 Hz, solo para mirar): en los fotogramas
  47–58 la ω pasa de 4790 a 386 °/s. La cifra de todo el clip de ese diagnóstico NO es válida
  (interpolé 223 fotogramas de hueco) y 8 Hz podría ser bajo para el brazo.

**Consecuencias:**
- Todas las velocidades del **brazo** reportadas hasta acá (incl. "1,7–2,6× Fleisig", los picos
  de 4000–6100 °/s, el orden `brazo > torso > pelvis` del drive) están contaminadas por codo
  sin filtrar: **no son evidencia**. (Ver la re-medición de abajo: las MAGNITUDES eran ruido;
  el ORDEN del drive de perfil persiste aunque con un adelanto mucho menor. Esta frase decía
  antes "el drive invertido NO es un hallazgo fisiológico": era demasiado fuerte.)
- Pelvis y torso NO están afectados por este hueco: las conclusiones sobre ellos se mantienen.
- La ventana acotada del brazo sigue siendo razonable, pero es secundaria: primero E3 y el
  umbral de salto.

**Candidatos (NO aplicados; tocan E3 y validación, y cambian todo lo medido del brazo):**
1. E3: filtrar los segmentos continuos válidos de una serie con NaN en vez de dejarla cruda.
2. Umbral de salto imposible en unidades físicas (cm/fotograma o m/s) y calibrado, no 0,5
   torsos; evaluarlo separando datos de ajuste y de medición.
3. Chequeo de consistencia entre pasos k (ver "pico sostenido"), con su límite para el brazo.
4. Revisar el corte de Winter único por clip (8–9 Hz) para el brazo.

Los diagnósticos que se hicieron primero en un scratchpad (serie del codo, conteo de series sin
filtrar, comparación por grupo, salto por fotograma, montaje de fotogramas, ángulo en el plano)
quedaron **versionados** en `backend/app/diagnosticos_e3.py` (principio 5).

### Re-medición con E3 corregido (motor 0.4.1) sobre los 36 clips — validada por Valentín (25/9)

**Estado:** Valentín validó esta re-medición el 25/9 (la conclusión previa sobre el drive y el
revés de tres cuartos quedó reemplazada por ésta). Punto 1 de E3 hecho (decisión 010, `dsp.py`,
`pipeline.py`, pruebas `test_dsp_segmentos.py` y `test_pipeline_e3_huecos.py`, que fallan con el
E3 anterior). Los puntos 2 (umbral de salto) y 3 (corte de Winter) NO se tocaron.
Datos: `docs/resultados/e4-fase-b-exploratorio-<modo>-e3-0.4.1.json` (0.4.0: sin sufijo).

- **Regresión:** pelvis y torso idénticos entre 0.4.0 y 0.4.1 (diferencia máxima 0,0000 °/s).
- **Brazo, p99 de ω a k=1 (mediana por grupo, viejo → nuevo, °/s):** saque perfil 4847 → 1300;
  saque tres cuartos 3771 → 1371; drive perfil 3857 → 790; drive tres cuartos 6600 → 2165; revés
  perfil 5226 → 953; revés tres cuartos 940 → 908 (ya estaba filtrado). Caída k=1→8: 63–81 % →
  1–10 %. **La "anomalía" del revés de tres cuartos desaparece**: era el único grupo bien filtrado.
- **Drive de perfil: la inversión persiste, más chica.** Brazo antes del torso en 4 de 5
  repeticiones con ancla de torso, pero con un adelanto de 38–92 ms (antes 133–288 ms) y
  velocidades de 380–676 °/s (antes 2594–4546). Con el fotograma: el pico cae en la caída de la
  raqueta, justo antes del golpe hacia adelante. Drive tres cuartos: brazo después del torso en
  5 de 6 (96–146 ms).
- **Revés de perfil: aparece brazo primero en 5 de 6** (−12 a −233 ms; antes 0, porque casi
  no era auditable). Saque perfil: brazo después del torso en 3/3 auditables (+62 a +79 ms) con
  1072–1356 °/s. Saque tres cuartos: pelvis>torso>brazo en 5/6, sin cambios.
- Patrón: con el brazo bien filtrado, **en perfil el pico del brazo (hombro→codo) tiende a llegar
  ANTES que el del torso en drive y revés; en tres cuartos y en el saque, después.** Candidata
  a explicación (no probada): el pico global del brazo captura la caída de la raqueta y no el
  golpe (ventana de búsqueda del brazo); alternativa: el ángulo de perfil.
- **Cuidado con las magnitudes:** con el corte de Winter por clip de 8–9 Hz el brazo probablemente
  está subestimado (el saque queda en ~0,55× Fleisig). Es el punto 3.

**Revisión retroactiva del corpus público** (`diagnosticos_e3 comparar-brazo`; A = E3 viejo sin
detector de z = estado de la decisión 008):
- En A, el codo "plausible" era el que SÍ se había filtrado y la muñeca "implausible" la que
  quedaba cruda: `zverev_saque_lateral_01` (codo filtrado 2126 vs muñeca cruda 10 076),
  `drive_lateral_01` (1567 vs 10 322). En `zverev_saque_lateral_03` ambas estaban filtradas y daban
  lo mismo (1821 vs 1756). En `_02` ambas crudas (16 283 vs 26 063). La preferencia por el codo
  estaba **confundida con qué serie se filtraba**.
- Con E3 nuevo (C): muñeca/codo = 0,95–2,0 (mediana 1,39, n = 13), no 10–40; cobertura igual
  (codo 0,83, muñeca 0,84). La decisión codo-vs-muñeca **no se revoca aquí**, pero su
  justificación original ("la muñeca da 15 000–42 000 °/s") no se sostiene: hay que decidirla de
  nuevo con datos limpios (anatomía: el codo es el eslabón del "brazo" de la cadena; desenfoque de
  la muñeca en el impacto sigue siendo un argumento).
- **Techo ×3 (Fleisig × 3 = 7104 °/s):** el codo filtrado del corpus público está en 0,40–0,94×
  Fleisig (946–2234 °/s). Su justificación de "ruido de MediaPipe" ya no aplica (el ruido era el
  hueco). Ojo: en el corpus público la escala temporal es estimada, así que estos múltiplos son
  aproximados. No se recalibra todavía.

### Hipótesis a contrastar (Valentín, 2026-09-25)

El saque tiene fase aérea y drive/revés no. **Si la pelvis de drive y revés se acerca más a
la referencia de Fleisig que la del saque, el salto explica el exceso** y no el ángulo de
cámara. Si mantiene el mismo exceso, apunta a la estimación de la cadera en perfil. Se
contrasta con el mismo análisis de sensibilidad al paso (k=1,2,4,8) aplicado a drive/revés.

### Candidato de recalibración (NO aplicado)

El techo de plausibilidad por segmento (Fleisig × `MARGEN_PLAUSIBILIDAD`) descartó picos de
pelvis de 1325 y 1386 °/s (techo 1320) que se comportan como movimiento continuo. Un error
de detección real es un salto puntual: **no sobrevive al cambio de paso de muestreo**.
Criterio candidato, "pico sostenido": comparar el pico a k=1 contra k=4 (o k=8); si se
mantiene (p. ej. cae menos de ~10 %), es movimiento; si colapsa, es glitch. Reemplazaría o
complementaría el techo fijo. **Límite conocido:** un pico real pero breve (el brazo en el
impacto dura <30 ms) también cae al promediar más fotogramas (saque de perfil: el brazo cae
~70 % entre k=1 y k=8, la pelvis solo ~4 %). El criterio discrimina bien en segmentos lentos
(pelvis, torso) y **no** debe aplicarse tal cual al brazo; para el brazo hay que buscar otra
firma (p. ej. duración del pico a mitad de altura). **No se toca ahora**: recalibrar sobre estas mismas
repeticiones contaminaría la medición del Criterio 1 (hace falta separar datos de ajuste y
de medición: p. ej. ajustar con perfil, medir con la sesión 2).

---

## 2026-09-24 — Catalogador: soporte de `fase-b/`

**Rama:** `etapa/4-cinematica`. Primera sesión de Fase B: 6 repeticiones del saque de perfil
(iPhone, 240 fps, `r_frame_rate=30/1`, factor 8, `escala_temporal = conocida`) catalogadas
a mano en `catalogo.csv`.

### Qué se hizo

- `app/catalogador.py`: sin `--dir` recorre `fase-a/` y `fase-b/` (rutas relativas a
  `KINETIQ_DATA_DIR`); `originales/` se saltea junto a `compilaciones/`; subcarpeta
  inexistente → aviso; chequeo cruzado `fps_declarados` catálogo vs archivo.
- Verificado que la normalización NTSC no confunde el caso Apple (30 + conocida + factor 8
  → 240 efectivos) con el caso público (factor estimado, escala desconocida): son
  mecanismos independientes. Pruebas en `test_ingest_normalizacion.py`.
- `test_corpus_fase_a.py` ajustado (escanea ambas fases, evalúa solo fase-a).
- Docs: decisión 004 §8, `backend/README.md`.
- Corrida real: 20 clips, 6 filas de fase-b OK (240 ef., unicidad 1.0), 0 avisos globales.
- `pytest -m "not slow"` → 146 en verde.

### Convención de carpetas (Fase B)

`fase-b/<sesion>/<gesto>/recortes/` = unidades de análisis (también los clips sin corte,
copiados tal cual); `originales/` = solo fuentes con recortes hermanos.

### Pendiente

Sumar al catálogo el resto de los cortes y los controles/deficientes; correr
`python -m app.catalogador` y luego `extraer_pose` (checklist de Fase B, arriba).

---

## 2026-08-27 (fix) — Detector de inversión de profundidad (z), `v0.3.1` + `v0.3.2`

**Ramas:** `fix/inversion-z` (`v0.3.1`) y `fix/inversion-z-calibracion` (`v0.3.2`),
ambas mergeadas a `main`. Fix a E2/E3, antes de seguir con la Etapa 4.

Surgió de la validación cualitativa de la Etapa 4: `zverev_saque_lateral_02` daba un
pico de brazo de 24 932 °/s. Investigado (decisión 009): `CODO_DER` **invierte el signo
de `z`** en el frame 566 (+0,098 → −0,050 m). Confianza 0,65 (pasa el umbral de 0,5) y
desplazamiento 3D 0,31 torsos (< 0,5): **ni la baja confianza ni el salto imposible lo
marcaban.**

### Qué se hizo

- `engine/validation.py`: `detectar_inversiones_z`. Firma de un glitch puntual real —
  **cinco condiciones**: confianza previa ≥ 0,80, cambio de signo de `z`,
  `|Δz|/torso > 0,20`, dominado por `z` (`|Δz| > 1,8·|Δxy|`), y **`z` vuelve** al signo
  original en ≤ 15 fotogramas. `ResultadoValidacion.inversiones_z`.
- `engine/preparacion.py`: excluye la franja `[frame_desde, frame_hasta]` antes de filtrar.
- `v0.3.1` era más laxa (sin confianza previa ni retorno) y disparaba 35–95 veces por
  clip, removiendo picos plausibles del brazo y exponiendo peores. `v0.3.2` la acota a
  3–45/clip sin perder el caso real.

### Hallazgo (para el Capítulo 6/7)

Aun con las cinco condiciones, sobre el corpus público el detector **dispara 16–45 veces
por saque** de Zverev (solo 3 en el drive). No son falsos positivos: en **toma lateral**
la `z` de las articulaciones rápidas del brazo/mano que da MediaPipe es poco más que
ruido que cruza el cero. Consecuencia: al excluir esas franjas, **las repeticiones de
saque del corpus público quedan "no auditables"** en vez de reportar un orden con un
número plausible por casualidad — correcto por R3, y la misma conclusión de la decisión
008: la toma lateral no sirve para el brazo rápido; **Fase B con tres cuartos**. El
`drive` (brazo más en el plano) sigue recuperando `pelvis → torso → brazo`.

### Pruebas

`pytest -m "not slow"` → **123 en verde**. `-m slow` → `test_inversion_z_corpus.py`
atrapa el frame 566 real y la franja queda como `TramoExcluido` en E3.

---

## 2026-08-27 (sesión 3) — Etapa 4: Cinemática y secuenciación (arranque, 4.1–4.6)

**Rama:** `etapa/4-cinematica` (desde `main`). **La Etapa 4 NO se cierra en esta sesión.**
**Modelo:** Sonnet 5 Medio.

Lecturas previas (convención): `capitulo-3` §3.3.3 y §3.3.4.1–§3.3.4.5. Confirmado con
Valentín: se construyen 4.1–4.6 (+ 4.6b con caveat en el reporte) usando el corpus
público; se difieren 4.7 (Criterio 1), 4.8 (Criterio 2) y el punto de decisión hasta
tener la Fase B. Lado dominante: columna nueva en `catalogo.csv`, sin default.

### Qué se hizo

- **Housekeeping (al abrir la sesión):** `.gitattributes` con `eol=lf` (commit
  `4fbce0e`; `renormalize` no tocó nada, los blobs ya estaban en LF). ADR 006 ampliado
  con el orden de palancas de optimización de inferencia (`model_complexity` más bajo →
  Vía A sobre ONNX). Ambos ya en `main`.
- **`engine/segmentos_corporales.py`** — cadena `pelvis → torso → brazo` como vectores
  directores. `brazo = HOMBRO_{dom} → MUNECA_{dom}`; `{dom}` de la columna
  `lado_dominante` del `catalogo.csv` (agregada esta sesión), sin valor por defecto.
- **`engine/kinematics.py`** (4.1–4.3) — `angulo_tres_puntos`, `serie_angulo_articular`,
  `serie_separacion_cadera_hombro`, `velocidad_angular_segmento` (°/s, escalar).
- **`engine/sequencing.py`** (4.4–4.6b) — `detectar_pico` (`find_peaks`; no auditable si
  cae en `TramoExcluido` o supera 8000 °/s = techo de plausibilidad física, no un
  ajuste), `orden_observado`, `segmentar` (auto/manual/fallback), `evaluar_repeticion`,
  `agregar` (con `nota` de caveat de corpus público en la estructura).
- **`app/analizar.py`** — CLI `python -m app.analizar --clip X` (pose caché → E3 → E4).
- **`catalogo.csv`** — columna `lado_dominante` (zverev/sinner = `der`; `reves_lateral_01`
  de Federer y los dos `desconocido` quedaron vacíos — ver pendientes).
- Versión del motor → `0.4.0`. Decisión 008 (incluye los hallazgos de la validación).

### Validación cualitativa sobre el corpus público (registrada tal cual salió)

Corrida de `analizar` sobre 3 saques de Zverev + drive de Sinner:

- **El pipeline corre de punta a punta sobre material profesional sin romperse.** El
  manejo de no auditables funciona.
- **La muñeca de la raqueta no es auditable en gestos rápidos:** `HOMBRO→MUNECA` da
  15 000–42 000 °/s en 3 de 4 clips (MediaPipe pierde la mano por desenfoque). Con
  `HOMBRO→CODO` (brazo superior) los valores son plausibles (1 700–2 300 °/s) en 3 de 4
  y en el **drive el orden sale `pelvis → torso → brazo` completo y plausible**.
- **Vista lateral:** en los saques, pelvis y torso pican a ~12–18 ms — al borde de lo
  resoluble; el orden entre ambos se invierte según el clip. Es el riesgo anticipado:
  rotación transversal sobre el eje de profundidad (§3.3.2.8). El brazo, cuando es
  auditable, queda claramente último.
- **Lectura para la tesis:** evidencia positiva (el drive recupera la cadena pese al
  sesgo y a la vista lateral; la prueba sintética de ordenamiento con sesgo lo confirma)
  y de límite (pelvis-vs-torso lateral ≈ 15 ms; muñeca no auditable). Ambas útiles;
  guían el encuadre de la Fase B (tres cuartos pone la rotación en el plano de imagen).

### Pruebas

`pytest -m "not slow"` → **128 en verde**. Incluye la **prueba de ordenamiento con
sesgo** (3 series sintéticas con offset constante + ruido → recupera pelvis→torso→brazo),
ángulos de geometría conocida, pico en tramo no auditable → no se reporta. `-m slow`:
`test_analizar_e4.py` (estructura coherente sobre pose real, sin aseverar correctitud).

### Ajustes tras la revisión de Valentín (misma sesión)

- **`brazo = HOMBRO→CODO` por defecto, configurable** (`brazo_via`).
- **`catalogo.csv`:** `reves_lateral_01` → `lado_dominante = der` (Federer juega de
  derecha; el "zurdo" era un dato equivocado).
- **Techo de plausibilidad POR SEGMENTO, anclado a Fleisig et al. (2003)** (§3.4.2.2):
  pelvis 440, torso 870, brazo 2368 °/s × `MARGEN_PLAUSIBILIDAD = 3` → 1320 / 2610 /
  7104 °/s. Criterio del margen en decisión 008 (incertidumbre del factor de
  ralentización estimado + ruido de MediaPipe).
- **`zverev_saque_lateral_02` investigado:** el pico de 24 932 °/s (codo) es un error
  de detección puntual, no un techo mal calibrado. Frame 566: la `z` de `CODO_DER`
  **cambia de signo** (~14 cm) con `x`,`y` suaves (inversión de profundidad de
  MediaPipe). Confianza 0,65 (pasa el umbral de 0,5) y desplazamiento 0,33 torsos
  (< `MAX_SALTO_TORSOS = 0,5`): **ni E2 ni E3 lo marcaron**. El techo lo corta →
  repetición no auditable (correcto). Propuesta (no aplicada): detector de inversión
  de signo en `z` en `engine/validation.py`.
- Efecto lateral del codo: la segmentación automática, antes inundada por los
  *glitches* de 40 000 °/s de la muñeca, empieza a funcionar (el drive se parte y una
  repetición sale `pelvis → torso → brazo` **correcta**, 827/1666/1744 °/s).

`pytest -m "not slow"` → **130 en verde**.

### Detector de inversión de z (aplicado, `v0.3.1` → `v0.3.2`)

Salió de investigar el pico de 24 932 °/s del punto anterior. Se hizo en ramas
propias (`fix/inversion-z`, `fix/inversion-z-calibracion`) y se mergeó a `main`
antes de rebasar `etapa/4-cinematica`. Detalle completo en la entrada **"(fix)"** de
más arriba y en la decisión 009.

### Comparación con dos clips públicos de tres cuartos (Valentín los consiguió)

`drive_trescuartos_01`, `saque_trescuartos_01` (240 fps efectivos, factor 8).
`catalogo.csv` actualizado a 14 clips (`test_corpus_fase_a.py` a 14, corre limpio).
También: `control_oclusion_02` jugador → alcaraz; `fps_efectivos` de los tres cuartos
corregido a 240 (el catalogador detectó la discrepancia 480 arrastrada).

**El tres cuartos, sobre estos dos clips no controlados, NO mejoró ninguna métrica:**

| | lateral | tres cuartos |
| --- | --- | --- |
| separación pelvis–torso | ~2–18 ms, orden que se invierte | 271 / 317 ms **pero torso antes que pelvis**, sin pico claro de pelvis |
| brazo auditable | drive sí (1744 °/s), saques no | drive al borde (6399 °/s), saque no (23365) |
| inversiones de z | 16–45 saques / 3 drive | 40 saque / 14 drive |
| tramos excluidos E3 | decenas | 75 (drive) / 150 (saque) — ~40 % del clip |

**Dos lecturas distintas, no confundirlas:**

1. **"El ángulo no lo resolvió":** con estos dos clips, cambiar a tres cuartos **no**
   convirtió la ambigüedad pelvis-torso (~15 ms) en una secuencia limpia, **no**
   volvió auditable el brazo del saque, y **no** bajó las inversiones de z. Si el
   único cambio fuera el ángulo, no alcanzaría.
2. **"No fue una prueba justa del ángulo":** estos dos clips son públicos, de baja
   tasa de bits (3–4 MB para 13–16 s), origen desconocido, sin segmentar (la
   ventana automática los recorta mal), `escala_temporal_conocida = False` y factor
   estimado a ojo. La Fase B es otra cosa: 240 fps **reales**, luz controlada,
   encuadre fijo medido, pausas en posición neutra que hacen la segmentación
   trivial, y repeticiones del mismo gesto. La comparación honesta pelvis-torso
   lateral vs tres cuartos **todavía no se hizo**; esto solo descartó el atajo.

La única evidencia positiva limpia sigue siendo `drive_lateral_01` (toma lateral):
`pelvis → torso → brazo` correcto, velocidades plausibles. Que el drive recupere la
cadena y el saque no, mismo encuadre y mismo pipeline, apunta a que el cuello de
botella es el gesto (velocidad de la mano en el impacto — límite del apartado 1),
no el pipeline.

---

## Estado al cerrar la sesión (2026-08-27)

**En `main` (pusheado):** Etapas 0–3 (`v0.1.0-etapa0` … `v0.4.0-etapa3`) + fixes
`v0.3.1` y `v0.3.2` (detector de inversión de z). El motor en `main` está en
`0.3.2`.

**En `etapa/4-cinematica` (rama abierta, sin merge, sin tag):** pasos 4.1–4.6 de la
Etapa 4 sobre esa base. Motor `0.4.0`. `pytest -m "not slow"` → **139 en verde**;
`-m slow` → 15 (incluye `test_corpus_fase_a.py` con 14 clips, `test_analizar_e4.py`,
`test_inversion_z_corpus.py`). Nada pendiente de commitear.

**Corpus (`kinetiq-data/`):** 14 clips catalogados y verificados, catalogador limpio
(solo avisos informativos de normalización NTSC). 12 laterales + 2 de tres cuartos.
Caché de pose (`backend/.cache/`) poblada para los 14.

**Lo que NO se hizo, a propósito** (precondición del plan — no tiene sentido pulir un
detector cuyos criterios de éxito todavía no se pueden medir): tareas 4.7 (Criterio 1),
4.8 (Criterio 2), 4.6b como medición formal, y el **punto de decisión de repliegue**.
La Etapa 4 no se cierra hasta tener el material propio.

## Cuando llegue el material de la Fase B — checklist

Precondición: el conjunto propio grabado y verificado (protocolo de grabación,
hito C1). Trabajar en `etapa/4-cinematica`.

1. **Ingesta y catálogo.** Copiar los clips a `kinetiq-data/fase-b/`. Agregar una
   fila por clip a `catalogo.csv` con **`escala_temporal = conocida`**, `factor_estimado = 1`,
   `fps_efectivos` reales (240), `lado_dominante` del jugador. Correr, desde `backend/`:
   `python -m app.catalogador` — debe salir sin avisos (ni siquiera de NTSC si se grabó
   a 240 exactos).
2. **Pose.** `python -m app.extraer_pose` (procesa lo nuevo, ~3–4 min por clip). Deja
   la caché lista.
3. **Análisis por clip.** `python -m app.analizar --clip <archivo> [--manual d1:h1,d2:h2]`.
   Para clips con 6 repeticiones y pausas del protocolo, la segmentación automática
   debería andar; si no, marcar las ventanas con `--manual`.
4. **Qué comparar (las tres preguntas que quedaron abiertas):**
   - **Pelvis-torso:** ¿la separación es estable y en el orden esperado
     (pelvis→torso) entre repeticiones del mismo saque? ¿El encuadre de tres cuartos
     da una separación más limpia que el de perfil? Comparar contra los ~2–18 ms
     invertidos de la toma lateral (decisión 008 §2).
   - **Brazo:** ¿el pico del segmento `brazo` (con `--brazo-via codo`) cae por debajo
     del techo de plausibilidad, o el desenfoque en el impacto lo mantiene no
     auditable también a 240 fps reales? Probar además `--brazo-via muneca`.
   - **Inversiones de z:** ¿cuántas veces dispara `detectar_inversiones_z` con `z`
     métrica real? Debería ser mucho menos que las 16–45/clip del corpus público.
5. **Recalibrar con datos reales** (todo con `escala_temporal_conocida = True`):
   - **Criterio de "pico sostenido vs. paso de muestreo"** como alternativa al techo fijo
     (ver entrada 2026-09-25); no calibrar y medir sobre las mismas repeticiones.
   - `MARGEN_PLAUSIBILIDAD` del techo (hoy ×3; sin la incertidumbre del factor
     estimado, probablemente conviene bajarlo). `_FLEISIG_MAX` / `techo_velocidad` en
     `engine/sequencing.py`.
   - Los cinco umbrales de `detectar_inversiones_z` en `engine/validation.py`.
   - `find_peaks` (`PROMINENCIA_*`, `SEPARACION_MIN_S`) y la segmentación
     (`QUIETUD_REL`, `DUR_MIN_REPETICION_S`) en `engine/sequencing.py`.
6. **Medición formal (4.7 / 4.8).** Implementar `4.7` (Criterio 1: proporción de
   repeticiones con orden repetible; meta 8/10) y `4.8` (Criterio 2: error angular vs
   medición manual sobre los mismos fotogramas; meta < 20,6°). Volcar los números a
   `docs/resultados/` con un script versionado (principio 5 del plan).
7. **Pruebas a activar / agregar:**
   - En `tests/integration/test_analizar_e4.py`: pasar de "estructura coherente" a
     aserciones reales sobre las repeticiones de la Fase B (orden, auditabilidad).
   - Nueva prueba de **repetibilidad del orden** entre las 6 repeticiones de un clip
     (base del Criterio 1).
   - Nueva prueba de **coherencia temporal** con el par real 240 fps / ralentizado
     del mismo gesto (pendiente desde la Etapa 1: hoy es sintética en
     `test_slowmo_coherencia.py`).
   - Reemplazar las pruebas de integración que hoy usan clips sintéticos de control
     por el material real equivalente de la Fase B, si lo hay.
8. **Punto de decisión.** Con los Criterios 1 y 2 medidos, aplicar la tabla del plan
   (continuar a E5 / repliegue a fase de preparación / repliegue a 2D / reformular
   alcance) y **documentar el resultado en `docs/decisiones/`** cualquiera sea —
   alimenta los Capítulos 6 y 7. Recién ahí: merge `etapa/4-cinematica` → `main`,
   tag `v0.5.0-etapa4`.

---

## 2026-08-27 (sesión 2) — Etapa 3: Procesamiento de señales

**Rama:** `etapa/3-senales` (desde `main`, con Etapas 0–2 mergeadas y pusheadas).
**Modelo:** Sonnet 5 Medio.

Lecturas previas (convención): `capitulo-3` §3.4.2.1–§3.4.2.6. Puntos A/B/C confirmados
por Valentín: re-extracción simple del corpus; un corte de Winter por clip (como
simplificación deliberada por el contrato congelado); interpolar huecos de hasta 5
fotogramas.

### Qué se hizo

- **Paso 0 — Coordenadas métricas.** `PoseFrame.puntos_mundo` (metros, centrado en
  caderas), `PoseFrame.get_mundo()`, `SecuenciaPose.tiene_mundo`. `MediaPipeBackend`
  lee `pose_world_landmarks`; `FakeBackend` emite `puntos_mundo` sintéticos (dims=3).
  Caché: arrays `kpw__*`, **esquema v2** — `cargar_si_vigente` descarta las cachés v1,
  así el corpus se **re-extrae solo**. `puntos` (imagen) queda para el overlay de E5.
- **`engine/dsp.py`** (3.1): `butterworth_fase_cero` con `filtfilt` (nunca `lfilter`).
  Guarda de Nyquist explícita (`corte_hz >= fps/2` → error). Rechaza NaN y series
  cortas.
- **`engine/preparacion.py`** (3.3): `preparar_series` excluye fotogramas sin
  detección, puntos de baja confianza y saltos imposibles (de `validation` de E2);
  interpola huecos ≤ 5 fotogramas; los largos → `TramoExcluido`. Una articulación
  totalmente excluida → tramo que abarca todo el clip.
- **`engine/winter.py`** (3.2): `analizar_serie` (residuo RMS vs corte) y `elegir_corte`
  (un corte por clip = el máximo de los cortes de las articulaciones rápidas).
- **`engine/pipeline.py`** (3.4): `procesar_e3` encadena validar → preparar → Winter →
  filtrar sobre la secuencia completa. `SecuenciaFiltrada.trazabilidad_filtro()` arma
  el bloque `trazabilidad.filtro` del contrato — **sin cambio de contrato** (el campo
  `corte_hz` ya existía; E3 lo llena).
- **`validation.py`**: parámetro `espacio` (`"imagen"` | `"mundo"`); `_dist` 3D. E3
  valida en `"mundo"`.
- Versión del motor → `0.3.0`. Decisión 007.

### Criterio de aceptación de la Etapa 3

| Punto | Estado |
| --- | --- |
| Prueba de fase cero pasa y su versión unidireccional falla | ✅ `test_dsp.py::test_fase_cero_conserva_el_instante_del_pico_y_la_unidireccional_no` |
| Señal con ruido conocido: reduce el ruido sin tocar la componente lenta | ✅ |
| Corte por encima de Nyquist: rechazado | ✅ |
| Winter elige un corte entre señal y ruido | ✅ |
| Pipeline completo sobre pose real → secuencia filtrada coherente | ✅ `test_pipeline_e3.py` (`slow`) *(pendiente de la re-extracción; ver abajo)* |

### Pruebas

`pytest -m "not slow"` → **114 en verde** (nuevas: `test_dsp`, `test_winter`,
`test_preparacion`, `test_validation` ampliado, `test_pose_base`/`test_pose_cache`
ampliados para `puntos_mundo`).

### Pendiente

- **Re-extracción del corpus con esquema v2** en curso al momento de escribir esto
  (background). El `test_pipeline_e3.py` (`slow`) se corre en cuanto termine.
- El filtro sobre clips con `escala_temporal_conocida = False` usa un `fps_efectivos`
  estimado → corte en Hz y velocidades absolutas aproximados; el **orden** de picos es
  inmune (§3.3.4.2). Sin acción, coherente con lo que ya marca E1.
- Si E4 muestra que un corte único por clip distorsiona alguna articulación → pasar a
  corte por articulación (ampliaría el contrato).

### Siguiente paso concreto

Cerrar la Etapa 3 (correr `test_pipeline_e3` sobre la caché re-extraída, merge
`etapa/3-senales` → `main`, tag `v0.4.0-etapa3`) y abrir la **Etapa 4 — Cinemática y
secuenciación** (el punto de decisión; dos semanas en el plan). Precondición del plan:
la Fase B (grabación propia) — Valentín la adelantó a esta semana. Lecturas de la
convención para E4: `capitulo-3` §3.3.3 y §3.3.4.1–§3.3.4.5.

---

## 2026-08-27 — Etapa 2: Estimación de pose

**Rama:** `etapa/2-pose` (desde `main`, con Etapas 0 y 1 ya mergeadas y pusheadas).
**Modelo:** Sonnet 5 Medio.

Lecturas previas (convención): `capitulo-3` §3.3.2.3–3.3.2.9 y `capitulo-4` §4.4.3.
Cuatro puntos de diseño confirmados por Valentín: A `static_image_mode=True`; B
interfaz + mapa canónico + MediaPipeBackend + FakeBackend (que **también** simula el
caso 2D-solo con `z=None`), sin Vía A real todavía; C `docs/resultados/` arranca en E2;
D distancia cadera-hombro como referencia interna para el umbral de salto imposible.

### Qué se hizo

- **2.1 · Contrato `PoseBackend`** (`engine/pose/base.py`). ABC: cada backend implementa
  `estimar_frame(frame_bgr, indice) -> PoseFrame`; la base arma la `SecuenciaPose`
  (`procesar`). `Punto` (x,y normalizados, z relativo o None, confianza), `PoseFrame`,
  `SecuenciaPose` (con `dims` 2/3, `cobertura`, `cobertura_articulacion`, `config_hash`).
  Context manager para liberar recursos.
- **2.3 · Mapa articular canónico** (`engine/pose/articulaciones.py`). 19
  `ArticulacionCanonica`; `MEDIAPIPE_A_CANONICO` (33→canónico) y `COCO_A_CANONICO`
  (17→canónico); `ARTICULACIONES_CORE` (13, lo que ambos entregan). Puntos de mano/pie
  solo MediaPipe (habilitan el indicador indirecto de rotación de hombro, §3.3.3.4).
- **2.2 · `MediaPipeBackend`** (`engine/pose/mediapipe_backend.py`). `static_image_mode=True`,
  `model_complexity=2`. `visibility` → confianza. `version` = `"mediapipe-0.10.18"`
  (va a `trazabilidad.backend_pose`).
- **`FakeBackend`** (`engine/pose/fake_backend.py`). Esqueleto plausible (posiciones
  nominales + balanceo + oscilación por articulación), `dims=2|3`, simula oclusión
  (confianza baja por articulación) y fotogramas sin detección. Es el segundo backend
  contra el que se prueba que la interfaz aguanta el caso 2D-solo.
- **2.4 · `engine/validation.py`**. `marcar_baja_confianza` (umbral 0.5),
  `detectar_saltos_imposibles` (umbral 0.5 longitudes de torso; sin torso no se juzga),
  `validar()` → `ResultadoValidacion` con cobertura auditable **por articulación**
  (§3.3.2.8).
- **2.5 · Caché** (`engine/pose/cache.py` + `config.get_cache_dir()`). `.pose.npz` +
  `.pose.json`. Clave = stem + backend id + hash de config. `cargar_si_vigente` compara
  una firma rápida del video y descarta la caché si el archivo cambió.
  `KINETIQ_CACHE_DIR` (default `backend/.cache/`, ignorado).
- **`app/extraer_pose.py`**. CLI: recorre el corpus, corre el backend, cachea. Si ya
  está y el video no cambió, no re-infiere. Probado con `--backend fake` sobre los 12
  clips.
- **2.6 · `app/bench_pose.py` + `docs/resultados/`**. Mide fps de inferencia y agrega la
  corrida a `docs/resultados/e2-velocidad-inferencia.json`.

### Criterio de aceptación de la Etapa 2

| Punto | Estado |
| --- | --- |
| Un video de la Etapa 0 produce un archivo de coordenadas completo con confianzas | ✅ `extraer_pose` → `.pose.npz`/`.pose.json` |
| Video con jugador visible: cobertura > 95 % | ✅ `test_mediapipe_backend.py` sobre `zverev_saque_lateral_01` (cobertura > 0.95) |
| Video con oclusión: puntos ocluidos marcados de baja confianza | ✅ `test_mediapipe_backend.py` sobre `control_oclusion_02` |
| El cambio de backend no altera la estructura de la salida | ✅ FakeBackend (2D y 3D) y MediaPipe producen la misma `SecuenciaPose` |
| Velocidad de inferencia medida y registrada | ✅ `docs/resultados/e2-velocidad-inferencia.json` |

### Dato duro (tarea 2.6, primer punto del indicador §2.4)

`static_image_mode=True` + `model_complexity=2`, 1080p, **CPU** (MediaPipe-Python no usa
la GTX 1050ti): **~3,6 fotogramas/segundo** (~280 ms/frame, p95 ~322 ms). Un clip de
~750 fotogramas ≈ 3–4 min; el corpus entero ≈ 40 min, **una sola vez** (después la
caché). Si en E4 el tiempo molesta: `model_complexity=1`, `static_image_mode=False`
(tracking), o bajar resolución antes de inferir. No se toca ahora ("no optimizar antes
de medir").

**Choca con la tesis:** el apartado 4.2.3 usó ~25 fps para justificar el procesamiento
asincrónico y estimar tiempos; 4.5.4 apoyó los costos en ese número. Casi 7× de
diferencia. Es un pendiente de **redacción** (no de código): reescribir 4.2.3 y 4.5.4
con el número medido antes de la entrega. Registrado en `docs/decisiones/006`.

### Pruebas

`pytest -m "not slow"` → **96 en verde** (unit de pose: articulaciones, base/FakeBackend,
validación, caché; integración con clips sintéticos). `-m slow` → MediaPipe sobre video
real (4) + corpus Fase A de la Etapa 1 (5).

### Pendiente

- **Vía A (YOLOv8-Pose 2D + elevación)**: no implementada. Se hace si el punto de
  decisión de E4 lo pide (plan de repliegue). La interfaz ya está lista para un backend
  de 17 puntos.
- `pose_world_landmarks` métricos de MediaPipe: no se guardan aún. **La Etapa 3 los va a
  necesitar**: el filtro va a operar sobre coordenadas métricas (ver plan de E3), así
  que E3 empieza extendiendo la captura de pose y re-extrayendo el corpus.
- Reevaluar la config de MediaPipe (complexity / tracking) si la velocidad molesta en E4.
- `.gitattributes` con `eol=lf`: **resuelto** (commit `4fbce0e`). `renormalize` no tocó
  ningún archivo; los blobs ya estaban en LF.
- **Calendario:** Valentín adelanta la Fase B (grabación propia, hito C1) a esta semana
  en vez del 22/9. No cambia nada del desarrollo en curso.

### Siguiente paso concreto

Abrir la **Etapa 3 — Procesamiento de señales**. Lecturas de la convención (hechas):
`capitulo-3` §3.4.2.1–3.4.2.6. Plan propuesto; pendiente de aprobación antes de escribir
código.

---

## 2026-08-26 (sesión 2) — Etapa 1: Ingesta y validación de FPS

**Rama:** `etapa/1-ingesta` (desde `etapa/0-fundaciones`, todavía sin merge a `main`).
**Modelo:** Sonnet 5 Medio.

Antes de planificar se leyeron los apartados de tesis que sustentan la etapa
(`capitulo-3`: 3.3.1.1, 3.4.2.2, y 3.3.4.2) y se releyó `decisiones/001`, según la
convención fijada.

### Qué se hizo

- **1.1 / 1.2 / 1.3 · `engine/ingest.py`.** Núcleo puro separado de la entrada/salida:
  - `clasificar_fps()` — tabla de aptitud (≥240 completo, 120–239 reducido, 60–119 solo
    preparación, <60 rechazado).
  - `evaluar()` — `fps_efectivos = fps_declarados × factor`; propaga la frecuencia de
    **captura**, nunca la de reproducción. El factor es externo (catálogo o manual).
    `<60` devuelve un resultado con `motivo_rechazo`, no una excepción.
  - `detectar_inconsistencias()` — contrasta tasa declarada vs `nb_frames/duración` vs
    `avg_frame_rate` (verificación 1 de la decisión 001).
  - `probe()` — OpenCV + enriquecimiento con `ffprobe` si está. Archivo corrupto →
    `IngestaError`, sin crash.
  - `iterar_fotogramas()` — generador, memoria constante (tarea 1.4).
- **Decisión 001 en código · `engine/framehash.py`.** `ratio_fotogramas_unicos()` por
  huella md5 exacta sobre la ventana central (no `mpdecimate`). `interpretar_ratio()` →
  `captura_real` / `repeticion_aislada` / `duplicacion_sistematica`.
- **1.5 · `app/catalogador.py`.** `python -m app.catalogador` (desde `backend/`).
  Recorre el corpus, toma el factor del `catalogo.csv`, combina las dos verificaciones
  en un "uso" final, escribe `catalogo-verificado.csv`. **No toca `catalogo.csv`.**
  `--sin-hash` para una pasada rápida. Detectó que las 4 filas de `catalogo.csv` tienen
  13 columnas en vez de 14 (fila mal formada): lo reporta y no cruza semánticamente
  contra esas filas.
- **Contrato.** Se agregó `escala_temporal_conocida: bool` (obligatorio) a
  `Trazabilidad` en `schemas/reporte.py` + ejemplo JSON. Cambio al contrato de la
  Etapa 0, hecho antes de integrar nada a `main`. Registrado en decisión 004.
- **Versión del motor** → `0.1.0`.
- **Decisión 004** (`docs/decisiones/004-ingesta-fps-y-verificacion.md`), `arquitectura.md`
  y `backend/README.md` actualizados (ffmpeg como dependencia del catalogador, cómo
  correr el catalogador).

### Criterio de aceptación de la Etapa 1

| Punto | Estado |
| --- | --- |
| Archivos de 30/60/120/240 fps devuelven su tasa real | ✅ (test de integración con clips ffmpeg) |
| Clip ralentizado (240 exportado a 30, factor 8) resuelve a 240 efectivos | ✅ |
| Prueba de coherencia temporal (240 vs ralentizado: misma duración real) | ✅ **sintética** |
| Metadatos inconsistentes se detectan y advierten | ✅ |
| Archivo corrupto / formato no soportado: error claro sin caída | ✅ |
| Video 240 fps / 20 s: la iteración no acumula memoria | ✅ (`tracemalloc`, pico <100 MB) |
| El catalogador procesa la Fase A completa sin errores y clasifica cada clip | ✅ lee y clasifica los 12; marca las inconsistencias del `catalogo.csv` (ver abajo) |
| Toda la lógica sobre la frecuencia efectiva, no la declarada | ✅ |

Corrida real del catalogador sobre `kinetiq-data/fase-a/` (12 clips, `compilaciones/`
excluida): 5 gestos en cámara lenta → `fps_efectivos` 500/480/300,
`escala_temporal_conocida = False`, `ratio_unicidad ≈ 1.0` (`captura_real`), `uso = E1-E4`;
4 controles a 30 fps → `rechazado`; 3 a 60 fps → `solo preparación`.

### Pruebas

`pytest -m "not slow"` → **64 en verde** (incluye las 12 de la Etapa 0). `-m slow` →
4 pasan sobre el material real + 1 `xfail` (catálogo con inconsistencias, ver abajo).
~2 min.

### Pendiente

- Sigue con la única prueba sintética sin equivalente real: duplicación sistemática de
  fotogramas (ningún clip real la tiene) y el par de coherencia temporal 240 vs
  ralentizado (depende de la Fase B, plazo 22/9). Marcadas en el código.
- Hash md5 por fotograma sobre 1080p: ~1 min por clip de 30 s. Aceptable como
  herramienta offline; si el corpus crece, submuestrear la ventana.
- `.gitattributes` con `eol=lf` (arrastre de la Etapa 0).

### Correcciones tras la revisión (misma sesión)

El corpus de la Fase A se amplió a **12 clips reales** (3 saques + 1 drive + 1 revés en
cámara lenta; 7 de control: 4 a 30 fps, 3 a 60 fps, con oclusión en varios). Al correr
el catalogador sobre el corpus nuevo aparecieron dos bugs propios, ya arreglados:

- **Tasas NTSC.** `59.94` fps (= 60000/1001) quedaba por debajo del umbral de 60 y se
  rechazaba por redondeo. Se agregó `normalizar_fps()`: ajusta a la tasa nominal si cae
  a <0.5%. Ahora `59.94 → 60 → solo preparación`, `29.97 → 30 → rechazado`.
- **Material de origen.** El catalogador escaneaba `fase-a/compilaciones/` (videos largos
  de los que se recortan los segmentos). Ahora salta `compilaciones/` por defecto
  (`--incluir-todo` para no saltearla).
- Alineado el vocabulario: `SOLO_PREPARACION` → `uso = "E1-E2 (solo preparacion)"`
  (**sin tilde**, por pedido de Valentín: es un token que viaja al CSV y se compara
  contra `catalogo.csv`; se mantiene ASCII para no depender de la codificación de la
  consola en Windows/Git Bash). Barrido del resto del código: los otros usos de la
  palabra con tilde son comentarios y prosa de docs (se dejan con ortografía correcta);
  la única otra cadena *generada* era `motivo_rechazo` en `ingest.py`, ya pasada a ASCII.
- El catalogador ahora reporta filas del `catalogo.csv` que no tienen archivo.

**Pruebas sintéticas retiradas** (había material real equivalente): parámetros 30/60 fps
de `test_ingest_video.py`. Se mantienen las sintéticas que no tienen equivalente real:
duplicación sistemática de fotogramas (ningún clip real la tiene) y el par de coherencia
temporal 240 vs ralentizado (depende de la Fase B, plazo 22/9).

`test_corpus_fase_a.py` reescrita contra los 12 clips reales: 5 gestos aptos E1-E4
(`escala_temporal_conocida = False`, sin duplicación), controles de 30 fps → rechazado,
de 60 fps → solo preparación.

### Cierre del `catalogo.csv` y merge

Valentín arregló el `catalogo.csv`: renombró la fila fantasma a
`control_reves_30fps_01.mp4`, quitó la fila de `zverev_saque_sideview.mp4` (compilación),
y puso `uso = rechazado` en los 4 controles a 30 fps. Quedan **12 filas parejas**.

`python -m app.catalogador` sobre el corpus final: **sin avisos globales, sin
inconsistencias**. Los únicos avisos por clip son las notas informativas de
normalización NTSC (`29.97 → 30`, `59.94 → 60`). Resultado:

| grupo | clips | uso |
| --- | --- | --- |
| gestos en cámara lenta | zverev ×3 (500 fps ef.), drive_lateral_01 (480), reves_lateral_01 (300) | `E1-E4`, `escala_temporal_conocida=False`, `captura_real` |
| control 60 fps | control_rally_60fps_01/02, control_oclusion_03 | `E1-E2 (solo preparacion)` |
| control 30 fps | control_drive_30fps_01, control_reves_30fps_01/02, control_oclusion_02 | `rechazado` |

Se quitó el `xfail` de `test_el_catalogo_no_tiene_inconsistencias` (ahora pasa como
prueba real). `pytest -m "not slow"` → 64 en verde; `-m slow` → 5 en verde.

**Merge hecho:** `etapa/0-fundaciones` → `main`, etiqueta `v0.1.0-etapa0`;
`etapa/1-ingesta` → `main`, etiqueta `v0.2.0-etapa1`. `main` funcional. Sin `push`
(local). **Etapa 1 cerrada.**

### Siguiente paso concreto

**Etapa 2 — Estimación de pose**, rama `etapa/2-pose` desde `main`. Plan ya propuesto y
aprobado en su forma general (lecturas hechas: `capitulo-3` 3.3.2.3–3.3.2.9, `capitulo-4`
4.4.3). Pendiente de confirmar 4 puntos de diseño antes de escribir código:
`static_image_mode`, alcance de la Vía A (YOLOv8-Pose), `docs/resultados/` desde E2, y el
umbral de "salto imposible" sin escala métrica.

---

## 2026-08-26 — Etapa 0: Fundaciones (tareas 0.1–0.4, 0.6, 0.7)

**Rama:** `etapa/0-fundaciones` (desde `4c954e8`). `main` sin tocar.

### Qué se hizo

- **Línea de base.** Primer commit (`10e1cb1`) consolidando el trabajo que vivía solo en el
  árbol de trabajo de `ajuste-tesis`: `CLAUDE.md`, `docs/` completo (plan, protocolo,
  decisión 001, capítulos 3 y 4 de la tesis) y los ajustes del prototipo Lovable. La rama
  `ajuste-tesis` queda intacta en `4c954e8`; qué se hace con ese contenido se decide en otra
  sesión.
- **0.4 · Higiene de git.** `.gitignore` ampliado: entornos virtuales, `__pycache__`,
  `.env` (se versiona solo `.env.example`), archivos de video, `package-lock.json` (el
  frontend usa bun; se descarta el lockfile de npm).
- **0.1 · Monorepo.** Todo el proyecto Lovable movido a `frontend/` con `git mv` (conserva
  historial). Creado el esqueleto `backend/`, `supabase/`, `tests/`, `.github/workflows/`
  según el apartado 4.3.5 de la tesis, transcripto en
  `docs/decisiones/003-estructura-monorepo.md`. El frontend **levanta y compila** desde la
  nueva ubicación (`bun run dev` y `bun run build` verificados).
- **0.2 · Entorno Python.** venv en `backend/.venv` creado con **`py -3.11`**.
  `requirements.txt` con versiones fijadas. **mediapipe instala y ejecuta en esta máquina**
  (CPU/XNNPACK; la GTX 1050ti no la usa la API de Python de mediapipe). Dos ajustes que
  hicieron falta:
  - `numpy` bajado a `1.26.4` porque mediapipe exige `numpy<2`.
  - Se usa `opencv-contrib-python` (no `opencv-python`): mediapipe depende de contrib, y
    tener las dos instaladas rompe el import de `cv2`.
- **Config de la ruta del corpus** (regla de arquitectura de esta sesión).
  `backend/app/config.py` → `get_data_dir()` lee `KINETIQ_DATA_DIR` del entorno o de
  `backend/.env`. Sin valor por defecto: si falta, error claro. `backend/.env` creado local
  (ignorado), `backend/.env.example` versionado. Decisión en
  `docs/decisiones/002-config-ruta-corpus.md`.
- **0.3 · Contrato del reporte congelado.** `backend/app/schemas/reporte.py` (Pydantic v2,
  `extra="forbid"`) transcribe el Anexo A. Ejemplo válido en
  `docs/contrato-reporte.ejemplo.json`.
- **0.6 · Decisiones.** `docs/decisiones/README.md` (plantilla + índice), ADR 002 y 003
  nuevas, ADR 001 corregida (venía con el markdown escapado y no renderizaba).
- **0.7 · Bitácora.** Este archivo.
- **Pruebas.** `pytest` → **12 pruebas en verde**: smoke, validación del contrato contra el
  ejemplo (y rechazo de datos mal formados), y resolución de `KINETIQ_DATA_DIR`.

### Criterio de aceptación de la Etapa 0

| Punto | Estado |
| --- | --- |
| `pytest` corre sin errores sobre una prueba trivial | ✅ 12/12 |
| El contrato del reporte valida un ejemplo ficticio | ✅ |
| El proyecto frontend levanta desde su nueva ubicación | ✅ `dev` y `build` |
| Corpus Fase A completo y verificado | ⏳ fuera de este chat (tarea 0.5, en curso) |
| Fase B agendada y equipo de captura probado | ⏳ fuera de este chat (hito C1, límite 22/9) |

### Pendiente

- **Detalle a no olvidar:** el `python` del sistema es 3.14; el venv se crea **siempre** con
  `py -3.11`. Anotado también en `backend/README.md`.
- Decidir en otra sesión si el contenido de `ajuste-tesis` se integra a `main`.
- Integrar `etapa/0-fundaciones` a `main` y etiquetar (`v0.1.0-etapa1` corresponde a la E1;
  para el cierre de E0 se puede usar `v0.1.0-etapa0` si se quiere un punto de retorno).
- `.gitattributes` con `eol=lf`: git avisa de conversiones CRLF/LF en Windows. No es
  urgente pero conviene fijarlo antes de que se sumen colaboradores.
- Revisar con Valentín el encabezado de `catalogo.csv` (no tiene columnas propias para
  "verificado por huella" ni "etapas"): lo formaliza el catalogador de la Etapa 1 (tarea 1.5).

### Siguiente paso concreto

Abrir la **Etapa 1 — Ingesta y validación de FPS** (`docs/plan-desarrollo.md`). Antes de
pedir el plan de esa etapa, leer el apartado de la tesis que cita su sección "Por qué"
(convención fijada esta sesión). La Etapa 1 trabaja sobre los 3 segmentos de Zverev ya
catalogados en `kinetiq-data/fase-a/segmentos/`.
