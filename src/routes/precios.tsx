import { createFileRoute } from "@tanstack/react-router";
import { Check } from "lucide-react";

export const Route = createFileRoute("/precios")({
  head: () => ({
    meta: [
      { title: "Precios — KinetiQ" },
      { name: "description", content: "Planes para jugadores, entrenadores y clínicas deportivas." },
    ],
  }),
  component: PricingPage,
});

function PricingPage() {
  const plans = [
    { name: "Free", price: "0", desc: "Probá la plataforma", features: ["1 video / mes", "Performance básico", "Sin reporte clínico"], cta: "Empezar", highlight: false },
    { name: "Player", price: "12", desc: "Para jugadores serios", features: ["Videos ilimitados", "Performance + comparativa pro", "Reporte clínico básico", "Historial 12 meses"], cta: "Suscribirme", highlight: true },
    { name: "Clinic", price: "49", desc: "Coaches y kinesiólogos", features: ["Multi-jugador", "Reporte clínico completo + PDF", "Export DICOM/HL7", "API + integraciones"], cta: "Contactar", highlight: false },
  ];
  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <div className="text-center">
        <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Precios</div>
        <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Simple. <span className="text-gradient-neon">Sin sorpresas.</span></h1>
      </div>
      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {plans.map((p) => (
          <div key={p.name} className={`relative rounded-3xl border bg-card p-8 ${p.highlight ? "border-neon shadow-neon" : "border-border"}`}>
            {p.highlight && <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-neon px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-neon-foreground">Más elegido</div>}
            <div className="font-display text-xl font-semibold">{p.name}</div>
            <div className="text-sm text-muted-foreground">{p.desc}</div>
            <div className="mt-6 flex items-end gap-1">
              <span className="font-display text-5xl font-bold">${p.price}</span>
              <span className="pb-2 font-mono text-xs text-muted-foreground">/mes</span>
            </div>
            <ul className="mt-6 space-y-3 text-sm">
              {p.features.map((f) => (
                <li key={f} className="flex items-start gap-2"><Check className="mt-0.5 h-4 w-4 shrink-0 text-neon" />{f}</li>
              ))}
            </ul>
            <button className={`mt-8 w-full rounded-xl px-6 py-3 font-display font-semibold ${p.highlight ? "bg-gradient-neon text-neon-foreground shadow-neon" : "border border-border bg-background text-foreground hover:border-neon/40"}`}>
              {p.cta}
            </button>
          </div>
        ))}
      </div>
    </main>
  );
}
