# Bitácora de desarrollo

Registro de cierre de cada sesión de trabajo con Claude Code. Una entrada por sesión, la
más reciente arriba. Cada entrada anota: **qué se hizo**, **qué quedó pendiente** y el
**siguiente paso concreto**.

---

## 2026-08-27 (fix) — Detector de inversión de profundidad (z)

**Rama:** `fix/inversion-z` (desde `main`). Fix a E2/E3 ya mergeadas, con su propia
etiqueta `v0.3.1`, antes de seguir con la Etapa 4.

Surgió de la validación cualitativa de la Etapa 4: el saque `zverev_saque_lateral_02`
daba un pico de brazo de 24 932 °/s. Investigado (decisión 009): `CODO_DER` **invierte
el signo de `z`** en el frame 566 (+0,098 → −0,050 m) y queda invertida hasta ~573.
Confianza 0,65 (pasa el umbral de 0,5) y desplazamiento 3D 0,31 torsos (< 0,5): **ni la
baja confianza ni el salto imposible lo marcaban.**

### Qué se hizo

- `engine/validation.py`: `detectar_inversiones_z` — cambio de signo de `z` + `|Δz| /
  torso > 0,18` + dominado por `z` (`|Δz| > 1,8·|Δxy|`). Detectada la entrada, extiende
  la franja mientras `z` mantiene el signo invertido (tope 25 fotogramas).
  `ResultadoValidacion.inversiones_z`.
- `engine/preparacion.py`: excluye toda la franja `[frame_desde, frame_hasta]` antes de
  filtrar (junto con baja confianza y saltos).
- Calibrado con el único caso real (`zverev_02` frame 566); deja pasar los dos falsos
  candidatos del mismo clip (dithering de z cerca del plano). Umbrales a revisar con la
  Fase B.
- Versión del motor → `0.3.1`. Decisión 009.

### Pruebas

`pytest -m "not slow"` → **121 en verde** (6 nuevas de inversión de z). `-m slow` → 14,
incluida `test_inversion_z_corpus.py` (el detector atrapa el frame 566 real y la franja
566–573 queda como `TramoExcluido` en E3).

### Siguiente paso concreto

Merge `fix/inversion-z` → `main` con `v0.3.1`, traer `etapa/4-cinematica` sobre esa base,
y seguir esperando la Fase B para 4.7/4.8 y el punto de decisión.
## 2026-08-27 (sesión 3) — Etapa 4: Cinemática y secuenciación (arranque, 4.1–4.6)

**Rama:** `etapa/4-cinematica` (desde `main`). **La Etapa 4 NO se cierra en esta sesión.**
**Modelo:** Sonnet 5 Medio.

Lecturas previas (convención): `capitulo-3` §3.3.3 y §3.3.4.1–§3.3.4.5. Confirmado con
Valentín: se construyen 4.1–4.6 (+ 4.6b con caveat en el reporte) usando el corpus
público; se difieren 4.7 (Criterio 1), 4.8 (Criterio 2) y el punto de decisión hasta
tener la Fase B. Lado dominante: columna nueva en `catalogo.csv`, sin default.

### Qué se hizo

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

### Pendiente

- **Revisar `brazo = HOMBRO→MUNECA` → `HOMBRO→CODO`** (la evidencia lo recomienda; el
  vector se aprobó como muñeca — decisión de Valentín, o hacerlo configurable).
- **`reves_lateral_01`:** el catálogo dice Federer zurdo, pero **Roger Federer juega de
  derecha**. `lado_dominante` quedó vacío a la espera de confirmación. Es exactamente el
  caso que la columna sin-default busca evitar.
- 4.7 / 4.8 / punto de decisión: Fase B.
- Calibrar `find_peaks` con más material; elegir "pico dominante plausible" en vez de
  descartar la serie si el más alto es implausible.
- La rama `etapa/4-cinematica` **queda abierta**, sin merge ni tag, hasta cerrar la etapa.

### Siguiente paso concreto

Definir con Valentín: (a) `brazo` codo vs muñeca vs configurable; (b) handedness de
`reves_lateral_01`. Después, esperar la Fase B para 4.7/4.8 y el punto de decisión.
Mientras tanto, la Etapa 4 no avanza más (no tiene sentido pulir un detector cuyos
criterios de éxito todavía no se pueden medir — precondición del plan).

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
