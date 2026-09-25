# docs/resultados/

Números medidos por el sistema, en formato reproducible. Cada archivo lo genera un
script versionado del backend; volver a correrlo debe dar (aprox.) el mismo valor
en la misma máquina.

Principio 5 del plan de desarrollo: *"Nada se mide sin poder reproducirse."*

| Archivo | Lo genera | Qué mide |
| --- | --- | --- |
| `e2-velocidad-inferencia.json` | `python -m app.bench_pose` (desde `backend/`) | fotogramas por segundo de la estimación de pose sobre el hardware disponible (tarea 2.6 / indicador §2.4 de la tesis). Lista de corridas; cada una anota máquina, backend, config, clip y resolución. |
| `e4-fase-b-exploratorio-clip.json` | `python -m app.explorar_fase_b` (desde `backend/`) | Exploración cualitativa de la Fase B por gesto y encuadre: pico de ω de pelvis/torso/brazo según el paso de muestreo, inversiones de z, orden y desfase pelvis→torso. Cada clip pre-cortado = 1 repetición. **Exploratorio: no calibra ni mide criterios.** |
| `e4-fase-b-exploratorio-auto.json` | `python -m app.explorar_fase_b --segmentacion auto` | Lo mismo con segmentación automática (valles de quietud), para comparar. |

Los resultados dependen del hardware: no se comparan entre máquinas, solo consigo
mismos a lo largo del tiempo.
