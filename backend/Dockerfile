# Contenedor del motor (KinetiQ).
#
# Imagen de producción desde la tarea 4.5.4 (CMD de abajo: servidor HTTP real). Sigue
# sirviendo para MEDIR (tarea 4.5.3): `docker run --entrypoint python <imagen> -m
# app.medir_contenedor /datos/clip.mov` sobre un clip montado, sin tocar el CMD por defecto.
#
# Base slim (no "alpine": mediapipe no publica ruedas para musl y compilarlo ahí es una fuente de
# problemas conocida). python:3.11 para que coincida con la versión fijada en desarrollo (ver
# requirements.txt: "el entorno se crea SIEMPRE con Python 3.11").
FROM python:3.11-slim

# Librerías de sistema que opencv-contrib-python necesita en tiempo de import, aunque el contenedor
# no tenga pantalla (cv2 se enlaza contra libGL/libSM/libXext/libXrender igual). Sin esto, el import
# de cv2 falla con "ImportError: libGL.so.1: cannot open shared object file".
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Capa de dependencias separada del código: reconstruir tras un cambio de código no reinstala
# mediapipe (~600 MB) de nuevo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Precalentamiento: MediaPipe descarga el modelo (.tflite) la PRIMERA vez que se instancia el
# backend, y `docker run --rm` no conserva esa descarga entre corridas (capa efímera). Sin este
# paso, cada medición de tiempo incluiría la descarga por red, mezclada con el tiempo de
# inferencia real. Se descargan los tres model_complexity (0/1/2) porque la tarea 4.5.3 los
# compara entre sí (velocidad/memoria vs cobertura).
RUN python -c "\
import numpy as np; \
from app.engine.pose.mediapipe_backend import MediaPipeBackend; \
img = np.zeros((128, 128, 3), dtype=np.uint8); \
[MediaPipeBackend(model_complexity=c).estimar_frame(img, 0) for c in (0, 1, 2)]; \
print('modelos de pose precalentados (complexity 0, 1, 2)')"

# Comando de producción (tarea 4.5.4): servidor HTTP real, no un script suelto. $PORT lo
# inyecta Render en tiempo de ejecución (Web Service, obligatorio en el plan gratuito —
# no existe "Background Worker" ahí, investigado al cerrar la tarea 4.5.1); si no está
# (p. ej. `docker run` local), cae a 8000. Forma shell (no exec) a propósito: así "$PORT"
# se expande; con la forma exec (CMD [...]) no lo haría.
#
# Para medir con medir_contenedor.py (tarea 4.5.3) en vez de levantar el servidor:
#   docker run --rm -v <clip>:/datos/clip.mov --entrypoint python <imagen> \
#       -m app.medir_contenedor /datos/clip.mov
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
