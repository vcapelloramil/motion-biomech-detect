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
- supera `VELOCIDAD_ANGULAR_MAX_PLAUSIBLE = 8000 °/s`. Esto **no es un parámetro de
  ajuste**: el hombro pico ~2368 °/s (Fleisig et al., §3.4.2.2); ~3× de margen. Por
  encima es un error de detección, no un movimiento.

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

Corrida de `python -m app.analizar` sobre los 4 clips públicos con lado dominante
confirmado (3 saques de Zverev + 1 drive de Sinner; el revés de Federer quedó
pendiente, ver §3). Se registran **tal cual salieron**, sin ajustar nada.

### Instantes de pico (segundos dentro de la ventana)

| clip | pelvis | torso | brazo (`HOMBRO→MUNECA`) | brazo (`HOMBRO→CODO`) |
| --- | --- | --- | --- | --- |
| zverev_saque_lateral_01 | 1.196 (700 °/s) | 1.184 (1040) | 1.258 — **15 751 °/s** | 1.238 — 2 292 °/s |
| zverev_saque_lateral_02 | 1.154 (637) | 1.154 (846) | 1.044 — **41 866 °/s** | 1.132 — **24 932 °/s** |
| zverev_saque_lateral_03 | 0.830 (550) | 0.812 (885) | 0.868 — 1 799 °/s | 0.862 — 1 883 °/s |
| drive_lateral_01 | 0.827 (827) | 0.833 (1666) | 0.952 — **26 624 °/s** | 0.956 — 1 744 °/s |

### Qué se observa

1. **El pipeline corre de punta a punta sobre material profesional real sin
   romperse.** El manejo de no auditables funciona: con `brazo = HOMBRO→MUNECA`, la
   velocidad implausible de la muñeca cerca del impacto (desenfoque de movimiento)
   se detecta y la repetición queda no auditable, en vez de reportar un orden
   basado en un número basura.

2. **La muñeca de la raqueta no es auditable en el saque/drive del corpus público.**
   `HOMBRO→MUNECA` da 15 000–42 000 °/s en 3 de 4 clips: MediaPipe pierde el punto
   de la mano en el fotograma más rápido. `HOMBRO→CODO` (brazo superior, el segmento
   anatómicamente correcto de la "cadena": el antebrazo y la mano son eslabones
   posteriores) da valores plausibles (1 700–2 300 °/s) en 3 de 4, y en el drive el
   orden sale **`pelvis → torso → brazo` completo y con velocidades plausibles**.
   `zverev_02` tiene un tramo de *tracking* malo cerca del impacto que ni el codo
   salva (correctamente no auditable).

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

---

## 3. Pendientes (no se tocan hasta la Fase B / el punto de decisión)

- **Revisar `brazo = HOMBRO→MUNECA` → `HOMBRO→CODO`.** La evidencia de arriba lo
  recomienda, pero el cambio queda para que Valentín lo apruebe (el vector se
  aprobó como `HOMBRO→MUNECA` en el plan). Alternativa: hacerlo configurable.
- **`reves_lateral_01` (Federer):** el catálogo lo marca zurdo, pero Roger Federer
  juega **de derecha** (revés a una mano con la derecha). La columna `lado_dominante`
  quedó vacía para ese clip a la espera de confirmación. Es justo el caso que la
  columna busca evitar: sin ella, el default habría medido el brazo equivocado en
  silencio.
- **Medición formal de Criterio 1 (4.7) y Criterio 2 (4.8)** y el **punto de
  decisión de repliegue**: requieren repeticiones controladas del mismo jugador
  (Fase B).
- Calibrar prominencia / separación de `find_peaks` con más material.
- Elegir "pico dominante plausible" en vez de descartar toda la serie si el pico
  más alto es implausible (posible refinamiento con datos de Fase B).

---

## Sin cambio de contrato

`secuenciacion` (con `repeticiones[]`, `picos[]`, `resumen`) y `metricas[]` ya
tienen la forma que 4.1–4.6b llenan. El `resumen.nota` se mapea a una `observacion`
de nivel 1 en E5, o se omite cuando el análisis corre sobre Fase B.
