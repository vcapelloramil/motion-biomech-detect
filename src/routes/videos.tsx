import { createFileRoute, Link } from "@tanstack/react-router";
import { Play, Calendar, Activity, AlertTriangle, Filter, Search } from "lucide-react";
import t1 from "@/assets/video-thumb-1.jpg";
import t2 from "@/assets/video-thumb-2.jpg";
import t3 from "@/assets/video-thumb-3.jpg";

export const Route = createFileRoute("/videos")({
  head: () => ({
    meta: [
      { title: "Mis videos — KinetiQ" },
      { name: "description", content: "Biblioteca de sesiones analizadas con visión artificial." },
    ],
  }),
  component: VideosPage,
});

function VideosPage() {
  const videos = [
    { thumb: t1, title: "Sparring · Drive cross", date: "12 May 2026", duration: "42:18", shots: 297, risk: "moderado", surface: "Hard", score: 82 },
    { thumb: t2, title: "Tanda de saques", date: "08 May 2026", duration: "18:04", shots: 86, risk: "bajo", surface: "Hard", score: 91 },
    { thumb: t3, title: "Partido amistoso · 3 sets", date: "01 May 2026", duration: "1:12:33", shots: 412, risk: "alto", surface: "Polvo", score: 74 },
    { thumb: t1, title: "Drill · Revés a una mano", date: "26 Abr 2026", duration: "27:51", shots: 188, risk: "bajo", surface: "Hard", score: 85 },
    { thumb: t2, title: "Saque + volea", date: "19 Abr 2026", duration: "33:40", shots: 142, risk: "moderado", surface: "Carpet", score: 79 },
    { thumb: t3, title: "Partido club · 2 sets", date: "12 Abr 2026", duration: "55:21", shots: 324, risk: "bajo", surface: "Polvo", score: 88 },
  ];

  const riskColor = { bajo: "text-court border-court/40", moderado: "text-clinic border-clinic/40", alto: "text-destructive border-destructive/40" } as const;

  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Biblioteca</div>
          <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Tus <span className="text-gradient-neon">sesiones</span></h1>
          <p className="mt-3 text-muted-foreground">6 videos analizados · 1.449 golpes detectados · 4 alertas clínicas</p>
        </div>
        <Link to="/upload" className="rounded-xl bg-gradient-neon px-5 py-3 font-display font-semibold text-neon-foreground shadow-neon">
          + Nuevo video
        </Link>
      </div>

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input placeholder="Buscar por título, fecha o tipo de golpe…" className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground" />
        </div>
        <button className="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm">
          <Filter className="h-4 w-4" /> Filtros
        </button>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {videos.map((v, i) => (
          <Link key={i} to="/performance" className="group overflow-hidden rounded-2xl border border-border bg-card transition-all hover:-translate-y-1 hover:border-neon/50 hover:shadow-neon">
            <div className="relative aspect-video overflow-hidden">
              <img src={v.thumb} alt={v.title} loading="lazy" className="h-full w-full object-cover transition-transform group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-background/10 to-transparent" />
              <div className="absolute left-3 top-3 flex items-center gap-1 rounded-md bg-background/80 px-2 py-1 font-mono text-[10px] backdrop-blur">
                <span className="h-1.5 w-1.5 rounded-full bg-neon" /> POSE OK
              </div>
              <div className="absolute right-3 top-3 rounded-md bg-background/80 px-2 py-1 font-mono text-[10px] backdrop-blur">{v.duration}</div>
              <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-neon shadow-neon transition-transform group-hover:scale-110">
                  <Play className="h-4 w-4 text-neon-foreground" fill="currentColor" />
                </div>
                <div className="rounded-md bg-background/80 px-2 py-1 font-mono text-[10px] backdrop-blur">{v.surface}</div>
              </div>
            </div>
            <div className="p-4">
              <div className="font-display font-semibold">{v.title}</div>
              <div className="mt-1 flex items-center gap-3 font-mono text-[11px] text-muted-foreground">
                <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{v.date}</span>
                <span className="flex items-center gap-1"><Activity className="h-3 w-3" />{v.shots} golpes</span>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <div>
                  <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">KinetiQ Score</div>
                  <div className="font-display text-2xl font-bold text-gradient-neon">{v.score}</div>
                </div>
                <div className={`flex items-center gap-1 rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase ${riskColor[v.risk as keyof typeof riskColor]}`}>
                  <AlertTriangle className="h-3 w-3" /> {v.risk}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
}
