import { useState, type FormEvent } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { MailCheck, AlertTriangle, Loader2 } from "lucide-react";
import { getSupabase, supabaseConfigurado } from "@/lib/supabase";
import {
  LARGO_MINIMO_CONTRASENA,
  ROLES,
  contrasenaValida,
  esRol,
  mensajeDeRegistro,
} from "@/lib/auth-errores";

export const Route = createFileRoute("/registro")({
  head: () => ({
    meta: [
      { title: "Crear cuenta — KinetiQ" },
      { name: "description", content: "Creá tu cuenta para cargar videos y ver tus reportes." },
    ],
  }),
  component: RegistroPage,
});

const CAMPO =
  "mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring";

function RegistroPage() {
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [rol, setRol] = useState("");
  const [consentimiento, setConsentimiento] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviadoA, setEnviadoA] = useState<string | null>(null);
  const [reenvio, setReenvio] = useState<{ estado: "idle" | "enviando" | "ok" | "error"; texto?: string }>({ estado: "idle" });

  const supabase = getSupabase();

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!supabase) return;
    if (!nombre.trim()) return setError("Escribí tu nombre.");
    if (!/^\S+@\S+\.\S+$/.test(correo.trim())) return setError("Escribí un correo válido.");
    if (!esRol(rol)) return setError("Elegí cómo vas a usar KinetiQ.");
    if (!contrasenaValida(contrasena)) {
      return setError(`La contraseña necesita al menos ${LARGO_MINIMO_CONTRASENA} caracteres, con letras y números.`);
    }
    if (!consentimiento) return setError("Para crear la cuenta tenés que aceptar el tratamiento de tus datos.");

    setEnviando(true);
    const { error: err } = await supabase.auth.signUp({
      email: correo.trim(),
      password: contrasena,
      options: {
        // El trigger de alta (decisión 018) lee `nombre` y `rol` de estos metadatos. El consentimiento queda
        // con fecha en la cuenta (Ley 25.326).
        data: { nombre: nombre.trim(), rol, consentimiento_datos_en: new Date().toISOString() },
        emailRedirectTo: `${window.location.origin}/ingreso?confirmado=1`,
      },
    });
    setEnviando(false);
    if (err) return setError(mensajeDeRegistro(err).texto);
    // Con la confirmación por correo activa, un correo ya registrado devuelve la misma respuesta (no revela
    // qué correos existen): se muestra el mismo aviso y el enlace a Ingreso.
    setEnviadoA(correo.trim());
  }

  async function reenviar() {
    if (!supabase || !enviadoA) return;
    setReenvio({ estado: "enviando" });
    const { error: err } = await supabase.auth.resend({
      type: "signup",
      email: enviadoA,
      options: { emailRedirectTo: `${window.location.origin}/ingreso?confirmado=1` },
    });
    setReenvio(
      err
        ? { estado: "error", texto: mensajeDeRegistro(err).texto }
        : { estado: "ok", texto: "Listo, te lo enviamos de nuevo. Puede tardar unos minutos." },
    );
  }

  if (enviadoA) {
    return (
      <main className="mx-auto max-w-md px-6 py-16">
        <div className="rounded-xl border border-border bg-card p-6">
          <MailCheck className="h-8 w-8 text-neon" aria-hidden="true" />
          <h1 className="mt-4 font-display text-2xl font-bold">Revisá tu correo</h1>
          <p className="mt-3 text-sm text-muted-foreground">
            Te enviamos un correo a <strong className="text-foreground">{enviadoA}</strong> para confirmar tu cuenta.{" "}
            <strong className="text-foreground">Revisá también la carpeta de spam o correo no deseado.</strong>
          </p>
          <p className="mt-3 text-sm text-muted-foreground">
            La cuenta se activa cuando tocás el enlace del correo. Mientras tanto no vas a poder ingresar.
          </p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={reenviar}
              disabled={reenvio.estado === "enviando"}
              className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:border-neon/50 disabled:opacity-60"
            >
              {reenvio.estado === "enviando" ? "Enviando…" : "Reenviar el correo"}
            </button>
            <Link to="/ingreso" className="text-sm text-muted-foreground underline underline-offset-4 hover:text-foreground">
              Ya confirmé: ingresar
            </Link>
          </div>
          {reenvio.texto && (
            <p role="status" className={`mt-3 text-sm ${reenvio.estado === "error" ? "text-destructive" : "text-muted-foreground"}`}>
              {reenvio.texto}
            </p>
          )}
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <h1 className="font-display text-3xl font-bold">Crear cuenta</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Para cargar videos y ver tus reportes. Te vamos a pedir que confirmes el correo.
      </p>

      {!supabaseConfigurado && <SinConfiguracion />}

      <form onSubmit={enviar} className="mt-8 space-y-5" noValidate>
        <div>
          <label htmlFor="nombre" className="text-sm font-medium">Nombre</label>
          <input id="nombre" className={CAMPO} value={nombre} onChange={(e) => setNombre(e.target.value)} autoComplete="name" required />
        </div>
        <div>
          <label htmlFor="correo" className="text-sm font-medium">Correo</label>
          <input id="correo" type="email" className={CAMPO} value={correo} onChange={(e) => setCorreo(e.target.value)} autoComplete="email" required />
        </div>
        <div>
          <label htmlFor="contrasena" className="text-sm font-medium">Contraseña</label>
          <input
            id="contrasena"
            type="password"
            className={CAMPO}
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
            autoComplete="new-password"
            aria-describedby="ayuda-contrasena"
            required
          />
          <p id="ayuda-contrasena" className="mt-1 text-xs text-muted-foreground">
            Al menos {LARGO_MINIMO_CONTRASENA} caracteres, con letras y números.
          </p>
        </div>
        <div>
          <label htmlFor="rol" className="text-sm font-medium">¿Cómo vas a usar KinetiQ?</label>
          <select id="rol" className={CAMPO} value={rol} onChange={(e) => setRol(e.target.value)} required>
            <option value="" disabled>Elegí una opción</option>
            {ROLES.map((r) => (
              <option key={r.valor} value={r.valor}>{r.etiqueta}</option>
            ))}
          </select>
          <p className="mt-1 text-xs text-muted-foreground">Define qué vista del reporte se abre primero. Lo podés cambiar después.</p>
        </div>
        <div className="flex items-start gap-3">
          <input
            id="consentimiento"
            type="checkbox"
            checked={consentimiento}
            onChange={(e) => setConsentimiento(e.target.checked)}
            className="mt-1 h-4 w-4 shrink-0"
            required
          />
          <label htmlFor="consentimiento" className="text-sm text-muted-foreground">
            Entiendo que mis datos y los videos que cargue se tratan según la Ley 25.326 de Protección de los Datos
            Personales, y que puedo solicitar su supresión.
          </label>
        </div>

        {error && (
          <p role="alert" className="flex items-start gap-2 rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={enviando || !supabaseConfigurado}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-gradient-neon px-4 py-2.5 text-sm font-semibold text-neon-foreground shadow-neon disabled:opacity-60"
        >
          {enviando && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
          Crear cuenta
        </button>
      </form>

      <p className="mt-6 text-sm text-muted-foreground">
        ¿Ya tenés cuenta?{" "}
        <Link to="/ingreso" className="text-foreground underline underline-offset-4">Ingresar</Link>
      </p>
    </main>
  );
}

function SinConfiguracion() {
  return (
    <p role="alert" className="mt-6 flex items-start gap-2 rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>
        Falta la configuración de la aplicación (<code>VITE_SUPABASE_URL</code> y <code>VITE_SUPABASE_ANON_KEY</code>).
        Ver <code>frontend/.env.example</code>.
      </span>
    </p>
  );
}
