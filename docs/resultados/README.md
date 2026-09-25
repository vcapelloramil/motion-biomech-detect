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
| `e4-fase-b-exploratorio-ancla-torso.json`, `...-ancla-pelvis.json` | `python -m app.explorar_fase_b -s ancla-torso -s ancla-pelvis` | Lo mismo con ventana anclada al pico global de torso (o de pelvis) ± 300 ms: una repetición por clip. Registra si el pico global del brazo cae fuera de la ventana y cuánto difieren entre sí ambas anclas. Los cuatro modos se calculan en una sola pasada (`-s` es repetible). |
| `e4-fase-b-exploratorio-<modo>-e3-0.4.1.json` | `python -m app.explorar_fase_b -s clip -s auto -s ancla-torso -s ancla-pelvis --etiqueta e3-0.4.1` | La misma exploración con E3 corregido (motor 0.4.1). Los archivos **sin sufijo** son de 0.4.0 (E3 con series sin filtrar) y valen solo como referencia del defecto (decisión 010). |
| `e3-retro-comparar-brazo-corpus-publico.json` | `python -m app.diagnosticos_e3 comparar-brazo --salida ...` | Revisión retroactiva del corpus público: velocidad del brazo con hombro→codo vs hombro→muñeca en tres estados del pipeline (A: E3 viejo sin detector de z = decisión 008; B: 0.4.0; C: 0.4.1). |
| `e3-corte-brazo-fase-b.json` | `python -m app.diagnosticos_e3 corte-brazo --salida ...` | ¿Un corte de Winter por clip sirve para el brazo? Corte por serie (valores concatenados vs tramo continuo más largo) y barrido del corte solo del codo (6–20 Hz) sobre velocidad, caída k1→k8, orden y adelanto del brazo (ancla de torso). Exploratorio. |
| `e3-fleisig-brazo-saque.json` | `python -m app.diagnosticos_e3 fleisig-brazo --salida ...` | Saque: pico de ω del vector hombro→codo y de ω del ángulo del codo (extensión) en la ventana anclada al torso, con los cocientes contra cada valor de Fleisig. Sustenta la decisión 011. |
| `e3-ventana-brazo-fase-b.json` | `python -m app.diagnosticos_e3 ventana-brazo --salida ...` | Barrido del adelanto (300…0 ms) con que se busca el pico del brazo antes del pico del torso: orden, desfase y cuántos picos se desplazan al acotar. Con adelanto 0, "brazo antes" es imposible por construcción. Exploratorio. |
| `pose-oclusion-lado-dominante.json` | `python -m app.diagnosticos_e3 oclusion-lado --salida ...` | Confianza y cobertura de hombro/codo/muñeca/cadera del lado dominante contra el no dominante, por sesión y encuadre, en tres tramos (reposo, ventana del gesto, clip). Sesión 2 solo con una muestra de 13 clips. Sustenta la decisión sobre una tercera sesión. |
| `e3-series-sin-filtrar.json` | `python -m app.diagnosticos_e3 sin-filtrar --salida ...` | Por clip y articulación: cuántas series tenían algún NaN (= sin filtrar en E3 < 0.4.1), con y sin el detector de inversión de z. |

Los resultados dependen del hardware: no se comparan entre máquinas, solo consigo
mismos a lo largo del tiempo.
