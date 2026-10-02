# Decisión 020 — Bug real: `procesar_video.py` ignoraba la cámara lenta (fps efectivos x8 mal)

**Fecha:** 2 de octubre de 2026
**Estado:** corregido y verificado contra datos reales
**Afecta a:** `backend/app/procesar_video.py` (tarea 4.5.3) · R1 (CLAUDE.md §2) · decisión 019 (semilla de la
API) · investigación de la tarea 4.5.4 (frecuencia del brazo no auditable, pedida por Valentín)

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

## La corrección

1. **`_factor_de_catalogo(nombre_archivo)`** (nueva función en `procesar_video.py`): busca el archivo en
   `catalogo.csv` (`KINETIQ_DATA_DIR`) y devuelve su `factor_estimado`/`escala_temporal` reales si existe la
   fila; si no (un upload real sin antecedente — el caso futuro de la Etapa 8), devuelve `factor=1.0` **sin
   inventar nada**, documentado como límite conocido: la detección automática de cámara lenta para uploads
   nuevos sigue sin resolver, depende de la pantalla de carga real (Etapa 8) o de que el usuario confirme el
   factor, y no se improvisa acá.
2. **`procesar_video` ahora llama a `engine.ingest.evaluar(md, factor=..., escala_conocida=..., origen_factor=...)`**
   en vez de usar `md.fps_declarados` a secas, y usa `ingesta.fps_efectivos` (no `md.fps_declarados`) en
   todos lados: al pasarle la frecuencia al backend de pose, y al guardar `videos.fps_real` y
   `videos.apto_fase_rapida`.
3. **R1 aplicado de verdad, no solo registrado:** si `ingesta.fps_efectivos < 120`, **no se corre la
   secuenciación completa** — la fase de preparación (lo único que R1 permitiría analizar por debajo de 120
   fps) todavía no está implementada (es de la Etapa 5), así que el video queda `estado = 'parcial'` con los
   metadatos reales y ningún `reportes_biomecanicos` que sugiera un análisis completo que no corresponde.
   Antes de esta corrección, `procesar_video.py` corría la secuenciación completa sin importar el fps,
   violando R1 en silencio.

## Verificado, no solo corregido en el código

- `tests/integration/test_procesar_video_e2e.py` y `test_api_analisis_e2e.py` tenían el mismo problema que
  expuso el bug: subían el clip a Storage con un nombre aleatorio (UUID), así que `procesar_video.py` nunca
  podía encontrarlo en el catálogo. Corregido para conservar el nombre real del archivo dentro de una carpeta
  con UUID (`{usuario}/{uuid}/{nombre_real}.mov`) — necesario para que la prueba ejercite el camino real, no
  uno que accidentalmente evita el bug por otro motivo.
- Con la corrección, ambas pruebas de punta a punta contra Supabase real vuelven a pasar, y **ya no aparece
  el aviso de pico no finito** para este clip — confirma que era exactamente este bug, no un problema del
  motor ni de los datos.

## Qué significa para la tarea 3 original (oclusión vs. problema de cálculo)

El `diagnostico_brazo_corpus.py` corre sobre la pose CACHEADA (extraída hace semanas por el pipeline oficial,
que sí calcula bien `fps_efectivos`), no por el camino con el bug. Su resultado (`docs/resultados/
diagnostico-brazo-corpus.json`, tabla en la bitácora) sigue siendo válido tal cual: representa el
comportamiento correcto del motor, no el bug. El bug era específico de `procesar_video.py` (código de la
tarea 4.5.3, no del motor ni del corpus ya extraído) y ya está corregido y verificado.

## Pendiente, con límite declarado

Detección automática del factor de cámara lenta para un video SIN fila de catálogo (un upload real de un
usuario, Etapa 8): no resuelta. `_factor_de_catalogo` devuelve `factor=1.0` en ese caso, lo cual es seguro
(R1 rechaza o limita el análisis si el fps declarado resulta insuficiente) pero **no detecta** una cámara
lenta que el usuario no declare — queda abierto para el diseño de la pantalla de carga real.
