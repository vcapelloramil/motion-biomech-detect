import { useState, type FormEvent } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { getSupabase, supabaseConfigurado } from "@/lib/supabase";
import { LARGO_MINIMO_CONTRASENA, contrasenaValida, mensajeDeRestablecer } from "@/lib/auth-errores";
import { useSesion } from "@/lib/sesion";

export const Route = createFileRoute("/restablecer")({
  head: () => ({
    meta: [
      { title: "Elegir una contraseña nueva — KinetiQ" },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: RestablecerPage,
});

const CAMPO =
  "mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring";

/**
 * Destino del enlace del correo "Recuperar contraseña". El cliente de Supabase lee la sesión de recuperación de la dirección
 * (`detectSessionInUrl`), así que acá basta con que haya sesión para poder elegir la contraseña nueva. Sin sesión: el enlace
 * venció, ya se usó o se entró a esta página sin pasar por el correo.
 */
function RestablecerPage() {
  const { sesion, cargando } = useSesion();
  const [clave, setClave] = useState("");
  const [repeticion, setRepeticion] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listo, setListo] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const supabase = getSupabase();
    if (!supabase) return;
    if (!contrasenaValida(clave)) {
      return setError(`Usá al menos ${LARGO_MINIMO_CONTRASENA} caracteres, con letras y números.`);
    }
    if (clave !== repeticion) return setError("Las dos contraseñas no coinciden.");
    setEnviando(true);
    const { error: err } = await supabase.auth.updateUser({ password: clave });
    setEnviando(false);
    if (err) return setError(mensajeDeRestablecer(err).texto);
    setListo(true);
  }

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <h1 className="font-display text-3xl font-bold">Elegir una contraseña nueva</h1>

      {cargando ? (
        <p role="status" className="mt-6 flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Verificando el enlace…
        </p>
      ) : listo ? (
        <div role="status" className="mt-6 rounded-md border border-border px-4 py-4 text-sm">
          <p className="flex items-start gap-2">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-neon" aria-hidden="true" />
            Listo: tu contraseña quedó cambiada.
          </p>
          <p className="mt-4">
            <Link to="/videos" className="text-foreground underline underline-offset-4">Ir a mi biblioteca</Link>
          </p>
        </div>
      ) : !sesion ? (
        <div role="alert" className="mt-6 rounded-md border border-border px-4 py-4 text-sm">
          <p className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-state-warn" aria-hidden="true" />
            Este enlace venció, ya se usó o no es válido. Pedí uno nuevo.
          </p>
          <p className="mt-4">
            <Link to="/recuperar" className="text-foreground underline underline-offset-4">Pedir un enlace nuevo</Link>
          </p>
        </div>
      ) : (
        <form onSubmit={enviar} className="mt-8 space-y-5" noValidate>
          <div>
            <label htmlFor="clave" className="text-sm font-medium">Contraseña nueva</label>
            <input id="clave" type="password" className={CAMPO} value={clave} onChange={(e) => setClave(e.target.value)} autoComplete="new-password" required />
            <p className="mt-1 text-xs text-muted-foreground">Al menos {LARGO_MINIMO_CONTRASENA} caracteres, con letras y números.</p>
          </div>
          <div>
            <label htmlFor="repeticion" className="text-sm font-medium">Repetí la contraseña</label>
            <input id="repeticion" type="password" className={CAMPO} value={repeticion} onChange={(e) => setRepeticion(e.target.value)} autoComplete="new-password" required />
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
            Cambiar la contraseña
          </button>
        </form>
      )}
    </main>
  );
}
