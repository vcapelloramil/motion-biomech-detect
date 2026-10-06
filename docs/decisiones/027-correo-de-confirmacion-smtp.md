# Decisión 027 — Correo de confirmación de registro: SMTP propio (el de Supabase no sirve para usuarios reales)

**Fecha:** 7 de octubre de 2026
**Estado:** **PROPUESTA — pendiente de que Valentín elija entre A y B** (ver "Decisión"). Se mantiene la **confirmación por correo obligatoria**
(decisión de Valentín: es un requisito serio con datos de salud).
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

## Decisión (propuesta de Claude)

- **Recomendada: A.** Es la única opción de la lista cuya entrega no depende de una excepción ni de un límite sin verificar. Valentín ya usa Cloudflare, donde se compra y se administra el
  dominio, y Brevo permite conectar el dominio con los registros DNS.
- **B es un puente aceptable** si no se quiere comprar un dominio antes del 20/10: sirve para las pruebas propias, con los riesgos de la tabla.
- Cualquiera sea la opción, quedan fijas estas piezas:
  1. **Correo de confirmación en español con la marca KinetiQ:** plantilla en `supabase/templates/confirmar-registro.html` (se pega en Authentication → Emails → "Confirm sign up").
  2. **La pantalla de Registro avisa que revisen la carpeta de spam** (especificación de frontend).
  3. **Supabase → Authentication → URL Configuration → Site URL** apunta al dominio público del frontend (decisión 026); si no, el enlace de confirmación lleva a una dirección local.
  4. Subir el límite de correos por hora en Authentication → Rate Limits según el volumen esperado.
  5. **Con dominio propio mejora la entrega** (SPF, DKIM y DMARC alineados): es la razón por la que A se recomienda aunque B funcione.

## Verificación

- **Automática** (`tests/integration/test_registro_confirmacion_login.py`, contra Supabase real): un usuario nuevo se registra, **no puede entrar sin confirmar**, confirma con el enlace y **entra**. El enlace
  se genera por la API de administración, así que **no envía correos reales** (no gasta cuota ni ensucia la reputación del remitente). Prueba la lógica de confirmación, no la entrega.
- **Manual (una vez, por Valentín):** registrarse con una dirección real propia, comprobar que llega el correo (y dónde: bandeja o spam), con remitente, asunto y marca correctos, y que el enlace lleva al frontend publicado.

## Consecuencias

- Hasta que esta decisión se cierre (A o B), el registro de usuarios que no sean del equipo de Supabase **no funciona** con la confirmación activa.
- El 20/10 (prueba desde el celular) depende de que haya SMTP funcionando, o de que el usuario de prueba se cree desde el panel de Supabase ya confirmado.
