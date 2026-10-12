# Paso A del recálculo con la tasa real — resultado (12/10/2026)

**Qué es:** las poses ya extraídas del corpus **horneado** (sin volver a correr MediaPipe) con el tiempo real de ese muestreo —**120,2 fps uniformes**, no los 240 que se asumieron—, la ventana de ± 300 ms
en tiempo real y la tolerancia de "ordenable" **en milisegundos con la misma constante que usa el producto** (1/120 s = 8,33 ms, estricta; decisión 032). Arnés: `backend/app/medicion_paso_a.py`; resultados:
`paso-a-sesion-2.json` (medición) y `paso-a-sesion-1.json` (réplica exploratoria, no independiente), atados al commit `3d88f89` con el árbol limpio, motor 0.5.0. Plan y pre-registro:
`docs/plan-recalculo-corpus-tasa-real.md` §2 y §3.

**Qué NO es:** no es la medición definitiva (eso es el Paso B, sobre los originales a ~200 fps reales con regularización a 240 Hz y 5 ms de resolución). Es el control rápido que dice cuánto se movió cada
cifra y qué conclusiones sobreviven. **Se informa tal cual salió, lado a lado con la medición original**, como se fijó antes de mirar.

**Qué se excluyó:** las repeticiones que empiezan en la rampa de velocidad (1 por sesión: `reves_perfil_240_02_rep01` y `saque_perfil_240_01_rep01`; `corpus-real-alineacion.json`). La toma `02` del saque
de tres cuartos **sí** entra (en el Paso B queda afuera por `IMG_6391`).

## 1. Criterio 1 — par cadera-tronco, tolerancia primaria (8,33 ms), contra la medición original

**Sesión 2 (conjunto de medición)**

| Grupo | n | Original: ordenables · 1a · 1b · orden | Paso A: ordenables · 1a · 1b · orden | Cumple (original → Paso A) |
| --- | --- | --- | --- | --- |
| Saque · perfil | 6 | 6 · 1,00 · 1,00 · tp | 5 · 0,83 · 1,00 · tp | cumple → **cumple** |
| Saque · tres cuartos | 18 | 9 · 0,50 · 1,00 · pt | 8 · 0,44 · 0,62 · pt | no → **no** |
| Drive · perfil | 6 | 6 · 1,00 · 1,00 · tp | 3 · 0,50 · 1,00 · tp | cumple → **no** |
| Drive · tres cuartos | 6 | 0 · 0,00 · — · — | 0 · 0,00 · — · — | no → **no** |
| Revés · perfil | 5 | 4 · 0,67 · 0,75 · pt | 3 · 0,60 · 0,67 · pt | no → **no** |
| Revés · tres cuartos | 6 | 6 · 1,00 · 0,83 · tp | 3 · 0,50 · 1,00 · tp | cumple → **no** |

**Sesión 1 (réplica exploratoria)**

| Grupo | n | Original: ordenables · 1a · 1b · orden | Paso A: ordenables · 1a · 1b · orden | Cumple (original → Paso A) |
| --- | --- | --- | --- | --- |
| Saque · perfil | 5 | 2 · 0,33 · 1,00 · tp | 4 · 0,80 · 1,00 · tp | no → **cumple** |
| Saque · tres cuartos | 6 | 3 · 0,50 · 0,67 · pt | 1 · 0,17 · 1,00 · pt | no → **no** |
| Drive · perfil | 6 | 4 · 0,67 · 1,00 · tp | 2 · 0,33 · 0,50 · pt | no → **no** |
| Drive · tres cuartos | 6 | 3 · 0,50 · 1,00 · pt | 0 · 0,00 · — · — | no → **no** |
| Revés · perfil | 6 | 3 · 0,50 · 0,67 · pt | 0 · 0,00 · — · — | no → **no** |
| Revés · tres cuartos | 6 | 3 · 0,50 · 0,67 · tp | 2 · 0,33 · 1,00 · tp | no → **no** |

**Cómo leerlo.** "1a" = ordenables sobre todas las repeticiones del grupo; "1b" = entre las ordenables, la fracción con el orden modal; el criterio pide 1a ≥ 0,8 **y** 1b ≥ 0,8 (decisión 014); "tp" =
tronco primero, "pt" = cadera primero.

- **Con tiempo real y la regla unificada, un solo grupo cumple el Criterio 1 en las dos sesiones: el saque de perfil** (1a 0,83 y 0,80; 1b 1,00; orden `tp`). **Drive de perfil y revés de tres cuartos
  dejan de cumplir** (1a 0,50): lo que parecía repetible dependía de la ventana y de la escala de tiempo equivocadas. Ningún grupo nuevo cumple en la sesión de medición.
- **No se puede atribuir todo el cambio al reloj.** Corregir los fps cambia también cuántos fotogramas abarca la ventana (± 36 en vez de ± 72), la separación mínima entre picos y los umbrales en °/s: es
  la medición que habría salido con el tiempo bien, no la original con otro reloj.
- Con la tolerancia más fina declarada de antemano (4,17 ms = un fotograma) cumplen más grupos; **un fotograma es justo la resolución del material**, así que esas cifras describen el límite del
  instrumento y no un resultado. Están en los JSON (`sens_4.2ms`, `sens_12.5ms`, `sens_16.7ms`).

## 2. ¿Es el "tronco primero" un artefacto de medición?

Pedido de Valentín (12/10): que el Paso A ayude a distinguirlo. **Lo que se pudo descartar y lo que no:**

| Hipótesis | Control | Resultado |
| --- | --- | --- |
| El tiempo estaba mal (240 en lugar de 120,2) | El Paso A mismo | **Descartada como causa única:** con el tiempo corregido el saque de perfil, el drive de perfil y el revés de tres cuartos siguen en `tp` |
| Es un efecto del filtro | Corte fijo de 4, 6, 8, 10 y 12 Hz contra el de Winter | **Descartada** en perfil y en revés de tres cuartos: el orden modal no cambia con el corte. En el saque de tres cuartos sí cambia (`pt` con Winter, `tp` con 8 Hz): **está en el límite de resolución** |
| Es un efecto de la definición (el motor usa la velocidad angular **total** del vector; la biomecánica habla de **giro axial**) | Giro alrededor de la vertical (plano horizontal) de las líneas de caderas y de hombros | **Descartada:** el giro axial da el mismo sentido en perfil (`tp`) y, en el saque de perfil, una diferencia **mayor** (sesión 2: mediana −129 ms contra −62 ms) |
| Depende de dónde está la cámara (el movimiento físico no puede depender del encuadre) | El mismo gesto en perfil y en tres cuartos | **Se sostiene. Es lo más informativo:** ver más abajo |
| Es lo que el jugador hace de verdad | — | **No se puede decidir con estos datos** (hace falta una medición independiente) |

**La dependencia del encuadre (las dos sesiones juntas, repeticiones ordenables a 8,33 ms):**

| | Cadera primero | Tronco primero | Dentro de la tolerancia |
| --- | --- | --- | --- |
| **Saque · perfil** | **0** | **9** | 1 |
| **Saque · tres cuartos** | **6** | 3 | 15 |
| Todos los gestos · perfil | 3 | 14 | 16 |
| Todos los gestos · tres cuartos | 6 | 8 | 34 |

En el **saque**, el único gesto con veredicto, la diferencia entre encuadres es de 0 de 9 contra 6 de 9 (prueba exacta de Fisher, p = 0,009; **exploratoria**: las repeticiones de una misma toma no son
independientes y es un solo jugador). En el conjunto de todos los gestos no llega a distinguirse (p = 0,23). Además, en el saque de perfil de la **sesión 2** la diferencia entre picos es de **−62 ms de mediana (−158 a −17)**:
**siete veces la resolución del material**, que no se explica por redondeo de fotogramas, y es donde la señal de la cadera está menos acoplada con la del tronco (correlación de ω 0,54 contra 0,89 en tres cuartos). **En la sesión 1 la misma comparación da −21 ms (n = 4) y una correlación de 0,92**: el sentido es el mismo (tronco primero, 4 de 4), la magnitud no.

**Lectura (cautelosa):**

- Lo que el sistema ve **depende de la cámara**: en perfil, la cadera llega tarde (a veces mucho); en tres cuartos, el orden esperado (cadera primero) aparece sobre todo con el giro axial (0,91 de las
  ordenables). Los dos no pueden ser el movimiento real: **al menos uno de los dos encuadres mide mal**.
- El sospechoso es el perfil: la cadera lejana queda tapada por el cuerpo (la decisión 013 ya documenta el mismo problema para el codo dominante), y MediaPipe infiere la profundidad de esos puntos.
  **Es una hipótesis, no una medición**: no hay una referencia independiente de la pelvis.
- **En tres cuartos el instrumento está en su límite:** en 34 de 48 repeticiones la cadera y el tronco quedan a 8,33 ms o menos (un fotograma a 120 fps). Ahí se puede decir "casi simultáneos", no
  "cadera primero".
- **Qué lo resolvería:** (1) el Paso B (240 Hz regularizados, 5 ms de resolución real) para el límite; (2) un golpe grabado a la vez desde perfil y desde tres cuartos para que la dependencia del encuadre
  sea del mismo movimiento y no de tomas distintas; (3) idealmente una medición independiente de la pelvis (otra cámara, o marcadores en una sola sesión).

## 3. Distribución de la diferencia de instantes (Δ = t_tronco − t_cadera; positivo = la cadera llegó primero)

**Sesión 2**

| Grupo | n | Mediana de Δ (ms) | Cuartiles (ms) | Cadera primero | Tronco primero | Dentro de 8,33 ms |
| --- | --- | --- | --- | --- | --- | --- |
| Saque · perfil | 6 | -62,4 | -158,1 a -16,6 | 0 | 5 | 1 |
| Saque · tres cuartos | 18 | 8,3 | 2,1 a 14,6 | 5 | 3 | 10 |
| Drive · perfil | 6 | -16,6 | -37,4 a -2,1 | 0 | 3 | 3 |
| Drive · tres cuartos | 6 | 0,0 | 0,0 a 0,0 | 0 | 0 | 6 |
| Revés · perfil | 5 | 8,3 | -8,3 a 16,6 | 2 | 1 | 2 |
| Revés · tres cuartos | 6 | -12,5 | -16,6 a -8,3 | 0 | 3 | 3 |

**Sesión 1**

| Grupo | n | Mediana de Δ (ms) | Cuartiles (ms) | Cadera primero | Tronco primero | Dentro de 8,33 ms |
| --- | --- | --- | --- | --- | --- | --- |
| Saque · perfil | 4 | -20,8 | -27,0 a -16,6 | 0 | 4 | 0 |
| Saque · tres cuartos | 6 | 8,3 | 2,1 a 8,3 | 1 | 0 | 5 |
| Drive · perfil | 6 | -8,3 | -8,3 a 4,2 | 1 | 1 | 4 |
| Drive · tres cuartos | 6 | 8,3 | -4,2 a 8,3 | 0 | 0 | 6 |
| Revés · perfil | 6 | 0,0 | -6,2 a 6,2 | 0 | 0 | 6 |
| Revés · tres cuartos | 6 | -8,3 | -114,4 a -8,3 | 0 | 2 | 4 |

## 4. Controles exploratorios (no pre-registrados)

Correlación de ω entre cadera y tronco en la ventana, desfase de máxima correlación (negativo: el tronco se adelanta) y orden modal por método (entre paréntesis, repeticiones ordenables).

**Sesión 2**

| Grupo | Correlación ω cadera–tronco | Desfase (ms) | Orden modal: Winter · 8 Hz fijo · giro axial | Cadera primero entre ordenables: Winter · 8 Hz · axial |
| --- | --- | --- | --- | --- |
| Saque · perfil | 0,54 | -20,8 | tp (5) · tp (4) · tp (5) | 0,00 · 0,00 · 0,00 |
| Saque · tres cuartos | 0,89 | 4,2 | pt (8) · tp (8) · pt (11) | 0,62 · 0,50 · 0,91 |
| Drive · perfil | 0,77 | -20,8 | tp (3) · tp (3) · tp (4) | 0,00 · 0,00 · 0,00 |
| Drive · tres cuartos | 0,92 | 0,0 | — (0) · — (0) · pt (1) | — · — · 1,00 |
| Revés · perfil | 0,70 | 0,0 | pt (3) · tp (4) · pt (3) | 0,67 · 0,50 · 0,67 |
| Revés · tres cuartos | 0,87 | -8,3 | tp (3) · tp (3) · tp (3) | 0,00 · 0,00 · 0,00 |

**Sesión 1**

| Grupo | Correlación ω cadera–tronco | Desfase (ms) | Orden modal: Winter · 8 Hz fijo · giro axial | Cadera primero entre ordenables: Winter · 8 Hz · axial |
| --- | --- | --- | --- | --- |
| Saque · perfil | 0,92 | -16,6 | tp (4) · tp (4) · tp (2) | 0,00 · 0,00 · 0,00 |
| Saque · tres cuartos | 0,94 | 0,0 | pt (1) · pt (1) · pt (1) | 1,00 · 1,00 · 1,00 |
| Drive · perfil | 0,84 | 0,0 | pt (2) · tp (2) · tp (2) | 0,50 · 0,00 · 0,50 |
| Drive · tres cuartos | 0,92 | 0,0 | — (0) · — (0) · pt (1) | — · — · 1,00 |
| Revés · perfil | 0,80 | 0,0 | — (0) · — (0) · — (0) | — · — · — |
| Revés · tres cuartos | 0,77 | 0,0 | tp (2) · tp (3) · tp (2) | 0,00 · 0,00 · 0,00 |

## 5. Qué cambia en el producto

1. **`RESPALDO_POR_GRUPO` (decisión 031, condición (b)) se actualizó con estas cifras:** `drive|perfil` y `reves|tres_cuartos` dejan de cumplir el Criterio 1. **Ningún veredicto cambia**, porque ninguno de los
   dos tenía referencia del orden (condición (a)). Con (a) y (b) sigue únicamente el **saque de perfil**.
2. **Y es justamente el grupo cuya medición es más sospechosa.** Con la regla tal como está escrita (031) todo saque de perfil sale **"desvío leve"**, y el Paso A muestra que ese orden depende del
   encuadre. **Propuesta (decisión 035, a aprobar): suspender el veredicto del saque de perfil** hasta que el orden coincida entre encuadres, y mostrarlo "solo registrado" con el motivo. Cambio de una línea
   en `RESPALDO_POR_GRUPO`; **no se aplicó**, es decisión de Valentín.
3. **Qué se le puede decir al jugador hoy** (sin inventar): el orden observado, con la advertencia de la resolución; nunca "tu cadera llegó tarde" como hallazgo.

## 6. Limitaciones

- **n pequeño y un solo jugador**: 6 repeticiones por grupo (18 el saque de tres cuartos); las repeticiones de una toma no son independientes. Todo es descriptivo.
- **Corpus horneado a 120 fps con ~7 % de fotogramas repetidos**: la resolución es 8,33 ms y no se puede mejorar sin los originales (Paso B).
- **Los controles del punto 4 no estaban pre-registrados** y se agregaron a pedido, sobre las mismas poses y sin tocar la medición. Se informan todos, también los que no apoyan la hipótesis.
- **Un control se descartó:** la medición en 2D (espacio de la imagen). `E3` excluye la mayoría de los puntos de la imagen porque sus umbrales están calibrados en metros; recalibrarlo es trabajo nuevo
  y queda afuera del Paso A. Se reemplazó por el giro axial.
- **No incluye el Criterio 3** (consistencia entre sesiones, instante del pico): la métrica (i), la separación cadera-hombro, no depende del tiempo; la (ii) se recalcula en el Paso B.

## Reproducir

```bash
cd backend
PYTHONPATH=. .venv/Scripts/python.exe -m app.medicion_paso_a --sesion 2 --salida ../docs/resultados/paso-a-sesion-2.json
PYTHONPATH=. .venv/Scripts/python.exe -m app.medicion_paso_a --sesion 1 --etiqueta replica-exploratoria --salida ../docs/resultados/paso-a-sesion-1.json
```

Se niega a correr con el árbol sucio (decisión 014). Las poses salen de `backend/.cache/pose` (no versionada); los videos no están en el repositorio.
