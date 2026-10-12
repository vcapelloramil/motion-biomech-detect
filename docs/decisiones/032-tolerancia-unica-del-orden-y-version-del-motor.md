# Decisión 032 — Una sola tolerancia para "ordenable" (1/120 s = 8,33 ms), compartida por el producto y el recálculo; motor 0.5.0; contrato 1.3

**Fecha:** 12 de octubre de 2026
**Estado:** vigente (pedido de Valentín tras la prueba del 12/10; implementada en el motor, pendiente de publicar)
**Afecta a:** `backend/app/engine/tolerancia_orden.py` (nuevo) · `backend/app/ensamblar_reporte.py` · decisiones 014, 015 y 031 · `docs/plan-recalculo-corpus-tasa-real.md` §3 · contrato del reporte (1.2 → **1.3**, aditiva) · versión del motor (0.4.1 → **0.5.0**) · Capítulo 7

---

## El problema

El reporte del revés de tres cuartos del 12/10 (`IMG_6395.mov`) afirmó "tronco antes que cadera" con **8,3 ms** de diferencia (dos fotogramas de la grilla de 240 Hz). El producto
usaba "τ = 1 fotograma **de la grilla**" (4,17 ms: ordenable si Δ > 4,17 ms), mientras que el pre-registro aprobado del recálculo (plan §3, aprobado el 9/10) fija la tolerancia
**en milisegundos: primaria 8,3 ms**, "que equivale a la tolerancia '1 fotograma' de la medición a 120 Hz". Eran dos reglas distintas para la misma pregunta, y la del producto era
**más permisiva** que la que se usó para medir el Criterio 1.

La causa de fondo es la de la decisión 030: la medición original (decisión 014) llamaba "1 fotograma" a 4,17 ms (240 fps nominales), pero el corpus era de **120 fps efectivos**,
así que ese fotograma medía en realidad 8,33 ms. La tolerancia física con la que se midieron los Criterios 1 y 3 es **8,33 ms**, no 4,17.

## Decisión

1. **Dos picos son ordenables si y solo si su diferencia es MAYOR que 1/120 s = 8,333 ms.** Con Δ ≤ 8,333 ms el orden "no se puede establecer a esta resolución": la repetición queda
   `no_auditable` con el motivo "simultaneidad al límite de resolución" (decisión 015, corrección del 29/9), conserva los picos medidos y no tiene veredicto. La desigualdad es
   **estricta**: dos fotogramas de la grilla de 240 Hz (8,333 ms) **no** son ordenables.
2. **Una sola constante:** `engine/tolerancia_orden.py` (`TOLERANCIA_ORDEN_S`, `es_ordenable`). La usa el ensamblador del reporte y **debe** importarla el arnés del recálculo (Paso A/B)
   para clasificar "ordenable"; no se redefine. Ahí mismo quedan las sensibilidades declaradas de antemano (4,2; 12,5; 16,7 ms = 0,5; 1,5 y 2 fotogramas a 120 Hz).
3. **Está en tiempo, no en fotogramas.** "1 fotograma" vale 8,3 ms a 120 fps, 5 ms a ~200 fps reales y 4,2 ms en la grilla de 240 Hz; cada archivo tiene el suyo. La resolución que se
   muestra al jugador es la **real del archivo** ("1 fotograma ≈ 5 ms a 200 fps reales"), no la de la grilla.
4. **El reporte registra la regla** (R4): `trazabilidad.tolerancia_orden_ms` (contrato **1.3**, aditivo; `null` en un reporte anterior, que usaba la regla de 4,17 ms).
5. **Versión del motor 0.5.0** (RNF-02): el motor cambió con el sello 0.4.1 puesto en cuatro commits (9/10 al 12/10); a partir de esta decisión los reportes nuevos se distinguen de
   los viejos por la versión. Tabla de commits por versión en la bitácora (12/10, "Versiones del motor").

## Consecuencias

- **Un veredicto o un orden menos.** Lo que antes salía "ordenable" con 8,3 ms (dos fotogramas de la grilla) ahora sale "no ordenable". Es **más conservador**, que es la dirección
  correcta ante R3 ("un dato equivocado presentado como bueno es peor que un dato faltante").
- **Cambia una cifra citada.** La nota 11 de `correcciones-pendientes-capitulo-4.md` (12/10) decía "8,3 ms = 2 fotogramas, por encima de la tolerancia: sí es establecible". Con esta
  regla el mismo golpe **no es ordenable**: se corrige allí. El dato "tronco 0,300 s y cadera 0,308 s" sigue siendo válido como medición; lo que cambia es qué se concluye de él.
- **No cambia ninguna medición congelada.** `medicion_criterio1.py` y sus resultados (decisión 014, τ en fotogramas del corpus a 120 Hz efectivos) no se tocan: la tolerancia física
  que usaron ya era ésta. Lo que sí hay que hacer en el Paso A es **leer la tolerancia desde `tolerancia_orden.py`** en el arnés nuevo, para que producto y recálculo no puedan
  separarse otra vez.
- **Puede dejar sin veredicto grupos que hoy lo tienen.** `RESPALDO_POR_GRUPO` se revisa en el Paso A (decisión 031) con la tolerancia ya unificada.
- Reportes anteriores no se recalculan: llevan su versión (`0.4.1`, contrato ≤ 1.2) y no traen `tolerancia_orden_ms`.

## Qué cambió en el código

- `engine/tolerancia_orden.py` (nuevo) · `ensamblar_reporte._evaluar_par` usa `es_ordenable` · la observación de simultaneidad informa diferencia, tolerancia y resolución real.
- Contrato **1.3**: `Trazabilidad.tolerancia_orden_ms` y `Artefactos.overlay_info` (ver decisión 033); `Reporte.version_contrato` admite `"1.3"`.
- `engine/version.py`: `0.5.0`, con la lista de lo que cambia.
- Pruebas: Δ = 4,2 / 8,33 / 8,33 (ambos sentidos) → no ordenable; 12,5 ms → ordenable; el contrato 1.2 sigue validando sin los campos nuevos.
