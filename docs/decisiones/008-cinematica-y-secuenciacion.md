# Decisión 008 — Cinemática y secuenciación (pasos 4.1–4.6) y hallazgos sobre corpus público

**Fecha:** 27 de agosto de 2026
**Estado:** vigente — **la Etapa 4 NO está cerrada**
**Afecta a:** Etapa 4 · contrato del reporte (`secuenciacion`, `metricas`) · Capítulos 6 y 7

Lleva a código los apartados §3.3.3 y §3.3.4.1–§3.3.4.5. Los pasos **4.7 (Criterio 1),
4.8 (Criterio 2) y el punto de decisión** quedan diferidos hasta tener el conjunto
propio de la Fase B; esta decisión cubre solo el arranque (4.1–4.6b) y una
**validación cualitativa temprana** sobre el corpus público.

---

## 1. Decisiones de diseño (4.1–4.6)

### Segmento del reporte ↔ articulaciones (§3.3.3.1)

| Segmento | Vector director |
| --- | --- |
| `pelvis` | eje `CADERA_IZQ → CADERA_DER` |
| `torso` | eje `HOMBRO_IZQ → HOMBRO_DER` |
| `brazo` | `HOMBRO_{dom} → MUNECA_{dom}` |

`{dom}` = lado dominante, que se lee de **`catalogo.csv`, columna nueva
`lado_dominante`** (`der` / `izq`). **No hay valor por defecto**: un zurdo con el
default `der` mediría el brazo equivocado sin que salte ningún error. Si la columna
está vacía para un clip, `analizar` falla con un mensaje claro (o se pasa `--lado`).

### Velocidad angular de un segmento (4.3)

`ω(t) ≈ ∠(u(t), u(t+1)) · fps`, con `u` el vector director unitario. Escalar,
sin elegir plano — evita problemas de *unwrap* y de qué plano medir en una vista
lateral. Para clips con `escala_temporal_conocida = False` el valor absoluto es
aproximado (fps estimado); el **instante** del pico no se afecta (§3.3.4.2 fila 6).

### Ángulos articulares (4.1)

Ángulo entre tres puntos (producto escalar) para rodilla (`CADERA–RODILLA–TOBILLO`),
codo (`HOMBRO–CODO–MUNECA`) y tronco-muslo (`HOMBRO–CADERA–RODILLA`), ambos lados.
Inmune al desvío fijo y a la escala (§3.3.4.2 fila 2).

### Detección de picos y no auditables (4.4)

`scipy.signal.find_peaks` con prominencia mínima (absoluta y relativa) y separación
mínima; el pico dominante es el más alto. Un pico se marca **no auditable** (no se
reporta ni se estima — R3) si:

- cae dentro de un `TramoExcluido` de E3 de alguna articulación del segmento, o
- supera el **techo de plausibilidad física del segmento**.

**Techo por segmento, anclado a la literatura** (no un número a ojo). Velocidades
angulares máximas de Fleisig et al. (2003) en tenistas de nivel mundial
(§3.4.2.2): pelvis 440 °/s, torso 870, hombro ≈2368 (`brazo`). El techo es
`Fleisig × MARGEN_PLAUSIBILIDAD`, con **`MARGEN_PLAUSIBILIDAD = 3`**.

Criterio del margen: (a) el factor de ralentización de los clips descargados es
una estimación (`escala_temporal_conocida = False`), así que el fps efectivo —y
con él ω— tiene incertidumbre de un factor cercano a 2; (b) el ruido de MediaPipe
(146 mm de error 3D, §3.3.2.5) infla las tasas instantáneas. Los valores de
Fleisig ya son el máximo de la élite mundial: un amateur no debería acercarse, así
que ×3 deja margen amplio para señal legítima y sigue siendo un orden de magnitud
por debajo de los *glitches* observados (15 000–42 000 °/s).

| segmento | Fleisig (°/s) | techo (×3, °/s) |
| --- | --- | --- |
| pelvis | 440 | 1 320 |
| torso | 870 | 2 610 |
| brazo | 2 368 | 7 104 |

Si a una repetición le falta el pico auditable de algún segmento → `auditable =
False`, sin orden observado.

### Segmentación (4.6)

Tres caminos: (1) sugerencia automática por valles de "quietud" (velocidad total
por debajo del 10 % del máximo, sostenida) — para la Fase B con las pausas del
protocolo; (2) override manual con `[(desde_s, hasta_s)]`; (3) fallback "todo el
clip = 1 repetición". Los clips del corpus público ya vienen pre-cortados a ~1
repetición, así que se usa (3)/(1).

### Agregación (4.6b) con caveat en el reporte

`ResumenSecuenciacion` incluye orden predominante, repeticiones correctas y
dispersión del instante del pico de torso. Cuando corre sobre corpus público lleva
un campo `nota` con el texto: *"Corpus público (sin repeticiones controladas del
mismo jugador): estos agregados son una validación cualitativa temprana, NO la
medición del Criterio 1 ni del Criterio 3"*. El caveat viaja en la estructura, no
solo en el código.

---

## 2. Validación cualitativa sobre el corpus público — resultados

Corrida de `python -m app.analizar` sobre los 5 clips públicos aptos. Se registran
**tal cual salieron**, sin ajustar nada. La tabla es la primera pasada (ventana =
todo el clip) para comparar los dos `brazo_via`; la segmentación automática cambió
después al pasar `brazo` a codo (ver punto 2).

### Instantes de pico de la primera pasada (segundos dentro de la ventana)

| clip | pelvis | torso | brazo (`HOMBRO→MUNECA`) | brazo (`HOMBRO→CODO`) |
| --- | --- | --- | --- | --- |
| zverev_saque_lateral_01 | 1.196 (700 °/s) | 1.184 (1040) | 1.258 — **15 751 °/s** | 1.238 — 2 292 °/s |
| zverev_saque_lateral_02 | 1.154 (637) | 1.154 (846) | 1.044 — **41 866 °/s** | 1.132 — **24 932 °/s** |
| zverev_saque_lateral_03 | 0.830 (550) | 0.812 (885) | 0.868 — 1 799 °/s | 0.862 — 1 883 °/s |
| drive_lateral_01 | 0.827 (827) | 0.833 (1666) | 0.952 — **26 624 °/s** | 0.956 — 1 744 °/s |
| reves_lateral_01 (Federer, `der`) | 0.290 (522) | 0.447 (385) | 1.000 — **6 448 °/s** | 1.000 — **10 208 °/s** |

### Qué se observa

1. **El pipeline corre de punta a punta sobre material profesional real sin
   romperse.** El manejo de no auditables funciona.

2. **La muñeca de la raqueta no es auditable en el saque/drive del corpus público.**
   `HOMBRO→MUNECA` da 15 000–42 000 °/s en 3 de 4 clips: MediaPipe pierde el punto
   de la mano en el fotograma más rápido. `HOMBRO→CODO` (brazo superior, el segmento
   anatómicamente correcto de la "cadena": el antebrazo y la mano son eslabones
   posteriores) da valores plausibles (1 700–2 300 °/s) en 3 de 4. **Decidido:
   `brazo = HOMBRO→CODO` por defecto, configurable (`brazo_via`)** — para
   re-testear con `muneca` bajo el encuadre de tres cuartos en la Fase B.
   Efecto lateral: con la muñeca, sus *glitches* de 40 000 °/s inundaban la
   "velocidad total" y rompían la segmentación automática; con el codo la
   segmentación por valles de quietud empieza a funcionar (el drive se parte en
   ventanas y una repetición sale `pelvis → torso → brazo` **correcta** con
   velocidades plausibles 827 / 1 666 / 1 744 °/s).

3. **`zverev_saque_lateral_02` — investigación del pico implausible de 24 932 °/s
   (con codo).** No es un techo mal calibrado: es un **error de detección puntual de
   ese clip que ni E2 ni E3 marcaron**.
   - En el fotograma 566, la coordenada `z` de `CODO_DER` **cambia de signo**
     (+0,095 → −0,050 m, ~14 cm) mientras `x`, `y` siguen suaves: una **inversión
     de profundidad** de MediaPipe (no distingue si el codo está delante o detrás
     del plano del cuerpo; §3.3.2.1).
   - La confianza en ese fotograma es **0,65**, por encima del umbral de 0,5 → el
     marcado por baja confianza **no lo atrapa**.
   - El desplazamiento 3D es ~0,15 m ≈ **0,33 longitudes de torso**, por debajo del
     umbral `MAX_SALTO_TORSOS = 0,5` → el detector de saltos imposibles **tampoco lo
     atrapa**.
   - La serie de `z` con la inversión llega a E4; la dirección del vector
     `HOMBRO→CODO` gira de golpe → ω salta a 24 932 °/s → lo corta el techo de
     plausibilidad → la repetición queda correctamente **no auditable**.
   - **El techo hizo su trabajo.** No se perdió un saque bueno por un techo malo:
     se marcó un saque donde la estimación de profundidad del codo se invierte.
   - **Gap detectado en los umbrales de E2/E3** (propuesta, no aplicada — toca
     etapas ya mergeadas): una inversión de signo de `z` de ~1/3 de torso pasa por
     debajo de los dos filtros. Opciones: (a) agregar a `engine/validation.py` un
     detector de **inversión de signo en `z`** (|Δz| por encima de un umbral con
     `x`,`y` estables) — apunta al modo de falla exacto, bajo riesgo de falsos
     positivos; (b) endurecer `MAX_SALTO_TORSOS` (~0,3) y/o hacerlo consciente de la
     velocidad implícita. Recomendación: (a). Pendiente de decidir si se hace ahora
     o junto con la continuación de la Etapa 4 tras la Fase B.

3. **Vista lateral: pelvis y torso quedan a ~12–18  ms.** En los saques de Zverev el
   pico de pelvis y el de torso caen casi juntos (12 ms en el 01, 18 ms en el 03),
   y el orden entre ambos se invierte según el clip. Es exactamente el riesgo
   anticipado: la rotación transversal de pelvis y torso en una toma lateral cae
   sobre el **eje de profundidad**, la coordenada más ruidosa de MediaPipe
   (§3.3.2.8). Puede ser real (los sacadores de élite tienen secuencia pelvis-torso
   muy comprimida) o puede ser ruido de profundidad que difumina ambos; con corpus
   público no se puede separar. El brazo, en cambio, queda claramente último cuando
   es auditable.

### Lectura para la tesis

**Evidencia positiva:** sobre el drive, con `brazo = HOMBRO→CODO`, el sistema
recupera la cadena `pelvis → torso → brazo` con instantes y velocidades
plausibles, pese al sesgo sistemático de los centros articulares y a la vista
lateral. La prueba de ordenamiento con sesgo (sintética) confirma el mismo
argumento de forma controlada (§3.3.4.2). **Evidencia negativa / de límite:** la
discriminación pelvis-vs-torso en toma lateral está en el borde de lo resoluble
(~15 ms), y la muñeca no es auditable con este backend en gestos rápidos. Ambos
resultados son insumos válidos: acotan qué puede y qué no puede afirmar el MVP y
guían el encuadre y el diseño de la Fase B (una toma de **tres cuartos** —Ángulo B
del protocolo— pone la rotación transversal más en el plano de la imagen).

### Comparación con dos clips públicos de tres cuartos

Se catalogaron dos clips de tres cuartos (`drive_trescuartos_01`,
`saque_trescuartos_01`, ~30 fps declarados × factor 8 = 240 efectivos) para
adelantar la comparación antes de grabar. **Resultado: el encuadre de tres
cuartos, sobre estos dos clips no controlados, NO mejoró ninguna de las tres
métricas.**

| métrica | toma lateral (zverev / drive) | tres cuartos (drive / saque) |
| --- | --- | --- |
| separación pelvis–torso | ~2–18 ms, orden que se invierte | 271 / 317 ms, pero **torso antes que pelvis** (invertido) y sin pico claro de pelvis: varios picos de magnitud parecida repartidos por el clip |
| brazo auditable | drive lateral: sí (1 744 °/s); saques: no | drive: al borde (6 399 °/s, ~2,7× Fleisig); saque: **no** (23 365 °/s) |
| inversiones de z (total / de brazo) | 16–45 / 1–3 (saques); 3 / 0 (drive) | 40 / 1 (saque); 14 / 0 (drive) |
| tramos excluidos por E3 | decenas | **75 (drive) / 150 (saque)** — ~40 % del clip |

Lectura: (1) la ambigüedad pelvis-torso **no** se resuelve sola cambiando el
ángulo con material de esta calidad; (2) el brazo del **saque** rápido sigue no
auditable en tres cuartos (el desenfoque en el impacto es un límite del apartado
1, no del encuadre); (3) la `z` no se estabiliza. Los dos clips son de baja
tasa de bits y origen desconocido, así que esto **no descarta** el tres cuartos
para la Fase B —donde habrá 240 fps reales, luz controlada, encuadre fijo,
pausas en posición neutra y repeticiones—, pero **sí descarta contar con el
ángulo de cámara como solución por sí solo**. La única evidencia positiva limpia
sigue siendo `drive_lateral_01` en toma lateral.

---

## 3. Resuelto en esta sesión y pendientes

**Resuelto:**

- **`brazo = HOMBRO→CODO` por defecto, configurable** (`brazo_via`) — decidido con
  Valentín; la evidencia y el argumento anatómico coinciden.
- **`reves_lateral_01`:** `lado_dominante = der`. Roger Federer juega **de derecha**;
  el dato "zurdo" del catálogo era un error, ya corregido.
- **Techo de plausibilidad por segmento, anclado a Fleisig** (§ "Detección de picos").
- **`zverev_saque_lateral_02`:** investigado; es un error de detección puntual
  (inversión de `z` del codo) que el techo marca correctamente como no auditable.

**Pendiente (no se toca hasta la Fase B / el punto de decisión):**

- **Detector de inversión de signo en `z`** en `engine/validation.py` (gap de umbrales
  de E2/E3, ver punto 3 de §2). Decidir si se hace ahora o con la continuación de E4.
- **Medición formal de Criterio 1 (4.7) y Criterio 2 (4.8)** y el **punto de decisión
  de repliegue**: requieren repeticiones controladas del mismo jugador (Fase B).
- Confirmar / descartar la casi-simultaneidad pelvis-torso (~12–18 ms) con encuadre de
  tres cuartos.
- Calibrar prominencia / separación de `find_peaks` y los parámetros de segmentación
  automática (`QUIETUD_REL`, `DUR_MIN_REPETICION_S`) con más material — baja prioridad:
  los clips de la Fase B traen pausas explícitas en posición neutra (protocolo §5).
- Elegir "pico dominante plausible" en vez de descartar toda la serie si el pico más
  alto es implausible.
- Conseguir 1–2 clips públicos con **encuadre de tres cuartos** para adelantar la
  comparación pelvis-vs-torso antes de gastar la sesión de grabación propia.

---

## Sin cambio de contrato

`secuenciacion` (con `repeticiones[]`, `picos[]`, `resumen`) y `metricas[]` ya
tienen la forma que 4.1–4.6b llenan. El `resumen.nota` se mapea a una `observacion`
de nivel 1 en E5, o se omite cuando el análisis corre sobre Fase B.
