import { createFileRoute } from "@tanstack/react-router";

/**
 * Privacidad (Ley 25.326). Es una declaración del responsable del proyecto: solo dice lo que el sistema hace HOY.
 * Si se agrega retención automática o el borrado desde Perfil, se actualiza acá en el mismo cambio.
 */
const CORREO_CONTACTO = "contacto@kinetiqtennis.me";
const ACTUALIZADO = "13 de octubre de 2026";

export const Route = createFileRoute("/privacidad")({
  head: () => ({
    meta: [
      { title: "Privacidad — KinetiQ" },
      {
        name: "description",
        content: "Qué datos guarda KinetiQ, para qué los usa y cómo pedir que se borren (Ley 25.326).",
      },
    ],
  }),
  component: PrivacidadPage,
});

function Seccion({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <section className="mt-10">
      <h2 className="font-display text-xl font-bold">{titulo}</h2>
      <div className="mt-3 space-y-3 text-sm leading-relaxed text-muted-foreground">{children}</div>
    </section>
  );
}

function PrivacidadPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Privacidad</div>
      <h1 className="mt-3 font-display text-4xl font-bold md:text-5xl">
        Tus datos, <span className="text-gradient-neon">claros</span>.
      </h1>
      <p className="mt-4 text-muted-foreground">
        KinetiQ es un proyecto final de Ingeniería en Informática (Universidad del Salvador). Esta página dice qué datos guarda, para qué y cómo
        pedir que se borren. Actualizada el {ACTUALIZADO}.
      </p>

      <Seccion titulo="Qué datos guarda">
        <ul className="list-disc space-y-2 pl-5">
          <li>
            <strong className="text-foreground">Tu cuenta:</strong> nombre, correo, rol que elegiste (jugador, entrenador o profesional) y la fecha en que
            aceptaste el tratamiento de datos. La contraseña la guarda el servicio de autenticación de forma cifrada: KinetiQ no la ve.
          </li>
          <li>
            <strong className="text-foreground">Los jugadores que cargás:</strong> nombre, mano dominante y nivel.
          </li>
          <li>
            <strong className="text-foreground">Cada sesión:</strong> golpe, encuadre, lado de la cámara, fecha y cómo dijiste que grabaste.
          </li>
          <li>
            <strong className="text-foreground">Los videos que subís</strong> (la imagen del jugador es un dato personal) y, de cada uno, lo que se
            calcula: el reporte (instantes, velocidades, ángulos y su confianza), tres fotogramas con el esqueleto dibujado, un video corto con el
            esqueleto y los tiempos de procesamiento.
          </li>
        </ul>
      </Seccion>

      <Seccion titulo="Para qué los usa">
        <p>
          Solo para analizar tus videos y mostrarte tus reportes y tu evolución. No se usan para publicidad ni se venden. Una persona con una cuenta
          distinta no ve tus videos ni tus reportes: el acceso está limitado por usuario.
        </p>
      </Seccion>

      <Seccion titulo="Dónde se guardan">
        <p>
          La base de datos y los archivos están en Supabase, en almacenamiento privado; el análisis corre en un servidor de Render y el sitio se sirve
          con Cloudflare. El correo de confirmación sale por un servicio de envío de correo.
        </p>
      </Seccion>

      <Seccion titulo="Cuánto tiempo los guarda">
        <p>
          Hasta que los elimines. No hay un borrado automático: tus datos y tus videos quedan guardados hasta que elimines un golpe, una sesión o
          toda tu cuenta.
        </p>
      </Seccion>

      <Seccion titulo="Tus derechos y cómo pedir el borrado">
        <p>
          La Ley 25.326 de Protección de los Datos Personales te da derecho a acceder a tus datos, corregirlos y pedir que se supriman. Lo podés
          hacer vos mismo desde <strong className="text-foreground">Perfil</strong>: ahí corregís tus datos y los de tus jugadores, descargás
          una copia en un archivo JSON y eliminás tu cuenta. Al eliminarla se borran tu cuenta, tus jugadores, tus sesiones, los reportes y los
          archivos de video e imágenes. Un golpe o una sesión sueltos se eliminan desde la Biblioteca y la vista de la sesión.
        </p>
        <p>
          Si no podés entrar a tu cuenta o algo no funciona, escribí a{" "}
          <a className="text-foreground underline underline-offset-4" href={`mailto:${CORREO_CONTACTO}`}>
            {CORREO_CONTACTO}
          </a>{" "}
          desde el correo con el que te registraste.
        </p>
        <p>
          La Agencia de Acceso a la Información Pública es el órgano de control de la Ley 25.326 y atiende las denuncias y reclamos de quienes
          crean que sus derechos no se respetaron.
        </p>
      </Seccion>

    </main>
  );
}
