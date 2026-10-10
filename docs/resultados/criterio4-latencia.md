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

Para comparar: en la máquina de desarrollo el mismo archivo tarda 130 s de cómputo (corrida local del 9/10, sin cola ni arranque en frío).

## Pendiente

- Registrar al menos una corrida por entorno (Free y, si se pasa a Standard, Standard) con las columnas nuevas.
- Medir con `fin − encolado` desde la base y no a mano.
