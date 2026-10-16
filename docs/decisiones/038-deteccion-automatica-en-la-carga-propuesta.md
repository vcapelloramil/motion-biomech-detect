# Decisión 038 — Detección automática, en la carga, del tipo de golpe, del encuadre y del lado de la cámara (diseño A aprobado; implementación después de la demo)

**Fecha:** 15 de octubre de 2026
**Estado:** **APROBADA en lo esencial por Valentín el 15/10/2026** (ver "Aprobación y pre-registro"): diseño **A**, criterio de aceptación del 5 % y del 20 % como **pre-registro** e implementación **después de la demo**.
Nada de esto está implementado; las cifras de acierto **no se midieron** todavía (**NO MEDIDO**): lo que sigue es el diseño de cómo medirlas.
**Afecta a (si se aprueba):** `docs/ux/especificacion-frontend.md` §5 (Cargar) · `backend/app/engine/encuadre.py` · `backend/app/procesar_video.py` · contrato del reporte (1.4 → 1.5, aditivo) ·
`backend/app/consistencia.py` y `routers/evolucion.py` · una migración aditiva · decisiones 013, 035 y 036 · plan §9
**Protocolo de datos nuevos que la acompaña:** `docs/protocolo-sesion-lado-derecho.md`

---

## El problema

Hoy el usuario **declara** en Cargar el golpe, el encuadre y el lado de la cámara. Las tres declaraciones pueden estar mal (el caso real del 12/10: un saque de tres cuartos subido como perfil, decisión 035)
y agregan tres preguntas a una pantalla que ya pide jugador, fecha y modo de captura. El tutor sugirió que el sistema las **detecte y proponga**.

## Criterio de diseño (el que pidió Valentín)

1. **El sistema detecta y propone; el usuario corrige.** Nunca se cambia nada en silencio.
2. **Si la detección es dudosa, lo dice** ("no pudimos determinarlo") **y pregunta**. Eso no es "no auditable" (R3: dato no confiable): es un estado de la propuesta.
3. **Se guardan las dos cosas**, lo declarado y lo detectado, con su confianza y la versión de la regla (R4). Una discrepancia se informa, no se "corrige".
4. **El frontend no calcula nada biomecánico** (CLAUDE.md §4): la detección corre en el servidor (el motor).

## Qué se sabe hoy (datos que ya están en el repositorio)

| Dato | Valor | Fuente |
| --- | --- | --- |
| Corpus etiquetado con poses (Paso B, originales a tasa real) | 76 repeticiones medidas: saque perfil 11, saque tres cuartos 18, drive perfil 12, drive tres cuartos 12, revés perfil 11, revés tres cuartos 12 | `docs/resultados/paso-b-resumen.md` |
| Lado de la cámara de todo el corpus | **izquierda del jugador (no dominante), en el 100 %** (confirmado por Valentín el 13/10) | decisión 013, actualización |
| Etiquetas de gesto y encuadre | **declaradas por el propio jugador**; hay al menos un error de etiqueta conocido (`IMG_6391`, saque de tres cuartos subido como perfil) | decisión 035 |
| Regla "hombro más cercano" por la `z` relativa de los hombros, en la ventana ±0,3 s del gesto, sobre 84 clips | "izquierda" en **74 de 84 (88 %)**; **falla en el revés de tres cuartos: 9 de 12 dan "derecha"** (el giro del cuerpo adelanta el hombro dominante); saque 36/36 y drive 24/24 bien | `docs/resultados/pose-oclusion-lado-dominante.json` (campo `lado_cercano`; tabulado de nuevo, no re-medido) |
| Contraste de encuadre D (giro de la línea de hombros en la preparación, de 0,8 a 0,3 s antes del pico del tronco) | calibrado **solo con el saque**: perfil 26–42° (mediana 35°), tres cuartos 50–83° (mediana 56°); verificado con 28 repeticiones de la misma muestra: 0 avisos falsos, 0 sin afirmar | `docs/resultados/paso-b-saque.md`, decisión 035 |
| Costo de procesar un golpe | ~0,18 s por fotograma en Render Standard (117–147 s por golpe de 3–4 s); la pose es la mayor parte | `docs/resultados/criterio4-latencia.md` |

## Aprobación y pre-registro (15/10/2026)

**Aprobado por Valentín:**

1. **Diseño A** (la detección corre dentro del análisis que ya existe, "propone después"); el diseño B (pasada rápida previa en la carga) queda para cuando la validación lo justifique.
2. **Criterio de aceptación:** por campo, **error ≤ 5 % entre los determinados** y **"no determinado" ≤ 20 %**. Si un campo no lo cumple, **no se asigna solo**: pasa a **"el sistema propone y el usuario confirma"**.
3. **La implementación va DESPUÉS de la demo (28–30/10).** Antes de la demo, **solo si el 24/10 el núcleo está completo: extender D (el contraste de encuadre) a drive y revés.** Nada de la pantalla de Cargar se toca antes.
4. **La sesión del lado derecho** (`docs/protocolo-sesion-lado-derecho.md`) la graba Valentín **cuando el clima lo permita**; avisa. Sin esa sesión no se programa (c).

**Resueltas el 15/10/2026 (segunda ronda):**

5. **Tipo de golpe: el usuario NO elige nada.** Si la detección es segura, el sistema **asigna el tipo solo**; si en una misma carga hay golpes de distinto tipo, **los separa solo en sesiones distintas y lo informa**
   ("5 saques y 1 drive"). **Solo pregunta si la detección es dudosa ("no determinado").** El usuario **siempre puede corregir** (mover un golpe a otra sesión). Si en la validación **no se cumple el criterio**
   (≤ 5 % de error entre los determinados, ≤ 20 % de "no determinado"), el tipo pasa a **"propone y el usuario confirma"**.
6. **El lado de la cámara entra en la clave de la serie de Evolución: sí.** Nunca se mezclan lados en una misma serie.

**Encuadre y lado de la cámara** (sin instrucción nueva): siguen el criterio base de esta decisión (el sistema detecta y propone, el usuario corrige, lo dudoso se pregunta); la asignación automática de esos dos campos
se decide con el mismo criterio de aceptación cuando haya datos del lado derecho.

### Pre-registro (fijado ANTES de ver resultados de detección)

Esto se escribe el 15/10/2026, **antes de calcular cualquier acierto**. Lo único visto de la detección es la tabla del campo `lado_cercano` de `pose-oclusion-lado-dominante.json` (74 de 84 en la ventana del gesto), que ya
estaba en el repositorio y **no es** la regla propuesta (la propuesta mira la preparación y exige margen). **No se reajusta nada después de ver la evaluación.**

| Qué se fija | Valor |
| --- | --- |
| Unidad | la **repetición**; los umbrales se ajustan en **una sesión** y se evalúan en **la otra** (24/9 ↔ 25/9) y, para el lado, en la sesión nueva del lado derecho |
| "Determinado" | el sistema afirma un valor; "no determinado" = no cumple el margen o la fracción de fotogramas |
| Error | `errores / determinados` (los "no determinados" no cuentan como error ni como acierto; se informan aparte) |
| **Aceptación** | error ≤ 5 % **y** no determinado ≤ 20 %, **por campo** y **por gesto** donde corresponda |
| Lado: regla | mediana de `z(hombro derecho) − z(hombro izquierdo)` en la preparación (de 0,8 a 0,3 s antes del pico del tronco); afirma solo si la **fracción de fotogramas con el mismo signo ≥ 0,8** y `|mediana|` supera un margen que se **fija en la sesión de ajuste** como el menor valor que da **0 errores** en esa sesión |
| Encuadre: regla | giro de la línea de hombros en la preparación (la definición de D); por gesto, **perfil ≤ P** y **tres cuartos ≥ T** con P y T fijados en la sesión de ajuste como los extremos observados (como en el saque: 42° y 50°); entre los dos, "no determinado" |
| Gesto: regla | saque = muñeca dominante sobre la nariz y codo sobre el hombro sostenido en la preparación; drive y revés = **la que de las tres candidatas** (sentido del giro axial con la mano, distancia entre muñecas, lado del eje del tronco) **dé 0 errores en la sesión de ajuste**; si ninguna, se declara que no se pudo y el campo se pregunta |
| Qué se informa | matriz de confusión, acierto con Wilson de 95 %, cobertura, y las etiquetas dudosas revisadas a mano (con el motivo) |

## Propuesta por campo

### (c) Lado de la cámara — el más barato y el que **no se puede validar con el corpus actual**

- **Método.** Reglas sobre la pose, en la **fase de preparación** (en reposo o de 0,8 a 0,3 s antes del pico del tronco, **no** sobre el golpe completo): mediana de `z(hombro derecho) − z(hombro izquierdo)`;
  el hombro más cercano a la cámara indica el lado. Ya existe la función `lado_cercano` (`diagnosticos_e3.py`). Se afirma solo si **|mediana| supera un margen** y la **fracción de fotogramas con el mismo signo ≥ 0,8**;
  si no, "no pudimos determinarlo". Indicador de apoyo: hacia dónde mira la cara (nariz respecto de las orejas). La `z` es **inferida** y tiene inversiones (decisión 009): por eso el margen y el segundo indicador.
- **Por qué en la preparación:** la tabla de arriba muestra que sobre el golpe completo la regla falla en el revés de tres cuartos.
- **Validación.** El corpus tiene **una sola clase** (todo "izquierda"): un 100 % de acierto **no informaría nada**. **Hace falta una sesión con la cámara a la derecha**
  (`docs/protocolo-sesion-lado-derecho.md`): 16 saques con la cámara a la derecha y 12 a la izquierda el mismo día dan una matriz 2 × 2 real. **Espejar las poses del corpus no sirve**: un diestro espejado
  es un zurdo con la cámara a su derecha, la misma relación mano-cámara que ya tenemos; verifica la simetría del código para zurdos, no el lado derecho de un diestro.
- **Dependencias:** ninguna (se puede detectar antes que el gesto y el encuadre).

### (b) Encuadre — extender D a drive y revés

- **Método.** El mismo contraste (giro de la línea de hombros en la preparación) con **un umbral por gesto**, calibrado con las poses del Paso B (24 repeticiones por gesto, 12 por encuadre) que ya están en
  `backend/.cache/corpus-real-pose-b`. Entre los dos umbrales no se afirma nada ("no pudimos determinarlo"). Como la preparación del drive y del revés no es la del saque (giro de unidad), **el umbral del saque no se reutiliza**.
- **Dependencia:** necesita el gesto (a) para elegir el umbral; con el gesto sin determinar, solo se afirma si el giro cae fuera de **ambos** rangos.
- **Límite nuevo:** con la cámara por delante en diagonal (tres cuartos), el valor absoluto del giro **no distingue "por delante" de "por detrás"**; no hace falta para decidir perfil o tres cuartos, pero no verifica
  el lado de la red.
- **Es el punto 1 de lo que sigue a la demo** (plan §9): ya estaba previsto, ahora tiene un uso más.

### (a) Tipo de golpe — el más difícil

- **Método (reglas simples, fijadas antes de mirar resultados):**
  - **Saque:** muñeca dominante por encima de la cabeza (nariz) y codo sobre el hombro, sostenido durante la preparación (posición de "trofeo"), y la otra muñeca arriba al comienzo (lanzamiento). Regla casi inequívoca contra drive y revés.
  - **Drive contra revés:** candidatos a medir, **sin elegir uno de antemano**: (i) sentido del giro axial de la línea de hombros en la aceleración (ya calculado en el Paso A) combinado con la mano dominante;
    (ii) distancia entre las dos muñecas durante la aceleración (revés a dos manos: chica; drive: grande; un revés a una mano queda ambiguo); (iii) de qué lado del eje del tronco pasa la muñeca dominante.
    El corpus tiene 12 + 12 repeticiones de cada uno: alcanza para **descartar** reglas, no para ajustar un clasificador (con un jugador y dos sesiones, un árbol aprendido se sobreajusta).
- **Límite fuerte:** drive y revés dependen de la técnica de **este** jugador (una o dos manos en el revés, que el repositorio no registra) y del lado de la cámara (el signo del giro depende de la `z`, que se invierte a veces).
  Por eso (c) va antes que (a).
- **Dependencias:** (c) → (a) → (b).

## Validación contra el corpus etiquetado

**Se fijan antes de mirar** (como el pre-registro del recálculo): los umbrales, la unidad de análisis y el criterio de aceptación.

| Qué | Cómo |
| --- | --- |
| Unidad y partición | la **sesión**: umbrales con la sesión 1 (24/9) y evaluación en la sesión 2 (25/9), y al revés; nunca se evalúa sobre lo que se usó para fijar el umbral |
| Qué se informa | por campo: **matriz de confusión** (gesto 3 × 3; encuadre 2 × 2 por gesto; lado 2 × 2 con la sesión del lado derecho), **% de acierto con intervalo de Wilson de 95 %**, **% "no determinado"** (cobertura) y el error **entre los determinados** |
| Criterio de aceptación (aprobado) | error entre los determinados **≤ 5 %** y "no determinado" **≤ 20 %**; si no, el campo **no se asigna solo**: el sistema propone y el usuario confirma |
| Qué cuenta como verdad | la etiqueta declarada, **revisada a mano** donde haya duda (hay un error de etiqueta conocido) |

**Límites que hay que declarar:** un solo jugador (diestro); un teléfono y un lugar; dos sesiones consecutivas; el corpus es **todo del lado izquierdo** (el lado no se valida sin la sesión nueva); no hay zurdos; tres cuartos
**por delante** (según Valentín el 15/10/2026) en todo el corpus; las etiquetas las puso la misma persona que las evalúa. Lo que salga **no generaliza a otros jugadores**: solo dice si la regla funciona en el material propio.

## Cómo cambian la carga, la sesión y la Evolución

**Dos diseños; se propone empezar por A.**

| | **A. Propone después** (post-hoc) | **B. Propone antes** (en la carga, la lectura literal de la sugerencia) |
| --- | --- | --- |
| Qué hace | La detección corre dentro del análisis que ya existe y el reporte y la vista de sesión dicen *"declaraste saque; el video parece un drive"*. El usuario puede **dejar los campos en "que lo detecte el sistema"** | Una **pasada rápida** previa (pose sobre 1 de cada ~5 fotogramas y en menor resolución) llena la propuesta en Cargar antes de analizar; el usuario confirma o corrige y recién ahí se analiza |
| Cómputo extra | **ninguno** (reutiliza la pose del análisis) | una segunda pasada de pose por golpe, estimada en ~15–30 s en Standard (**NO MEDIDO**: derivada de 0,18 s por fotograma completo) o pausar el análisis en un estado nuevo `por_confirmar` |
| Carga | casi igual (campos opcionales) | la pantalla pasa a "subí los golpes → mirá lo que detectamos → confirmá" |
| Riesgo | bajo | medio: estado nuevo, espera en la pantalla, más pruebas |

**Efectos comunes:**

- **Datos.** Una columna aditiva `videos.deteccion` (jsonb: valor, confianza, motivo, versión de la regla; la escribe solo el servidor, como los tiempos) y `trazabilidad.deteccion` en el reporte (contrato 1.5, aditivo).
  Migración **aditiva**: no rompe nada de lo que está en producción.
- **Tipo de golpe y sesiones mezcladas (resuelto el 15/10).** En una misma carga, el sistema **separa solo** los golpes por tipo detectado en **sesiones distintas** (mismo jugador y fecha, con el tipo, el encuadre y el lado que
  corresponden) y lo **informa** ("5 saques y 1 drive"), con la opción de **corregir** cualquiera (mover un golpe a otra sesión). Un golpe **"no determinado" no se asigna ni se excluye**: se pregunta, y mientras tanto se cuenta
  con lo declarado y se marca. Un golpe **ya separado se sigue viendo** en la Biblioteca (nada desaparece en silencio) y su reporte lleva lo detectado y la confianza.
- **Si el criterio no se cumple** para el tipo de golpe: la separación **no es automática**: el sistema propone ("parece un drive") y el usuario confirma antes de que se cree la sesión.
- **Evolución (resuelto el 15/10: sí).** Hoy elige jugador × golpe × encuadre y **avisa** si el lado de la cámara cambia entre sesiones. **El lado pasa a ser parte de la clave de la serie** (nunca se mezclan
  lados). Los cambios en `consistencia.py` y `routers/evolucion.py` son chicos.
- **Lo que no cambia:** ningún veredicto (035 y 036); el contraste de encuadre existente se integra, no se duplica.

## Esfuerzo y calendario

| Pieza | Sesiones | Nota |
| --- | --- | --- |
| Banco de validación sobre las poses cacheadas (matrices, partición por sesión) | 0,5–0,75 | sin cómputo nuevo |
| (b) D para drive y revés (umbral por gesto) | 0,5–1 | **ya estaba en el plan §9, punto 1** |
| (c) Detector de lado + prueba con la sesión del lado derecho | 0,5 + 0,25 | depende de grabar |
| (a) Reglas de gesto | 1–1,5 | incierto: depende de qué separe drive de revés en este jugador |
| `deteccion` en el motor y el contrato 1.5 + migración aditiva | 0,75–1 | |
| Cargar (propuesta por golpe, confirmar, "no pudimos determinarlo"), mover golpe, ajuste de Evolución | 1,5–2 | |
| Pruebas y regresión | 0,5 | |
| **Total (diseño A completo)** | **≈ 4–5** | el diseño B suma ~1 (pasada rápida y estado nuevo) |

**¿Entra antes de la demo del 28–30/10? Solo una parte, y condicionada.** Quedan 13 días; el núcleo restante es ≈ 1,25 sesiones (respaldo con restauración probada, ensayo) más las pruebas de los pasos 5 y 6 y de
esta semana, con un ritmo observado de 1 a 1,5 sesiones por día y la regla de recorte del plan (si el 24/10 el núcleo no está al 80 %, se recorta). Recomendación:

1. **Antes de la demo (0,5–1 sesión, sin tocar el flujo de carga):** el banco de validación y **(b) D para drive y revés**, que ya estaba previsto y solo extiende un aviso existente. **Solo si el 24/10 el núcleo está al 80 %.**
2. **Después de la demo, en este orden:** sesión del lado derecho → (c) → diseño A de (a) y (b) en la carga → recién entonces evaluar B.
3. **No se recomienda** meter (a) ni la pantalla nueva de Cargar antes del 28/10: es la pantalla por la que pasa todo, y un error ahí rompe la demo.

## Decisiones (estado al 15/10/2026)

| # | Pregunta | Estado |
| --- | --- | --- |
| 1 | ¿Se empieza por A (propone después)? | **Aprobado** |
| 2 | ¿Criterio de aceptación del 5 % de error y 20 % de "no determinado"? | **Aprobado, como pre-registro** |
| 3 | ¿Un golpe que contradice a su sesión se mueve a pedido o se reagrupa solo? | **Resuelta para el tipo de golpe: se separa solo, en sesiones distintas, y se informa; solo pregunta si es dudoso; el usuario corrige. Si la validación no cumple el criterio: propone y confirma.** Encuadre y lado: propone y el usuario corrige |
| 4 | ¿El lado de la cámara entra en la clave de la serie de Evolución? | **Sí** |
| 5 | ¿Se graba la sesión del lado derecho antes de programar (c)? | **Sí**: la graba Valentín cuando el clima lo permita |
| 6 | ¿Qué parte entra antes de la demo? | **Solo D para drive y revés, y solo si el 24/10 el núcleo está completo** |

## Riesgos

| Riesgo | Respuesta |
| --- | --- |
| Un detector que acierta sobre un jugador y falla con otro | Se declara el límite; el criterio es "propone y confirma", no "decide" |
| El usuario acepta sin mirar | La propuesta muestra el esquema de la cámara y el motivo; las discrepancias quedan registradas |
| Las inversiones de `z` (009) dan un lado equivocado con confianza | Margen mínimo, fracción de fotogramas, segundo indicador (cara) y "no pudimos determinarlo" |
| Tiempo: la demo | La parte que entra antes es la que no toca la carga |
