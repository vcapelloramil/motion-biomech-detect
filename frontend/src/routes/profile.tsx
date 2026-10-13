import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Settings,
  Bell,
  User,
  Calendar,
  MapPin,
  Trophy,
  Activity,
  Share2,
} from "lucide-react";
import avatar from "@/assets/profile-avatar.jpg";
import { RutaProtegida } from "@/components/ruta-protegida";
import { DatosDeEjemplo } from "@/components/datos-de-ejemplo";

export const Route = createFileRoute("/profile")({
  head: () => ({
    meta: [
      { title: "Mi perfil — KinetiQ" },
      { name: "description", content: "Perfil del jugador y configuración." },
    ],
  }),
  // Requiere sesión (especificación §3). La barrera real son RLS y la API; esto evita mostrar datos de ejemplo a un anónimo.
  component: () => (
    <RutaProtegida>
      <ProfilePage />
    </RutaProtegida>
  ),
});

function ProfilePage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <DatosDeEjemplo detalle="Tu perfil, los planes y los datos son una maqueta: todavía no se leen ni se guardan." />
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Perfil</div>

      {/* HEADER */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-3xl border border-border bg-card p-8">
          <div className="flex flex-wrap items-center gap-6">
            <img
              src={avatar}
              alt="Marco Rivera"
              className="h-24 w-24 rounded-2xl object-cover ring-2 ring-neon/40"
            />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h1 className="font-display text-3xl font-bold">Marco Rivera</h1>
              </div>
              <div className="mt-1 flex flex-wrap gap-4 font-mono text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> Buenos Aires, AR
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" /> Miembro desde Feb 2026
                </span>
                <span className="flex items-center gap-1">
                  <Trophy className="h-3 w-3 text-neon" /> Nivel 4.5 NTRP
                </span>
              </div>
              <div className="mt-3 flex gap-2">
                <button className="rounded-md border border-border bg-background px-3 py-1.5 text-xs">
                  Editar perfil
                </button>
                <button className="flex items-center gap-1 rounded-md border border-border bg-background px-3 py-1.5 text-xs">
                  <Share2 className="h-3 w-3 text-clinic" /> Compartir un reporte
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { k: "23", l: "Sesiones analizadas" },
              { k: "412", l: "Repeticiones medidas" },
              { k: "42°", l: "Separación cadera-hombro" },
              { k: "1", l: "Alerta de carga" },
            ].map((s) => (
              <div key={s.l} className="rounded-xl border border-border bg-background p-4">
                <div className="font-display text-2xl font-bold text-gradient-neon">{s.k}</div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  {s.l}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* MENU */}
        <aside className="rounded-3xl border border-border bg-card p-6">
          <div className="font-display font-semibold">Configuración</div>
          <ul className="mt-4 space-y-1 text-sm">
            {[
              { i: <User className="h-4 w-4" />, l: "Datos personales" },
              { i: <Bell className="h-4 w-4" />, l: "Notificaciones" },
              { i: <Activity className="h-4 w-4" />, l: "Métricas preferidas" },
              { i: <Share2 className="h-4 w-4" />, l: "Compartir con un profesional" },
              { i: <Settings className="h-4 w-4" />, l: "Privacidad" },
            ].map((m) => (
              <li
                key={m.l}
                className="flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground hover:bg-secondary hover:text-foreground"
              >
                {m.i}
                {m.l}
              </li>
            ))}
          </ul>
        </aside>
      </div>

      {/* RECENT */}
      <section className="mt-12">
        <h2 className="font-display text-2xl font-bold">Actividad reciente</h2>
        <div className="mt-5 rounded-2xl border border-border bg-card divide-y divide-border">
          {[
            {
              i: <Activity className="h-4 w-4 text-neon" />,
              t: "Tanda de saques plano · 6 repeticiones",
              d: "Hoy · cobertura auditable 4 de 6",
            },
            {
              i: <Activity className="h-4 w-4 text-clinic" />,
              t: "Reporte generado",
              d: "Hoy · 1 alerta de carga documentada en el saque 5",
            },
            {
              i: <Activity className="h-4 w-4 text-neon" />,
              t: "Drive cruzado con canasto · 24 repeticiones",
              d: "8 May 2026 · cobertura auditable 24 de 24",
            },
          ].map((a, i) => (
            <div key={i} className="flex items-center gap-4 px-5 py-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-background">
                {a.i}
              </div>
              <div className="flex-1">
                <div className="font-display text-sm font-semibold">{a.t}</div>
                <div className="font-mono text-[11px] text-muted-foreground">{a.d}</div>
              </div>
              <Link to="/videos" className="text-xs text-neon hover:underline">
                Ver
              </Link>
            </div>
          ))}
        </div>
      </section>

      <p className="mt-12 max-w-3xl text-xs text-muted-foreground">
        KinetiQ documenta el movimiento observado y entrega los valores medidos con su nivel de confianza. No es un producto sanitario ni
        reemplaza la evaluación de un profesional.
      </p>
    </main>
  );
}
