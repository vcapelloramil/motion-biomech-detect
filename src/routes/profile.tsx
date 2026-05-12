import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, Crown, Settings, Bell, User, Calendar, MapPin, Trophy, Activity, Stethoscope } from "lucide-react";
import avatar from "@/assets/profile-avatar.jpg";

export const Route = createFileRoute("/profile")({
  head: () => ({
    meta: [
      { title: "Mi perfil — KinetiQ" },
      { name: "description", content: "Perfil del jugador, plan y configuración." },
    ],
  }),
  component: ProfilePage,
});

function ProfilePage() {
  const plans = [
    {
      name: "Free", price: "0", desc: "Probá la plataforma", current: false,
      features: ["1 video / mes", "Performance básico", "Sin reporte clínico"],
    },
    {
      name: "Player", price: "12", desc: "Para jugadores serios", current: true,
      features: ["Videos ilimitados", "Comparativa con jugadores ATP/WTA", "Reporte clínico básico", "Historial 12 meses"],
    },
    {
      name: "Clinic", price: "49", desc: "Coaches y kinesiólogos", current: false,
      features: ["Multi-jugador", "Reporte clínico completo + PDF", "Export DICOM/HL7", "API + integraciones"],
    },
  ];

  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Perfil</div>

      {/* HEADER */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-3xl border border-border bg-card p-8">
          <div className="flex flex-wrap items-center gap-6">
            <img src={avatar} alt="Marco Rivera" className="h-24 w-24 rounded-2xl object-cover ring-2 ring-neon/40" />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h1 className="font-display text-3xl font-bold">Marco Rivera</h1>
                <span className="inline-flex items-center gap-1 rounded-full bg-gradient-neon px-2 py-0.5 font-mono text-[10px] text-neon-foreground">
                  <Crown className="h-3 w-3" /> PLAYER
                </span>
              </div>
              <div className="mt-1 flex flex-wrap gap-4 font-mono text-xs text-muted-foreground">
                <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> Buenos Aires, AR</span>
                <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> Miembro desde Feb 2026</span>
                <span className="flex items-center gap-1"><Trophy className="h-3 w-3 text-neon" /> Nivel 4.5 NTRP</span>
              </div>
              <div className="mt-3 flex gap-2">
                <button className="rounded-md border border-border bg-background px-3 py-1.5 text-xs">Editar perfil</button>
                <button className="flex items-center gap-1 rounded-md border border-border bg-background px-3 py-1.5 text-xs">
                  <Stethoscope className="h-3 w-3 text-clinic" /> Invitar a kinesiólogo
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { k: "23", l: "Videos analizados" },
              { k: "1.449", l: "Golpes registrados" },
              { k: "82", l: "KinetiQ Score" },
              { k: "1", l: "Alertas activas" },
            ].map((s) => (
              <div key={s.l} className="rounded-xl border border-border bg-background p-4">
                <div className="font-display text-2xl font-bold text-gradient-neon">{s.k}</div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{s.l}</div>
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
              { i: <Stethoscope className="h-4 w-4" />, l: "Datos médicos" },
              { i: <Settings className="h-4 w-4" />, l: "Privacidad" },
            ].map((m) => (
              <li key={m.l} className="flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground hover:bg-secondary hover:text-foreground">
                {m.i}{m.l}
              </li>
            ))}
          </ul>
        </aside>
      </div>

      {/* SUBSCRIPTION */}
      <section className="mt-12">
        <div className="flex items-end justify-between">
          <div>
            <div className="font-mono text-xs uppercase tracking-widest text-neon">Suscripción</div>
            <h2 className="mt-2 font-display text-3xl font-bold md:text-4xl">Tu plan actual: <span className="text-gradient-neon">Player</span></h2>
            <p className="mt-2 text-muted-foreground">Próxima renovación: 12 de junio de 2026 · USD 12 / mes</p>
          </div>
          <button className="hidden rounded-md border border-border px-4 py-2 text-sm md:block">Gestionar pago</button>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {plans.map((p) => (
            <div key={p.name} className={`relative rounded-3xl border bg-card p-7 ${p.current ? "border-neon shadow-neon" : "border-border"}`}>
              {p.current && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-neon px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-neon-foreground">
                  Plan actual
                </div>
              )}
              <div className="font-display text-xl font-semibold">{p.name}</div>
              <div className="text-sm text-muted-foreground">{p.desc}</div>
              <div className="mt-5 flex items-end gap-1">
                <span className="font-display text-5xl font-bold">${p.price}</span>
                <span className="pb-2 font-mono text-xs text-muted-foreground">/mes</span>
              </div>
              <ul className="mt-5 space-y-2.5 text-sm">
                {p.features.map((f) => (
                  <li key={f} className="flex items-start gap-2"><Check className="mt-0.5 h-4 w-4 shrink-0 text-neon" />{f}</li>
                ))}
              </ul>
              <button
                disabled={p.current}
                className={`mt-7 w-full rounded-xl px-5 py-3 font-display font-semibold transition ${
                  p.current
                    ? "cursor-not-allowed border border-border bg-background text-muted-foreground"
                    : p.name === "Clinic"
                    ? "bg-gradient-clinic text-neon-foreground shadow-clinic"
                    : "bg-gradient-neon text-neon-foreground shadow-neon hover:scale-[1.02]"
                }`}
              >
                {p.current ? "Activo" : p.name === "Free" ? "Cambiar a Free" : `Upgrade a ${p.name}`}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* RECENT */}
      <section className="mt-12">
        <h2 className="font-display text-2xl font-bold">Actividad reciente</h2>
        <div className="mt-5 rounded-2xl border border-border bg-card divide-y divide-border">
          {[
            { i: <Activity className="h-4 w-4 text-neon" />, t: "Análisis de sparring · Drive cross", d: "Hoy · KinetiQ Score 82" },
            { i: <Stethoscope className="h-4 w-4 text-clinic" />, t: "Reporte clínico generado", d: "Hoy · Alerta moderada en hombro derecho" },
            { i: <Crown className="h-4 w-4 text-neon" />, t: "Plan Player renovado", d: "1 May 2026" },
            { i: <Activity className="h-4 w-4 text-neon" />, t: "Tanda de saques analizada", d: "8 May 2026 · KinetiQ Score 91" },
          ].map((a, i) => (
            <div key={i} className="flex items-center gap-4 px-5 py-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-background">{a.i}</div>
              <div className="flex-1">
                <div className="font-display text-sm font-semibold">{a.t}</div>
                <div className="font-mono text-[11px] text-muted-foreground">{a.d}</div>
              </div>
              <Link to="/videos" className="text-xs text-neon hover:underline">Ver</Link>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
