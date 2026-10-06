# Decisión 027 — Correo de confirmación de registro: SMTP propio (el de Supabase no sirve para usuarios reales)

**Fecha:** 7 de octubre de 2026
**Estado:** **vigente, 7/10/2026 (Valentín): opción A en curso —dominio gratis con el GitHub Student Developer Pack— y opción B como respaldo si el Pack no sale.** Se
mantiene la **confirmación por correo obligatoria** (decisión de Valentín: es un requisito serio con datos de salud).
**Afecta a:** Supabase Auth (SMTP, plantilla, *Site URL*) · pantalla de Registro (`docs/ux/especificacion-frontend.md` §3) · plan de punta a punta ·
`tests/integration/test_registro_confirmacion_login.py`

---

## El problema

El proyecto exige que un usuario nuevo pueda registrarse, **confirmar su correo** y entrar, como si el sistema fuera público. Verificado el 7/10/2026
contra la documentación de Supabase:

- El correo **integrado** de Supabase entrega **2 mensajes por hora** y **solo a direcciones del equipo del proyecto** ("refuses to deliver messages to
  addresses that are not part of the project's team"), sin garantía de servicio, y es solo "para exploración y pruebas". **Un usuario real no podría registrarse.**
- Con SMTP propio, Supabase aplica al principio un límite bajo de **30 mensajes por hora**, que se sube desde Authentication → Rate Limits.

## Lo que se verificó sobre Brevo (la propuesta inicial)

La propuesta de partida era Brevo (plan gratuito, 300 por día), verificando **una sola dirección de remitente** y **sin dominio propio**. Lo verificado:

| Punto | Resultado | Fuente |
| --- | --- | --- |
| Plan gratuito | 300 correos por día, con relé SMTP y API para correos transaccionales. | Fuentes secundarias (la página de precios de Brevo no se pudo leer automáticamente). |
| Remitente con `gmail.com` | **No se puede autenticar**: Brevo exige un dominio propio. Si el dominio no está autenticado, Brevo **reemplaza el remitente** por uno propio (`t-sender-sib.com` / `brevosend.com`). | Personal de Brevo en su comunidad: "The old gmail address won't work, as per the Google and Yahoo requirements"; guías técnicas. |
| Entrega a Gmail y Yahoo sin dominio verificado | Hay reportes de correos **aceptados por Brevo que nunca llegan**, sin error. | Reporte de un desarrollador (dev.to). |
| Marca "Sent with Brevo" | Una fuente secundaria dice que el plan gratuito siempre la agrega; no se pudo confirmar si aplica a correos transaccionales por SMTP. | Fuente secundaria, **sin confirmar**. |

**Conclusión:** la propuesta *"Brevo sin dominio propio, verificando una sola dirección"* **no es confiable** para usuarios nuevos reales, sobre todo si tienen Gmail. El supuesto
que no se sostiene es el del remitente sin dominio. Brevo en sí (plan, límites, SMTP) sí sirve **si hay un dominio propio autenticado**.

## Alternativas consideradas

| | Descripción | A favor | En contra |
| --- | --- | --- | --- |
| **A — Dominio propio + Brevo** | Se compra un dominio, se lo autentica en Brevo (registros SPF, DKIM y DMARC) y se envía desde una dirección de ese dominio. | Entrega confiable a cualquier proveedor; sirve para el futuro; el DNS puede vivir en Cloudflare, donde ya se publica el frontend. | Cuesta un dominio (precio **no verificado**: depende de la extensión) y requiere cargar registros DNS. |
| **B — Cuenta Gmail dedicada por SMTP** | Una cuenta de Gmail solo para esto (p. ej. `kinetiq.app@gmail.com`), con verificación en dos pasos y una *contraseña de aplicación*, usando `smtp.gmail.com` (puerto 465 o 587). | Sin dominio ni costo; el correo sale de los servidores de Google, con firma y alineación propias. | **Supabase solo lo documenta para Google Workspace**, no para cuentas personales (no verificado que esté soportado); **no se verificaron los límites de envío ni los términos de uso** para una cuenta personal; riesgo de bloqueo de la cuenta. |
| C — Desactivar la confirmación | — | Cero configuración. | **Descartada por Valentín**: con datos de salud la confirmación es un requisito. |

## Decisión (Valentín, 7/10/2026)

**Opción A, sin costo, por el GitHub Student Developer Pack; opción B como respaldo.** Las dos quedan documentadas acá, con sus pasos.

- **A — en curso.** Valentín pidió el GitHub Student Developer Pack (la verificación estudiantil puede tardar unos días). El Pack incluye, de Namecheap, **1 año de registro de un dominio `.me` y 1 certificado SSL** mientras
  se sea estudiante (verificado en la página oficial del Pack el 7/10/2026; **el Pack no incluye ningún servicio de envío de correo**, por eso se usa Brevo con ese dominio). Con el dominio: Brevo autentica el dominio
  (SPF, DKIM y DMARC) y el correo sale de una dirección de ese dominio. El precio de renovación del `.me` después del año gratis **no está verificado** (una fuente secundaria menciona unos USD 5 por año).
- **B — respaldo.** Si el Pack no sale (o no sale a tiempo para el 20/10): cuenta Gmail dedicada con contraseña de aplicación por SMTP. Con los límites y riesgos de la tabla de alternativas (no documentado por Supabase para cuentas
  personales; límites de envío sin verificar). Es un puente, no la solución definitiva.
- **El frontend sigue en `.pages.dev` por ahora** (decisión 026). Si se consigue el dominio, **después** se puede usar también para el frontend; no es condición del correo.
- Quedan fijas, con cualquiera de las dos:
  1. **Correo de confirmación en español con la marca KinetiQ:** plantilla en `supabase/templates/confirmar-registro.html` (se pega en Authentication → Emails → "Confirm sign up").
  2. **La pantalla de Registro avisa que revisen la carpeta de spam** (especificación de frontend).
  3. **Supabase → Authentication → URL Configuration → Site URL** apunta al dominio público del frontend (hoy el `.pages.dev` que se publique); si no, el enlace de confirmación lleva a una dirección local.
  4. Subir el límite de correos por hora en Authentication → Rate Limits según el volumen esperado.
  5. **Con dominio propio mejora la entrega** (SPF, DKIM y DMARC alineados): es la razón por la que A es la solución y B el puente.

## Procedimientos

### A — Dominio `.me` (Student Pack) + Brevo

1. **Student Pack:** pedirlo en education.github.com con el correo o la credencial estudiantil. Al aprobarse, activar la oferta de Namecheap desde la página del Pack.
2. **Registrar el dominio** en Namecheap con la oferta (un `.me`, por ejemplo `kinetiq.me` si está libre; la elección del nombre es de Valentín).
3. **DNS:** dos caminos. (i) Dejar el DNS en Namecheap y agregar ahí los registros de Brevo; o (ii) apuntar los *nameservers* del dominio a Cloudflare y administrar el DNS allá (útil si después se usa el dominio para el frontend). Cualquiera sirve para el correo.
4. **Brevo:** crear la cuenta (plan gratuito) y en Senders, Domains & Dedicated IPs → Domains agregar el dominio. Brevo muestra los registros a cargar: código de verificación (TXT), DKIM y DMARC (TXT, al menos `p=none`). Cargarlos en el DNS y pulsar "Authenticate". Esperar la propagación.
5. Crear el remitente `no-reply@<dominio>` con el nombre "KinetiQ".
6. **Brevo → SMTP & API → SMTP:** generar una clave SMTP. Servidor `smtp-relay.brevo.com`, puerto `587`; el usuario y la clave los muestra esa pantalla (**verificar los valores exactos en pantalla**).
7. **Supabase → Authentication → Emails → SMTP Settings:** activar SMTP propio con el remitente del punto 5, nombre "KinetiQ" y esos datos. Después: plantilla, *Site URL* y límite de correos (puntos 1, 3 y 4 de arriba).
8. **Prueba manual de entrega** (una vez): registrarse con un correo real propio y comprobar dónde llega (bandeja o spam), con remitente, asunto y marca correctos, y que el enlace lleva al frontend publicado.

### B — Gmail dedicado (respaldo)

1. Crear una cuenta de Gmail **solo para esto** (p. ej. `kinetiq.app@gmail.com`); no usar la cuenta personal.
2. Activar la **verificación en dos pasos** y generar una **contraseña de aplicación** (cuenta de Google → Seguridad → Contraseñas de aplicaciones).
3. **Supabase → Authentication → Emails → SMTP Settings:** servidor `smtp.gmail.com`, puerto `465` (o `587`), usuario = ese Gmail, contraseña = la de aplicación, remitente = ese Gmail, nombre "KinetiQ". La contraseña de aplicación solo vive en el panel de Supabase, nunca en el repositorio.
4. Plantilla, *Site URL*, límite de correos y prueba manual, como en A (puntos 1, 3, 4 y 8).
5. **Cuando llegue el dominio, pasar a A** y dar de baja la contraseña de aplicación.

## Verificación

- **Automática** (`tests/integration/test_registro_confirmacion_login.py`, contra Supabase real): un usuario nuevo se registra, **no puede entrar sin confirmar**, confirma con el enlace y **entra**. El enlace
  se genera por la API de administración, así que **no envía correos reales** (no gasta cuota ni ensucia la reputación del remitente). Prueba la lógica de confirmación, no la entrega.
- **Manual (una vez, por Valentín):** registrarse con una dirección real propia, comprobar que llega el correo (y dónde: bandeja o spam), con remitente, asunto y marca correctos, y que el enlace lleva al frontend publicado.

## Consecuencias

- Hasta que haya un SMTP propio funcionando (A o B), el registro de usuarios que no sean del equipo de Supabase **no funciona** con la confirmación activa.
- El 20/10 (prueba desde el celular) depende de que haya SMTP funcionando, o de que el usuario de prueba se cree desde el panel de Supabase ya confirmado (como ya se hizo para la prueba del iPhone).
- Si el Pack tarda más allá del 20/10, se pasa a B sin cambiar nada más del sistema; el cambio es solo de los datos de SMTP en el panel.
