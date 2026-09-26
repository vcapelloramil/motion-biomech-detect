# Decisión 014 — Diseño de la medición formal de los Criterios 1, 2 y 3

**Fecha:** 26 de septiembre de 2026
**Estado:** **VIGENTE (congelada)** desde el commit que incluye esta versión y el código de medición, con
**una excepción**: la definición del "instante de pico" del Criterio 3 (ver más abajo) queda pendiente de
confirmación de Valentín. **Ese punto no se mide hasta confirmarlo.**
**Afecta a:** tareas 4.7 y 4.8 del plan · punto de decisión de la Etapa 4 · Capítulos 6 y 7 · decisiones
011, 012 y 013

---

## Congelamiento

Se fijan **antes** de medir las definiciones, los umbrales y las reglas de cumplimiento. Motor `0.4.1`.
Ningún parámetro cambia entre este congelamiento y el informe: techo de plausibilidad, ventana anclada al
torso (± 300 ms), corte de Winter automático (un corte por clip), detector de inversión de `z`, umbral de
salto imposible (sin recalibrar), `brazo_via = codo`. Cada resultado registra el hash del commit y la
versión del motor con que se generó.

## Principios

1. **Sesión 2 = conjunto de medición; sesión 1 = réplica exploratoria** (etiquetada así, no
   independiente: se usó para explorar y fijar criterios de trabajo). *Confirmado por Valentín.*
2. **Transparencia:** una tanda automática llegó a ejecutar `explorar_fase_b` sobre la sesión 2 sin que se
   leyera ningún resultado; se descartaron los archivos. De la sesión 2 solo se leyeron confianza y
   cobertura de pose (decisión 013) **antes** de este congelamiento.
3. **Unidad de análisis:** la repetición (un clip pre-cortado), con la ventana anclada al torso.
4. Se reportan **todos** los resultados, también los que no cumplen, y cuántas repeticiones quedan fuera.
5. Todo reproducible: scripts versionados y resultados en `docs/resultados/`.

## Criterio 1 — pelvis, torso y brazo distinguibles y ordenables de forma repetible (meta 8 de 10)

**Universo.** Sesión 2: 48 repeticiones (saque de perfil 6; saque de tres cuartos 18 en tres tomas `02`,
`02b`, `02c`; drive de perfil 6 y de tres cuartos 6; revés de perfil 6 y de tres cuartos 6). Sesión 1
(réplica): las 36 repeticiones de esos mismos seis grupos a 240 fps (sin controles de 30/60 fps ni tomas
de espaldas o fuera de cuadro).

**Definiciones.** Los instantes de los picos son fotogramas enteros (1 fotograma = 4,17 ms).
- **Repetición válida:** pose detectada y ancla de torso auditable (R3).
- **Ordenable con tolerancia τ:**
  - *par (pelvis, torso):* ambos picos auditables y |Δ| **> τ** fotogramas;
  - *cadena (pelvis, torso, brazo):* los tres picos auditables y cada par consecutivo del orden observado
    separado **> τ** fotogramas.
- **τ = 1 fotograma** (primaria; "más de 1" = al menos 2 fotogramas, 8,3 ms). **Sensibilidad declarada de
  antemano: τ = 2 y 3.** *Confirmado por Valentín.*

**Dos mediciones separadas, que NO se fusionan** (*confirmado por Valentín*):

- **1 — Repetibilidad del orden (regla del criterio original).** *Cualquiera sea el orden.*
  - **1a** = ordenables / **todas** las repeticiones del grupo (se informa también ordenables / válidas,
    la lectura literal de la tesis: "8 de cada 10 repeticiones válidas").
  - **1b** = entre las ordenables, la fracción que comparte el **orden modal** (matriz de concordancia).
  - El Criterio 1 **se cumple en un grupo si 1a ≥ 0,8 y 1b ≥ 0,8.**
- **1c — Coincidencia con el orden esperado** (medida **aparte**, sin umbral de cumplimiento, **no
  cuenta** como fallo ni como éxito del Criterio 1). Fracción de ordenables con `pelvis → torso` (par) o
  `pelvis → torso → brazo` (cadena). Permite decir, por ejemplo, "en perfil el orden es repetible pero
  invertido". **Limitación (decisión 011):** el orden esperado del **brazo** no tiene fundamento
  bibliográfico (el brazo es un proxy de orientación); para la cadena, 1c es informativo del *balanceo*
  del brazo y **no comparable con la literatura**. El único 1c comparable es el del par pelvis-torso.

**Grupos.** Cadena: saque, drive y revés de **tres cuartos** (el saque, agrupado y también por toma;
las tomas `02b` y `02c` cuentan aquí). Par pelvis-torso: los tres gestos en **perfil y tres cuartos**.
Proporciones con intervalo de Wilson de 95 %. Si no se cumple: replegarse a la fase de preparación
(Capítulo 4); esa decisión no se toma en este documento.

## Criterio 2 — error angular (meta < 20,6°)

**Goniometría manual: la hace Valentín.** Protocolo ciego, `python -m app.criterio2`.

- **Conjunto:** sesión 2. **18 fotogramas** (entre los 15 y 20 pedidos): **3 por estrato**, con estratos =
  gesto (saque, drive, revés) × encuadre (perfil, tres cuartos). Del saque de tres cuartos, solo la toma
  principal `02`. Un fotograma por repetición (clips distintos).
- **Ángulos:** **rodilla** (cadera-rodilla-tobillo) y **codo** (hombro-codo-muñeca), **ambos en cada
  fotograma** → 36 mediciones (18 por articulación).
- **Selección (regla fija, con semilla `26092026`, antes de conocer el error):**
  - candidatos: fotogramas a −300, −150 y 0 ms del pico crudo del torso (sin E3) de cada repetición;
  - **elegibles solo si el sistema reporta confianza razonable** (*pedido de Valentín*): en ese fotograma,
    los tres puntos de cada ángulo con confianza **≥ 0,6**, tomando para cada ángulo el lado con mayor
    confianza mínima; se requieren **ambos** ángulos;
  - por estrato, sorteo con la semilla entre los elegibles, uno por repetición; si hay menos de 3 se toman
    todos y se informa el faltante.
- **Limitación a declarar:** al medir solo donde el sistema es confiable, el resultado vale **para la
  región auditable**, no para todo el gesto; el codo medido será, en muchos fotogramas, el **no
  dominante** (el dominante suele estar tapado, decisión 013). Se registra el lado de cada medición.
- **Comparación:** el sistema en el **plano de la imagen** (píxeles, con `ancho` y `alto`; la goniometría
  manual es 2D). El ángulo 3D queda como resultado secundario y **no queda validado** por esta vía.
- **Medición ciega:** fotogramas **sin esqueleto**, identificadores opacos, orden aleatorio, planilla CSV.
  Se pide el ángulo **interior (0–180°) en el vértice** en el plano de la imagen. Opcional: repetir 5
  fotogramas para estimar el error intra-observador. La clave (qué clip, qué fotograma, qué valor dio el
  sistema) **queda fuera del repositorio y no se abre** hasta terminar de medir.
- **Cumplimiento:** por articulación (no un único número): media, mediana, percentil 95, sesgo con signo.
  **Cumple si la media es < 20,6° en cada articulación.** Si no: replegarse a 2D con encuadre controlado.

## Criterio 3 (redefinido, decisión 012) — consistencia entre sesiones

- **Solo el saque de tres cuartos usa la toma `02`** (*pedido de Valentín*): `02b` y `02c` quedan para el
  Criterio 1 y **no** entran en el Criterio 3. Los demás grupos usan sus seis repeticiones por sesión.
- **Métricas** (*confirmadas por Valentín*): **(i) separación cadera-hombro máxima** (°) y **(ii)
  dispersión del instante de pico**, comparando la variación **entre sesiones** con la **intra-sesión**.
- **Regla:** por métrica y grupo, σ_w = desvío robusto intra-sesión (MAD × 1,4826, promediado entre las dos
  sesiones) y Δ = |mediana s1 − mediana s2|, con intervalo bootstrap de Δ. **Consistente si Δ ≤ σ_w.**
  Cumplimiento: ≥ 75 % de las combinaciones métrica × grupo consistentes. *(Propuesta de Claude; no
  objetada.)*
- **(i) Separación cadera-hombro máxima:** máximo, dentro de la ventana ± 300 ms del ancla, del ángulo entre
  el eje de caderas y el de hombros (3D, series filtradas por E3).
- **(ii) "Instante de pico": DEFINICIÓN PENDIENTE — [A CONFIRMAR].** Con una repetición por clip y la
  ventana anclada al pico del torso, "el instante del pico dentro de la ventana" es una constante; y el
  instante dentro del clip depende de cómo se cortó. Hace falta un **origen** propio del gesto.
  **Propuesta:** *instante del pico de torso medido desde el instante de máxima separación cadera-hombro*
  (ms), ambos eventos de la misma repetición. **No se mide (ii) hasta que Valentín confirme la definición.**
- **Precondición (decisión 012):** informar la equivalencia de encuadre entre sesiones (tamaño del torso en
  píxeles y posición horizontal del jugador, mediana por clip) y **señalar** las diferencias de más de
  20 % *(criterio informativo; no excluye clips)*.
- **Qué no se afirma:** que el sistema detecte un cambio real de técnica (decisión 012).
