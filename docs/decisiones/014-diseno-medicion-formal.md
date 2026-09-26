# Decisión 014 — Diseño de la medición formal de los Criterios 1, 2 y 3

**Fecha:** 26 de septiembre de 2026
**Estado:** **PROPUESTA — NO VIGENTE hasta que Valentín confirme los puntos marcados [A CONFIRMAR].**
Nada de lo que sigue se mide hasta entonces.
**Afecta a:** tareas 4.7 y 4.8 del plan · punto de decisión de la Etapa 4 · Capítulos 6 y 7 · decisión 012

---

## Por qué se escribe antes de medir

Una vez que se miran los órdenes y los tiempos de la sesión 2, no se puede des-mirar: cualquier
definición o umbral elegido después queda expuesto a ajustarse a lo que salió. Por eso las definiciones
y las reglas de cumplimiento se fijan y se commitean **antes** de correr la medición.

## Principios

1. **Congelar antes de medir.** Motor `0.4.1` (se registra el hash del commit al congelar). Ningún
   umbral cambia entre el congelamiento y el informe: techo de plausibilidad, ventana de ±300 ms, corte
   de Winter automático, detector de inversión de `z`, umbral de salto imposible (sin recalibrar).
2. **Separar ajuste y medición.** La sesión 1 se usó ampliamente para explorar y fijar criterios de
   trabajo: es el **conjunto exploratorio**. De la sesión 2 solo se miró la confianza de pose (no
   órdenes ni tiempos): es el **conjunto de medición**. *[A CONFIRMAR]* Medición primaria sobre la
   sesión 2; la sesión 1 se informa aparte como réplica, marcada como no independiente.
3. **Unidad de análisis:** la repetición (un clip pre-cortado), con la ventana anclada al torso
   (`ancla-torso`, decisión de la ventana anclada). Se reportan **todos** los resultados, también los
   que no cumplen, y cuántas repeticiones quedan fuera por no ser válidas.
4. **Alcance por encuadre (decisión 011):** el brazo solo se evalúa en tres cuartos; en perfil se evalúan
   pelvis y torso. "Repetible" no significa "correcto": no se juzga contra un orden esperado.
5. **Todo reproducible:** scripts versionados y resultados en `docs/resultados/`.

## Criterio 1 — pelvis, torso y brazo distinguibles y ordenables de forma repetible (meta 8 de 10)

- **Repetición válida:** clip con pose detectada y ancla de torso auditable (pico de torso fuera de
  tramos excluidos y bajo el techo). El denominador son **todas** las repeticiones del grupo; se informa
  cuántas no son válidas.
- **1a — distinguibles y ordenables:** los tres picos (pelvis, torso, brazo) son auditables y cada par
  consecutivo del orden observado difiere en más de **τ**. *[A CONFIRMAR]* τ = **1 fotograma (4,17 ms)**,
  la resolución de muestreo (recomendación); se informa también con τ = 2 y 3 fotogramas como
  sensibilidad **declarada de antemano**.
- **1b — repetibles:** entre las repeticiones ordenables de un grupo (sesión × gesto × encuadre), la
  fracción que comparte el orden modal (matriz de concordancia del orden).
- **Regla de cumplimiento:** *[A CONFIRMAR]* 1a ≥ 0,8 **y** 1b ≥ 0,8, por grupo.
- **Grupos:** *[A CONFIRMAR]* Criterio 1 formal = cadena completa en saque, drive y revés de **tres
  cuartos**; pelvis→torso (dos picos) en perfil y tres cuartos, informado como resultado parcial.
- **Si no se cumple:** replegarse a la fase de preparación (Capítulo 4). Esa decisión no se toma aquí.

## Criterio 2 — error angular en articulaciones proximales (meta < 20,6°)

**Requiere goniometría manual sobre fotogramas: no puede hacerla Claude.**

- **Fotogramas:** *[A CONFIRMAR]* N y regla de selección. Propuesta: regla fija, definida por el motor
  antes de conocer el error (p. ej. instante del pico de torso y instante de máxima separación
  cadera-hombro, en 2 repeticiones por gesto y encuadre de la sesión 2). No se eligen fotogramas a mano
  mirando el resultado.
- **Ángulos:** *[A CONFIRMAR]* rodilla (cadera-rodilla-tobillo), tronco-muslo (hombro-cadera-rodilla) y
  separación cadera-hombro. La goniometría manual es **2D**, así que se compara con el ángulo calculado
  en el **plano de la imagen**, no con el 3D de `puntos_mundo`. Limitación a declarar: el ángulo 3D no
  queda validado por esta vía.
- **Medición ciega:** fotogramas exportados **sin esqueleto**, en orden aleatorio, con una planilla CSV
  para cargar los valores (herramientas como Kinovea o ImageJ). *[A CONFIRMAR]* quién mide (una o dos
  personas) y con qué definición anatómica de los puntos.
- **Cumplimiento:** error por articulación (no un único número, apartado 3.3.2.8): media, mediana y
  percentil 95. *[A CONFIRMAR]* Cumple si la media es < 20,6° en cada articulación.
- **Si no se cumple:** replegarse a análisis 2D con encuadre controlado (Capítulo 4).

## Criterio 3 (redefinido, decisión 012) — consistencia entre sesiones

- **Métricas** (fijadas ahora): (i) desfase pelvis→torso (ms); (ii) desfase torso→brazo (ms), solo tres
  cuartos; (iii) pico de velocidad de pelvis y de torso (°/s); (iv) separación cadera-hombro máxima (°).
- **Por métrica y grupo:** dispersión intra-sesión σ_w (desvío robusto, MAD × 1,4826, de las
  repeticiones de una misma sesión) y diferencia entre sesiones Δ = |mediana s1 − mediana s2|, con
  intervalo bootstrap de Δ.
- **Regla:** *[A CONFIRMAR]* "consistente" si Δ ≤ k · σ_w con k = 1 (recomendación).
- **Cumplimiento:** *[A CONFIRMAR]* la fracción de combinaciones métrica × grupo consistentes (propuesta:
  ≥ 75 %).
- **Precondición (decisión 012):** documentar la equivalencia de encuadre entre sesiones (tamaño del torso
  en píxeles y posición horizontal del jugador, mediana por clip). *[A CONFIRMAR]* umbral de diferencia
  aceptable y cómo tratar las **tres tomas** (`02`, `02b`, `02c`) del saque de tres cuartos de la sesión 2
  (agrupadas o por separado).
- **Qué no se afirma:** que el sistema detecte un cambio real de técnica (decisión 012).

## Preguntas abiertas para Valentín

1. τ del Criterio 1 (1 fotograma recomendado) y la regla 1a ≥ 0,8 y 1b ≥ 0,8.
2. ¿Sesión 2 como conjunto de medición primario y sesión 1 como réplica?
3. Grupos del Criterio 1: ¿cadena completa solo en tres cuartos?
4. Criterio 2: ángulos, N, regla de selección, quién mide, comparación 2D y media < 20,6°.
5. Criterio 3: métricas, k, fracción exigida, equivalencia de encuadre y las tres tomas del saque.
