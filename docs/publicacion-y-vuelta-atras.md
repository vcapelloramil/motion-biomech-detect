# Publicar y volver atrás (Render y Cloudflare)

**Para qué:** que publicar una versión nueva tenga siempre un camino de regreso escrito **antes** de apretar el botón.
**Estado de producción conocido al escribirlo (15/10/2026):** servidor y frontend en el commit **`56a13c1`** (motor 0.5.4, contrato 1.4). Es el **"último bueno conocido"** al que se vuelve.

## 0. Qué se publica y qué riesgo trae

| Pregunta | Respuesta (verificada en el repositorio) |
| --- | --- |
| ¿Hay migraciones de base? | **No.** `git diff origin/main respaldo-13-10 -- supabase` está vacío. Los pasos 5 y 6 y los cambios del 15/10 no tocan el esquema ni las políticas: **no hay nada que deshacer en la base** |
| ¿Qué cambia en el servidor? | `DELETE /cuenta`, `GET /evolucion` (rutas nuevas, aditivas), la nota del lado de la cámara en el reporte (motor **0.5.5**, sin cambio de contrato) y la lectura de `lado_camara` de la sesión |
| ¿Qué cambia en el frontend? | Perfil real, Evolución, PDF como documento A4, esquema de encuadre nuevo en Cargar, "Tu actividad" |
| ¿Qué es irreversible? | **Eliminar una cuenta** (`DELETE /cuenta`) borra datos y archivos para siempre. Por eso hay un respaldo antes de publicar (`docs/respaldo-y-restauracion.md`) |
| ¿Se pueden romper entre sí? | Un frontend nuevo contra un servidor viejo: Perfil y Evolución fallan en esas dos llamadas, el resto sigue. Un servidor nuevo con el frontend viejo: sin efecto visible. **Por eso se publica primero el servidor y después el frontend, y se vuelve atrás al revés** |

## 1. Antes de publicar (lista)

1. **Respaldo reciente** de la base y de Storage, verificado: `python -m app.respaldo exportar …` y `verificar` (ver `docs/respaldo-y-restauracion.md`).
2. **Pruebas en verde** sobre la rama que se publica: servidor (`cd backend && PYTHONPATH=. .venv/Scripts/python.exe -m pytest ../tests -m "not slow" -q`) y frontend (`cd frontend && bun test && node_modules/.bin/tsc --noEmit && bun run build`).
3. **Sin análisis en curso:** reiniciar Render con un golpe procesando lo deja `procesando`; la recuperación al arrancar lo reencola (suma un intento), pero conviene no depender de eso. Mirar la Biblioteca o la tabla `videos` (estados `encolado` y `procesando`).
4. Anotar el commit que está en producción (el de vuelta atrás) y el commit que se va a publicar.

## 2. Publicar

```bash
cd C:\Users\valen\motion-biomech-detect
git checkout main
git merge --ff-only respaldo-13-10      # avanza main sin merge commit
git push origin main                    # Render redeploya el servidor solo
```

1. **Esperar el despliegue de Render** (panel → servicio `kinetiq-motor` → *Events*: "Deploy live") y comprobar `GET <URL de la API>/health`: debe responder `estado: ok` y `version_motor: 0.5.5`.
   Verificar **tres veces seguidas** (como el 14/10): un servicio que arranca y se cae da un `ok` y después no.
2. **Recién entonces republicar el frontend:**

```bash
cd C:\Users\valen\motion-biomech-detect\frontend
bun run build
node_modules\.bin\wrangler.exe deploy
```

3. **Prueba de humo** (5 minutos, con una cuenta de prueba, **sin** usar "Eliminar mi cuenta" en una cuenta real): ingresar → Biblioteca → abrir un reporte (¿aparece la nota del lado solo si corresponde?) →
   Perfil (¿"Tu actividad" muestra números?) → Evolución → "Descargar PDF" → Cargar (¿el esquema dice "Recomendado"?).

## 3. Cuándo volver atrás

Volver atrás **sin discutir** si: `/health` no responde `ok` a los 10 minutos del despliegue; no se puede ingresar ni cargar un golpe; algún reporte existente deja de abrir; la Biblioteca o la vista de sesión dan error 5xx. Un detalle visual
**no** es motivo: se corrige hacia adelante.

## 4. Volver atrás en Cloudflare (frontend) — primero

El frontend es un Worker (`kinetiq`). Cada `wrangler deploy` crea una versión y se puede volver a una anterior.

**Opción A — desde la consola:**

```bash
cd C:\Users\valen\motion-biomech-detect\frontend
node_modules\.bin\wrangler.exe deployments list          # lista las versiones desplegadas, la más nueva primero
node_modules\.bin\wrangler.exe rollback --message "vuelta a 56a13c1"   # sin id: vuelve a la versión inmediatamente anterior
node_modules\.bin\wrangler.exe rollback <id-de-version> --message "vuelta a 56a13c1"   # a una en particular
```

**Opción B — desde el panel:** Cloudflare → *Workers & Pages* → `kinetiq` → *Deployments* → elegir la versión anterior → *Rollback*.

**Opción C — reconstruir el commit bueno** (si la versión anterior ya no está disponible; es el camino que no depende de lo que Cloudflare conserve):

```bash
cd C:\Users\valen\motion-biomech-detect
git worktree add ..\kinetiq-bueno 56a13c1
cd ..\kinetiq-bueno\frontend
bun install
bun run build
node_modules\.bin\wrangler.exe deploy
cd ..\.. && git worktree remove kinetiq-bueno
```

Después de cualquiera: abrir `https://kinetiqtennis.me` en una ventana privada y comprobar que la Biblioteca y un reporte abren. *(No verificado por mí: cuántas versiones conserva Cloudflare. Por eso existe la opción C.)*

## 5. Volver atrás en Render (servidor) — segundo

**Opción A — desde el panel (la rápida):** panel de Render → servicio `kinetiq-motor` → *Events* o *Deploys* → buscar el despliegue del commit `56a13c1` → *Rollback*. Vuelve a la misma imagen anterior sin reconstruir.
*Verificar en el panel:* Render puede **desactivar el despliegue automático** del servicio al hacer un rollback; si es así, hay que volver a activarlo (*Settings → Build & Deploy → Auto-Deploy*) cuando se publique una versión corregida.

**Opción B — con git (deja la historia limpia y vuelve a desplegar solo):**

```bash
cd C:\Users\valen\motion-biomech-detect
git checkout main
git revert --no-edit 56a13c1..HEAD       # un commit de reversión por cada commit publicado
git push origin main                     # Render redeploya el estado anterior
```

No se usa `git push --force` sobre `main`.

Comprobar después `GET <URL de la API>/health`: `version_motor` debe volver a `0.5.4`.

## 6. Qué no se deshace

- **Los datos que los usuarios hayan creado** con la versión nueva (sesiones, golpes) quedan: el esquema no cambió, así que la versión anterior los lee igual.
- **Una cuenta eliminada** con `DELETE /cuenta`: solo se recupera desde un respaldo (y sin contraseña: el usuario usa "Olvidé mi contraseña"). Ver `docs/respaldo-y-restauracion.md`.
- **Variables de entorno de Render** (`KINETIQ_CORS_ORIGINS`, etc.) y **la configuración de Supabase** (SMTP, URLs de redirección) no cambian con un rollback de código.
