import { useState, type FormEvent } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { getSupabase, supabaseConfigurado } from "@/lib/supabase";
import { mensajeDeRecuperacion } from "@/lib/auth-errores";

export const Route = createFileRoute("/recuperar")({
  head: () => ({
    meta: [
      { title: "Recuperar contraseña — KinetiQ" },
      { name: "description", content: "Pedí un enlace para elegir una contraseña nueva." },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: RecuperarPage,
});

const CAMPO =
  "mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring";

function RecuperarPage() {
  const [correo, setCorreo] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const supabase = getSupabase();
    if (!supabase) return;
    if (!/^\S+@\S+\.\S+$/.test(correo.trim())) return setError("Escribí un correo válido.");
    setEnviando(true);
    const { error: err } = await supabase.auth.resetPasswordForEmail(correo.trim(), {
      // El enlace del correo vuelve a esta misma aplicación (hay que tenerla en las direcciones permitidas de Supabase).
      redirectTo: `${window.location.origin}/restablecer`,
    });
    setEnviando(false);
    if (err) {
      const m = mensajeDeRecuperacion(err);
      // "Correo desconocido" no existe como respuesta: no se revela si una cuenta existe (privacidad).
      if (m.tipo === "espera" || m.tipo === "red") return setError(m.texto);
    }
    setEnviado(true);
  }

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <h1 className="font-display text-3xl font-bold">Recuperar contraseña</h1>

      {!supabaseConfigurado && (
        <p role="alert" className="mt-6 flex items-start gap-2 rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          Falta la configuración de la aplicación. Ver <code>frontend/.env.example</code>.
        </p>
      )}

      {enviado ? (
        <div role="status" className="mt-6 rounded-md border border-border px-4 py-4 text-sm">
          <p className="flex items-start gap-2">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-neon" aria-hidden="true" />
            <span>
              Si <strong>{correo.trim()}</strong> tiene una cuenta, te enviamos un enlace para elegir una contraseña nueva. Revisá también
              la carpeta de spam o correo no deseado. El enlace dura poco tiempo.
            </span>
          </p>
          <p className="mt-4">
            <Link to="/ingreso" className="text-foreground underline underline-offset-4">Volver a ingresar</Link>
          </p>
        </div>
      ) : (
        <form onSubmit={enviar} className="mt-8 space-y-5" noValidate>
          <p className="text-sm text-muted-foreground">
            Escribí el correo con el que te registraste y te enviamos un enlace para elegir una contraseña nueva.
          </p>
          <div>
            <label htmlFor="correo" className="text-sm font-medium">Correo</label>
            <input id="correo" type="email" className={CAMPO} value={correo} onChange={(e) => setCorreo(e.target.value)} autoComplete="email" required />
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
            Enviarme el enlace
          </button>
          <p className="text-sm text-muted-foreground">
            <Link to="/ingreso" className="text-foreground underline underline-offset-4">Volver a ingresar</Link>
          </p>
        </form>
      )}
    </main>
  );
}
