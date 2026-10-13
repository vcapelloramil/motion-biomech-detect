# Decisión 037 — Un empate de cadera y tronco es un golpe medido ("sin diferencia medible"), y un pico que falta lleva su motivo

**Fecha:** 13 de octubre de 2026 (noche)
**Estado:** **APLICADA en local por pedido de Valentín** (motor 0.5.4, contrato 1.4); sin publicar todavía.
**Afecta a:** `backend/app/ensamblar_reporte.py` · `backend/app/schemas/reporte.py` (contrato 1.4, aditivo) · `backend/app/consistencia.py` · `procesar_video.py` (estado final) · frontend (Biblioteca,
reporte, sesión, Procesando) · corrige la nota del 29/9 de la decisión 015 y la salvedad sobre "no ordenable" · R3

---

## El problema (producción, sesión 1 del corpus, 13/10)

1. **Un golpe con la cadera en 0,296 s y el tronco en 0,300 s salía con la etiqueta "NO AUDITABLE".** Los dos picos se midieron, con confianza; lo que no hay es diferencia mayor que la tolerancia del
   orden (8,33 ms, decisión 032). La decisión 015 (corrección del 29/9) había dejado ese caso como "no auditable con un motivo". R3 reserva "no auditable" para datos que **no son confiables**, y este sí
   lo es: es un resultado, no una falla.
2. **La Biblioteca decía "1 de 6 medibles".** Contaba como medido solo al golpe cuyo orden se podía establecer, así que cinco golpes medidos y empatados figuraban como "no medibles". La consistencia
   entre golpes tenía la misma definición.
3. **El pico del brazo faltaba sin que se supiera por qué**, y la tarjeta del brazo desaparecía de "Tres momentos".

## Decisión

1. **"Golpe medido" = los picos de cadera y de tronco se midieron con confianza suficiente** (confianza ≥ 0,5, el umbral de la validación del motor), **aunque empaten**. Aparte se cuenta cuántos de los
   medidos tienen el **orden distinguible** (diferencia mayor que la tolerancia). Es la misma definición en el servidor (`ensamblar_reporte.par_medido`, `consistencia.py`, estado final del video) y en el
   frontend (`golpeMedido`, `ordenDistinguible`).
2. **El empate es "sin diferencia medible a esta resolución"**: una observación nueva, `sin_diferencia_medible` (contrato 1.4, aditivo), con una pastilla gris neutra con ícono y texto. No es un estado del
   semáforo ni un "no se pudo medir". **"No auditable" queda solo para datos no confiables** (R3). Los reportes ya guardados con "no auditable" por simultaneidad se leen como "sin diferencia medible" sin
   tocar lo guardado.
3. **El estado del video es "completado" cuando el golpe está medido**, no cuando su orden es distinguible: un empate no es un análisis a medias.
4. **Un pico que no se midió dice cuál y por qué** (`picos_no_medidos` por repetición, contrato 1.4): el motivo del motor se traduce a palabras simples (se vio el X % del golpe, no hubo un momento
   claro de máxima velocidad, el pico cayó donde no se veía con confianza, valor imposible, casi sin datos) y se muestra como una tarjeta **"Pico del brazo: no medido"** en "Tres momentos" y en la
   observación del brazo.

## Qué no cambia

- La repetición con empate sigue con `auditable: false` y su motivo (`simultaneidad…`) en la secuenciación: es "no ordenable", no un dato perdido; los picos **sí** están en `picos`. Ese campo significa
  "el orden se pudo establecer"; "medido" se lee de los picos.
- Ningún veredicto del orden (decisiones 035 y 036).

## Consecuencias

- La Biblioteca y la tarjeta "Golpes medidos" de la sesión dicen **"N de M medidos · K con orden distinguible"**; con empates sistemáticos (la resolución del archivo es la que es) un grupo puede tener 6
  de 6 medidos y 0 con orden distinguible, y se dice tal cual.
- Los reportes anteriores a 0.5.4 muestran "sin diferencia medible" donde antes decían "no auditable"; no hace falta recalcular.

## Pendiente

- El **brazo**: se midió. Con el motor actual lo pierden **52 de 76** repeticiones del corpus (68 %); con el anterior, 7 (9 %); en el saque en tres cuartos, 18 de 18 contra 2 de 18. La causa es la
  oclusión real del codo en el armado del golpe (confianza del estimador ≈ 0 en la primera mitad de la ventana), no una regla demasiado estricta: `docs/resultados/brazo-por-golpe.md`. Decide Valentín si
  se muestra el máximo de la parte visible como dato parcial (opción 2 de ese documento).
