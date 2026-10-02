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
- **No hay en el corpus ningún clip real de un solo golpe grabado en modo normal** (todos los recortes de la
  Fase B son cámara lenta) para probar de punta a punta "normal con fps alto → análisis completo" contra un
  archivo real — se prueba con la unidad pura (`_factor_y_motivo`) en vez de inventar o forzar un archivo que
  no existe; anotado así en el propio test, no silenciado.

## Qué significa para la tarea 3 original (oclusión vs. problema de cálculo)

El `diagnostico_brazo_corpus.py` corre sobre la pose CACHEADA (extraída hace semanas por el pipeline oficial,
que sí calcula bien `fps_efectivos`), no por el camino con el bug. Su resultado (`docs/resultados/
diagnostico-brazo-corpus.json`, tabla en la bitácora) sigue siendo válido tal cual: representa el
comportamiento correcto del motor, no el bug. El bug era específico de `procesar_video.py` (código de la
tarea 4.5.3, no del motor ni del corpus ya extraído) y ya está corregido y verificado.
