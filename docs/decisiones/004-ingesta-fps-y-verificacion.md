# Decisión 004 — Ingesta: dos verificaciones, factor externo y frecuencia efectiva

**Fecha:** 26 de agosto de 2026
**Estado:** vigente
**Afecta a:** Etapa 1 · contrato del reporte · catalogador · Capítulo 6

Continúa y lleva a código la [decisión 001](001-admision-corpus.md).

---

## El problema

Un FPS mal leído no produce ruido: produce un reporte "internamente coherente y
completamente falso" (tesis, 3.3.1.1). El orden de los picos de velocidad —el núcleo
del sistema— es inmune al desvío fijo y a la escala, pero **sí** lo arruina un FPS mal
leído (3.3.4.2). La ingesta es la única defensa. Hay que decidir cómo se lee la
frecuencia real, cómo se maneja el material de cámara lenta y cómo se clasifica cada
clip.

---

## Decisiones

### 1. Dos verificaciones independientes, ninguna suficiente sola

| Verificación | Herramienta | Qué detecta |
| --- | --- | --- |
| Metadatos | `ffprobe` (enriquece a OpenCV) + contraste interno | tasa declarada vs `nb_frames/duración` vs `avg_frame_rate` incoherentes |
| Unicidad de fotogramas | huella md5 exacta por fotograma (`engine/framehash.py`) | fotogramas duplicados que invalidan la información temporal |

Un archivo puede pasar una y fallar la otra (decisión 001). **No** se usa `mpdecimate`:
da falsos duplicados con cámara lenta buena.

### 2. OpenCV para el motor, ffprobe para el catalogador

- `engine/ingest.probe()` abre con **OpenCV** (tasa declarada, conteo, resolución) y,
  si `ffprobe` está en el PATH, **enriquece** con `r_frame_rate`, `avg_frame_rate`,
  `nb_frames` y `duration` del contenedor —más fiables para el contraste; el conteo de
  OpenCV es estimado en algunos códecs—.
- **`ffmpeg`/`ffprobe` es dependencia declarada del catalogador y de las pruebas de
  integración, no del núcleo del motor.** Sin ffprobe la ingesta sigue funcionando solo
  con OpenCV (con menos poder de contraste). Documentado en `backend/README.md`.

### 3. El factor de ralentización es externo, y `escala_temporal_conocida` viaja al reporte

Para material descargado el factor **no puede inferirse** de los metadatos (es
justamente el hallazgo de la decisión 001: los dos casos son indistinguibles). Se pasa
a mano o se toma de `catalogo.csv` (`factor_estimado`). `engine/ingest.evaluar()`
calcula `fps_efectivos = fps_declarados * factor` y **propaga la frecuencia de captura,
nunca la de reproducción**.

Cuando el factor es una estimación (cronometrada a ojo, decisión 001 paso 3), la escala
temporal **no es confiable**: sirve para el ORDEN de los picos, no para velocidades
absolutas. Para que el reporte no presente una estimación como un dato medido (regla
R3), se agregó **`escala_temporal_conocida: bool` a `Trazabilidad`** en el contrato
(obligatorio, sin default). Es un cambio al contrato congelado en la Etapa 0, hecho
antes de integrar nada a `main`.

### 4. Tabla de aptitud por frecuencia efectiva (plan 1.3)

| fps efectivos | `AptitudFaseRapida` | Decisión |
| --- | --- | --- |
| ≥ 240 | `COMPLETO` | análisis completo, incluido el impacto |
| 120–239 | `REDUCIDO` | apto; impacto con confianza reducida |
| 60–119 | `SOLO_PREPARACION` | solo fase de preparación |
| < 60 | `RECHAZADO` | no se analiza |

**Normalización de tasas NTSC.** Antes de clasificar, `evaluar()` ajusta la tasa
declarada a su valor nominal si cae a menos de 0.5% de una tasa estándar (24, 25, 30,
48, 50, 60, 96, 100, 120, 240). Un archivo a 59.94 fps (60000/1001) es material "60p":
tratarlo como `< 60` y rechazarlo sería un artefacto de la aritmética de video, no una
decisión. `fps_declarados_normalizado` viaja en el `ResultadoIngesta` y el catalogador
lo reporta como nota informativa cuando difiere del crudo.

**`< 60` es un resultado, no una excepción.** `evaluar()` devuelve un
`ResultadoIngesta` con `aptitud == RECHAZADO` y `motivo_rechazo`, para que el rechazo
quede registrado y sea trazable (R4). La excepción (`IngestaError`) se reserva para
archivos que no abren o están corruptos.

### 5. Regla de combinación de las dos verificaciones (catalogador)

El "uso" final es la intersección de la aptitud por fps efectivos y la categoría de
unicidad:

- `RECHAZADO` (fps) → `rechazado`, sin importar la unicidad.
- `duplicacion_sistematica` (unicidad) → **cae a `E1-E2`**, sin importar los fps.
- `repeticion_aislada` → se agrega " (con reservas)".
- resto → `E1-E4` o `E1-E2 (solo preparacion)` según la aptitud.

### 6. El catalogador no toca `catalogo.csv`

`catalogo.csv` tiene campos curados a mano (factor, gesto, observaciones de
verificación). El catalogador **lee** de ahí lo que no puede inferir y **escribe
aparte** `catalogo-verificado.csv` con lo computado. Avisa de discrepancias (uso o
`fps_efectivos` que no coinciden, inconsistencias de metadatos, filas con cantidad de
columnas incorrecta, y **filas del catálogo sin archivo correspondiente**). Sobre una
fila mal formada usa lo que puede leer pero no hace cruces semánticos contra ella.

Se corre desde `backend/`: `python -m app.catalogador` (usa `KINETIQ_DATA_DIR`).
`--sin-hash` omite la verificación de unicidad para una primera pasada rápida.

### 7. Se cataloga `segmentos/` y `control/`, no `compilaciones/`

`fase-a/compilaciones/` contiene los videos largos de origen de los que se recortan los
segmentos. No son unidades de análisis: el catalogador salta cualquier subcarpeta
llamada `compilaciones` por defecto (`--incluir-todo` para no saltearla). El "uso" para
`SOLO_PREPARACION` se etiqueta `"E1-E2 (solo preparacion)"` —**sin tilde a propósito**:
es un token que viaja al CSV y se compara contra `catalogo.csv`, se mantiene ASCII para
no depender de la codificación de la consola en Windows/Git Bash. Alineado con el
vocabulario del `catalogo.csv` (`E1-E4` = completo, `E1-E2` = uso limitado).

---

## Consecuencias

- El material de gestos en cámara lenta (Zverev 25×20=500, drive 60×8=480, revés
  25×12=300 fps efectivos; escala desconocida; sin fotogramas duplicados) se cataloga
  como **apto para fase rápida (`E1-E4`) con `escala_temporal_conocida = False`**. Los
  controles a 30 fps → `rechazado`; a 60 fps → `solo preparación`.
- La huella md5 por fotograma sobre la ventana central de un clip de ~30 s a 1080p
  tarda ~1 min; catalogar la Fase A actual (12 clips, los rechazados no se hashean) con
  hash completo tarda ~2 minutos. Es una herramienta offline de admisión; si el corpus
  crece mucho, la mitigación es submuestrear la ventana o hashear una versión reducida
  (no se hace ahora: "no optimizar antes de medir").
- **Para el Capítulo 6:** que la frecuencia declarada de un archivo no refleje la de
  captura es un modo de falla que la literatura de pose en deporte no discute (decisión
  001). Queda documentado como riesgo del sistema y limitación del material público.

## Pendiente

- Con el corpus real ampliado a 12 clips se retiraron las pruebas sintéticas de 30/60
  fps y de oclusión. Quedan dos sintéticas sin equivalente real: la de **duplicación
  sistemática de fotogramas** (ningún clip del corpus la tiene) y la de **coherencia
  temporal** (240 fps vs su ralentizado del mismo gesto), que depende de la Fase B
  (plazo 22/9). Marcadas en el código.
