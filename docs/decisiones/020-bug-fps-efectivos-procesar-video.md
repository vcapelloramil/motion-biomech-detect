# Decisión 020 — Bug real de fps, corregido con una declaración de modo de captura del usuario

**Fecha:** 2 de octubre de 2026
**Estado:** corregido e implementado (diseño final aprobado por Valentín, con dos correcciones sobre la
primera propuesta — ver "Primer arreglo" y "Diseño final" más abajo); falta que Valentín aplique la
migración `20261002000000_modo_captura_y_trazabilidad_escala.sql` desde el editor SQL.
**Afecta a:** `backend/app/procesar_video.py` (tarea 4.5.3) · esquema de datos (`sesiones.modo_captura`,
`videos.motivo_fallo`, `reportes_biomecanicos.escala_temporal_conocida`/`.origen_factor` — decisión 018
ampliada) · `docs/ux/especificacion-frontend.md` §5 · R1/R2/R3/R4 (CLAUDE.md §2) · decisión 019 (semilla de
la API) · investigación de la tarea 4.5.4 (frecuencia del brazo no auditable, pedida por Valentín)

---

## Cómo se encontró

Valentín pidió (cierre de la tarea 4.5.4) medir qué porcentaje de golpes del corpus de la Fase B termina con
el pico de BRAZO no auditable, separando oclusión de un problema de cálculo. Al escribir
`app/diagnostico_brazo_corpus.py` (de solo lectura, sobre la pose ya cacheada) y comparar su resultado contra
lo que `procesar_video.py` reportaba en vivo para el MISMO clip
(`20260924_VCR_drive_perfil_240_01_rep01.mov`), los dos daban resultados distintos: el diagnóstico (caché)
decía auditable; `procesar_video.py` (en vivo) decía `NaN`, motivo "serie demasiado corta o incompleta".

Comparando los landmarks fotograma a fotograma entre la pose cacheada y una extracción fresca del mismo
archivo: **idénticos, diferencia 0.** No es un problema de determinismo de MediaPipe. La diferencia real
estaba en los metadatos: `fps_efectivos cacheada: 240.0` contra `fps_efectivos fresca: 30.0`.

## La causa

`20260924_VCR_drive_perfil_240_01_rep01.mov` es una captura en cámara lenta de iPhone: el contenedor declara
30 fps de reproducción, pero la captura real es 240 fps (factor 8, confirmado en `catalogo.csv` por formato
Apple y coincidencia de huella, columna `observaciones`). `procesar_video.py` (escrito en la tarea 4.5.3) tomaba
`probe().fps_declarados` como `fps_efectivos` **directamente**, con el comentario "los clips de la Fase B ya
vienen a la frecuencia real" — **ese comentario era falso**, no verificado contra el catálogo cuando se
escribió. Con el valor sin corregir, toda velocidad angular salía calculada como si cada fotograma estuviera
8 veces más separado en el tiempo de lo real, y el tamaño de la ventana de secuenciación (`margen_ancla_s *
fps`) se achicaba de 72 a 9 fotogramas — explica el motivo "serie demasiado corta o incompleta" en ese caso
puntual, y en general cualquier resultado de velocidad/orden de picos sobre ese clip quedaba inválido, no solo
el brazo.

**No es un bug del motor.** `engine/sequencing.py`, `engine/kinematics.py`, etc. hicieron exactamente lo que
se les pidió con el `fps_efectivos` que recibieron — el problema es que `procesar_video.py` les pasaba un
valor equivocado. La detección de cámara lenta (factor, escala temporal) ya existía
(`engine/ingest.py::evaluar`, decisión 001) pero `procesar_video.py` no la invocaba.

## Primer arreglo (insuficiente, reemplazado el mismo día)

Primera versión: `_factor_de_catalogo(nombre_archivo)` buscaba el archivo en `catalogo.csv`
(`KINETIQ_DATA_DIR`) y usaba su `factor_estimado`/`escala_temporal` reales. **Valentín lo objetó antes de
aplicarlo a producción:** solo funciona con clips del corpus de prueba. Un usuario sube `IMG_4012.MOV` sin
fila de catálogo, y el archivo solo no alcanza para saber si es cámara lenta — confirmado por Valentín con
sus propios clips: los slow-mo de iPhone declaran 30 fps aunque se hayan capturado a 240, se recorten donde
se recorten (PC o teléfono). El catálogo queda para el corpus de prueba, nunca como fuente del factor en
producción.

## Diseño final: el usuario declara el modo de captura

1. **`sesiones.modo_captura`** (migración `20261002000000`, no edita las ya aplicadas): `'normal'` |
   `'camara_lenta_120'` | `'camara_lenta_240'`, `not null` sin default — una declaración por sesión
   (especificación de frontend §5, campo "¿Cómo lo grabaste?"), no por video.
2. **`_factor_y_motivo(modo_captura, fps_contenedor)`** (reemplaza a `_factor_de_catalogo`) combina la
   declaración con el fps real del contenedor (normalizado NTSC, `engine.ingest.normalizar_fps`, ya
   existente):
   - `'normal'` → **nunca falla**: `fps_efectivos` = fps del contenedor, sean los que sean. Corrección de
     Valentín sobre la primera versión de esta decisión, que hacía fallar "normal" con un contenedor ≥ 120 fps
     — **equivocado**: "normal" significa "sin cámara lenta", no "fps bajo"; hay teléfonos que graban 120+ fps
     en modo normal, y eso es válido. R1 decide después si esos fps alcanzan para el análisis completo.
   - `'camara_lenta_120'` / `'camara_lenta_240'` → factor = fps objetivo ÷ fps del contenedor. Si el factor es
     un entero ≥ 1, `fps_efectivos` = el fps que declaró el usuario (120 o 240). Si no, el video queda
     `'fallido'`.
3. **`videos.motivo_fallo`** (migración `20261002000000`): **código cerrado** (`check`), no texto libre —
   hoy solo `'modo_captura_incompatible'`. El texto en lenguaje llano para el jugador lo resuelve el frontend
   (R2); el detalle técnico (fps del contenedor, factor calculado) va al log del contenedor, nunca a esta
   columna ni a lo que ve el usuario (corrección de Valentín sobre la primera versión, que iba a guardar
   texto libre). Motivos nuevos se agregan con una migración nueva cuando existan de verdad (video corrupto,
   formato no soportado, etc.), no se anticipan.
4. **`reportes_biomecanicos.escala_temporal_conocida` y `.origen_factor`** (mismas migración): el contrato
   JSON congelado (`schemas/reporte.py: Trazabilidad.escala_temporal_conocida`) nunca se persistía en la
   base — se agrega ahora, junto con este ajuste, como trazabilidad (R4) de dónde salió `fps_efectivos`.
5. **R1 aplicado de verdad, no solo registrado:** por debajo de 120 fps efectivos (independientemente del
   modo), no se corre la secuenciación completa — la fase de preparación todavía no está implementada (Etapa
   5), así que el video queda `'parcial'` con los metadatos reales, sin `reportes_biomecanicos` que sugiera
   un análisis completo que no corresponde.
6. **El catálogo queda solo para el corpus y las pruebas**, nunca como fuente del factor en producción — ya
   no interviene en `procesar_video.py` en absoluto.

## Verificado, no solo corregido en el código

- `tests/unit/test_procesar_video_factor.py` (15 casos, sin red): `'normal'` nunca falla en ningún fps
  probado (23,976 a 480), los factores de cámara lenta dan el entero esperado incluyendo normalización NTSC,
  y las combinaciones inconsistentes fallan con el código cerrado.
- `tests/integration/test_procesar_video_modo_captura_fallido.py`: un clip real de 25 fps del corpus público
  declarado `camara_lenta_240` (240/25 = 9,6, no cierra) deja el video `'fallido'`, con
  `motivo_fallo = 'modo_captura_incompatible'`, `fps_real` y `apto_fase_rapida` en `null` (no se guesea un
  valor ya demostrado no confiable), y ningún `reportes_biomecanicos`.
- `tests/integration/test_procesar_video_e2e.py` y `test_api_analisis_e2e.py`: declaran `camara_lenta_240`
  sobre un clip real de la Fase B (en vez de depender del catálogo) y conservan el nombre real del archivo
  dentro de una carpeta con UUID — con la corrección, vuelven a pasar y **ya no aparece el aviso de pico no
  finito**.
- **"Normal con ≥ 120 fps" se prueba solo con la función pura, y no es un descuido:** el iPhone con el que se
  grabó el corpus (iPhone 15 Pro Max) solo graba a 120 fps (o más) en modo cámara lenta; en modo normal el
  máximo es 60 fps. Por eso no existe —ni se puede producir con este equipo— un clip real grabado en modo
  normal con un contenedor de 120 fps o más. La rama se cubre con `_factor_y_motivo` (9 valores de fps de
  23,976 a 480) en vez de forzar o fabricar un archivo; el caso real de modo normal que sí existe (60 fps) se
  prueba de punta a punta (ver "Error inverso" más abajo). Otros teléfonos que sí graban 120 fps en normal
  quedan cubiertos por la misma función pura, sin haberse probado con un archivo propio.

## Metadatos de cámara lenta de un `.MOV` de iPhone, según ffprobe (2/10/2026)

Medido sobre los originales del corpus (iPhone 15 Pro Max, iOS 26.6.2, HEVC 1920x1080): **ningún campo del
archivo dice "cámara lenta" ni "240"**. No hay etiqueta, ni átomo `slo`/`slow` (se buscó en el contenedor), y
`com.apple.quicktime.full-frame-rate-playback-intent` vale `0` tanto en cámara lenta como en normal, así que
no discrimina. Lo único que cambia es indirecto y propio de este equipo:

| | normal 30 fps | normal 60 fps | cámara lenta 240 (original) | cámara lenta 240 (recorte `-c copy`) |
| --- | --- | --- | --- | --- |
| `r_frame_rate` / `avg_frame_rate` | 30/1 · 29,99 (VFR) | 59,94 · 59,96 (VFR) | 30/1 · 30/1 (CFR exacto) | 30/1 · 30/1 |
| `time_base` | 1/600 | 1/600 | 1/2400 | 1/19200 |
| formato de pixel | 10 bit, HLG, Dolby Vision | 10 bit, HLG, Dolby Vision | 8 bit SDR, bt709 | 8 bit SDR, bt709 |
| flujos en el contenedor | 7 (con metadatos por cuadro) | 7 | 3 | 2 |
| tags Apple (marca, modelo, ubicación, fecha) | sí | sí | sí | **no** (el recorte los pierde) |

- El enlentecimiento ya viene **horneado**: los paquetes del original de cámara lenta están separados 1/30 s
  (4861 cuadros en 162,03 s del contenedor = 30,0 fps); la duración real de captura (162,03 / 8 = 20,25 s) solo
  se conoce asumiendo el factor, el archivo no la declara.
- El recorte con `ffmpeg -c copy` (el procedimiento del protocolo) conserva el formato de pixel y el CFR de 30
  fps pero pierde la fecha, el modelo del equipo y los flujos de metadatos: deja menos pistas, no más.
- **Conclusión: nada útil para decidir el factor.** Las diferencias (8 bit SDR + CFR + 3 flujos para cámara
  lenta; 10 bit HLG + VFR + 7 flujos para normal) son un efecto colateral de cómo este iPhone graba cada modo
  con la configuración por defecto de video HDR, no un dato declarado: sirven, como mucho, para descartar un
  caso (un archivo 10 bit HLG con tasa variable **no puede** ser una cámara lenta exportada de este teléfono),
  nunca para confirmarla, y no valen para Android ni para un iPhone con el video HDR apagado. La declaración
  del usuario sigue siendo la única fuente del factor, como pide este diseño.

## Error inverso: declarar cámara lenta sobre un video normal (2/10/2026)

El caso que `_factor_y_motivo` **acepta a propósito** (240/60 = 4 y 240/30 = 8 son enteros ≥ 1): el usuario
declara `camara_lenta_240` sobre un video grabado en modo normal. Probado con tres clips reales:
el recorte propio de 60 fps (`20260924_VCR_saque_perfil_060_01_rep01.mov`, un saque de 5 s cortado con
`-c copy` del original de ~1 minuto grabado a propósito en modo normal; sumado a `catalogo.csv` con
`factor_estimado = 1`), `control_drive_30fps_01` y `saque_perfil_030`.

- **`normal` + 60 fps, de punta a punta contra Supabase real:** `fps_real = 60`, `apto_fase_rapida = false`,
  aptitud `solo_preparacion`, video `parcial`, sin reporte, sin `motivo_fallo` (no es un fallo).
- **Declarados `camara_lenta_240` — los techos de plausibilidad (Fleisig x 3) los marcan, los tres, pero con
  poco margen y por un solo segmento:**

| clip (contenedor → factor) | segmento que dispara el techo | velocidad medida / techo | resultado |
| --- | --- | --- | --- |
| recorte 60 fps (x4) | pelvis | 1783 / 1320 °/s (x1,35) | repetición no auditable |
| `control_drive_30fps_01` (x8) | torso (el ancla) | 2826 / 2610 °/s (x1,08) | "sin ancla", no auditable |
| `saque_perfil_030` (x8) | pelvis | 2385 / 1320 °/s (x1,81) | repetición no auditable |

  Con los fps correctos, ningún techo se dispara en ninguno. **Pero la detección es condicional, no una
  garantía:** salta porque el segmento más rápido de *estos* jugadores supera techo/factor (pelvis > 330 °/s
  reales con factor 4, torso > 326 °/s con factor 8). Un golpe más lento, o un `camara_lenta_120` sobre 60 fps
  (factor 2), pasaría los techos con un orden "correcto" y números inflados — un reporte limpio y falso. Los
  techos son una red de seguridad contra el ruido de detección, no un control de la declaración.
- Dejado como prueba automática (`tests/integration/test_techos_plausibilidad_declaracion_erronea.py`, 6
  casos, sin Supabase): caracteriza lo observado — correcta no dispara ningún techo; declarada de más, la
  repetición no sale auditable. Si cambian los techos o el pipeline y falla, es una señal real, no un detalle.

### Control adicional explorado y propuesta (NO implementada: DIFERIDA por decisión de Valentín, 6/10/2026)

**Estado:** diferida. No se implementa hasta contar con la calibración de su umbral con datos del Criterio 3
(variación entre sesiones del mismo atleta, `docs/resultados/criterio3.json`). Queda acá como propuesta, no
como pendiente de aprobación.

**Descartado con datos — banda de duración del gesto.** Se midió la duración real de la fase activa (ventana
alrededor del pico global donde la velocidad total supera el 10 % del máximo) en los 84 clips de 240 fps bien
declarados y en los tres clips normales bajo ambas declaraciones:

| | duración real de la fase activa (s) |
| --- | --- |
| corpus 240 fps, saque (n = 36) | mín 0,04 · p10 0,31 · mediana 0,39 · máx 0,89 |
| corpus 240 fps, drive (n = 24) | mín 0,05 · p10 0,09 · mediana 0,39 · máx 0,97 |
| corpus 240 fps, revés (n = 24) | mín 0,16 · p10 0,70 · mediana 0,92 · máx 1,39 |
| normales, declarados bien (60 / 30 / 30 fps) | 0,70 · 0,73 · 0,63 |
| normales, declarados `camara_lenta_240` | 0,18 · 0,08 · 0,11 |

Los valores de la declaración errónea (0,08–0,18 s) caen **dentro** del rango del corpus bien declarado
(drive: p10 = 0,09; saque: mín 0,04): una banda por gesto con esta definición de "duración" no separa. Una
duración útil necesita el marcador de fase independiente (inicio y fin del golpe), que sigue siendo trabajo
futuro (decisión 011) — no se improvisa un umbral.

**Propuesta: comparar contra el propio atleta** (CLAUDE.md §3, "comparar al jugador consigo mismo"). Un error
de declaración escala **los tres segmentos a la vez** por el mismo factor (x2, x4, x8), cosa que un cambio real
de técnica no hace. Con al menos una sesión previa del mismo atleta, gesto y encuadre, si los picos de
pelvis, torso y brazo de una sesión nueva superan (o quedan por debajo de) la mediana de las anteriores por un
factor ≥ 2 en los tres a la vez, el video queda `fallido` con un código nuevo
(`velocidad_inconsistente_con_historial`, migración nueva) y el frontend le pide al jugador confirmar el modo
de captura. Cubre justamente los casos que los techos dejan pasar (golpe lento, factor 2 o 4). **Límites,
declarados:** necesita historial — la primera sesión de un atleta solo tiene los techos, que es el caso de
menor protección; y su umbral (≥ 2) hay que calibrarlo con la variación entre sesiones que ya se midió en el
Criterio 3 antes de fijarlo, no se elige a ojo. Se implementaría junto con la comparación contra la sesión
anterior de la Etapa 5 (tarea 5.2), que ya necesita ese historial.

## Limitaciones a declarar en la tesis (Capítulos 6 y 7)

Registradas acá según la práctica del proyecto (esta decisión se suma a la lista de pendientes de redacción
de CLAUDE.md §5); no se edita ningún capítulo todavía.

1. **La detección del error inverso por techos de plausibilidad es condicional, no una garantía.** Cuando el
   usuario declara cámara lenta sobre un video grabado en modo normal, la combinación declaración + contenedor
   se acepta si el factor es un entero ≥ 1 (240/60 = 4, 240/30 = 8) — es lo esperado, no un fallo. Lo único
   que frena entonces un reporte limpio pero falso son los techos de plausibilidad (Fleisig × 3 por segmento),
   que saltan solo si el segmento más rápido supera techo/factor: en las tres pruebas reales saltaron, con
   márgenes de ×1,08 a ×1,81. **Un factor ×2** (p. ej. `camara_lenta_120` sobre un video de 60 fps) **o un
   golpe lento pueden pasar** los techos con un orden "correcto" y velocidades infladas. Se declara así: el
   sistema no detecta de forma confiable una declaración de modo de captura equivocada; la fuente del factor
   es la declaración del usuario.
2. **Sin historial, la protección es solo la de los techos.** El control contra el propio atleta (propuesta
   de arriba, diferida) necesita al menos una sesión previa; la primera sesión de un atleta es el caso de
   menor protección.
3. **El caso "normal con ≥ 120 fps" se probó solo con la función pura**, no con un archivo real: el equipo
   de grabación (iPhone 15 Pro Max) solo graba a 120 fps o más en cámara lenta.
4. **No hay detección de cámara lenta a partir del archivo.** Los metadatos de un `.MOV` de iPhone no
   traen ninguna marca de cámara lenta; las diferencias indirectas (8 bit SDR / CFR / 3 flujos) son un efecto
   de cómo este teléfono graba cada modo con la configuración de HDR por defecto, no un dato declarado, y se
   pierden o no aplican a otros equipos.

## Qué significa para la tarea 3 original (oclusión vs. problema de cálculo)

El `diagnostico_brazo_corpus.py` corre sobre la pose CACHEADA (extraída hace semanas por el pipeline oficial,
que sí calcula bien `fps_efectivos`), no por el camino con el bug. Su resultado (`docs/resultados/
diagnostico-brazo-corpus.json`, tabla en la bitácora) sigue siendo válido tal cual: representa el
comportamiento correcto del motor, no el bug. El bug era específico de `procesar_video.py` (código de la
tarea 4.5.3, no del motor ni del corpus ya extraído) y ya está corregido y verificado.
