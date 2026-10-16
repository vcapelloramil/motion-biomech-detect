# Decisión 038, etapa 1 — validación de la detección automática del tipo de golpe y del encuadre (16/10/2026)

**Qué es:** la medición de cuánto acierta, **sobre el corpus etiquetado y sin tocar el producto**, una regla que detecte el **tipo de golpe** (saque / drive / revés) y el **encuadre** (perfil / tres cuartos). Es la etapa 1
de la actualización del 16/10 de la decisión 038; la etapa 2 (integrarlo en Cargar) **no se programa** sin el OK de Valentín y solo si esto cumple.
Arnés: `backend/app/medicion_deteccion.py` (prueba: `tests/unit/test_medicion_deteccion.py`). Datos: las poses del Paso B (`backend/.cache/corpus-real-pose-b`, originales del iPhone a tasa real, regularizados a 240 Hz, 76
repeticiones). Resultados crudos: `deteccion-038-etapa1.json` (por repetición y por pliegue) y `deteccion-038-etapa1-estadisticos.json` (los estadísticos de cada repetición).

## Qué se fijó antes de medir

Esto se escribió y se confirmó (commit del arnés y de este apartado) **antes de calcular cualquier acierto**. Ningún estadístico por clase se vio antes. Lo único mirado antes fue una **convención** sin etiquetas: en el mundo
métrico del corpus el eje y crece hacia abajo (la nariz queda por encima de la cadera: mediana −0,64 m) y la grilla es de 240 Hz.

**Partición (pre-registro del 15/10):** los cortes se fijan en **una** sesión y se evalúan en **la otra**; se hacen los dos pliegues (ajuste 24/9 → evaluación 25/9, y ajuste 25/9 → evaluación 24/9) y el resultado formal es
el **agregado de los dos** (cada repetición se evalúa una sola vez, con cortes que no la vieron). Unidad: la repetición. "Determinado" = el sistema afirma un valor; "no determinado" = sin pico del tronco auditable, sin datos
suficientes o en la franja entre cortes. **Error = errores / determinados.** Aceptación, por campo y por gesto: **error ≤ 5 % y no determinado ≤ 20 %**. Verdad: la etiqueta del nombre del archivo (declarada por el propio jugador).

**Qué se mide, en qué ventana (misma ventana de preparación que el contraste D; aceleración justo antes del pico del tronco):**

| Estadístico | Definición | Sirve para |
| --- | --- | --- |
| `s_saque` | fracción de los fotogramas de la **preparación** (de 0,8 a 0,3 s antes del pico del tronco) con la muñeca dominante **por encima de la nariz** y el codo dominante **por encima del hombro** dominante | saque contra el resto (posición de "trofeo") |
| `c1_giro` | giro neto (°) de la línea de hombros alrededor de la vertical en la **aceleración** (de 0,3 s antes al pico del tronco): mediana de los últimos 0,05 s menos la de los primeros 0,05 s, con el signo espejado para el zurdo | drive contra revés (candidata i) |
| `c2_munecas` | mediana, en la aceleración, de la distancia entre las dos muñecas, en anchos de hombros | drive contra revés (candidata ii; el revés a dos manos queda chico) |
| `c3_eje` | mediana, en la aceleración, de la posición de la muñeca dominante respecto del centro de los hombros sobre el eje de los hombros (positivo = del lado de la mano dominante), en anchos de hombros | drive contra revés (candidata iii) |
| `giro_hombros` | el contraste D del producto (`encuadre.giro_hombros_grados`, preparación) | perfil contra tres cuartos |

**Cortes (por extremos observados en la sesión de ajuste, como D con el saque):** para dos clases A (valores bajos) y B (valores altos): `P = máximo de A`, `T = mínimo de B`; ≤ P → A, ≥ T → B, **entre P y T "no
determinado"**. Si las clases se solapan en la sesión de ajuste (P ≥ T) la regla **no separa** y lo que cae en la zona común tampoco se afirma.
- **Gesto:** paso 1, saque (`s_saque` alto) contra drive y revés; paso 2, sobre lo que no es saque, **la candidata (c1, c2 o c3) que separe sin errores la sesión de ajuste y tenga la mayor brecha relativa** (brecha / diferencia de
  medianas); la clase alta es la de mayor mediana en el ajuste. **Si ninguna separa, drive contra revés queda "no determinado"** y se declara que no se pudo.
- **Encuadre:** un par (P, T) **por tipo de golpe**, con `giro_hombros` y el tipo **verdadero** de la sesión de ajuste. En la evaluación se informan **dos variantes**: (a) con el tipo **verdadero** (aísla la regla de
  encuadre) y (b) con el tipo **detectado** (es lo que haría el producto: el error de tipo se propaga). Con el tipo "no determinado" solo se afirma si el giro cae del mismo lado bajo los cortes de **todos** los tipos.
- **Mano dominante: es un dato del jugador (perfil), no se detecta.** Todo el corpus es de un diestro; la regla para zurdos es el espejo y **no está validada**.
- **No se usa** la cláusula "la otra muñeca arriba al comienzo" del saque: un recorte de 2 a 5 s no tiene un "comienzo" definido. Es un cambio declarado respecto del texto del 15/10.
- **Lo que no se ajusta después:** ventanas, definiciones y reglas de arriba no se tocan después de ver los resultados. Si algo falla se informa que falla.

**Límites que se declaran de antemano:** un solo jugador (diestro); un teléfono, un lugar; dos sesiones consecutivas; cámara siempre a la izquierda del jugador; tres cuartos por delante; **una sola técnica de revés** (el
repositorio no registra si es a una o dos manos); las etiquetas las puso la misma persona que las evalúa (y hay un error de etiqueta conocido, `IMG_6391`, excluido por incompleto); con 76 repeticiones, **cero errores
da un intervalo de Wilson de 95 % hasta ~4,8 %**, y por tipo de golpe (~24) hasta ~14 %: un "cumple" **no generaliza** a otros jugadores ni a otros lados de la cámara; solo dice si la regla funciona en este material.

## Resultado de la corrida formal (reglas pre-registradas; commit `fee1003`, árbol limpio, motor 0.5.5)

76 repeticiones (35 de la sesión 1, 41 de la sesión 2; saque 29, drive 24, revés 23). **75 tienen pico del tronco auditable** (1 queda "no determinado" por eso). Resultado **agregado de los dos pliegues**:

| Campo | Determinados | Errores | **Error entre determinados** (Wilson 95 %) | **No determinado** | ¿Cumple (≤ 5 % y ≤ 20 %)? |
| --- | --- | --- | --- | --- | --- |
| **Tipo de golpe** (saque / drive / revés) | 1 de 76 | 1 | 100 % (21–100 %) | **98,7 %** | **No** |
| · saque | 0 de 29 | — | — | 100 % | No |
| · drive | 0 de 24 | — | — | 100 % | No |
| · revés | 1 de 23 | 1 | 100 % | 95,7 % | No |
| **Encuadre**, con el tipo de golpe **verdadero** | 35 de 76 | 5 | 14,3 % (6,3–29,4 %) | **53,9 %** | **No** |
| · saque | 18 de 29 | 0 | **0 %** (0–17,6 %) | 37,9 % | No (por el no determinado) |
| · drive | 13 de 24 | 2 | 15,4 % (4,3–42,2 %) | 45,8 % | No |
| · revés | 4 de 23 | 3 | 75 % (30,1–95,4 %) | 82,6 % | No |
| **Encuadre**, con el tipo **detectado** (lo que haría el producto) | 6 de 76 | 4 | 66,7 % (30–90 %) | **92,1 %** | **No** |

**Ningún campo cumple el criterio pre-registrado.** El mejor es el encuadre del saque (0 errores entre los 18 determinados), pero con el 38 % sin determinar.

Matrices de confusión (fila = verdad, columna = lo que dijo el sistema; `n.d.` = no determinado):

| Tipo de golpe | saque | drive | revés | n.d. |
| --- | --- | --- | --- | --- |
| **saque** (29) | 0 | 0 | 0 | 29 |
| **drive** (24) | 0 | 0 | 0 | 24 |
| **revés** (23) | 1 | 0 | 0 | 22 |

| Encuadre (tipo verdadero) | perfil | tres cuartos | n.d. |
| --- | --- | --- | --- |
| **perfil** (34) | 12 | 3 | 19 |
| **tres cuartos** (42) | 2 | 18 | 22 |

**Por pliegue** (ajuste → evaluación): sesión 1 → sesión 2 (41 repeticiones): tipo de golpe, 1 determinado (error); encuadre con el tipo verdadero, 23 determinados y 3 errores (13 %), 43,9 % sin determinar (saque: 14 determinados, 0 errores,
22 % sin determinar). Sesión 2 → sesión 1 (35 repeticiones): tipo de golpe, 0 determinados; encuadre con el tipo verdadero, 12 determinados y 2 errores (17 %), 65,7 % sin determinar (saque: 4 determinados, 0 errores, 64 % sin determinar).

### Qué falló, regla por regla

1. **Saque contra el resto (`s_saque`, posición de "trofeo" en la preparación): no separa.** En las 8 repeticiones de saque con dato (de 29), `s_saque` vale **0,0 en todas**; en drive y revés vale hasta 0,5–0,7. Las clases se solapan en las dos sesiones de ajuste
   (la regla exige que el saque tenga valores altos). Además **32 de las 76 repeticiones no tienen dato**: el brazo dominante queda lejos de la cámara (que está siempre a la izquierda del jugador) y la pose lo pierde (la misma oclusión
   del brazo de la decisión 013). En el control de implementación (un saque de perfil y uno de tres cuartos), en la ventana de preparación la muñeca queda 5 a 18 cm **por debajo** de la nariz y la altura llega recién en el contacto: la regla,
   tal como se pre-registró, mide un instante que no es el de la altura máxima de este jugador.
2. **Drive contra revés: ninguna candidata separa las dos sesiones.** En el pliegue 1 → 2 separan `c2_munecas` y `c3_eje` (se eligió `c2`), pero en la sesión 2 → 1 ninguna: **un solo valor atípico por clase rompe la separación por extremos**
   (p. ej. `c3_eje` en la sesión 2: drive entre 0,03 y 1,32 anchos de hombros y revés entre −1,14 y 0,75, aunque las medianas están lejos: 0,66–1,12 contra −1,11 a −0,41). Con la regla pre-registrada, drive/revés queda **sin determinar**.
3. **Encuadre del saque: la regla es correcta y los cortes son estrechos.** 0 errores en 18 determinados; el no determinado alto sale de fijar los cortes con 10 y 18 repeticiones (extremos observados de una sola sesión: 35,8°–49,9° y 41,9°–56,5°). Los cortes que usa hoy el
   producto (42° y 50°) se fijaron con **las dos sesiones**: en el mismo corpus dejan 0 errores y 1 sin determinar de 28, pero eso **no es una evaluación** (la muestra se vio entera).
4. **Encuadre de drive: el contraste D no lo distingue** (en cada sesión los rangos de perfil y de tres cuartos se solapan: sesión 1, perfil 28–72° y tres cuartos 34–63°; sesión 2, perfil 27–46° y tres cuartos 33–72°).
5. **Encuadre de revés: el contraste D va al revés que en el saque.** Revés de **perfil**: giro de 26–60° (sesión 1, mediana 51°) y 54–86° (sesión 2, mediana 59°); revés de **tres cuartos**: 9–18° (sesión 1) y 10–64° (sesión 2, mediana 17°, con un valor atípico de 64°).
   La orientación pre-registrada (perfil ≤ P, tres cuartos ≥ T) **no corresponde al revés**. Es coherente con el hallazgo del Paso B de que **el revés no sigue el patrón del saque y del drive** y no se explica con estos datos.

### Qué significa para el calendario

- **La etapa 2 no se propone:** la condición era "solo si la etapa 1 cumple", y **no cumple en ningún campo**. Con el tipo de golpe 98,7 % sin determinar, la carga tendría que preguntar siempre; y con el encuadre
  66,7 % de error (con el tipo detectado), un "detecta y propone" sería peor que declarar.
- **Lo que esta corrida NO dice:** que el tipo de golpe o el encuadre sean indetectables desde la pose. Dice que **estas reglas simples, con este corpus de un jugador y dos sesiones, no alcanzan el criterio**. Las medianas de varias
  señales sí separan las clases (ver el análisis exploratorio abajo); lo que falta es una regla robusta a valores atípicos y **datos nuevos para validarla sin hacer trampa**: cualquier regla elegida mirando estas dos sesiones ya no se puede
  evaluar con ellas.

## Análisis exploratorio posterior (post hoc: NO cuenta para el criterio)

Se hizo **después** de ver el resultado de arriba, con una definición escrita antes de correrlo (`backend/app/medicion_deteccion_exploratorio.py`, commit `1eef8d7`; resultados: `deteccion-038-etapa1-exploratorio.json`) y con las mismas dos
particiones. Cambia tres cosas respecto de lo pre-registrado: (1) el saque se mide en el **contacto** (de 0,15 s antes a 0,10 s después del pico del tronco: muñeca dominante por encima de la nariz), no en la preparación; (2) el corte es **por la
mitad de las medianas** de cada clase en la sesión de ajuste, sin franja de "no determinado" (el no determinado de la tabla es solo falta de dato); (3) la orientación del encuadre por tipo de golpe se toma de la mediana de ajuste (así el revés
queda invertido). **Se diseñó viendo ambas sesiones: es optimista por construcción.** No se puede citar como acierto de la detección; sirve para decidir qué grabar y qué reglas probar con datos nuevos.

| Regla exploratoria (con el tipo verdadero cuando es encuadre) | Determinados | Errores | Error (Wilson 95 %) | Sin dato |
| --- | --- | --- | --- | --- |
| Saque contra el resto: muñeca sobre la nariz en el contacto | 70 de 76 | 7 | 10,0 % (4,9–19,2 %) | 6 |
| Drive contra revés: `c3_eje` (lado del eje de los hombros) | 45 de 47 | 5 | 11,1 % (4,8–23,5 %) | 2 |
| Drive contra revés: `c2_munecas` (distancia entre muñecas) | 40 de 47 | 4 | 10,0 % (4,0–23,1 %) | 7 |
| Drive contra revés: `c1_giro` (giro de hombros) | 47 de 47 | 13 | 27,7 % (16,9–41,8 %) | 0 |
| Encuadre del saque: `giro_hombros` | 28 de 29 | 0 | 0 % (0–12,1 %) | 1 |
| Encuadre del drive: `giro_hombros` | 24 de 24 | 5 | 20,8 % (9,2–40,5 %) | 0 |
| Encuadre del revés: `giro_hombros` (orientación invertida) | 23 de 23 | 2 | 8,7 % (2,4–26,8 %) | 0 |

**Lectura (con la salvedad de arriba):**
- **Las señales sí tienen información:** con un corte simple por la mitad de las medianas, el saque se separa del resto con ~10 % de error y drive contra revés con ~10 % (`c3` o `c2`). **Ninguna llega al 5 %** ni siquiera en este
  análisis optimista, y para el tipo de golpe completo habría que encadenar dos reglas (saque contra el resto, después drive contra revés): los errores se suman (del orden del 20 %).
- **El encuadre del saque se sostiene** (0 errores en 28, con el contraste D que ya está en el motor). **El de drive y revés no llega:** 21 % y 9 %, y en el revés con el sentido invertido.
- **Cinco revés de perfil** tienen la muñeca dominante por encima de la nariz en el contacto (`20260924_VCR_reves_perfil_240_01_rep01`, `rep02` y `rep03`; `20260925_VCR_reves_perfil_240_02_rep02` y `rep03`) y son la mayor parte de los 6 errores del saque contra el
  resto. Puede ser un error de la pose (muñeca intercambiada con la otra, que ya se vio con la oclusión del brazo), una técnica de revés distinta o una etiqueta equivocada: **hay que mirar esos cinco videos a mano** (el pre-registro pide revisar las etiquetas dudosas;
  no los vi). Si fueran un error de etiqueta, cambiaría el resultado de esta tabla, no el de la corrida formal.
- **Los saques sin dato de muñeca** (`02b` rep04–06, `02c` rep05, `01` rep03) son tomas de tres cuartos donde el brazo dominante queda tapado por el cuerpo: es la oclusión de la decisión 013, no un problema de la regla.

## Qué hace falta para que una detección pueda cumplir (propuesta, sin programar)

1. **Datos nuevos para validar** (ninguna regla elegida mirando estas dos sesiones se puede evaluar con ellas): una sesión con saque, drive **y** revés, perfil y tres cuartos, de ≥ 12 repeticiones por celda, idealmente en un día y un lugar distintos
   (se puede sumar a la sesión del lado derecho, `docs/protocolo-sesion-lado-derecho.md`, que hoy solo tiene saques), y anotar si el revés es a una o dos manos.
2. **Reglas robustas a valores atípicos** (medianas y fracciones en lugar de extremos) y un "no determinado" explícito entre dos cortes, **fijadas antes** de mirar la sesión nueva.
3. **Mirar a mano los cinco revés de perfil de arriba** (¿pose, técnica o etiqueta?).
4. Con esto el criterio del 5 % de error solo es alcanzable si la regla es mucho mejor que las probadas; si no, el tipo de golpe queda en **"el sistema propone y el usuario confirma"** (el segundo camino de la decisión 038), que no necesita llegar al 5 %.
