# backend/ — motor biomecánico y (más adelante) API

Núcleo en Python del proyecto KinetiQ. Hoy contiene el contrato del reporte y la
configuración; los módulos del pipeline se agregan etapa por etapa (ver
`docs/plan-desarrollo.md`).

## Requisito: Python 3.11

El entorno virtual se crea **siempre** con Python 3.11. El `python` del sistema en esta
máquina es 3.14, y **mediapipe no soporta 3.14** (además exige `numpy<2`). Si el venv se
crea con `python` a secas, la instalación de dependencias falla.

```bash
# desde la raíz del repositorio
py -3.11 -m venv backend/.venv
```

Activar:

```bash
# Windows (PowerShell)
backend\.venv\Scripts\Activate.ps1
# Windows (CMD)
backend\.venv\Scripts\activate.bat
# Git Bash
source backend/.venv/Scripts/activate
```

Instalar dependencias:

```bash
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
```

### Dependencia externa: ffmpeg / ffprobe

El **catalogador** (`app/catalogador.py`) y las pruebas de integración usan `ffprobe`
para leer metadatos del contenedor y `ffmpeg` para generar clips de prueba. Tienen que
estar en el `PATH`. El núcleo del motor (`engine/`) funciona sin ellos, con menos poder
de contraste de metadatos. Ver `docs/decisiones/004-ingesta-fps-y-verificacion.md`.

```bash
ffprobe -version   # para confirmar que está disponible
```

## Configuración

El motor no tiene rutas de video hardcodeadas. La ubicación del corpus se toma de la
variable `KINETIQ_DATA_DIR` o del archivo `backend/.env` (ver
`docs/decisiones/002-config-ruta-corpus.md`).

```bash
cp backend/.env.example backend/.env   # y editar el valor
```

Opcional: `KINETIQ_CACHE_DIR` para los resultados intermedios del motor (coordenadas de
pose extraídas). Si no se define, se usa `backend/.cache/` (ignorada por git).

## Pruebas

```bash
# desde la raíz del repositorio, con el venv activado
pytest                 # todo
pytest -m "not slow"   # omite las que decodifican video real (corpus Fase A)
```

Las pruebas de integración se saltan solas si no hay `ffmpeg`. La prueba de aceptación
del corpus se salta si no hay `KINETIQ_DATA_DIR`.

## Herramientas de línea de comandos

Todas se corren desde `backend/` (para que `app` esté en el path).

```bash
# Catalogar y verificar el corpus (Etapa 1). Escribe catalogo-verificado.csv
# junto al corpus; NO modifica catalogo.csv.
# Sin --dir recorre fase-a/ y fase-b/ de KINETIQ_DATA_DIR; saltea compilaciones/ y
# originales/ (las unidades de análisis de fase-b van en <sesion>/<gesto>/recortes/).
python -m app.catalogador
python -m app.catalogador --sin-hash          # sin verificación de huella (rápido)
python -m app.catalogador --dir RUTA          # una sola carpeta

# Extraer y cachear las coordenadas de pose de los clips (Etapa 2).
python -m app.extraer_pose                     # todos los clips, MediaPipe
python -m app.extraer_pose --clip zverev_saque_lateral_01.mp4
python -m app.extraer_pose --backend fake --max-frames 30

# Medir la velocidad de inferencia de un backend (Etapa 2, tarea 2.6).
# Agrega la corrida a docs/resultados/e2-velocidad-inferencia.json
python -m app.bench_pose --clip zverev_saque_lateral_01.mp4 --frames 120

# Analizar un clip de punta a punta: pose (caché) -> E3 -> E4 (Etapa 4).
python -m app.analizar --clip zverev_saque_lateral_01.mp4
python -m app.analizar --clip reves_lateral_01.mp4 --lado izq
```

## Estructura

```
backend/
  requirements.txt        dependencias de ejecución (versiones fijadas)
  requirements-dev.txt     + pytest
  .env.example             plantilla de configuración local
  app/
    config.py              resolución de KINETIQ_DATA_DIR / KINETIQ_CACHE_DIR
    catalogador.py          CLI: cataloga y verifica el corpus (E1, tarea 1.5)
    extraer_pose.py         CLI: extrae y cachea coordenadas de pose (E2)
    bench_pose.py           CLI: mide la velocidad de inferencia (E2, tarea 2.6)
    schemas/
      reporte.py           contrato del reporte (Anexo A del plan)
    engine/                núcleo biomecánico, sin dependencias web
      version.py           versión del motor, se sella en cada reporte
      ingest.py             E1: FPS reales, cámara lenta, aptitud, iterador de fotogramas
      framehash.py          E1: unicidad de fotogramas por huella (decisión 001)
      validation.py         E2b: baja confianza + saltos imposibles (espacio imagen/mundo)
      dsp.py                E3: Butterworth de fase cero (filtfilt)
      preparacion.py        E3: exclusión de atípicos + interpolación de huecos cortos
      winter.py             E3: análisis residual -> corte objetivo
      pipeline.py           E3: orden validar -> preparar -> Winter -> filtrar
      segmentos_corporales.py  E4: la cadena pelvis -> torso -> brazo
      kinematics.py         E4: ángulos, separación cadera-hombro, velocidad angular
      sequencing.py         E4: picos, orden observado, segmentación, agregación
      pose/
        base.py             contrato PoseBackend + SecuenciaPose
        articulaciones.py   mapa articular canónico (MediaPipe 33 / COCO 17)
        mediapipe_backend.py  backend por defecto
        fake_backend.py     backend sintético para pruebas (incluye caso 2D-solo)
        cache.py            persistencia de coordenadas (.pose.npz + .pose.json)
    routers/  workers/     API (Etapa 6)
```
