# Criterio 4 — latencia de procesamiento de punta a punta

Registro de los datos de latencia. El umbral de tolerancia lo definían los usuarios (plan §4, semana 4, ítem e): se
reporta el **valor medido, sin umbral**. Nada se simula.

## Cómo se registra

Desde la migración `20261010000000_tiempos_de_procesamiento.sql`, cada video guarda tres instantes (UTC), escritos solo por el servidor:

| Columna | Qué marca | Quién lo escribe |
| --- | --- | --- |
| `encolado_en` | La API aceptó la orden de analizar (`POST /analisis/{id}/procesar`) | la API |
| `inicio_procesamiento_en` | El contenedor empezó a procesarlo | `procesar_video` |
| `fin_procesamiento_en` | Terminó, con éxito o con fallo | `procesar_video` |

**Latencia de punta a punta = fin − encolado** (incluye la espera en cola y el arranque en frío de Render); **cómputo = fin − inicio**.
La pantalla Procesando ya muestra "Tardó X" cuando hay datos.

## Datos

| # | Fecha | Video | Entorno | Duración del video | Fotogramas | Latencia de punta a punta | Cómo se obtuvo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 9/10/2026 | `IMG_6376.mov` (saque, perfil, iPhone, Formato: Actual, 20,6 MB) | Render **Free**, MediaPipe `model_complexity=2` | 2,5 s | 501 visibles (499 decodificados) | **~9 min** | **Manual**: lo midió Valentín (envío → `completado`). Las columnas de tiempo no existían todavía; la base solo confirma que el reporte se creó 16 min después del alta del video, que incluye el intento fallido por CORS. |
| 2 | 12/10/2026 | `IMG_6395.mov` (revés, tres cuartos, iPhone, Formato: Actual; recorte de 3,0 s) | Render **Free**, MediaPipe `model_complexity=2` | 3,0 s | 599 | **677,8 s (11 min 18 s)**; cómputo 676,6 s | **Medido por la base** (`encolado_en` → `fin_procesamiento_en`). Regularizado (16,7 % interpolados), escala conocida, `completado`. |
| 3 | 12/10/2026 (noche) | Recorte real de 3,1 s del original `IMG_6395.MOV` (`recorte3.mov`, HEVC 1080p, 626 fotogramas fuente, 27 MB; subido por el usuario de prueba) | Render **Standard** (1 CPU, 2 GB), motor 0.5.0, MediaPipe `model_complexity=2`, **con fotogramas clave y video** | 3,1 s | 626 | **117,4 s (1 min 57 s)**; cómputo 116,0 s | **Medido por la base** (`encolado_en` → `fin_procesamiento_en`) con la API de producción y un usuario de prueba (luego borrado). `completado`, escala conocida, reporte 1.3 con tres fotogramas y video. **5,8 veces más rápido que Free** para un archivo comparable (fila 2). |
| 4 | 12/10/2026 (noche) | **Primera prueba real de punta a punta con el celular**: saque de perfil, original a 200,8 fps, recortado, sin cámara lenta, "Formato: Actual" (805 fotogramas) | Render **Standard**, motor 0.5.0, con fotogramas clave y video (360 px, CRF 30) | ~4,0 s | 805 | **148 s (2 min 28 s)** medido por Valentín; **146,7 s** de procesamiento en el log | **Log de Render** (`procesar_video`): total **146,71 s**, **RSS pico 748,4 MB**, artefactos **10,2 s** (3 fotogramas clave, video de 160 KB). `completado`, escala conocida, 16,3 % interpolados. |

Para comparar: en la máquina de desarrollo el mismo archivo tarda 130 s de cómputo (corrida local del 9/10, sin cola ni arranque en frío).

## Costo estimado de los artefactos (decisión 033, 12/10/2026)

Medido en la PC de desarrollo sobre un recorte real de 3,1 s (626 fotogramas fuente): pose 134 s; **fotogramas clave + video con esqueleto 9,1 s (+6,8 %)**; el pico de memoria del proceso no cambia (460 MB,
lo fija MediaPipe) y `ffmpeg` suma 56 MB como proceso aparte. Escalado con el factor medido en Render Free (×5,2): **+47 s** (11 min 18 s → ~12 min); en Standard, ~+11 s. **Falta medirlo en Render**: el log de
`procesar_video` imprime "artefactos en X s" y el RSS pico.

### Memoria: el primer dato en Linux

**RSS pico 748,4 MB en Render Standard** (el mismo proceso medía ~460 MB en la PC de desarrollo con Windows y 480 MB en Free para un golpe más corto). Dos lecturas, las dos importantes:

- **En Free (512 MB) este golpe se habría cortado por memoria.** Es el dato que faltaba para la decisión 023: Standard no es un lujo de velocidad, es la condición para que un golpe de 3–4 s entre.
- **El margen en Standard (2 GB) es amplio (~1,3 GB)**, así que subir el video con esqueleto a 720 px (decisión 033, actualizada el 12/10: ~76 MB más de `ffmpeg` y ~7 s más) entra sin riesgo.
- El tiempo de procesamiento de este golpe (146,7 s por 805 fotogramas, 0,18 s por fotograma) es coherente con la fila 3 (117 s por 626, 0,19 s por fotograma): **la latencia escala con los fotogramas**, ~3 min para un golpe de 5 s.

## Pendiente

- ~~Registrar al menos una corrida por entorno (Free y Standard) con las columnas nuevas.~~ Hecho el 12/10 (filas 2 y 3). Falta el RSS pico en Linux con los artefactos (solo está en el log de Render).
- ~~Medir con `fin − encolado` desde la base y no a mano.~~ Hecho el 12/10 (fila 2).
- **Rechazos por archivo convertido (el recorte con cámara lenta de `IMG_6395.mov`: 12,0 s que llegaron a 50 fps):** 15 y 18 s de punta a punta; es el tiempo de rechazar, no de analizar.
- ~~Un golpe de 3 s tarda ~11 min en el plan Free: evaluar el plan Standard y volver a medir.~~ Standard: ~2 min (fila 3). Una sesión de 6 golpes: ~12 min.
