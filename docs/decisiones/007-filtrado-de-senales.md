# Decisión 007 — Qué filtra el filtro, y el orden del pipeline de señales

**Fecha:** 27 de agosto de 2026
**Estado:** vigente
**Afecta a:** Etapa 3 · Etapa 4 · contrato del reporte (`trazabilidad.filtro`)

Lleva a código los apartados §3.4.2.1–§3.4.2.6 de la tesis.

---

## 1. El filtro opera sobre coordenadas métricas 3D (`pose_world_landmarks`)

No sobre las coordenadas normalizadas de imagen + z relativo que produce E2 para
el overlay.

- Las coordenadas de imagen **mezclan el movimiento del cuerpo con el zoom y el
  paneo de cámara**. Varios clips del corpus tienen paneo. Las `pose_world_landmarks`
  están centradas en las caderas: filtrar aísla el movimiento del jugador.
- El `z` de las coordenadas de imagen no es métrico; el de las world landmarks sí
  (metros), y es lo que la cinemática de E4 va a consumir.
- El análisis de Winter (elección del corte) es más interpretable sobre una señal
  en metros que sobre píxeles cuya escala cambia con la distancia al jugador.

Costo: E3 empezó extendiendo la captura de pose (`PoseFrame.puntos_mundo`, esquema
de caché v2) y **re-extrajo el corpus**. Los backends 2D puros (Vía A sin
elevación) no tienen world landmarks; para ellos el pipeline cae a `puntos`
(imagen). El overlay de E5 usa siempre `puntos` **sin filtrar**.

## 2. Fase cero, obligatorio (`filtfilt`, nunca `lfilter`)

`engine/dsp.butterworth_fase_cero` aplica un Butterworth de 4º orden hacia adelante
y hacia atrás. Un filtro unidireccional corre la señal en el tiempo de forma
distinta según el contenido frecuencial de cada segmento, y eso cambia el orden
aparente de los picos —justo lo que el sistema mide (§3.4.2.3)—. La prueba de
aceptación (`test_dsp.py`) verifica que `filtfilt` conserva el instante de un pico
conocido **y que la misma verificación sobre `lfilter` falla**.

`_filtro_unidireccional` existe solo para esa prueba. No se usa en el pipeline.

## 3. Guarda de Nyquist explícita

`corte_hz >= fps/2` → `ParametroDSPInvalido`. Ningún filtro puede separar
frecuencias por encima de la mitad de la tasa de muestreo (§3.4.2.2).

**Nota:** para clips con `escala_temporal_conocida = False` (material descargado en
cámara lenta), `fps_efectivos` es una estimación, así que el corte en Hz y las
velocidades absolutas son aproximados. El filtro igual saca el ruido relativo, y
el **orden** de los picos es inmune a un error de escala temporal global
(§3.3.4.2). Coherente con lo que ya marca la Etapa 1.

## 4. Remoción de atípicos antes de filtrar (§3.4.2.5)

El filtro no elimina un dato disparatado: lo desparrama sobre los vecinos.
`engine/preparacion.preparar_series` excluye, **antes** de filtrar: fotogramas sin
detección, puntos por debajo del umbral de confianza, y puntos marcados como salto
imposible (los tres vienen de `engine/validation` de la Etapa 2, ahora con
parámetro `espacio="mundo"`). Huecos de hasta **5 fotogramas** se interpolan
linealmente; los más largos quedan como `NaN` y se registran como `TramoExcluido`
(no se estiman — regla R3).

## 5. Un corte de Winter por clip

`engine/winter.elegir_corte` calcula el análisis residual por serie (de las
articulaciones rápidas) pero devuelve **un solo corte para toda la secuencia**: el
máximo de los cortes por serie, para conservar la banda de la articulación más
rápida.

Es una **simplificación deliberada**, no una limitación técnica: el contrato del
reporte, congelado en la Etapa 0, tiene un único `trazabilidad.filtro.corte_hz`. El
análisis por serie ya está implementado; si la Etapa 4 muestra que un corte único
distorsiona alguna articulación, se pasa a corte por articulación (y habría que
ampliar el contrato).

## 6. Orden del pipeline (§3.4.2.6), documentado en `engine/pipeline.py`

```
detección de pose (E2)
  → validación (baja confianza + saltos imposibles)
  → preparación (excluir no confiables, interpolar huecos cortos)
  → elección del corte (Winter)
  → filtrado Butterworth de fase cero
  → [E4: segmentación de repeticiones y cálculo de velocidades]
```

Se filtra la **secuencia completa** antes de cualquier recorte: `filtfilt` necesita
margen de borde y las ventanas de repetición de E4 son demasiado cortas.

## Consecuencias

- El corte elegido se persiste en `trazabilidad.filtro.corte_hz`; el resto del
  bloque (`tipo`, `orden`, `fase_cero`) sale de `SecuenciaFiltrada.trazabilidad_filtro()`.
  **Sin cambio de contrato.**
- Los `TramoExcluido` alimentan `cobertura.tramos_no_auditables` del reporte en E5.
- Como no se usa un modelo de elevación (MediaPipe da 3D directo), el paso
  "(elevación 3D)" del orden canónico de la tesis no existe en esta implementación;
  el filtro va directo sobre la salida de MediaPipe.
