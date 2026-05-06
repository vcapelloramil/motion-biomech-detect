import { createFileRoute } from "@tanstack/react-router";
import { Activity, TrendingUp, Target, Zap, MapPin } from "lucide-react";

export const Route = createFileRoute("/performance")({
  head: () => ({
    meta: [
      { title: "Performance — KinetiQ" },
      { name: "description", content: "Métricas de juego, comparativas con jugadores pro y reportes accionables." },
    ],
  }),
  component: PerformancePage,
});

function PerformancePage() {
  const shots = [
    { name: "Drive", count: 142, speed: 118, accuracy: 78, color: "neon" },
    { name: "Revés", count: 96, speed: 102, accuracy: 71, color: "neon" },
    { name: "Saque", count: 38, speed: 168, accuracy: 64, color: "clinic" },
    { name: "Volea", count: 21, speed: 88, accuracy: 82, color: "neon" },
  ] as const;

  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Performance</div>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Tu rendimiento, <span className="text-gradient-neon">medido</span>.</h1>
      <p className="mt-4 max-w-2xl text-lg text-muted-foreground">Cada golpe convertido en datos. Compará tu sesión con tu yo de la semana pasada o con un jugador top.</p>

      {/* SESSION OVERVIEW */}
      <div className="mt-10 grid gap-4 md:grid-cols-4">
        {[
          { i: <Activity />, k: "297", l: "Golpes detectados" },
          { i: <Zap />, k: "168 km/h", l: "Saque máximo" },
          { i: <Target />, k: "73%", l: "Precisión global" },
          { i: <TrendingUp />, k: "+8%", l: "vs. sesión previa" },
        ].map((s) => (
          <div key={s.l} className="rounded-2xl border border-border bg-card p-5">
            <div className="text-neon">{s.i}</div>
            <div className="mt-3 font-display text-3xl font-bold">{s.k}</div>
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{s.l}</div>
          </div>
        ))}
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-3">
        {/* SHOT BREAKDOWN */}
        <div className="rounded-2xl border border-border bg-card p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-xl font-semibold">Distribución de golpes</h3>
            <div className="font-mono text-xs text-muted-foreground">Sesión · 06 Mayo 2026</div>
          </div>
          <div className="mt-6 space-y-5">
            {shots.map((s) => (
              <div key={s.name}>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 rounded-full ${s.color === "neon" ? "bg-neon" : "bg-clinic"}`} />
                    <span className="font-display font-semibold">{s.name}</span>
                    <span className="font-mono text-xs text-muted-foreground">×{s.count}</span>
                  </div>
                  <div className="font-mono text-xs text-muted-foreground">{s.speed} km/h · {s.accuracy}% acc</div>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-secondary">
                  <div className={`h-full ${s.color === "neon" ? "bg-gradient-neon" : "bg-gradient-clinic"}`} style={{ width: `${s.accuracy}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* HEATMAP */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <h3 className="font-display text-xl font-semibold">Cobertura de cancha</h3>
          <div className="mt-4 aspect-[3/4] w-full rounded-xl border border-border bg-court/40 p-3">
            <div className="relative grid h-full w-full grid-cols-6 grid-rows-8 gap-px overflow-hidden rounded-lg bg-foreground/5">
              {Array.from({ length: 48 }).map((_, i) => {
                const heat = Math.random();
                return <div key={i} style={{ backgroundColor: `oklch(0.84 0.22 145 / ${heat * 0.7})` }} />;
              })}
              <div className="pointer-events-none absolute inset-x-0 top-1/2 h-px bg-foreground/40" />
            </div>
          </div>
          <div className="mt-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            <span>Bajo</span><MapPin className="h-3 w-3" /><span>Alto</span>
          </div>
        </div>
      </div>

      {/* COMPARISON */}
      <div className="mt-10 rounded-3xl border border-neon/30 bg-card p-8">
        <div className="font-mono text-xs uppercase tracking-widest text-neon">Comparativa Pro</div>
        <h3 className="mt-2 font-display text-2xl font-bold md:text-3xl">Tu drive vs. Carlos Alcaraz</h3>
        <div className="mt-6 grid gap-6 md:grid-cols-3">
          {[
            { k: "Velocidad raqueta", you: 118, pro: 145, unit: "km/h" },
            { k: "Ángulo de impacto", you: 27, pro: 32, unit: "°" },
            { k: "Rotación de cadera", you: 64, pro: 86, unit: "°" },
          ].map((c) => (
            <div key={c.k} className="rounded-xl border border-border bg-background p-5">
              <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground">{c.k}</div>
              <div className="mt-3 flex items-end gap-3">
                <div>
                  <div className="font-mono text-[10px] text-muted-foreground">VOS</div>
                  <div className="font-display text-2xl font-bold text-neon">{c.you}{c.unit}</div>
                </div>
                <div className="text-muted-foreground">vs</div>
                <div>
                  <div className="font-mono text-[10px] text-muted-foreground">PRO</div>
                  <div className="font-display text-2xl font-bold">{c.pro}{c.unit}</div>
                </div>
              </div>
              <div className="mt-3 h-1.5 rounded-full bg-secondary">
                <div className="h-full rounded-full bg-gradient-neon" style={{ width: `${(c.you / c.pro) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
