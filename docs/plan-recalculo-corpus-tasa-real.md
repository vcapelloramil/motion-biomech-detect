# Plan de recálculo de los Criterios 1 y 3 con la tasa real (para aprobar — **no se recalculó nada todavía**)

**Estado:** propuesta, 9/10/2026. Origen: decisión 030 (el corpus horneado es un remuestreo a ~120 fps con rampas, no 240 fps).
**Regla de los videos:** los archivos (originales reales, recortes, derivados) **no se suben al repositorio**. Se leen desde
`C:\Users\valen\Desktop\corpus-originales-reales` y `kinetiq-data`; todo derivado (ventanas cortadas, poses, marcas de tiempo, miniaturas) va a `backend/.cache/`
(ya ignorada por git) o al directorio temporal. Al repositorio solo van resultados numéricos agregados (`docs/resultados/*.json`) y código.

## 1. Qué hay y qué falta

| Pregunta | Respuesta |
| --- | --- |
| ¿Están los 16 originales? | Sí: 16 de 16 HEVC con marcas de tiempo reales, tasa real media 199,9–201,0 fps; **ninguno horneado**. |
| ¿Cuál no sirve? | **`IMG_6391.mov`**: tiene 2503 fotogramas; debería tener ~15 200 (original completo de `saque_trescuartos_240_02`). **Hay que bajarlo de nuevo** ("original sin modificar", extensión `.MOV`). Sin él faltan 6 repeticiones de `saque|trescuartos|toma 02` (sesión 2). |
| ¿Por qué 16 y no 17 o 18? | Son las 16 grabaciones de cámara lenta (8 por sesión). Los dos horneados que sobran en el corpus (`saque_perfil_030_01`, `saque_perfil_060_01`) son **controles de velocidad normal**: no se hornearon y no entran. Mencioné 17 porque conté una repetición del control de 60 fps. |
| ¿Los fotogramas del horneado corresponden uno a uno con los del original? | **No.** El horneado es el original **remuestreado a 120,2 fps** (1,67 fotogramas reales por fotograma horneado, ~7 % repetidos) con rampas a velocidad normal en los extremos. Cada fotograma horneado **sí se puede asignar** a un fotograma real (orden monótono 99,1–99,9 %), pero la cantidad no coincide. |
| ¿Dónde caen las repeticiones? | 88 ubicadas (el 98 % con la meseta entera, 2 empiezan en la rampa). Son 66 893 fotogramas reales en total. |

## 2. Dos pasos, de menor a mayor costo

### Paso A — corrección rápida sobre las poses ya extraídas (horas de trabajo, minutos de cómputo)

Reusa la **caché de pose del horneado** y le pone la **tasa real del muestreo**: 120,2 fps uniformes (la meseta). No re-extrae pose.

- **Qué corrige:** velocidades (÷2,0 sobre lo reportado), ms (×2,0), el corte del filtro de Winter (que se elegía como si fueran 240 fps) y el significado de "un fotograma" (8,3 ms).
- **Qué no corrige:** la resolución temporal (sigue siendo 120 fps), los ~7 % de fotogramas repetidos, y las **2 repeticiones que empiezan en la rampa** (se excluyen de este paso y se informan).
- **Sirve para:** saber ya cuánto se movió cada cifra y qué conclusiones sobreviven, y como control de consistencia de B.

### Paso B — medición definitiva sobre los originales reales (≈ 8 h de pose en segundo plano)

Es lo que hará el producto con un archivo "Actual": tasa real **leída de las marcas de tiempo**, regularización a 240 Hz con los puntos interpolados contados.

1. **Ventanas:** para cada repetición, el tramo real equivalente (`real_idx` de la ubicación, ya calculada, con un margen de 0,5 s a cada lado) se corta del original con copia de flujo
   (sin recodificar) a `backend/.cache/corpus-real/`. Se verifica que cada ventana tiene los fotogramas esperados.
2. **Pose:** `MediaPipeBackend()` con la **misma configuración** que la medición original (para que la comparación sea por el tiempo, no por el estimador). ~0,44 s por fotograma en esta PC: **~8 h**
   para los 66 893 fotogramas; la sesión 2 y la 1 se pueden partir en dos noches. Con `IMG_6391`, +6 repeticiones (~+0,6 h).
3. **Medición:** `probe` (marcas reales) → `regularizar` a 240 Hz → E3 con corte de Winter automático → secuenciación anclada al torso (±300 ms), brazo vía codo: **igual** que la medición original.
4. **Resultados:** `docs/resultados/criterio1-sesion-N-tiempo-real.json` y `criterio3-tiempo-real.json`, atados a un commit (el arnés se niega a correr con el árbol sucio, como en la decisión 014), con la trazabilidad de la
   regularización por repetición.

## 3. Qué se fija **antes** de mirar los resultados (pre-registro)

La medición original (decisión 014) se congeló antes de medir. Esta también, **por escrito acá**, para que el resultado no se pueda ajustar a lo que dé:

| Decisión | Propuesta | Por qué |
| --- | --- | --- |
| Umbral del Criterio 1 | **0,8**, sin cambios (1a y 1b ≥ 0,8 por grupo) | Es el del apartado 4.3.4. No se mueve para que cierre. |
| Grupos | Los mismos (gesto × encuadre, par y cadena) | Comparabilidad. |
| **Tolerancia de "ordenable"** | **Primaria: 8,3 ms** (equivale a la tolerancia "1 fotograma" de la medición a 120 Hz = 2 fotogramas a 240 Hz). **Sensibilidad: 4,2; 12,5; 16,7 ms** | La tolerancia en fotogramas no es comparable entre 120 y 240 Hz; en milisegundos sí. |
| Qué es "el resultado" de la tesis | **B** (tasa real medida). **A** se informa como control. | B es el camino del producto y mide RNF-01. |
| Qué se reporta si el resultado empeora | Se reporta igual, con la comparación contra la medición original lado a lado | Es un resultado para el Capítulo 7, no una corrección a ocultar. |
| Criterio 3 | `separacion_cadera_hombro_max` (grados, sin cambios) e `instante_pico_torso_desde_max_sep_ms` (ms, **corregido**) | Solo la segunda depende del tiempo. |
| Criterio 2 | **Sin recálculo** (ángulos) | No depende de la tasa. |

## 4. Qué cambia y qué se espera (sin adelantar resultados)

- **Velocidades:** ~½ de las reportadas en la meseta. En los gestos del brazo habrá menos casos sobre el techo de Fleisig.
- **ms:** el doble de los reportados.
- **Resolución:** B mide a 4,2 ms por fotograma contra los 8,3 ms de la medición original: los empates de 0–3 fotogramas (el 69 % de las repeticiones tenía pelvis y torso a ≤ 3 fotogramas) **pueden
  resolverse o no**; no se sabe de antemano. Es la razón por la que la tolerancia se fija en milisegundos.
- **Criterio 1:** puede mejorar, empeorar o quedar igual. El único grupo que cumplía (`drive|perfil`, 1a = 0,83) era frágil; no hay forma de decir de antemano si lo seguirá siendo.

## 5. Orden, costo y quién hace qué

| # | Qué | Quién | Esfuerzo | Bloquea |
| --- | --- | --- | --- | --- |
| 1 | Bajar `IMG_6391` completo | Valentín | 5 min | las 6 repeticiones de la toma 02 |
| 2 | Aprobar este plan y el pre-registro (§3) | Valentín | — | todo lo demás |
| 3 | **Paso A**: arnés + corrida + tabla comparativa | Claude | ~medio día | — |
| 4 | **Paso B**: cortar ventanas, extraer pose, medir | Claude (la PC de Valentín tiene que quedar encendida ~8 h) | ~1 día de trabajo + 8 h de cómputo | — |
| 5 | Resultados al Capítulo 7 + decisión 031 | Claude | ~medio día | — |

**No bloquea el MVP:** el producto no depende de este recálculo (ya lee la tasa real). Compite con el trabajo del flujo de punta a punta por el tiempo de Claude: ver el plan del MVP.

## 6. Riesgos

| Riesgo | Respuesta |
| --- | --- |
| Una ventana real no coincide con el recorte original (error de alineación) | Se verifica con el largo y con la distancia de contenido; las que no pasen se informan y se excluyen, no se fuerzan. |
| Disco: ventanas HEVC de ~16 MB c/u (~1,4 GB) y poses | En `backend/.cache/` (gitignored); se pueden borrar al terminar. |
| La PC se apaga a mitad | La extracción es por repetición y cacheada: se reanuda. |
| Que B dé distinto de A | Es información: la diferencia entre 120 Hz uniforme y 200 Hz regularizado **es** el efecto de la resolución y de las marcas reales. Se informa. |
| Un `.MOV` se cuele en un commit | Verificación `git status`/`git ls-files '*.mov' '*.MOV'` antes de cada commit; `.gitignore` ya excluye `*.mov`, `*.MOV`, `*.mp4`, `.cache/`. |
