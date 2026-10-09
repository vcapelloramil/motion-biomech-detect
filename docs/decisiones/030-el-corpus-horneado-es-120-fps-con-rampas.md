# Decisión 030 — El corpus horneado no es de 240 fps: es un remuestreo a ~120 fps con rampas de velocidad (corrige la magnitud de la 029)

**Fecha:** 9 de octubre de 2026
**Estado:** vigente en lo **medido** (16 originales reales, 15 pares alineados por contenido, 88 repeticiones ubicadas). El **recálculo no se hizo**: su plan está
en `docs/plan-recalculo-corpus-tasa-real.md`, a aprobar por Valentín.
**Afecta a:** todo lo medido del corpus (Criterios 1 y 3, techos de plausibilidad, velocidades y ms) · decisión 029 (su escala ×1,2 queda **superada**: es ×2,0) ·
decisión 020 (el factor 8 del horneado) · `catalogo.csv` · Capítulos 4, 6 y 7 · R1

---

## El problema

La decisión 029 midió que el iPhone captura con una tasa real media de ~199 fps (no 240) y estimó, por simulación, que las velocidades del corpus estaban sobreestimadas
×1,2. Esa estimación **suponía** que cada fotograma horneado era un fotograma real consecutivo. Valentín descargó los **16 originales reales** (HEVC, marcas de tiempo
reales, tasa real media **199,9 a 201,0 fps**) y se pudo comprobar esa suposición contra los archivos horneados con que se midió todo. **No se cumple.**

## Qué se midió

### Los 16 originales reales (`Desktop\corpus-originales-reales`, sin tocar; no se suben al repositorio)

| | |
| --- | --- |
| Códec / resolución | HEVC, 1920×1080, sin rotación |
| Marcas de tiempo | reales y variables: nominal 239,98 fps, **real media 199,9–201,0 (mediana ~200,6)**, 16,3–16,7 % de fotogramas perdidos |
| ¿Alguno horneado a 30 fps? | **Ninguno** |
| Pre-roll oculto | 0, salvo `IMG_6391` (89) |
| **`IMG_6391.mov`** | **No es la grabación completa**: 2503 fotogramas (12,5 s, 81 MB) contra ~15 200 esperados; es el único `.mov` en minúscula. **Hay que volver a bajarlo.** |

### El emparejamiento

- **16 de 16 pares exactos por fecha y hora de creación** (`com.apple.quicktime.creationdate`). Los 2 horneados sin par (`saque_perfil_030_01`, `saque_perfil_060_01`) son los
  **controles de velocidad normal**: nunca se hornearon, no hay nada que recuperar y no entran al recálculo. (Se bajaron 16 archivos, no 18; los 16 son los de cámara lenta, y alcanzan.)
- El horneado trae **el 46 %** de los fotogramas del original real (0,460–0,463) y dura 3,07 veces más.

### Los fotogramas horneados NO corresponden uno a uno con los reales

Alineados por contenido (miniaturas de 64×36, mejor coincidencia, orden monótono en el 99,1–99,9 % de los pasos) en los **15 pares completos**:

| | Valor |
| --- | --- |
| Fotogramas reales por fotograma horneado, en la **meseta** | **1,665 a 1,675** (mediana 1,67), idéntico en los 15 pares |
| Equivale a | un muestreo uniforme a **120,2 fps en tiempo real**, reproducido a 30 fps: cámara lenta de **4×**, no de 8× |
| Extremos del archivo | **rampas a velocidad normal**: 6,6–6,7 reales por horneado (= tiempo real a 30 fps) al principio y al final |
| Fotogramas horneados **repetidos** | 5,7 a 11,4 % (el export elige el fotograma real más cercano a una grilla de 120 Hz y, cuando falta uno, repite) |
| Tramos en la meseta | 87–92 % de las ventanas de 200 fotogramas |

### Dónde caen las repeticiones

Las **88 repeticiones** ubicadas (de 94; faltan las 6 de `saque_trescuartos_240_02`, por `IMG_6391`) son cortes contiguos del horneado (la ventana tiene el largo del recorte
en las 88). **86 de 88 (98 %) caen enteras en la meseta**; **2 empiezan dentro de una rampa**: `saque_perfil_240_01_rep01` y `reves_perfil_240_02_rep01`, el primer tercio a 3,4 y a 6,7 reales
por horneado. Los 7 recortes restantes del catálogo no entran: las 6 de `IMG_6391` y la de velocidad normal.

## Consecuencias para lo ya medido (reemplaza la escala de la decisión 029)

El motor supuso 240 fps (factor 8 sobre 30 fps). El muestreo real del corpus es **120 fps**. Cada intervalo entre fotogramas es el doble de lo supuesto:

| Qué | Efecto |
| --- | --- |
| **Velocidades absolutas** (cap. 7, techos de plausibilidad, Fleisig) | **×2,0 sobreestimadas** (no ×1,2 como decía la 029). Un pico de 1500 °/s medido es ~750 °/s reales. |
| **Intervalos en ms** (Δ pelvis-torso, `instante_pico_torso_desde_max_sep_ms`) | **×0,5 subestimados**: un intervalo medido de 50 ms es de 100 ms. |
| **Ángulos** (Criterio 2) | **No cambian.** |
| **Resolución temporal** | **120 fps, no 240**: un fotograma son **8,3 ms**, no 4,2. La tolerancia "1 fotograma" del Criterio 1 son 8,3 ms. |
| **R1 y la aptitud** | El corpus es "reducido" (120–239), **en el borde inferior**, no "completo". Cualquier texto que diga "240 fps" para estos datos es incorrecto. |
| **`escala_temporal_conocida = true`** del catálogo | **Falso** para los 97 clips: ni la tasa nominal ni el factor eran los reales. |
| **Orden de los picos** | Se mide en fotogramas y la meseta es uniforme, así que **el orden real no cambia**; sí cambia lo que significa "ordenable" (8,3 ms por fotograma) y los puntos de corte del filtro (E3 elige el corte en Hz con la tasa equivocada). |
| **Techos de plausibilidad** | Con velocidades **reales la mitad**, "ningún techo salta con la declaración correcta" se cumple de sobra, y las **detecciones del error inverso** que se apoyaban en pasar un techo (decisión 020, márgenes de 1,08×) **hay que revisarlas con la escala corregida**. |
| **Declarar `camara_lenta_120`** sobre estos archivos | Daría factor 4 y **120 fps: la tasa correcta**. La declaración "240" que se usó era la equivocada para un horneado de iPhone. |

La **simulación de la 029 sigue siendo válida** como medida del efecto de la *irregularidad* de las marcas (±4–8 ms de corrimiento de los picos, saltos del brazo), pero **no** como medida de la escala: la escala real del corpus es ×2.

## Lo que sí tenía razón la 029

Que una tasa asumida invalida las velocidades absolutas y que RNF-01 ("el sistema lee la tasa real del archivo y nunca la asume") es necesario. Aquí se ve más grave: el corpus se asumió a **240 y el muestreo real era 120**, y la declaración "cámara lenta 240" convertía en
"conocida" una escala que estaba mal por un factor 2.

## Trabajo hecho en el motor (obligatorio para el flujo real, aprobado por Valentín)

- **`probe()` lee los fotogramas visibles** (descarta el pre-roll), corrige `nb_frames` y `duracion_s`, y mide la **tasa real media** de las marcas: un recorte de Archivos pasa de "479 fotogramas / 169,28 fps"
  a **398 fotogramas, 198,87 fps reales (239,98 nominales), 81 de pre-roll**. Los horneados del corpus no cambian.
- **`evaluar()` usa la tasa real media** en archivos con marcas de tiempo real (normalizada solo si cae a menos de 0,5 % de un estándar: 59,94 → 60).
- **Videos verticales:** `probe()` e `iterar_fotogramas()` activan la orientación automática de OpenCV (antes salían acostados).
- **`procesar_video._tasa_del_archivo`:** con marcas en tiempo real el factor es 1 y la escala es conocida (**medida**), con `origen_factor = "marcas_de_tiempo"`; `modo_captura` deja de definir la tasa.
  Un archivo convertido por el teléfono (100 fps) deja de fallar con `modo_captura_incompatible`: lo atrapa R1.
- **Regularización temporal** (`engine/regularizacion.py`): interpola las poses a una grilla uniforme a 240 Hz antes de E3, **cuenta los puntos interpolados** y los informa (**contrato v1.1**: `fps_nominal`,
  `fotogramas_perdidos_pct`, `regularizacion`; un reporte 1.0 sigue siendo válido). Probada de punta a punta sobre un recorte real (398 fotogramas, 82 interpolados = 17,1 %).
- **29 pruebas nuevas** (regularización, tasa del archivo, lectura de E0 con un clip vertical sintético, contrato v1.1, funciones del alineamiento); suite rápida: **366 pasan**.

## Pendiente

1. ~~Volver a bajar `IMG_6391`~~ **Resuelto por decisión de Valentín (9/10): `IMG_6391` es un video corto en el iPhone, no se vuelve a bajar.** Las 6 repeticiones de `saque|trescuartos|toma 02` **quedan afuera** del recálculo (anotado). Discrepancia no investigada: el horneado de esa toma tiene 7011 fotogramas, que a la razón de los otros 15 pares corresponderían a ~15 200 fotogramas reales; el real trae 2503.
2. ~~Aprobar el plan de recálculo~~ **Aprobado el 9/10:** pre-registro tal cual; **solo el Paso A y después de la prueba de punta a punta**; el Paso B, opcional, después del MVP.
3. **Reetiquetar** `escala_temporal` en `catalogo.csv` y marcar el `factor_estimado = 8` como "supuesto; el muestreo real es ~120 fps" (fuera del repositorio).
4. **Motivo de fallo propio** para el archivo convertido por el teléfono (migración) y la integración de la regularización en el reporte persistido (tarea 5.4): **entran al flujo de punta a punta** (decisión de Valentín, 9/10), son las piezas 1–3 del plan.
5. **Capítulo 7**: lo registrado en `docs/tesis/correcciones-pendientes-capitulo-4.md`.
