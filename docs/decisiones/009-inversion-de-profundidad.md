# Decisión 009 — Detector de inversión de profundidad en la validación (E2b/E3)

**Fecha:** 27 de agosto de 2026
**Estado:** vigente
**Afecta a:** Etapa 2 (`engine/validation.py`) · Etapa 3 (`engine/preparacion.py`) · Etapa 4 · Capítulo 6

Es un **fix a etapas ya mergeadas**, hecho en su propia rama (`fix/inversion-z`) con
sus pruebas y su etiqueta (`v0.3.1`), antes de seguir con la Etapa 4.

---

## El problema

En la validación cualitativa de la Etapa 4 (decisión 008) el saque
`zverev_saque_lateral_02` produjo una velocidad angular del brazo de 24 932 °/s —
un valor imposible que el techo de plausibilidad cortó correctamente, pero cuya
causa había que entender.

Al mirar la secuencia de pose fotograma a fotograma alrededor del pico (frame 566,
≈1,13 s), `CODO_DER` en el espacio métrico:

| frame | z (m) | confianza |
| --- | --- | --- |
| 564 | +0,095 | 0,99 |
| 565 | +0,098 | 0,99 |
| **566** | **−0,050** | **0,65** |
| 567 | −0,087 | 0,56 |
| … | (z negativa hasta ~573) | |
| 574 | +0,022 | 0,95 |

Es una **inversión de profundidad**: MediaPipe no distingue si el codo está delante
o detrás del plano del cuerpo y, en el instante rápido, da vuelta la coordenada `z`
de golpe (§3.3.2.1). La dirección del vector `HOMBRO→CODO` gira 180° en el eje de
profundidad → ω se dispara.

**Ni E2 ni E3 lo marcaban:**

- **Baja confianza:** en el frame 566 la confianza es **0,65**, por encima del
  umbral de 0,5.
- **Salto imposible:** el desplazamiento 3D del frame 565→566 es
  `√(0,148² + 0,051²) ≈ 0,156 m`, sobre un torso de ~0,51 m → **0,31 longitudes de
  torso**, por debajo de `MAX_SALTO_TORSOS = 0,5`.

## La decisión

Se agrega un **tercer control** a `engine/validation.py`:
`detectar_inversiones_z(seq, *, espacio)`.

Firma de una inversión de profundidad — MediaPipe venía siguiendo bien una
articulación, de golpe elige el lado equivocado del plano del cuerpo, y corrige.
Las **cinco** condiciones a la vez:

1. **Confianza alta antes** del cambio: `confianza(frame previo) ≥ 0,80`
   (`CONF_MIN_PRE_INVERSION`). Si la articulación ya venía mal seguida, su `z` es
   ruido crónico —lo maneja el marcado por baja confianza—, no una inversión.
2. **Cambio de signo de `z`** entre fotogramas consecutivos (`z0 · z1 < 0`).
3. **Magnitud apreciable:** `|Δz| / longitud_de_torso > 0,20`
   (`UMBRAL_INVERSION_Z_TORSOS`). El frame 566 da 0,29.
4. **Dominado por `z`:** `|Δz| > 1,8 · |Δ(x, y)|` (`FACTOR_DOMINANCIA_Z`). El frame
   566 da 2,9. Descarta el movimiento 3D genuino, donde `x`, `y` también se mueven.
5. **`z` vuelve** al signo original dentro de `MAX_SPAN_INVERSION_Z = 15`
   fotogramas. Si no vuelve, es un cambio de posición real, no un glitch.

`frame_hasta` es el último fotograma con el signo invertido; `preparar_series`
excluye `[frame_desde, frame_hasta]`.

### Calibración y qué se observó en el corpus público

Anclada en `zverev_saque_lateral_02` frame 566 (único caso real disponible), donde
`CODO_DER` y `HOMBRO_DER` cumplen las cinco condiciones. Descarta el dithering de
`z` cerca del plano (frames 574–575 del mismo clip).

**Hallazgo importante, para el Capítulo 6/7:** sobre el corpus público, con las
cinco condiciones, el detector **igual dispara 16–45 veces por clip de saque** de
Zverev (y solo 3 en el drive). No son falsos positivos del detector: en toma
lateral, la coordenada `z` de las articulaciones rápidas del brazo y de la mano
(muñeca, dedos) que devuelve MediaPipe **es poco más que ruido que cruza el cero
todo el tiempo**. El detector está identificando correctamente que ese canal no es
confiable.

Consecuencia: al excluir todas esas franjas, la velocidad angular del segmento
`brazo` de los saques de Zverev queda no auditable → **las repeticiones de saque
del corpus público pasan a "no auditable"** en vez de reportar un orden con un
número de velocidad plausible por casualidad. Es el comportamiento correcto por la
regla R3 ("un dato faltante es mejor que un dato equivocado"), y es la misma
conclusión de la decisión 008: **la toma lateral no sirve para el brazo rápido; la
Fase B tiene que ir con encuadre de tres cuartos.** El `drive` (movimiento del
brazo más en el plano de la imagen) sigue recuperando `pelvis → torso → brazo`.

**La validación real del detector es la Fase B**, con `z` métrica de verdad (240
fps, luz controlada), donde una inversión genuina será rara y el detector la
marcará limpio. Los cinco umbrales se revisan ahí.

### Propagación a E3 y E4

`ResultadoValidacion.inversiones_z` viaja como los otros controles.
`engine/preparacion.preparar_series` excluye **toda la franja** `[frame_desde,
frame_hasta]` de cada articulación afectada, antes de filtrar. Si la franja supera
el hueco interpolable (5 fotogramas) queda como `TramoExcluido` → no se estima
(R3), y E4 la ve como tramo no auditable. En `zverev_saque_lateral_02` la franja
566–573 (8 fotogramas) queda excluida y la repetición del saque, no auditable —
que es el resultado correcto.

## Consecuencias

- Un modo de falla no obvio (documentado en el Capítulo 1 como límite de la cámara
  única) queda **detectado y marcado automáticamente** en vez de aparecer como un
  número basura o un orden de picos falso.
- Backends 2D puros (Vía A sin elevación): `z` es `None` → el detector no hace
  nada, sin coste.
- **Para el Capítulo 6:** la inversión de profundidad en el instante de máxima
  velocidad es un riesgo específico de la estimación 3D directa monocular; queda
  documentado con un caso medido y con la mitigación implementada.
- Pendiente: revisar los tres umbrales con el material de la Fase B (240 fps
  reales, `escala_temporal_conocida = True`).
