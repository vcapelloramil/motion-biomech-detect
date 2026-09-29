# Etapa 4.5 — esqueleto del contenedor del motor (KinetiQ).
#
# Por ahora sirve para MEDIR (tarea 4.5.3): corre app.medir_contenedor sobre un clip montado y
# reporta tiempo y memoria pico. El comando por defecto queda abierto (bash) para poder invocar
# distintas mediciones sin reconstruir la imagen; docker-compose / el comando de despliegue real
# se define en la tarea 4.5.4, cuando el contenedor también hable con Supabase.
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

# Sin ENTRYPOINT fijo todavía: se invoca explícitamente `python -m app.medir_contenedor ...` (o lo
# que corresponda) al correr el contenedor, hasta que la tarea 4.5.4 defina el comando de producción.
CMD ["bash"]
