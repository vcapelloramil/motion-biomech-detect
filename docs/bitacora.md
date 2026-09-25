# Bitácora de desarrollo

Registro de cierre de cada sesión de trabajo con Claude Code. Una entrada por sesión, la
más reciente arriba. Cada entrada anota: **qué se hizo**, **qué quedó pendiente** y el
**siguiente paso concreto**.

---

## 2026-09-25 — Fase B: extracción de pose, ventana anclada y corrección de E3 (motor 0.4.1)

**Rama:** `etapa/4-cinematica` (sin merge, sin tag). Motor `0.4.1`. `pytest -m "not slow"` →
**189 en verde**; los tests lentos que usan E3 sobre pose real (5) también pasan.

### Estado al cierre de la sesión

**Lo que se sostiene (medido con E3 0.4.1, 36 repeticiones propias, 1 jugador, 1 sesión):**
- Pelvis y torso NO se vieron afectados por el defecto de E3 (diferencia 0,0000 °/s entre 0.4.0 y
  0.4.1). Sus conclusiones se mantienen: orden pelvis→torso en el límite de resolución (desfases
  de ±4–13 ms; 1 fotograma = 4,17 ms), pelvis más rápida que el torso en el saque (1,15–1,46×),
  gradiente de gestos saque > drive > revés en ambos encuadres.
- El brazo, con la serie bien filtrada: p99 de ω a k=1 de 790–2165 °/s (mediana por grupo),
  caída k1→k8 de 1–10 %. La "anomalía del revés de tres cuartos" era el único grupo bien filtrado.
- **Patrón por encuadre (ancla de torso): brazo DESPUÉS del torso en saque de tres cuartos, drive
  de tres cuartos y revés de tres cuartos; brazo ANTES en drive de perfil (4/5) y revés de perfil
  (5/6).** Robusto al corte del codo entre 8 y 15 Hz en esos cinco grupos (en revés de perfil,
  a 6 Hz baja a 3/6); magnitud del adelanto
  dependiente del corte (drive perfil: −179 ms a 6 Hz, −33 ms a 15 Hz; revés perfil: −10 a −19 ms,
  casi simultáneo). **El saque de perfil NO es robusto:** con el codo a ≤ 8 Hz el brazo llega
  después (+62 a +67 ms, 0/3 con brazo primero); a ≥ 10 Hz llega antes (−58 a −67 ms, 2/3). n = 3.

**Lo que NO está resuelto / en revisión:**
- El pico global del brazo puede capturar la caída de la raqueta (preparación) y no el golpe
  (fotogramas de drive rep03/rep04). La ventana acotada del brazo **no se implementó**: Valentín
  quiere ver primero que el patrón por encuadre se sostenga con las magnitudes ya corregidas
  (ver arriba) antes de acotar algo que pueda enmascararlo.
- Referencia de Fleisig para el brazo (≈ 2368 °/s): en la tesis la tabla la etiqueta "Hombro"; un
  vector hombro→codo no ve la rotación axial del húmero, así que **podría no ser una referencia
  comparable** (y entonces "0,55× Fleisig" no significa nada). Por verificar contra el artículo.
- Umbral de salto imposible (0,5 torsos ≈ 62 m/s): sigue sin recalibrarse. Punto 2 pendiente.
- Decisión codo vs muñeca: NO se reabre en código; la justificación empírica de la decisión 008
  quedó invalidada y está registrada como **pendiente de redacción del Capítulo 4** en la
  decisión 010 (y con una nota de aviso en la 008).
- Sin merge/tag de la Etapa 4; 4.7 y 4.8 y el punto de decisión siguen pendientes (los umbrales
  aún no están congelados: no calibrar y medir sobre las mismas repeticiones).

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
