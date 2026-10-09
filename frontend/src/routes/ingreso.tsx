import { useEffect, useState, type FormEvent } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { getSupabase, supabaseConfigurado } from "@/lib/supabase";
import { mensajeDeIngreso } from "@/lib/auth-errores";
import { useSesion } from "@/lib/sesion";

export const Route = createFileRoute("/ingreso")({
  // `?confirmado=1` lo agrega el enlace del correo de confirmación (ver registro.tsx).
  validateSearch: (search: Record<string, unknown>): { confirmado?: boolean } => ({
    confirmado: search.confirmado === "1" || search.confirmado === 1 || search.confirmado === true ? true : undefined,
  }),
  head: () => ({
    meta: [
      { title: "Ingresar — KinetiQ" },
      { name: "description", content: "Ingresá a tu cuenta para cargar videos y ver tus reportes." },
    ],
  }),
  component: IngresoPage,
});

const CAMPO =
  "mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring";

function IngresoPage() {
  const { confirmado } = Route.useSearch();
  const { sesion, cargando } = useSesion();
  const navegar = useNavigate();
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<{ texto: string; sinConfirmar: boolean } | null>(null);
  const [reenvio, setReenvio] = useState<string | null>(null);

  // Con sesión (recién ingresada, o la que dejó el enlace de confirmación) se va a la biblioteca.
  useEffect(() => {
    if (!cargando && sesion) navegar({ to: "/videos" });
  }, [cargando, sesion, navegar]);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setReenvio(null);
    const supabase = getSupabase();
    if (!supabase) return;
    setEnviando(true);
    const { error: err } = await supabase.auth.signInWithPassword({ email: correo.trim(), password: contrasena });
    setEnviando(false);
    if (err) {
      const m = mensajeDeIngreso(err);
      setError({ texto: m.texto, sinConfirmar: m.tipo === "correo-sin-confirmar" });
    }
    // Si salió bien, onAuthStateChange actualiza la sesión y el efecto de arriba navega.
  }

  async function reenviar() {
    const supabase = getSupabase();
    if (!supabase || !correo.trim()) return setReenvio("Escribí tu correo arriba y volvé a tocar.");
    const { error: err } = await supabase.auth.resend({
      type: "signup",
      email: correo.trim(),
      options: { emailRedirectTo: `${window.location.origin}/ingreso?confirmado=1` },
    });
    setReenvio(err ? "No pudimos reenviarlo ahora. Probá en unos minutos." : "Listo, te lo enviamos de nuevo. Revisá también el spam.");
  }

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <h1 className="font-display text-3xl font-bold">Ingresar</h1>

      {confirmado && (
        <p role="status" className="mt-4 flex items-start gap-2 rounded-md border border-border px-3 py-2 text-sm">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-neon" aria-hidden="true" />
          Tu correo quedó confirmado. Ya podés ingresar.
        </p>
      )}

      {!supabaseConfigurado && (
        <p role="alert" className="mt-6 flex items-start gap-2 rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <span>
            Falta la configuración de la aplicación (<code>VITE_SUPABASE_URL</code> y <code>VITE_SUPABASE_ANON_KEY</code>).
            Ver <code>frontend/.env.example</code>.
          </span>
        </p>
      )}

      <form onSubmit={enviar} className="mt-8 space-y-5" noValidate>
        <div>
          <label htmlFor="correo" className="text-sm font-medium">Correo</label>
          <input id="correo" type="email" className={CAMPO} value={correo} onChange={(e) => setCorreo(e.target.value)} autoComplete="email" required />
        </div>
        <div>
          <label htmlFor="contrasena" className="text-sm font-medium">Contraseña</label>
          <input id="contrasena" type="password" className={CAMPO} value={contrasena} onChange={(e) => setContrasena(e.target.value)} autoComplete="current-password" required />
        </div>

        {error && (
          <div role="alert" className="rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
            <p className="flex items-start gap-2">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              {error.texto}
            </p>
            {error.sinConfirmar && (
              <button type="button" onClick={reenviar} className="mt-2 text-foreground underline underline-offset-4">
                Reenviar el correo de confirmación
              </button>
            )}
          </div>
        )}
        {reenvio && <p role="status" className="text-sm text-muted-foreground">{reenvio}</p>}

        <button
          type="submit"
          disabled={enviando || !supabaseConfigurado}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-gradient-neon px-4 py-2.5 text-sm font-semibold text-neon-foreground shadow-neon disabled:opacity-60"
        >
          {enviando && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
          Ingresar
        </button>
      </form>

      <p className="mt-6 text-sm text-muted-foreground">
        ¿Todavía no tenés cuenta?{" "}
        <Link to="/registro" className="text-foreground underline underline-offset-4">Crear cuenta</Link>
      </p>
    </main>
  );
}
