# Decisión 005 — Percepción de pose: contrato intercambiable, MediaPipe por defecto

**Fecha:** 27 de agosto de 2026
**Estado:** vigente
**Afecta a:** Etapa 2 · Etapa 3 · Etapa 4 · contrato del reporte (`backend_pose`)

Lleva a código la decisión del apartado 4.4.3 de la tesis.

---

## El problema

El stack original decía "YOLOv8-Pose para pose 3D". Es incorrecto: YOLOv8-Pose son
**17 puntos (x, y, visibilidad), sin profundidad — es un detector 2D** (§3.3.2.3,
§4.4.3). Hay dos vías válidas: **A** (YOLOv8-Pose 2D + un modelo de elevación
temporal) y **B** (MediaPipe Pose, 33 puntos, 3D directo, una sola dependencia).

## Decisiones

### 1. Contrato interno de percepción, dos implementaciones sobre él

`engine/pose/base.py` define `PoseBackend` (ABC): cada backend implementa
`estimar_frame(frame_bgr, indice) -> PoseFrame`; el recorrido y el ensamblado de la
`SecuenciaPose` los da la clase base. E3/E4 reciben siempre la misma estructura sin
saber qué backend se usó.

### 2. MediaPipe Pose por defecto

`MediaPipeBackend` es el backend del MVP: tridimensionalidad de extremo a extremo
con una sola dependencia, 33 puntos (incluye mano → mitiga parcialmente la
limitación de rotación de hombro de §3.3.3.4), y el mejor de los 3D directos en
Rode et al. (2025).

### 3. `static_image_mode=True` por defecto

Cada fotograma se estima por separado, sin el suavizado temporal interno de
MediaPipe. La señal sale lo más cruda posible; el filtrado de fase cero lo hace E3,
que es quien debe hacerlo (§3.4.2.6). El modo con tracking queda por configuración.
`model_complexity=2` por defecto (es análisis offline; la precisión importa más que
la velocidad).

### 4. Vía A (YOLOv8-Pose) — diferida

Esta etapa construye la interfaz, el mapa canónico, `MediaPipeBackend` y un
`FakeBackend`. La Vía A real (ONNX + modelo de elevación + depuración de dos
etapas) se implementa cuando el punto de decisión de la Etapa 4 diga que hace
falta: es el plan de repliegue (§3.3.2.9). El `FakeBackend` **también simula el
caso 2D-solo** (`dims=2`, `z=None`), así que la interfaz ya queda ejercitada contra
ese escenario.

### 5. Mapa articular canónico

`engine/pose/articulaciones.py`: `ArticulacionCanonica` (19 valores) + tablas
`MEDIAPIPE_A_CANONICO` (33→canónico) y `COCO_A_CANONICO` (17→canónico). El core (13
articulaciones) lo entregan ambos; los puntos de mano y pie solo MediaPipe. Los
laterales `IZQ`/`DER` son los que etiqueta el modelo (izquierda/derecha anatómica
del jugador). `SecuenciaPose.dims` (2 ó 3) le dice al motor si `z` está poblado.

### 6. Coordenadas: imagen normalizada + z relativo

`x, y` en `[0, 1]` (esquina superior izquierda = 0,0). `z` = profundidad relativa
de MediaPipe, o `None` en 2D. `confianza` en `[0, 1]` (para MediaPipe, la
`visibility` del landmark). Los `pose_world_landmarks` métricos de MediaPipe quedan
disponibles para agregarlos en E4 si los ángulos 3D los necesitan.

### 7. Caché de coordenadas — `KINETIQ_CACHE_DIR`

`engine/pose/cache.py` guarda la `SecuenciaPose` en `.pose.npz` + `.pose.json`. La
carpeta se toma de `KINETIQ_CACHE_DIR` (entorno o `backend/.env`); si no está, se
usa `backend/.cache/` (ignorada por git). A diferencia del corpus, la carpeta se
**crea** si no existe: es contenido regenerable. La clave de caché incluye el hash
de la configuración del backend; al cargar se compara una firma rápida del video
(tamaño + mtime + primeros 64 KB) y si cambió, la caché se considera vencida.

### 8. `escala_temporal_conocida` y el umbral de "salto imposible"

El material descargado no tiene escala métrica. `engine/validation.py` expresa el
umbral de salto imposible en **fracciones de la longitud del torso** (distancia
cadera-hombro), que es la regla interna: estable (§3.3.3.2) y sin depender de una
escala que no tenemos.

---

## Consecuencias

- **Velocidad de inferencia medida** (tarea 2.6, primer dato del indicador §2.4):
  con `static_image_mode=True` + `model_complexity=2` sobre 1080p en CPU
  (MediaPipe-Python no usa la GPU), **~3,6 fotogramas/segundo** (~280 ms/frame).
  Ver `docs/resultados/e2-velocidad-inferencia.json`. Un clip de ~750 fotogramas
  tarda ~3–4 min; el corpus completo, ~40 min, **una sola vez** (después la caché).
  Si en E4 el tiempo molesta, las palancas son: `model_complexity=1`,
  `static_image_mode=False` (tracking), o reducir resolución antes de inferir. No
  se toca ahora.
- El `backend_pose` del contrato del reporte se llena con `backend.version`
  (p. ej. `"mediapipe-0.10.18"`).
- La Vía A, cuando se implemente, solo tiene que cumplir `PoseBackend` y traducir
  sus 17 puntos con `COCO_A_CANONICO`; nada de E3/E4 cambia.
