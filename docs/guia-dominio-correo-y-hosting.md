# Guía paso a paso: dominio `.me`, correo de confirmación (Brevo + Supabase) y la aplicación en tu dominio

**Para:** Valentín · **Fecha:** 12/10/2026 · **Decisiones:** 027 (correo), 026 (hosting), 034 (esta guía) · **Tiempo:** ~1,5 h tuyas, más esperas de DNS (minutos a unas horas).

Esto lo tenés que hacer vos en los paneles (yo no puedo crear cuentas ni entrar a tus paneles). Cada paso dice **cómo saber que salió bien**. Lo que depende del nombre
del dominio lo hago yo cuando me lo pases (parte E).

## Respuesta corta: ¿pasar los DNS a Cloudflare? **Sí.**

1. **Es lo único que permite usar tu dominio para la aplicación.** Un Worker de Cloudflare (`kinetiq`, el que hoy sirve el `workers.dev`) solo acepta un *Custom Domain* si la zona del dominio
   está **activa en Cloudflare** ([documentación](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)). Con el DNS en Namecheap no se puede.
2. **No te cuesta nada** (plan Free de Cloudflare) y **los registros del correo conviven sin problema** en la misma zona (van como "solo DNS", nube gris).
3. **Un solo lugar** para la aplicación, el correo y, más adelante, el reenvío de `contacto@` a tu Gmail.
4. Lo único que cambia: en Namecheap el dominio queda apuntando a los servidores de nombres de Cloudflare; el registro (y la renovación) sigue siendo de Namecheap.

**Orden recomendado: A → B → C → D → E.** El DNS en Cloudflare va primero porque los registros de Brevo se cargan ahí.

---

## Estado verificado el 12/10 (kinetiqtennis.me)

Lo que se pudo comprobar **desde afuera, sin entrar a ningún panel** (consulta de DNS pública y API pública de GitHub):

| Qué | Resultado |
| --- | --- |
| Servidores de nombres | **Ya apuntan a Cloudflare** (`owen.ns.cloudflare.com` y `sue.ns.cloudflare.com`): la parte B.3 está hecha |
| Registros publicados en la raíz y en `www` | **Ninguno** (ni `A`, `AAAA`, `CNAME`, `TXT` ni `MX`): la zona está vacía. No queda nada apuntando a GitHub |
| Repositorio que creó NC.me | **`vcapelloramil.github.io`** (creado el 12/10 a las 18:48 UTC): solo tiene `CNAME` (con `kinetiqtennis.me`) y `README.md`; un único commit "Added CNAME file for custom domain" |

## Qué dejó NC.me (GitHub Pages) y qué borrar

NC.me, al elegir "GitHub Pages", **creó el repositorio `vcapelloramil.github.io`** —el repositorio especial del *sitio de usuario*— con un archivo `CNAME` que declara tu dominio. Además
suele cargar en Namecheap los registros de GitHub Pages. **Nada de eso sirve para KinetiQ** y una parte lo estorba:

**1. Registros DNS — borrar, si aparecen en Cloudflare (DNS → Records), todos estos:**

| Tipo | Nombre | Valor | Por qué sobra |
| --- | --- | --- | --- |
| `A` (cuatro) | `@` (la raíz) | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` | Apuntan la raíz a GitHub; el Worker necesita la raíz libre para su *Custom Domain* |
| `AAAA` (cuatro) | `@` | `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153` | Lo mismo, por IPv6 |
| `CNAME` | `www` | `vcapelloramil.github.io` | Manda `www` a GitHub; si querés `www`, se redirige a la raíz desde Cloudflare |
| `TXT` | `_github-pages-challenge-vcapelloramil` | (un código) | Es la verificación de dominio de GitHub Pages; solo existe si la pediste |

Hoy **ya no hay ninguno publicado** (se verificó por DNS). Si al importar la zona Cloudflare los ofrece, **no los importes**; si ya están cargados, borralos. **Dejá los registros `NS` y `SOA`:** los maneja Cloudflare.

**2. El repositorio `vcapelloramil.github.io` — se puede eliminar, y conviene.** No contiene nada tuyo (dos archivos que generó NC.me). Y **no es inocuo mientras exista**: es el *sitio de usuario*, y con un
`CNAME` los sitios de proyecto de tu cuenta (`ProyectoFinal_CapelloRamil`, `PreEntrega2_CapelloRamil`, `EntregaFinalCapelloRamil`, que tienen Pages) **pasan a servirse desde `kinetiqtennis.me/<proyecto>/`**,
dominio que ahora es de KinetiQ y donde esos sitios no van a existir: los enlaces de esos trabajos se rompen. Para dejarlo limpio, **en este orden**:

1. Primero los registros (punto 1): sin eso, borrar el repositorio deja el dominio apuntando a GitHub, y **otra cuenta podría reclamarlo** como dominio personalizado de su propio Pages.
2. En GitHub: `vcapelloramil.github.io` → **Settings → Pages → Custom domain → Remove** (quita el dominio del sitio).
3. Después: **Settings → General → Danger Zone → Delete this repository** (te pide escribir el nombre).
4. Si en **Settings → Pages → Verified domains** de tu cuenta figura `kinetiqtennis.me`, quitalo.

Si preferís **no borrar** el repositorio: alcanza con borrar el archivo `CNAME` (y con eso los proyectos vuelven a `vcapelloramil.github.io/<proyecto>/`). No toca `motion-biomech-detect`, que es otro repositorio.

## A. Conseguir el dominio (Namecheap, por el Student Pack)

1. Entrá a tu página del [GitHub Student Developer Pack](https://education.github.com/pack) y buscá la oferta de **Namecheap** (1 año de un `.me`, con SSL). Activala **desde esa página** (no desde Namecheap directo), porque ahí se aplica el descuento.
2. Creá o ingresá a tu cuenta de Namecheap y buscá el nombre. Sugerencias: `kinetiq.me`; si no está libre, `kinetiqtenis.me`, `kinetiqsports.me`, `usekinetiq.me`. **Elegí uno corto: va en el correo y en la dirección.**
3. En el carrito, el total tiene que dar **0** por el dominio. **Dejá activada la privacidad del registro** (WHOIS/"Withheld for Privacy"): oculta tu dirección y teléfono. Si te ofrece cosas pagas (hosting, correo, SSL), **no las agregues**.
4. Confirmá tu correo en Namecheap.

**Salió bien si:** en *Domain List* aparece `<nombre>.me` como "Active", con vencimiento a un año. *(Hecho: `kinetiqtennis.me`, con la renovación automática apagada. **Anotá la fecha de vencimiento**: sin renovación, el dominio —y el correo de confirmación— dejan de funcionar al año.)*
**Anotá** también cuánto cuesta la renovación (aparece en la lista): la oferta es de 1 año.

## B. Pasar el DNS a Cloudflare

1. En Cloudflare (dashboard) → **Add a domain** (*Onboard a domain*) → escribí `<nombre>.me` → plan **Free**.
2. Cloudflare escanea los registros que encuentre (no vas a tener ninguno útil) y te muestra **dos servidores de nombres** (algo como `xxx.ns.cloudflare.com`). Copiálos tal cual.
3. En Namecheap → *Domain List* → **Manage** → sección *Nameservers* → cambiá **Namecheap BasicDNS** por **Custom DNS** → pegá los dos → guardá (tilde verde).
   Si tenés DNSSEC activado en Namecheap, apagalo antes (por defecto está apagado).
4. Volvé a Cloudflare y esperá que la zona pase a **Active** (llega un correo; suele ser de minutos a algunas horas, hasta 24).

**Salió bien si:** Cloudflare muestra el dominio como **Active**.
**Si no pasa en 24 h:** revisá que escribiste los dos nombres exactos y que no quedó ninguno viejo de Namecheap.

## C. Brevo: autenticar tu dominio y sacar la clave SMTP

> Brevo pide que el remitente sea de un **dominio autenticado**: con `gmail.com` los correos se aceptan y no llegan (decisión 027). Por eso el dominio va primero.

1. Creá la cuenta en [Brevo](https://www.brevo.com) (plan gratuito: unos 300 correos por día). Te va a pedir validar el correo y algunos datos de la cuenta; son de Brevo, no de tu proyecto.
2. **Settings → Senders, Domains & Dedicated IPs → Domains → Add a domain** → `<nombre>.me` → elegí **"Authenticate the domain yourself"** (manual).
3. Brevo muestra los registros **de tu cuenta** (copiá los valores exactos desde ahí; los de otras guías no sirven). Son tres tipos, según la [documentación de Brevo](https://help.brevo.com/hc/en-us/articles/12163873383186):
   - **Brevo code** — un `TXT` en la raíz (`@`).
   - **DKIM** — dos `CNAME` (`brevo1._domainkey` y `brevo2._domainkey`) o un `TXT`, según tu cuenta.
   - **DMARC** — un `TXT` en `_dmarc` (con `p=none` alcanza para empezar).
4. En Cloudflare → tu dominio → **DNS → Records → Add record**, uno por uno, y en **todos** poné **Proxy status: "DNS only"** (nube **gris**). Un `CNAME`/`TXT` de verificación con la nube naranja falla.
5. Volvé a Brevo y tocá **Authenticate**. Puede tardar minutos (la propagación completa, hasta 48 h).
6. **Senders → Add a sender:** nombre **KinetiQ**, correo `no-reply@<nombre>.me`.
   *Si Brevo te pide confirmar la dirección y no tenés buzón en ese dominio:* en Cloudflare → **Email → Email Routing** activá el reenvío (gratis) de `no-reply@<nombre>.me` (o de todo el dominio) a tu Gmail, y confirmá desde ahí.
7. **SMTP & API → SMTP → Generate a new SMTP key:** copiá la clave **una sola vez** (después no se vuelve a mostrar). Los datos son:

   | Campo | Valor |
   | --- | --- |
   | Servidor | `smtp-relay.brevo.com` |
   | Puerto | `587` |
   | Usuario | el que muestra esa pantalla (el correo con el que abriste la cuenta de Brevo) |
   | Contraseña | la clave SMTP que acabás de generar |

   *Verificá estos valores en la pantalla de Brevo: son los de la decisión 027, que no pude releer automáticamente porque el sitio de ayuda de Brevo bloquea las lecturas.*

**Salió bien si:** el dominio figura **Authenticated** en Brevo (los tres ítems en verde) y tenés la clave SMTP anotada **fuera del repositorio**.

## D. Supabase: usar ese SMTP, la plantilla y las direcciones permitidas

1. **Authentication → Emails → SMTP Settings** ([documentación](https://supabase.com/docs/guides/auth/auth-smtp)): activá *Enable custom SMTP* y cargá:
   - *Sender email*: `no-reply@<nombre>.me` · *Sender name*: `KinetiQ`
   - *Host*: `smtp-relay.brevo.com` · *Port*: `587` · *Username* y *Password*: los de arriba.
2. **Authentication → Rate Limits:** con SMTP propio Supabase arranca en **30 correos por hora**; subilo (p. ej. 100) para que un grupo de registros no se frene.
3. **Authentication → Emails → "Confirm sign up":** pegá el contenido de [`supabase/templates/confirmar-registro.html`](../supabase/templates/confirmar-registro.html) y poné el asunto en español (p. ej. "Confirmá tu cuenta de KinetiQ").
4. **Authentication → URL Configuration:**
   - **Site URL:** `https://<nombre>.me` (cuando la parte E esté hecha; hasta entonces dejá el `workers.dev`).
   - **Redirect URLs (lista permitida):** agregá `https://<nombre>.me/**` y dejá `https://kinetiq.v-capelloramil.workers.dev/**` mientras convivan. El frontend arma el enlace con `window.location.origin`, así que **no hay que tocar código** para esto.
5. **Contraseña olvidada** (ya está hecha la pantalla: `/recuperar` pide el enlace y `/restablecer` elige la contraseña nueva): en **Authentication → Emails → "Reset Password"** pegá
   [`supabase/templates/restablecer-contrasena.html`](../supabase/templates/restablecer-contrasena.html), con el asunto "Elegí una contraseña nueva en KinetiQ". Usa el mismo SMTP. El enlace del correo vuelve a
   `https://<nombre>.me/restablecer`, que tiene que estar en las **Redirect URLs** del punto anterior (`https://<nombre>.me/**` ya lo cubre).

**Salió bien si:** (1) registrás una cuenta nueva con **tu Gmail real** y el correo llega (fijate si cae en spam), con remitente `KinetiQ <no-reply@<nombre>.me>`, y el enlace te lleva a la aplicación. En Gmail: *Mostrar original* → **SPF: PASS, DKIM: PASS, DMARC: PASS**. (2) En `/ingreso` tocás "¿Olvidaste tu contraseña?", pedís el enlace con ese correo, llega, y el enlace te deja elegir una contraseña nueva.

## E. La aplicación en `https://<nombre>.me` (en lugar de `workers.dev`)

Yo hago el cambio de código; vos los clics del panel. Cuando me pases el nombre:

1. **Yo:** agrego a `frontend/wrangler.jsonc` `"routes": [{ "pattern": "<nombre>.me", "custom_domain": true }]` (el repositorio es la única fuente: no se configura a mano en el panel), actualizo las decisiones 026 y 027 y la guía de despliegue.
2. **Vos:** `cd frontend; bun run build; .\node_modules\.bin\wrangler.exe deploy`. Cloudflare crea solo el registro DNS y el certificado.
   *Un solo requisito: el nombre `<nombre>.me` no puede tener ya un `CNAME` propio en la zona.*
3. **Vos — Render → kinetiq-motor → Environment:** `KINETIQ_CORS_ORIGINS` = `https://<nombre>.me,https://kinetiq.v-capelloramil.workers.dev,http://localhost:8080` (separados por comas). **Cambiar una variable reinicia el servicio:** hacelo cuando no haya un análisis en curso.
4. **Vos — Supabase:** el *Site URL* del punto D.4.
5. **Prueba:** abrí `https://<nombre>.me`, registrate con un correo nuevo, confirmá, ingresá, subí un golpe. Si el navegador dice "CORS" al disparar el análisis, la variable del punto 3 no tiene el dominio exacto (con `https://`, sin barra final).

**Salió bien si:** `https://<nombre>.me` abre KinetiQ con candado, y el flujo de registro → confirmación → ingreso → carga funciona desde ahí.

## Qué queda después

- El `workers.dev` sigue funcionando (no hace falta darlo de baja), pero **el que se muestra a los profesores es `https://<nombre>.me`**.
- **Renovación:** la oferta es de 1 año; anotala (el dominio tiene que seguir vivo hasta la defensa y la rendición del Capítulo 7).
- **Respaldo:** si Brevo diera problemas, el camino B de la decisión 027 (Gmail con contraseña de aplicación) sigue vigente; el cambio es solo de los datos de SMTP en Supabase.
- **Qué me tenés que pasar para seguir:** el nombre del dominio, y un "listo" cuando la parte D.1 funcione (o el síntoma si no).
