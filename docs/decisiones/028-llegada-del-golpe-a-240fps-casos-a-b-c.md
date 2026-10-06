# Decisión 028 — Cómo llega un golpe grabado a 240 fps (casos a, b y c) y qué hace E0 con ellos

**Fecha:** 7 de octubre de 2026
**Estado:** vigente en lo implementado y medido; **abierta** en dos puntos que dependen de la prueba del iPhone (ver "Pendiente").
**Afecta a:** `backend/app/engine/uniformidad_temporal.py` · `backend/app/inspeccionar_subidas.py` · `procesar_video._factor_y_motivo` (decisión 020) ·
`docs/ux/especificacion-frontend.md` §5 · E0 (`engine/ingest.py`) · Capítulos 6 y 7 (limitaciones)

---

## El problema

Valentín observó con su iPhone que, al **recortar un golpe del medio** de una grabación en cámara lenta (en Fotos), el recorte se reproduce a velocidad normal pero el archivo sigue
figurando a más de 200 fps. Su lectura: el archivo conserva los 240 fotogramas por segundo reales y pierde la indicación de reproducción lenta. Eso significa que **un mismo golpe puede llegar al
servidor de tres formas**, que las marcas de tiempo del contenedor no permiten distinguir del todo:

| Caso | Qué es | Marcas de tiempo | Fotogramas | ¿Válido? |
| --- | --- | --- | --- | --- |
| **(a)** | 240 fps **en tiempo real** (el recorte del medio) | separadas 1/240 s | todos | Sí |
| **(b)** | **Cámara lenta horneada** a 30 fps (el formato del corpus propio) | separadas 1/30 s | todos (los de la captura) | Sí |
| **(c)** | **30 fps en tiempo real con fotogramas descartados** (reenviado por mensajería, convertido con un editor) | separadas 1/30 s | 1 de cada 8 | **No** |

**Lo que las marcas de tiempo pueden y no pueden decir:** distinguen (a) de (b)/(c). **No distinguen (b) de (c)**: las dos son 1/30 s constante. Hace falta saber cuánto duró el gesto en la vida real
(cuántos fotogramas tendría que haber: duración real × 240 en (b), × 30 en (c)). Esa duración la sabe el usuario, no el archivo.

## Lo implementado

1. **`engine/uniformidad_temporal.py`** (lógica pura, 17 pruebas sin video): `clasificar_caso` decide (a), (b), (c) o *indeterminado* a partir de las marcas, la cantidad de fotogramas y la duración real; sin
   duración real, un archivo a ~30 fps queda **indeterminado** y no se adivina (R3). `marcas_de_tiempo` lee los `pts` con ffprobe. Un único intervalo atípico (se midió en el corpus: el último fotograma de un
   recorte) no vuelve variable a un archivo.
2. **El inspector** (`python -m app.inspeccionar_subidas --email … --duracion-real S`) informa, por cada selector de la página de prueba del iPhone: fps del contenedor, fotogramas, duración, tipo de marcas de tiempo
   y el caso (a, b o c). Verificado con archivos reales fabricados a partir de un recorte propio: re-temporizado a 240 fps (→ a), el recorte tal cual (→ b), con 7 de cada 8 fotogramas descartados (→ c).
3. **`_factor_y_motivo` con (a):** `camara_lenta_240` sobre un contenedor de 240 fps da **factor 1 y 240 fps efectivos, aptitud completa** (también con 239,76 y 240,24 normalizados, y con `camara_lenta_120` sobre 120).
   Declarar `normal` el mismo archivo también da 240 efectivos. 8 pruebas nuevas en `tests/unit/test_procesar_video_factor.py`.
4. **Formulario de carga** (especificación §5): explica que la pregunta es **cómo se grabó, no cómo se ve ni cómo llega el archivo** — "si usaste cámara lenta, elegí cámara lenta aunque el video recortado se vea a velocidad normal"
   — y advierte que un video que perdió fotogramas por el camino no se recupera con ninguna opción.

## Lo medido en el corpus propio (`docs/resultados/uniformidad-temporal-corpus.json`, reproducible con `python -m app.diagnostico_uniformidad_corpus`)

- **115 clips** (18 originales, 97 recortes): las marcas de tiempo son **constantes en todos**; **30 fps** en todos los de cámara lenta y **60 fps** en los dos de velocidad normal. **Todos los clips de cámara lenta del corpus son del caso (b).**
  El corpus **no tiene ningún ejemplo real de (a) ni de (c)**: esos casos se cubren con pruebas unitarias y archivos fabricados, y con la prueba del iPhone (pendiente).

## Velocidad no uniforme (rampas): evaluado, y **corrección de un error mío**

Una cámara lenta de iPhone con el tramo lento editado puede tener tramos a velocidad normal en los extremos, horneados descartando fotogramas. Con marcas constantes no se ven en los tiempos. Se probó un detector por contenido
(energía de movimiento entre fotogramas) y se midió contra el corpus.

**Corrección.** Durante el trabajo se interpretó que los saltos de movimiento al principio y al final de los originales eran rampas de velocidad. **Era un error.** Mirando los fotogramas (el final del original de 190 s
muestra a la persona acercándose al teléfono, agarrándolo y cortando la grabación) y comprobando que **los dos originales de velocidad normal, que no tienen rampas, dan el mismo patrón**, lo que el detector mide es **manejo de la cámara y movimiento brusco**, no rampas. Los originales del corpus
**no tienen rampas** (toda la grabación es cámara lenta). **No hay ninguna rampa real en el corpus.**

| Umbral (energía > N × base, durante ≥ 0,5 s) | recortes de golpe marcados (de 95) | clips completos de velocidad normal (de 2) | originales (de 18) |
| --- | --- | --- | --- |
| ≥ 3× | 32 (34 %) | 2 | 18 |
| ≥ 5× (por defecto) | **5 (5,3 %)** | 2 | 18 |
| ≥ 6× | 1 (1,1 %) | 2 | 18 |
| ≥ 8× (el factor de una rampa real) | **0** | 2 | 18 |

Los 18 originales y los dos clips completos de velocidad normal se marcan siempre, porque el detector responde a **cualquier** movimiento mucho mayor que el habitual, no solo a rampas. Con 8× no marca ningún golpe válido, pero una rampa real de 8× quedaría justo en ese umbral, así que tampoco sirve para detectarla de forma confiable.

**Decisión: E0 NO rechaza por velocidad no uniforme.** Razones:
1. El detector **no distingue una rampa de un movimiento brusco**, y no hay una rampa real con la cual calibrarlo.
2. Con el umbral por defecto rechazaría 5 de cada 95 golpes válidos (5,3 %); subiéndolo a 8× no rechaza ninguno, pero ahí una rampa de 8× queda justo en el borde. Un rechazo falso también es un error, y se suma al costo de una subida desde el celular.
3. La exposición está acotada: el bucket limita a 50 MB y el formulario avisa a partir de ~8 s, así que un clip con rampa tiene que ser corto y el usuario tuvo que editar las barras de cámara lenta a propósito.
4. Existe una red de seguridad parcial: si el golpe cae dentro de una rampa, las velocidades salen ×8 y los techos de plausibilidad (decisión 020) lo marcan, pero **de forma condicional y con poco margen** (1,08× a 1,81× en los casos medidos).

El módulo conserva `detectar_tramos_acelerados` como **diagnóstico experimental** (el inspector lo informa como "tramos con mucho más movimiento por fotograma", sin llamarlos rampas) y su docstring declara el límite.

## El caso (c) es el riesgo real

`_factor_y_motivo` **no puede detectar (c)**: 30 fps × factor 8 = 240 cierra igual que en (b), y el motor multiplicaría todas las velocidades por 8 sin avisar. Es el mismo problema que el "error inverso" de la decisión 020 (normal declarado como cámara lenta),
con las mismas defensas condicionales (techos de plausibilidad) y la misma propuesta diferida (control contra historial, decisión 020). Qué puede cambiar esto: la prueba del iPhone dirá **si Safari entrega (c)** (fotogramas descartados al pasar por el selector de archivos).
Si lo hace, el formulario tiene que dejar de ofrecer ese camino o pedir la duración real del gesto.

## Pendiente

1. **Prueba del iPhone** (https://kinetiq-prueba-iphone.pages.dev/, cuatro selectores): dirá si Safari entrega el recorte como (a), como (b) o como (c) **y si el recorte del medio conserva realmente los 240 fps** (por ahora es la lectura de Valentín, no un dato medido). Necesita la duración real del golpe.
2. **Una rampa real:** para calibrar un detector hay que tener una. Valentín puede producirla editando en Fotos las barras de cámara lenta de un video (dejando los extremos a velocidad normal) y subiéndolo con el selector A. Con ella se decide si vale la pena un detector basado en la pose (la velocidad de las articulaciones da un escalón ×8 que el manejo de la cámara no produce de la misma forma), o si basta con la advertencia al usuario.
3. **Limitaciones para los Capítulos 6 y 7:** el caso (c) se detecta solo de forma condicional; las rampas no se detectan.

## Consecuencias

- El inspector y el diagnóstico del corpus quedan como instrumentos de medición (solo lectura). Ninguno cambia el comportamiento de producción.
- **E0 no cambia en esta decisión.** Si la prueba del iPhone muestra (c), se abre una decisión nueva que supersede a esta.
- Las marcas de tiempo del archivo (`fps_por_marcas`) todavía no se guardan en la trazabilidad del reporte; se evaluará al ensamblar el reporte (tarea 5.4).
