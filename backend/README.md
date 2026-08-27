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

## Pruebas

```bash
# desde la raíz del repositorio, con el venv activado
pytest                 # todo
pytest -m "not slow"   # omite las que decodifican video real (corpus Fase A)
```

Las pruebas de integración se saltan solas si no hay `ffmpeg`. La prueba de aceptación
del corpus se salta si no hay `KINETIQ_DATA_DIR`.

## Catalogador del corpus

```bash
cd backend
python -m app.catalogador              # usa KINETIQ_DATA_DIR, con verificación de huella
python -m app.catalogador --sin-hash   # primera pasada rápida, sin verificación de huella
```

Escribe `catalogo-verificado.csv` junto al corpus. No modifica `catalogo.csv`.

## Estructura

```
backend/
  requirements.txt        dependencias de ejecución (versiones fijadas)
  requirements-dev.txt     + pytest
  .env.example             plantilla de configuración local
  app/
    config.py              resolución de KINETIQ_DATA_DIR
    catalogador.py          CLI: cataloga y verifica el corpus (Etapa 1, tarea 1.5)
    schemas/
      reporte.py           contrato del reporte (Anexo A del plan)
    engine/                núcleo biomecánico, sin dependencias web
      version.py           versión del motor, se sella en cada reporte
      ingest.py             E1: FPS reales, cámara lenta, aptitud, iterador de fotogramas
      framehash.py          E1: unicidad de fotogramas por huella (decisión 001)
      pose/                backends de estimación de pose (Etapa 2)
    routers/  workers/     API (Etapa 6)
```
