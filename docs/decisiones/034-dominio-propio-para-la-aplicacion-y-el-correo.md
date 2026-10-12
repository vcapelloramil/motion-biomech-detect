# Decisión 034 — Dominio `.me` propio para la aplicación y el correo, con el DNS en Cloudflare

**Fecha:** 12 de octubre de 2026
**Estado:** vigente (decisión de Valentín: tiene el Student Pack y consigue el dominio; **pendiente de que pase el nombre**)
**Afecta a:** decisión 026 (el frontend deja de mostrarse en `workers.dev`) · decisión 027 (la opción A pasa de "en curso" a "ejecutándose": Brevo con el dominio) · `frontend/wrangler.jsonc` ·
`KINETIQ_CORS_ORIGINS` en Render · Supabase (*Site URL* y direcciones permitidas) · plan §8 (punto 1)

---

## El problema

La decisión 027 dejó el correo de confirmación esperando el dominio (Student Pack) y la 026 dejó el frontend en `workers.dev` "por ahora, si se consigue el dominio después se puede usar también para el
frontend". El Pack ya está: hay que decidir **dónde vive el DNS**, porque de eso depende si la aplicación puede usar el dominio.

## Decisión

1. **El DNS del dominio vive en Cloudflare** (plan Free). Razón principal: un Worker solo acepta un *Custom Domain* si la zona del dominio está **activa en Cloudflare**
   (documentación de Cloudflare Workers, "Custom Domains"). Con el DNS en Namecheap no se puede usar el dominio para la aplicación. Razones secundarias: costo cero; los registros del correo (Brevo: código,
   DKIM, DMARC) conviven en la misma zona, **como "solo DNS"** (nube gris); un único lugar para todo.
2. **Brevo autentica el dominio** y envía como `KinetiQ <no-reply@<dominio>>`; **Supabase** usa el SMTP de Brevo (`smtp-relay.brevo.com:587`). Es la opción A de la 027.
3. **La aplicación se muestra en `https://<dominio>`.** El Worker `kinetiq` se asocia al dominio **desde `frontend/wrangler.jsonc`** (`routes` con `custom_domain: true`), no a mano en el panel: el repositorio
   sigue siendo la única fuente (decisión 026). El `workers.dev` queda funcionando durante la transición y en `KINETIQ_CORS_ORIGINS`.
4. **Sin cambios de código en el frontend para el enlace de confirmación**: usa `window.location.origin`; solo exige que el dominio esté en las direcciones permitidas de Supabase.
5. **El camino B de la 027 (Gmail con contraseña de aplicación) sigue siendo el respaldo**: el cambio es solo de los datos de SMTP en el panel.

## Hecho al 12/10/2026 (verificado desde afuera)

- **Dominio:** `kinetiqtennis.me` (Namecheap, Student Pack, renovación automática apagada). **Los servidores de nombres ya apuntan a Cloudflare** (`owen.ns.cloudflare.com`, `sue.ns.cloudflare.com`).
- **La zona está vacía:** ningún registro `A`, `AAAA`, `CNAME`, `TXT` ni `MX` publicado en la raíz ni en `www`. Faltan los de Brevo (código, DKIM, DMARC) y el *Custom Domain* del Worker.
- **NC.me configuró GitHub Pages** (el flujo que ofrece el Student Pack): creó el repositorio **`vcapelloramil.github.io`** en la cuenta de Valentín, con un `CNAME` (`kinetiqtennis.me`) y un `README.md`.
  Ese repositorio es el *sitio de usuario* de GitHub: con un `CNAME`, hace que los sitios de proyecto de la cuenta se redirijan a `kinetiqtennis.me/<proyecto>/`.

## Regla de limpieza (decisión)

1. **Ningún registro del dominio apunta a GitHub.** Los de GitHub Pages (`A` y `AAAA` de `185.199.108–111.153` y `2606:50c0:8000–8003::153`, `CNAME www`, `TXT _github-pages-challenge-*`) se borran o no se importan.
2. **El repositorio `vcapelloramil.github.io` se elimina** (o, como mínimo, se le quita el `CNAME`) **después** de borrar esos registros, para no dejar un dominio apuntando a GitHub sin dueño en la zona.
3. Detalle y pasos en `docs/guia-dominio-correo-y-hosting.md` ("Qué dejó NC.me y qué borrar").

## Consecuencias

- Se habilita el **registro abierto** (correos de confirmación a cualquier proveedor) y **"Olvidé mi contraseña"** (pantalla y plantilla preparadas con el punto 1 del plan §8).
- **El dominio vence al año** (oferta del Pack): hay que anotarlo y renovarlo si la aplicación tiene que seguir en pie después de la defensa. Costo de renovación sin verificar.
- Cambiar `KINETIQ_CORS_ORIGINS` **reinicia** el servicio de Render: se hace cuando no haya un análisis en curso.
- La guía con los pasos de los paneles, el orden y cómo comprobar cada uno está en [`docs/guia-dominio-correo-y-hosting.md`](../guia-dominio-correo-y-hosting.md).
- Capítulo 4 (despliegue): la corrección 1 de `correcciones-pendientes-capitulo-4.md` ("Cloudflare, no Vercel") suma "con dominio propio y DNS en Cloudflare".
