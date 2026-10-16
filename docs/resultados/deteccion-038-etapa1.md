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
