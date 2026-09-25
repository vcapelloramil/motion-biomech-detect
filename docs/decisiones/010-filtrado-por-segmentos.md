# Decisión 010 — E3 filtra por segmentos continuos (antes dejaba crudas las series con huecos)

**Fecha:** 25 de septiembre de 2026
**Estado:** vigente (motor `0.4.1`)
**Afecta a:** Etapa 3 (`engine/pipeline.py`, `engine/dsp.py`) · Etapa 4 (todas las velocidades del brazo) · decisión 008 · Capítulo 6/7

---

## El problema

`procesar_e3` (decisión 007) filtraba solo las series **sin ningún NaN**. Una serie con algún
tramo largo excluido (más de 5 fotogramas: baja confianza, salto imposible o inversión de `z`) se
devolvía **entera sin filtrar**; el propio código lo marcaba como "simplificación". Con el
detector de inversión de `z` (decisión 009) las exclusiones son frecuentes en las articulaciones
rápidas: sobre las 36 repeticiones de la Fase B, **hombro/codo derecho quedaron sin filtrar en
6/6 clips de cinco de los seis grupos**; pelvis y torso, en 0 %.

Consecuencia: el codo (crudo, con jitter de 2–9 cm por fotograma y confianza alta) entraba a E4
contra un hombro ya filtrado. La velocidad del brazo (`hombro→codo`) salía inflada por ruido
(3800–6600 °/s en cinco de los seis grupos, con una caída de 63–81 % al calcularla entre
fotogramas más separados, la firma del ruido) y ninguna regla de validación lo advertía: la confianza es alta y el umbral de
salto imposible (0,5 torsos ≈ 26 cm/fotograma ≈ 62 m/s) es demasiado laxo para atrapar jitter.

## Alternativas consideradas

1. **Interpolar todos los huecos y filtrar la serie completa.** Inventa movimiento en tramos que
   no se midieron y el filtro lo desparrama hacia los datos buenos (la prueba
   `test_rellenar_el_hueco_con_ceros_SI_arrastra_artefactos` lo demuestra con la variante de
   ceros: error 10× mayor en el borde). Viola R3 (no rellenar huecos con estimaciones silenciosas).
2. **Dejar la serie cruda (statu quo).** Mezcla datos ruidosos con datos filtrados sin avisar.
3. **Filtrar cada segmento continuo por separado (elegida).** Los NaN se conservan exactamente;
   cada tramo válido se filtra con `filtfilt` (fase cero); un tramo más corto que el mínimo de
   `filtfilt` (16 muestras con orden 4) **no se deja crudo**: pasa a NaN y se registra como
   `TramoExcluido`.

## Decisión

`butterworth_fase_cero_por_segmentos` (`engine/dsp.py`) y `procesar_e3` la usa para toda serie. Se
sube el motor a `0.4.1`.

## Lo que se verificó

- **Fase cero y bordes** (`tests/unit/test_dsp_segmentos.py`, sintéticas): el hueco no se rellena;
  con señal limpia el error en el borde del hueco es < 1 % de la amplitud; un pico a 8–40 muestras
  del borde conserva su instante (± 1 muestra). **Limitación conocida:** en el extremo de un
  segmento el filtro atenúa menos el ruido (error ~3,6× el del interior), aunque nunca peor que
  el dato crudo. Un segmento aislado de 16 muestras (67 ms) todavía reduce el error (0,0135 vs
  0,0198 de ruido crudo).
- **Regresión:** sobre las 36 repeticiones de la Fase B, pelvis y torso dan **exactamente** los
  mismos valores en 0.4.0 y 0.4.1 (diferencia máxima 0,0000 °/s).
- **Efecto en el brazo:** el p99 de ω a k=1 (mediana por grupo) pasa de 3771–6600 °/s a
  790–2165 °/s en los cinco grupos afectados (el revés de tres cuartos, ya filtrado, queda igual:
  940 → 908) y la caída entre k=1 y k=8 pasa de 63–81 % a 1–10 %, como pelvis y torso. La fracción de
  fotogramas con tramo excluido casi no cambia (0–4 puntos).

## Consecuencias

- **Todo lo medido del brazo antes de 0.4.1 queda invalidado** (magnitudes y órdenes). Los JSON
  de `docs/resultados/e4-fase-b-exploratorio-*.json` sin sufijo son de 0.4.0; los de 0.4.1 llevan
  el sufijo `-e3-0.4.1`.
- **Decisión 008 (techo ×3):** el techo ×3 (7104 °/s) queda a 3–10 veces del brazo filtrado
  típico; su justificación de "ruido de MediaPipe" ya no aplica. **No se recalibra todavía.**
- **PENDIENTE DE REDACCIÓN — Capítulo 4: la justificación empírica de `brazo = hombro→codo`
  (decisión 008, punto 2) ya no se sostiene con las series filtradas correctamente.**
  - *Lo que se afirmó:* "la muñeca da 15 000–42 000 °/s en 3 de 4 clips; con el codo los valores son
    plausibles (1 700–2 300 °/s)".
  - *Por qué no vale:* en esa comparación la serie del codo estaba **filtrada** y la de la muñeca
    **cruda** en dos de los cuatro clips (`zverev_saque_lateral_01`: 2126 vs 10 076 °/s;
    `drive_lateral_01`: 1567 vs 10 322); en `zverev_saque_lateral_02` ambas crudas (16 283 vs
    26 063); y en `zverev_saque_lateral_03` ambas filtradas daban lo mismo (1821 vs 1756). La
    diferencia entre codo y muñeca estaba confundida con qué serie se filtró.
  - *Con E3 0.4.1* (ambas filtradas, n = 13 clips): muñeca/codo = 0,95–2,0 (mediana 1,39), no
    10–40; valores de la muñeca plausibles (1500–3100 °/s en el corpus público); cobertura de
    datos válidos equivalente (codo 0,83, muñeca 0,84). Fuente:
    `docs/resultados/e3-retro-comparar-brazo-corpus-publico.json`.
  - *Lo que se mantiene:* la decisión de usar el codo **por el argumento anatómico** (el codo es
    el eslabón del segmento "brazo" de la cadena; antebrazo y mano son eslabones posteriores). No
    se reabre en código. Cambia solo la justificación.
  - *Qué hacer al redactar:* no escribir que la muñeca se descartó por valores disparatados.
    Decir que se eligió el codo por criterio anatómico y que la comparación empírica inicial
    estaba contaminada por un defecto de filtrado, corregido en 0.4.1. Es un ajuste de
    redacción pendiente, como el de la velocidad de inferencia (decisión 006).
- **Pendientes (no aplicados):** umbral de salto imposible en unidades físicas; corte de Winter
  por clip (8–9 Hz) para el brazo; ambas cosas se calibran separando datos de ajuste y de medición.
