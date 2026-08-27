# docs/resultados/

Números medidos por el sistema, en formato reproducible. Cada archivo lo genera un
script versionado del backend; volver a correrlo debe dar (aprox.) el mismo valor
en la misma máquina.

Principio 5 del plan de desarrollo: *"Nada se mide sin poder reproducirse."*

| Archivo | Lo genera | Qué mide |
| --- | --- | --- |
| `e2-velocidad-inferencia.json` | `python -m app.bench_pose` (desde `backend/`) | fotogramas por segundo de la estimación de pose sobre el hardware disponible (tarea 2.6 / indicador §2.4 de la tesis). Lista de corridas; cada una anota máquina, backend, config, clip y resolución. |

Los resultados dependen del hardware: no se comparan entre máquinas, solo consigo
mismos a lo largo del tiempo.
