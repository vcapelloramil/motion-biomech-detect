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
pytest
```

## Estructura

```
backend/
  requirements.txt        dependencias de ejecución (versiones fijadas)
  requirements-dev.txt     + pytest
  .env.example             plantilla de configuración local
  app/
    config.py              resolución de KINETIQ_DATA_DIR
    schemas/
      reporte.py           contrato del reporte (Anexo A del plan) — CONGELADO
    engine/                núcleo biomecánico, sin dependencias web
      version.py           versión del motor, se sella en cada reporte
      pose/                backends de estimación de pose (Etapa 2)
    routers/  workers/     API (Etapa 6)
```
