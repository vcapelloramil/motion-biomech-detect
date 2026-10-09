# Decisión 029 — La tasa real de captura no es la nominal y varía por video: el motor la lee del archivo (RNF-01)

**Fecha:** 9 de octubre de 2026
**Estado:** vigente en lo **medido**. El diseño de la sección "Propuesta para el producto" es una **propuesta, no implementada**, a aprobar por Valentín. El recálculo del
corpus **no se hizo** (se pidió primero el diagnóstico).
**Afecta a:** `backend/app/engine/ingest.py` (`probe`, `evaluar`), `procesar_video._factor_y_motivo` · decisiones 001, 004, 017, 020 y 028 · `catalogo.csv` · contrato del reporte (decisión 024) ·
RNF-01 y R1 · Capítulos 4 (RNF-01, tabla de plan de pruebas), 6 y 7 · `docs/ux/especificacion-frontend.md` §5

---

## El problema

Todo el motor supone **240 fps** para los clips de cámara lenta del corpus propio. Dos hechos lo ponen en duda:

1. Los archivos del corpus están **horneados a 30 fps** (decisión 020): el contenedor trae los fotogramas con marcas de tiempo reescritas a 1/30 s, así que **no dice a qué tasa se capturó**. El 240 viene de la declaración del usuario
   (`catalogo.csv`: `factor_estimado = 8`, `escala_temporal = conocida`, observación "captura real 240 fps confirmada por formato Apple y huella 300/300").
2. Valentín observó en Fotos (ⓘ) que sus videos se grabaron a **~200–201 fps** (los del corpus) y a **~170 fps** (uno nuevo, probablemente por la luz), aunque la cámara dice 240.

**RNF-01 (Capítulo 4):** "El sistema lee la tasa de cuadros **real** del archivo y **nunca la asume**. Si es menor a 120 fps, el análisis de la fase de aceleración se marca como no auditable."
Esta decisión confirma que el requisito es necesario y muestra que el procesamiento del corpus **no lo cumplía** (asumió 240).

## Qué se midió (9/10/2026, con `app.inspeccionar_subidas`, sobre las subidas de la página de prueba del iPhone)

| Subida | Cómo se obtuvo | Códec | Fotogramas visibles | Duración | Marcas de tiempo (nominal → real media) | Caso |
| --- | --- | --- | --- | --- | --- | --- |
| **Recorte, Fotos (7/10)** | selector de Safari, formato por defecto | H.264 | 201 | 2,01 s | 100 → **100 fps** | tiempo real, **< 120 (R1)** |
| **`recorte-desde-archivos`** | el mismo recorte, guardado en Archivos, "Elegir archivos" | **HEVC** | **398** (el contenedor dice 479) | 2,005 s | 239,98 → **198,9 fps** (17,1 % de fotogramas perdidos) | **(a) tiempo real a ~200 fps** (R1: reducido, 120–239) |
| **`recorte-opciones-actual`** | el mismo recorte, desde Fotos con **Opciones → Formato: Actual** | HEVC | 398 | 2,005 s | idéntico | **mismo video que el anterior** (42 bytes de metadatos de diferencia) |
| **`slow-mo-sin-recortar`** | cámara lenta sin recortar, selector de Fotos por defecto | H.264 (con **rotación −90°**) | 405 | 9,485 s | 60 → **42,7 fps** (28,9 % perdidos) | tiempo real, **< 60: rechazado por R1** |

Los selectores `A`, `B`, `C` y `D` entregan el mismo archivo en cada grupo (mismo tamaño, mismas marcas): **el atributo `accept` no cambia nada.** 1920×1080 en todos.

### Lo que se aprendió de esos archivos

1. **El camino que conserva la captura es el formato "Actual"**: Archivos y "Opciones → Actual" entregan el **HEVC original con las marcas de tiempo reales de cada fotograma**. El camino por defecto de Fotos ("más compatible")
   **reexporta a H.264 y descarta fotogramas** (100 fps en el recorte corto; 60 nominales y 43 reales en el largo): por debajo de R1, y la captura no se recupera.
2. **Las marcas de tiempo reales son irregulares.** Nominal 240 (1/240 s), pero faltan fotogramas con un **patrón casi periódico**: 356 intervalos de 1 período y 41 de 3 (faltan dos), uno cada ~12 fotogramas
   (`docs/resultados/tasa-real-iphone-huella.json`). Tasa media **198,9 fps**: coincide con los ~200 que muestra Fotos.
3. **E0 lee mal ese archivo.** El contenedor declara **479 fotogramas** y un `avg_frame_rate` de **169,28 fps** (los dos cuentan 81 fotogramas de **pre-roll** anteriores al inicio del recorte, que no se ven), y `probe()` toma esa tasa como `fps_declarados`; OpenCV decodifica solo 398.
   Hoy `camara_lenta_240` **falla** sobre ese archivo (240/169,28 no es entero) y `normal` lo **analiza con 169,28 fps**, una tasa que no es ni la nominal ni la real.
4. **Un video vertical llega acostado** (rotación −90° que OpenCV no aplica por defecto). Defecto aparte de E0, registrado como tarea; no es parte de esta decisión.
5. **El catálogo afirma "escala conocida" sin base:** la huella de fotogramas únicos descarta duplicados, **no detecta fotogramas perdidos**.

## Impacto en lo ya medido (diagnóstico, sin recalcular)

**Qué se sabe con certeza (analítico).** Si la tasa real media es *r* y el motor supone 240: cada velocidad reportada es **×(240/*r*)** la real (×1,21 a 199 fps; **×1,41 a 170 fps**) y cada intervalo en ms es **×(*r*/240)** (×0,83 a 199 fps).
Los **ángulos** no dependen del tiempo.

**Qué se midió por simulación** (`python -m app.diagnostico_tasa_real_corpus`, resultado en `docs/resultados/tasa-real-sensibilidad.json`). Sobre las **84 repeticiones** de la Fase B (poses ya extraídas), se quitaron fotogramas
con la huella real medida (12 desplazamientos, 1008 corridas, tasa simulada 198–200 fps) y se tomó la serie resultante **como uniforme a 240 fps**, que es lo que el motor hace con un archivo horneado. El arnés de referencia reproduce los
fotogramas de pico ya guardados del Criterio 1 (**48 de 48**). **Limitación:** el corpus ya trae sus propias pérdidas, así que la simulación mide el efecto de una **segunda capa** de pérdidas (del mismo orden que la real, aproximadamente
×√2 sobre la perturbación respecto de la verdad); y el patrón de pérdida del corpus **no se pudo verificar por contenido** (no aparece la huella periódica de ~12 fotogramas), solo se apoya en los ~200 fps de Fotos.

| | Resultado |
| --- | --- |
| Velocidad pico, aparente / real | mediana **1,12–1,16** (pelvis 1,12; torso 1,14; brazo 1,16); p90 hasta 1,24 (pelvis, torso) y **1,38** (brazo) |
| Error del instante del pico (cuando no salta) | mediana **4,2 ms** (1 fotograma); p90 8–12 ms |
| Picos que **saltan a otro máximo** (> 50 ms) | pelvis 8 %, torso 5 %, **brazo 17 %** |
| Orden de los picos (pelvis→torso / cadena) | **igual en 88,8 % / 86,3 %** de las corridas |
| ¿"ordenable" cambia? (par pelvis-torso, tolerancia 1 / 2 / 3 fotogramas) | **23 % / 18 % / 14 %** de las corridas |
| Separación pelvis-torso **de la referencia** | mediana **2 fotogramas**; ≤ 1: 38,5 %; ≤ 3: 69 % |
| El orden cambia según esa separación | 0–1 fotogramas: **18 %**; 2–3: 8 %; 4–8: 6 %; más de 20: 7 % (aquí no es una inversión por cercanía sino un pico que salta a otro máximo) |

**Qué cambia y qué no:**

| Qué | ¿Cambia? | Detalle |
| --- | --- | --- |
| **Ángulos** (Criterio 2: rodilla, codo…) | **No** | No dependen del tiempo. |
| **Velocidades absolutas** (Capítulo 7, techos de plausibilidad, Fleisig) | **Sí, ×1,2 a ×1,4** | Sobreestimadas. Para los techos el error es **conservador**: con velocidades reales menores, "ningún techo salta con la declaración correcta" se cumple todavía más. Las cifras de la decisión 020 sobre clips de velocidad **normal** (30/60 fps reales) no cambian. |
| **Intervalos en ms** (Δ pelvis-torso, `instante_pico_torso_desde_max_sep_ms` del Criterio 3) | **Sí, ×0,83** (a 199 fps) | Subestimados. |
| **Criterio 3** (conclusiones) | **Casi no** | Compara variabilidades dentro de la misma escala; solo se distorsiona si las dos sesiones tuvieron tasas distintas. A verificar con la tasa de cada sesión. |
| **Orden de los picos, el real** | **No** | Una deformación creciente del tiempo preserva el orden. |
| **Orden de los picos, el estimado** (Criterio 1) | **Sí, es sensible** | Los picos de pelvis y torso están casi siempre a 0–3 fotogramas; ahí cualquier perturbación puede invertirlos. **La expectativa de que "el orden no cambiaría" vale para el orden real, no para el estimado.** |
| **Criterio 1, el único grupo que cumple** (`drive|perfil`, 1a = 0,83 contra el umbral 0,80) | **Frágil** | Sigue cumpliendo en 10 de 12 mundos perturbados (tolerancia 1) y en **6 de 12** (tolerancia 2): un par de repeticiones decide. |
| **Criterio 1, los grupos que no cumplen** | **Robusto** | De las 25 combinaciones (grupo × tolerancia × par/cadena) que no cumplen, **19 no cumplen en ninguno de los 12 mundos** y las otras 6 cumplen solo en 1 o 2 de 12. La conclusión negativa no depende de la tasa. |
| **`escala_temporal_conocida = true`** (97 clips del catálogo; reportes de prueba) | **Falso** | Debe ser "nominal/estimada". |
| **`videos.fps_real = 240`** de los reportes de prueba | **Falso** | Sin impacto en datos de usuarios: no hay datos de producción. |

## Cómo obtener la tasa real por clip

1. **Producto (archivos "Actual" / de Archivos):** leerla de las **marcas de tiempo de los fotogramas visibles** (`engine/uniformidad_temporal.marcas_de_tiempo`, ya implementado y probado en esta decisión): tasa nominal, tasa real media,
   intervalos y fotogramas de pre-roll. No usar `nb_frames` ni `avg_frame_rate` del contenedor.
2. **Corpus (horneado, tasa perdida):**
   - **Mejor:** volver a exportar cada grabación original con **Archivos / Opciones → Actual** (o transferir con "Mantener originales"), obtener sus marcas reales y **asignarlas a los fotogramas del archivo horneado** (el orden y la cantidad de fotogramas
     deben coincidir uno a uno; se verifica contando). Son **17 grabaciones** de las que salen los 94 recortes. Con eso se rehace el eje de tiempo sin volver a extraer la pose.
   - **Aproximado:** la tasa que muestra Fotos (ⓘ) de cada una de las 17 grabaciones, usada como **factor de escala** sobre velocidades y ms, con la incertidumbre de la simulación para el orden. No corrige la irregularidad.
   - **No sirve:** deducirla del contenido (no se halló una huella detectable en el corpus).

## Propuesta para el producto (no implementada)

1. **Aceptar solo archivos con marcas de tiempo reales como "auditables completos" (caso a).** Es lo que entrega **Opciones → Formato: Actual** o Archivos. La tasa **sale del archivo**; la declaración del usuario no la define (RNF-01).
2. **Regularización temporal (una etapa nueva entre la validación E1b y el filtrado E3):** con las marcas reales, remuestrear las coordenadas de las articulaciones a una grilla uniforme a la tasa nominal (interpolación) **antes** del filtrado de E3, que exige muestreo uniforme.
   El eje de tiempo queda en tiempo real; las pérdidas (≤ 3 períodos ≈ 12 ms, mucho menos que el período de la banda útil del gesto) se interpolan. Un hueco largo dentro de la ventana del golpe se marca como tramo no auditable.
3. **R1 se evalúa sobre la tasa real media medida**, no la nominal: ~199 fps → "reducido" (120–239), no "completo". Menos de 120 → no auditable (RNF-01).
4. **Archivo horneado (caso b, 30 fps constantes):** su tasa real **se desconoce**. Se acepta **solo como degradado**: el **orden** y los **ángulos** valen; las **velocidades absolutas y los ms se marcan no auditables** (R3) y `escala_temporal_conocida = false`.
   Es la salida más honesta con el corpus actual y con quien suba un video transferido a una computadora. Opcional: un campo "la tasa que muestra Fotos" que mejore la escala, con su incertidumbre.
5. **`modo_captura`:** deja de **definir** la tasa. Para (a) es redundante (factor 1 siempre); se conserva como **trazabilidad** y como **chequeo de consistencia** (declaró cámara lenta y el archivo llegó a 30 fps constantes, o a 100 fps convertido). Para (b) sigue siendo la única fuente de la tasa **nominal**.
   `_factor_y_motivo` dejaría de fallar con `modo_captura_incompatible` para un archivo en tiempo real: el motivo engañoso de la decisión 028 desaparece.
6. **Un motivo de fallo propio** para "el teléfono convirtió el video a menos de 120 fps" (con migración), con el texto: "Tu teléfono convirtió el video al subirlo. En el selector tocá **Opciones → Formato: Actual**, o subilo desde la app Archivos".
7. **Contrato v1.1 (aditivo):** `trazabilidad.fps_nominal`, `fotogramas_perdidos_pct` y `origen_tasa` (`marcas_de_tiempo` | `declaracion_usuario`), con `fps_real` = tasa real media medida. Se registra en una decisión propia al implementarlo.

## ¿Hay que recalcular?

**Recomendación:** **no recalcular ahora el Criterio 1 con el mismo material.** Lo hace mejor la **autovalidación de la semana 4**, que mide con archivos que ya traen las marcas reales (caso a) y con la regularización temporal;
recalcular el corpus horneado sin las marcas reales solo cambiaría una escala que ya se conoce (×1,2). **Sí corresponde**, antes de redactar el Capítulo 7:
(a) anotar que las velocidades y los ms del corpus están sobreestimados/subestimados por un factor 1,2–1,4 (o corregirlos con la tasa de Fotos), (b) reetiquetar `escala_temporal` en el catálogo como **nominal**, y
(c) **decir en el Capítulo 7 que el único grupo que cumple el Criterio 1 es frágil**. Si Valentín consigue re-exportar las 17 grabaciones originales con las marcas reales, **sí vale la pena** recalcular los criterios 1 y 3 con el eje de tiempo corregido.

## Pendiente

1. **Probar "cámara lenta sin recortar" con Opciones → Actual.** No se probó: la subida `slow-mo-sin-recortar` usó el formato por defecto. Es el caso que más le va a pasar a un usuario real, y dirá si "Actual" también entrega las marcas reales cuando hay rampas de velocidad.
2. **Decidir** las propuestas 1–7 (qué aceptar, la regularización temporal, `modo_captura`, motivo de fallo, contrato v1.1) y si se re-exportan las 17 grabaciones del corpus.
3. **Reetiquetar** `escala_temporal` en `catalogo.csv` (fuera del repositorio).
4. **Capítulos 4, 6 y 7:** RNF-01 y su plan de pruebas deben incluir "archivo convertido por el teléfono"; limitaciones: tasa nominal contra real, orden estimado frágil con picos a 0–3 fotogramas, formato "Actual" requerido.

## Consecuencias

- La página de prueba y el inspector ya miden la **tasa real media** y los fotogramas visibles; `uniformidad_temporal.marcas_de_tiempo` pasó a leer solo los visibles. **E0 no cambia en esta decisión.**
- El mensaje que ve el usuario cuando falla la tasa tiene que explicar el **camino que funciona** (Opciones → Actual), no pedir que revise el modo.
- Con esto la prueba del iPhone **cambia de estado**: hay un camino que llega a ≥ 120 fps. El riesgo del 20/10 pasa de "bloqueante" a "a verificar con 'cámara lenta sin recortar' y con la regularización temporal".
