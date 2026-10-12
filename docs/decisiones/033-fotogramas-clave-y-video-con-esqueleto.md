# Decisión 033 — Fotogramas clave y video corto con esqueleto en el reporte: bucket aparte, falla suave y costo medido

**Fecha:** 12 de octubre de 2026
**Estado:** vigente (implementada; **falta aplicar la migración `20261012000000` y publicar** para que el reporte real los tenga)
**Afecta a:** `backend/app/engine/render.py` (nuevo) · `backend/app/procesar_video.py` · migración `20261012000000_bucket_artefactos.sql` · contrato 1.3 · `reporte.$videoId.tsx` ·
tabla 4.7 y apartado 4.5.3 de la tesis · decisión 023 (plan de Render)

---

## El problema

La tabla 4.7 de la tesis pone el **renderizado del esqueleto** y el reproductor sincronizado en el núcleo del MVP, y el apartado 4.5.3 promete que, al borrarse el original a los 7 días,
se **conserva el video con esqueleto en resolución reducida** como evidencia visual. El reporte del 12/10 no tenía nada de eso: `artefactos` vacío. Pedido de Valentín: (a) los tres
fotogramas clave con esqueleto (picos de cadera, tronco y brazo) en Storage y en el reporte; (b) un video corto, liviano y en baja resolución, que se conserve aunque el original se borre;
y una estimación de costo en tiempo y memoria en Render.

## Decisión

1. **Qué se genera** (`engine/render.py`, una sola pasada por el clip, después de secuenciar y mientras el clip sigue en disco):
   - **Tres JPEG** (≤ 720 px de alto, calidad 80, ~115 KB c/u) en el fotograma **real** más cercano al pico de cada segmento (nunca uno interpolado), con el esqueleto de ESE fotograma.
   - **Un MP4 H.264** (360 px de alto, CRF 30, ~130 KB para 1,6 s) con la ventana del golpe ± 0,5 s, **en cámara lenta fija** (30 cuadros/s sobre la grilla uniforme: ×8 a 240 Hz). El
     factor viaja en el reporte (`overlay_info.factor_lento`): la cámara lenta no se disfraza.
   - Ambos **acercados al jugador** (recuadro de su pose en la ventana + 30 %): en una toma abierta ocupa ~15 % del cuadro y a 360 px no se ve el gesto.
2. **Qué se dibuja (R3/R4):** solo puntos con confianza ≥ 0,5; un punto dudoso no se dibuja ni se completa. Cadera, hombros y brazo dominante con los colores de segmento de la
   especificación §2 (violeta, turquesa, blanco) para que el gráfico y la imagen hablen igual.
3. **Bucket aparte `artefactos`** (migración nueva): privado, 15 MB por objeto, solo `image/jpeg` y `video/mp4`; el usuario **lee y borra** su carpeta (`<usuario_id>/<video_id>/…`) y no
   escribe. Razones: el bucket `videos` solo admite mp4/mov y deja escribir al usuario; y la retención de 7 días (4.5.3) borra originales sin poder arrastrar la evidencia.
4. **Falla suave.** Los artefactos son un complemento: cualquier error al generarlos o subirlos queda en el log y el reporte sale igual con `artefactos` vacío ("no generado", no "cero").
   El video es, a su vez, opcional respecto de los fotogramas (sin `ffmpeg` o con un fallo del codificador, los tres momentos salen igual).
5. **Contrato 1.3:** `Artefactos.overlay_info` = `{desde_s, hasta_s, fps_reproduccion, factor_lento}` para que el reproductor (cuando exista) vuelva al eje del análisis. Las rutas se
   guardan también en `videos.ruta_fotograma_*` y `reportes_biomecanicos.ruta_overlay` (columnas que ya existían).
6. **El cliente firma la URL al leer** (1 h, `createSignedUrls`); el reporte guarda rutas, no URLs (decisión 025).

## Costo medido (PC de desarrollo, no Render) y estimado en Render

Recorte real de 3,1 s del iPhone (`IMG_6395`, HEVC 1080p, 626 fotogramas fuente, grilla de 749 puntos), `MediaPipe model_complexity=2`:

| Etapa | PC de desarrollo | Render Free (×5,2, factor medido el 12/10 para el mismo tipo de archivo) | Standard (1 CPU) |
| --- | --- | --- | --- |
| Pose (la que ya existía) | 134 s | ~11 min (medido: 676 s) | ~2,6 min (91 s por 360 fotogramas en Docker de 1 vCPU, decisión 023) |
| Regularizar + E3 + secuenciar | 1,9 s | ~10 s | ~2,3 s |
| **Fotogramas clave + video** | **9,1 s** (+6,8 %) | **~47 s** | **~11 s** |
| Pico de memoria del proceso | 460 MB (lo fija MediaPipe; los artefactos no lo suben: 157 → 159 MB) | **480 MB medidos sobre 512 MB** | sobra (2 GB) |
| `ffmpeg` (proceso aparte, 1 hilo) | 56 MB | **+56 MB al lado de un proceso que ya está en ~480** | sobra |

- **Tiempo:** +7 % en cualquier plan. En Free pasaría de 11 min 18 s a ~12 min; no es lo que decide el plan.
- **Memoria:** sí lo es. En Free el margen medido es de **32 MB** (decisión 023). En Windows el proceso devuelve la memoria de MediaPipe antes de los artefactos (460 → 109 MB); **en
  el contenedor Linux no está medido que la devuelva**, y `ffmpeg` suma 56 MB. Si no la devuelve, Free queda en ~536 MB sobre 512: un corte por memoria. No lo pude medir acá (Docker no
  estaba en marcha); **se mide solo con el primer golpe real en Render**: `procesar_video` imprime "artefactos en X s" y el RSS pico en el log.
- **Almacenamiento:** ~470 KB por golpe (3 JPEG + 1 MP4). Una sesión de 10 golpes: ~5 MB. Despreciable frente a los 1 GB del plan gratuito de Supabase.

## Recomendación

**Pasar a Standard antes de publicar esto** (USD 25/mes, decisión 023 ya aprobada: "Standard por criterio y siempre para la defensa"). Tres razones independientes de los artefactos
—11 min por un golpe de 3 s, 32 MB de margen y el riesgo de suspensión a mitad de una sesión— y una cuarta que aparece con ellos: el único margen que quedaba en Free es el que el
`ffmpeg` se come. Si se prefiere medir primero en Free, el fallo es **suave**: si el contenedor se queda sin memoria el proceso se corta (el video queda `procesando` y la recuperación
al arranque, 6.5, todavía no existe), así que la medida de prudencia es hacer la primera prueba con **un** golpe y mirar el log.

## Qué no hace (y por qué)

- **No hay reproductor sincronizado** (video + curvas en un eje): el `<video>` es el nativo, con la nota de la cámara lenta. El reproductor es la tarea 8.7, diferida.
- **No dibuja ángulos** sobre el esqueleto (la tabla 4.7 los nombra): no hay todavía una magnitud angular en el reporte que mostrar (ver `docs/reporte-mas-valor.md`).
- **No borra el original a los 7 días** (política 7.6, diferida): el bucket aparte la deja lista.
