import { createFileRoute } from "@tanstack/react-router";
import { Cpu, Database, Eye, Layers, Scan, Shield } from "lucide-react";

export const Route = createFileRoute("/tecnologia")({
  head: () => ({
    meta: [
      { title: "Tecnología — KinetiQ" },
      { name: "description", content: "YOLO Pose, biomecánica y dataset propio anotado por profesionales." },
    ],
  }),
  component: TechPage,
});

function TechPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Tecnología</div>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Visión artificial <span className="text-gradient-neon">para tenis</span>, end-to-end.</h1>
      <p className="mt-4 max-w-2xl text-lg text-muted-foreground">Pipeline propio sobre modelos YOLO para detección de pose, raqueta y trayectoria de pelota — todo con la latencia más baja del mercado.</p>

      <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[
          { i: <Eye />, t: "YOLOv9-Pose", d: "Backbone con 17 keypoints corporales + 4 keypoints de raqueta. Fine-tuned en partidos reales." },
          { i: <Scan />, t: "Tracking temporal", d: "Suavizado Kalman + interpolación Bezier para movimientos fluidos a 30/60fps." },
          { i: <Layers />, t: "Capa biomecánica", d: "Cálculo de ángulos articulares, momentos angulares y velocidad de transferencia." },
          { i: <Cpu />, t: "Edge inference", d: "Procesamos en GPU optimizada. Latencia promedio: 18 ms por frame." },
          { i: <Database />, t: "Dataset propio", d: "120k+ frames anotados manualmente por entrenadores y kinesiólogos certificados." },
          { i: <Shield />, t: "Privacidad", d: "Tus videos son tuyos. Cifrado end-to-end. Eliminación bajo demanda. ISO 27001." },
        ].map((b) => (
          <div key={b.t} className="rounded-2xl border border-border bg-card p-6 transition-colors hover:border-neon/40">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-neon">{b.i}</div>
            <h3 className="mt-4 font-display text-lg font-semibold">{b.t}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{b.d}</p>
          </div>
        ))}
      </div>

      <div className="mt-12 rounded-3xl border border-border bg-card p-8">
        <h2 className="font-display text-2xl font-bold">Pipeline de visión</h2>
        <div className="mt-6 grid gap-3 md:grid-cols-5">
          {["Frame extract", "YOLO Pose", "Tracking", "Biomecánica", "Reporte dual"].map((s, i) => (
            <div key={s} className="rounded-xl border border-border bg-background p-4">
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Stage 0{i + 1}</div>
              <div className="mt-1 font-display font-semibold">{s}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
