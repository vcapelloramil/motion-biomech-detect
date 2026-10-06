# Decisión 026 — El frontend se publica en Cloudflare, y el repositorio es la única fuente del código (Lovable deja de editarlo)

**Fecha:** 7 de octubre de 2026
**Estado:** vigente — decisión de Valentín. La **corrección del Capítulo 4 queda pendiente** (ver
`docs/tesis/correcciones-pendientes-capitulo-4.md`).
**Afecta a:** `frontend/` · `CLAUDE.md` §5 (despliegue objetivo) · Capítulo 4 §4.5.1 y la tabla del stack · plan de punta a punta

---

## El problema

Dos cosas del plan original ya no reflejan la realidad:

1. **El hosting.** El Capítulo 4 y `CLAUDE.md` dicen que el frontend va en **Vercel** (plan Hobby). Pero el frontend que generó Lovable (TanStack Start) **viene
   configurado para Cloudflare Workers** (`frontend/wrangler.jsonc`, `@cloudflare/vite-plugin`, `src/server.ts`). Publicarlo en Vercel exige cambiar el adaptador de
   despliegue y volver a probarlo.
2. **Quién edita el código.** El prototipo nació en Lovable y el repositorio lo importó (26/8/2026). Con dos lugares de edición hay conflictos cruzados, y el plan
   de punta a punta necesita conectar el frontend a datos reales (cliente de Supabase, sesión, pantallas), lo que se hace en el repositorio.

## Decisión

1. **Hosting del frontend: Cloudflare**, donde ya está configurado. No se porta a Vercel.
2. **El repositorio es la única fuente del código del frontend.** Lovable **deja de editar código** a partir del 7/10/2026. Las modificaciones las hace Claude Code en este
   repositorio, con commits revisables. (Valentín confirma en Lovable que el proyecto deje de sincronizar cambios hacia el repositorio, para que no vuelva a pisarlo.)
3. **Variables del frontend:** solo valores públicos (URL de Supabase, clave anon, URL de la API). Ningún secreto en el frontend (CLAUDE.md §4).

## Alternativas consideradas

- **Portar a Vercel** (lo que dice la tesis): retrabajo de despliegue sin beneficio para el MVP. Descartada.
- **Seguir editando en Lovable en paralelo:** dos fuentes de verdad, cambios que se pisan. Descartada.

## Consecuencias

- **Capítulo 4 a corregir:** §4.5.1 (topología de despliegue: el diagrama y el párrafo "Interfaz en Vercel"), y las tablas del stack y de costos que listan Vercel; se anota en
  `docs/tesis/correcciones-pendientes-capitulo-4.md`. `CLAUDE.md` §5 se actualiza en esta misma entrega.
- **No verificado todavía:** las cuotas del plan gratuito de Cloudflare para el volumen del MVP; se revisan antes de publicar. El mecanismo de publicación (compilación de Cloudflare
  conectada al repositorio, o `wrangler` por línea de comandos) se decide al hacer la primera publicación.
- **CORS de la API:** el origen público del frontend en Cloudflare es el único que se permite en Render.
- La URL de Supabase Auth (*Site URL*) tiene que apuntar a ese dominio público para que el enlace del correo de confirmación funcione (decisión 027).
