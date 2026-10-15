# Respaldo y restauración (paso 7 del plan §8)

**Por qué existe:** Supabase **Free no incluye respaldos**. Hasta el 15/10/2026 no había ninguna copia de la base ni de los videos, y la aplicación ya permite eliminar cuentas (`DELETE /cuenta`).
**Qué quedó hecho:** una herramienta de respaldo (`backend/app/respaldo.py`), una prueba de restauración en un Postgres local descartable (`tools/respaldo/restaurar_prueba.py`) y un primer respaldo verificado y restaurado.

## 1. Qué cubre y qué no

| Cubre | No cubre (hay que rehacerlo a mano) |
| --- | --- |
| Las **nueve tablas** de `public` (`usuarios`, `atletas`, `sesiones`, `versiones_motor`, `videos`, `reportes_biomecanicos`, `metricas`, `alertas`, `reportes_sesion`), fila por fila | **Contraseñas** de las cuentas (la API de administración no las expone): tras restaurar, cada usuario usa "Olvidé mi contraseña" (el correo propio funciona desde el 15/10) |
| Las **cuentas** (`auth.users`: id, correo, fechas, metadatos) | **Configuración del proyecto Supabase:** SMTP (clave de Brevo), *Site URL* y *Redirect URLs*, plantillas de correo (`supabase/templates/`), límites de envío |
| Los **archivos** de los buckets `videos` y `artefactos`, con SHA-256 | **Variables de entorno de Render** (`SUPABASE_URL`, clave `service_role`, `KINETIQ_CORS_ORIGINS`, token de la API) y la configuración de Cloudflare |
| El **esquema**: no se respalda, **se reconstruye** con `supabase/migrations/` (13 archivos, en orden) y la prueba comprueba que aplican sobre una base vacía | Una copia completa de Postgres con `pg_dump` (incluye `auth` con las contraseñas): ver §6 |

## 2. Hacer un respaldo

Desde `backend/` (con `backend/.env` cargado, como el resto de las herramientas):

```bash
cd C:\Users\valen\motion-biomech-detect\backend
PYTHONPATH=. .venv/Scripts/python.exe -m app.respaldo exportar --salida "C:/Users/valen/kinetiq-data/respaldos"
```

- Crea `respaldo-AAAAMMDD-HHMMSS/` con `tablas/*.jsonl`, `auth/usuarios.jsonl`, `storage/<bucket>/...` y `manifiesto.json` (conteos, huellas SHA-256, commit del repositorio, migraciones esperadas) y **lo verifica solo** al terminar.
- **Se niega a escribir dentro del repositorio:** el respaldo tiene **datos personales** (correos y videos de personas). Se guarda en una carpeta local fuera del repositorio y **no se sube a ningún lado**.
- Verificarlo de nuevo en cualquier momento: `python -m app.respaldo verificar "<carpeta del respaldo>"`.
- Tamaño y tiempo del primero: 840 MB (33 videos y 47 artefactos), unos 7 minutos (sin cronometrar con precisión).

**Cuándo:** antes de **cada publicación** (`docs/publicacion-y-vuelta-atras.md`), antes de **cada migración**, el día anterior a la **demo** y después de cualquier sesión con datos nuevos que importe conservar. Conservar los dos o tres últimos.
*Un respaldo que vive solo en la misma PC protege de un error de software, no de la pérdida de la PC: conviene copiar la carpeta a un disco externo o a un almacenamiento privado propio.*

## 3. Probar que se puede restaurar

Un respaldo que nunca se restauró no es una garantía. La prueba **no toca Supabase ni producción**: levanta un Postgres embebido y descartable, crea lo mínimo de la plataforma, aplica las migraciones, carga el respaldo y compara.

```bash
python -m venv venv_respaldo
venv_respaldo\Scripts\pip install pgserver "psycopg[binary]"
venv_respaldo\Scripts\python tools\respaldo\restaurar_prueba.py "C:\Users\valen\kinetiq-data\respaldos\respaldo-AAAAMMDD-HHMMSS" --salida informe.json
```

Comprueba, y sale con error si alguna falla: (1) las 13 migraciones aplican sobre una base vacía; (2) todas las columnas del respaldo existen en el esquema; (3) **cada tabla restaurada es igual fila por fila** al respaldo; (4) las cuentas;
(5) cada archivo de Storage coincide con su huella; (6) **cada video** de la base tiene su archivo en el bucket; (7) **las políticas de acceso restauradas aíslan**: cada cuenta ve solo sus videos.

### Resultado del primer respaldo (15/10/2026) — `docs/resultados/respaldo-restauracion-2026-10-15.json`

| Qué | Valor |
| --- | --- |
| Respaldo | 3 cuentas · 1 jugador · 8 sesiones · 18 videos · 17 reportes · 35 métricas · 6 versiones del motor · 0 alertas · 33 + 47 archivos (840 MB) |
| Integridad (`verificar`) | **íntegro** |
| Restauración (`restaurar_prueba.py`, PostgreSQL 16.2 local) | **verificada: 16 de 16 comprobaciones** |
| Desviación del arnés | el Postgres embebido no trae `pgcrypto`; las migraciones solo lo piden para `gen_random_uuid()`, que es nativo: se omitió esa línea y quedó anotado en el informe |

**Lo que esta prueba demuestra y lo que no:** demuestra que el respaldo está completo y es coherente, que el esquema se reconstruye desde las migraciones y que los datos y las políticas funcionan restaurados. **No** demuestra la restauración
en un proyecto Supabase real (otra versión de Postgres, GoTrue y Storage reales): eso se hace en §4 el día que haga falta, o en un proyecto de prueba si se quiere ensayar.

## 4. Restaurar de verdad (proyecto Supabase nuevo)

1. **Crear un proyecto** en Supabase y anotar su URL y sus claves (no van al repositorio).
2. **Aplicar el esquema:** correr en orden los 13 archivos de `supabase/migrations/` en el editor SQL (o con la CLI de Supabase).
3. **Crear las cuentas** con los mismos `id` (las tablas dependen de ellos): con la API de administración de Auth, una por cada línea de `auth/usuarios.jsonl`, con el correo confirmado y los mismos metadatos.
   *No verificado: que esa API acepte fijar el `id`. Si no lo acepta, la alternativa es insertar en `auth.users` desde el editor SQL antes de cargar las tablas.* Los disparadores de alta crean la fila de `usuarios`: cargar `usuarios` con `on conflict (id) do update`.
4. **Cargar las tablas** en este orden (claves foráneas): `usuarios`, `atletas`, `sesiones`, `versiones_motor`, `videos`, `reportes_biomecanicos`, `metricas`, `alertas`, `reportes_sesion`.
5. **Subir los archivos** de `storage/videos` y `storage/artefactos` con la misma ruta (`<usuario_id>/<video_id>/…`).
6. **Reconfigurar:** SMTP (Brevo), *Site URL* y *Redirect URLs* (`https://kinetiqtennis.me`), `SUPABASE_URL` y la clave de servicio en Render, `KINETIQ_CORS_ORIGINS`, y las variables públicas del frontend (`VITE_SUPABASE_URL`, clave `anon`) → volver a publicar el frontend.
7. **Avisar a los usuarios** que usen "Olvidé mi contraseña".
8. **Verificar:** ingresar, abrir la Biblioteca y un reporte con su video, y mirar que `/health` de la API responda.

## 5. Después de la restauración: lo que cambia

- Los `id` de los reportes y de los videos se conservan, así que los enlaces del propio usuario siguen funcionando.
- Los análisis que estaban `encolado` o `procesando` en el momento del respaldo se reencolan al arrancar el servidor (recuperación al arrancar).

## 6. Complemento recomendado: copia completa con `pg_dump`

El respaldo lógico de arriba no incluye las contraseñas. La copia **completa** de la base se hace con la cadena de conexión que da el panel de Supabase (*Project Settings → Database → Connection string*), que lleva la contraseña
de la base de datos y **no** la tengo yo ni está en el repositorio:

```bash
pg_dump "postgresql://postgres:<CONTRASEÑA-DE-LA-BASE>@<HOST-DEL-PANEL>:5432/postgres" --schema=public --schema=auth -Fc -f kinetiq-completo.dump
```

(Con `psql`/`pg_restore` instalados; el comando exacto y el host salen del panel.) Se guarda igual que el otro respaldo: fuera del repositorio. Conviene hacerlo al menos antes de la demo y de la defensa.
