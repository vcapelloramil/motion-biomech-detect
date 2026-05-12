import { createFileRoute, Link } from "@tanstack/react-router";
import heroPose from "@/assets/player-hero.jpg";
import kineticChain from "@/assets/clinic-session.jpg";
import { Activity, Brain, HeartPulse, Target, Upload, Video, Zap, ScanLine, ArrowRight, Stethoscope, BarChart3 } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "KinetiQ — Análisis biomecánico de tenis con visión artificial" },
      { name: "description", content: "Plataforma con YOLO que analiza performance y salud articular en jugadores de tenis." },
      { property: "og:title", content: "KinetiQ — Tenis + IA + Biomecánica" },
      { property: "og:description", content: "Performance + análisis clínico de la cadena cinética desde un video." },
    ],
  }),
  component: Home,
});

function Home() {
  return (
    <main>
      {/* HERO */}
      <section className="relative overflow-hidden bg-hero-glow">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-6 py-20 lg:grid-cols-2 lg:py-28">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-neon/30 bg-neon/10 px-3 py-1 font-mono text-xs uppercase tracking-widest text-neon">
              <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-neon" />
              YOLO v9 · Pose Estimation · Tenis
            </div>
            <h1 className="mt-6 font-display text-5xl font-bold leading-[1.05] md:text-7xl">
              Tu juego y tu cuerpo, <span className="text-gradient-neon">decodificados</span>.
            </h1>
            <p className="mt-6 max-w-xl text-lg text-muted-foreground">
              KinetiQ analiza videos de tus partidos con visión artificial para mejorar tu <strong className="text-foreground">performance técnica</strong> y, además, evaluar tu <strong className="text-foreground">cadena cinética</strong> para prevenir lesiones.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/performance" className="group inline-flex items-center gap-2 rounded-xl bg-gradient-neon px-6 py-3 font-semibold text-neon-foreground shadow-neon transition-transform hover:scale-105">
                <Upload className="h-4 w-4" /> Subir un video
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link to="/clinica" className="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-6 py-3 font-semibold text-foreground hover:border-clinic">
                <Stethoscope className="h-4 w-4 text-clinic" /> Ver módulo clínico
              </Link>
            </div>
            <div className="mt-10 grid grid-cols-3 gap-6 border-t border-border pt-6">
              {[
                { k: "17", v: "Joints detectados" },
                { k: "30fps", v: "Análisis en tiempo real" },
                { k: "94%", v: "Precisión articular" },
              ].map((s) => (
                <div key={s.v}>
                  <div className="font-display text-3xl font-bold text-gradient-neon">{s.k}</div>
                  <div className="font-mono text-xs uppercase tracking-wider text-muted-foreground">{s.v}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="relative overflow-hidden rounded-3xl border border-border shadow-elevated">
              <img src={heroPose} alt="Análisis de pose en jugador de tenis" width={1536} height={1024} className="w-full" />
              <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
              <div className="pointer-events-none absolute inset-x-0 top-0 h-24 animate-scan bg-gradient-to-b from-neon/40 to-transparent" />
              {/* HUD */}
              <div className="absolute left-4 top-4 glass rounded-lg px-3 py-2 font-mono text-[10px]">
                <div className="text-muted-foreground">FRAME 0042 · POSE</div>
                <div className="text-neon">CONF 0.97</div>
              </div>
              <div className="absolute right-4 top-4 glass rounded-lg px-3 py-2 font-mono text-[10px]">
                <div className="text-muted-foreground">RACKET SPEED</div>
                <div className="text-neon">128 km/h</div>
              </div>
              <div className="absolute bottom-4 left-4 right-4 glass rounded-xl px-4 py-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Cadena cinética</div>
                    <div className="font-display text-sm font-semibold">Transferencia: pelvis → hombro · 92%</div>
                  </div>
                  <div className="font-mono text-xs text-clinic">★ Óptima</div>
                </div>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-secondary">
                  <div className="h-full w-[92%] bg-gradient-clinic" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TWO PILLARS */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 max-w-2xl">
          <div className="font-mono text-xs uppercase tracking-widest text-neon">Dos motores · una plataforma</div>
          <h2 className="mt-3 font-display text-4xl font-bold md:text-5xl">Performance <span className="text-muted-foreground">+</span> <span className="text-gradient-clinic">Salud articular</span></h2>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <PillarCard
            tag="Performance"
            color="neon"
            icon={<BarChart3 className="h-5 w-5" />}
            title="Mejorá tu técnica con datos reales"
            desc="Velocidad de raqueta, ángulo de golpe, posicionamiento, cobertura de cancha y heatmaps. Comparativas frame-a-frame con jugadores ATP/WTA."
            features={["Velocidad y rotación", "Cobertura y desplazamiento", "Comparativa pro", "Reporte por partido"]}
            cta="Ver análisis de performance"
            to="/performance"
          />
          <PillarCard
            tag="Clínico"
            color="clinic"
            icon={<HeartPulse className="h-5 w-5" />}
            title="Cuidá tu cuerpo: cadena cinética"
            desc="Detectamos compensaciones, asimetrías y patrones de riesgo articular usando keypoints YOLO + biomecánica. Reportes para vos y tu kinesiólogo."
            features={["Asimetrías hombro/cadera", "Riesgo de codo y hombro", "Carga articular acumulada", "Plan preventivo"]}
            cta="Explorar módulo clínico"
            to="/clinica"
          />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 text-center">
          <div className="font-mono text-xs uppercase tracking-widest text-neon">Pipeline</div>
          <h2 className="mt-3 font-display text-4xl font-bold md:text-5xl">De un video a un diagnóstico en <span className="text-gradient-neon">60 segundos</span></h2>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[
            { i: <Video />, t: "01 · Capturá", d: "Grabá con tu celular desde el fondo o el lateral. 30+ fps recomendado." },
            { i: <Upload />, t: "02 · Subí", d: "Drop del video en la app. Procesamos hasta 4K en la nube." },
            { i: <ScanLine />, t: "03 · Detectamos", d: "YOLO Pose extrae 17 keypoints por frame del cuerpo y la raqueta." },
            { i: <Brain />, t: "04 · Diagnóstico", d: "Reporte dual: performance + clínico, con plan accionable." },
          ].map((s, idx) => (
            <div key={s.t} className="relative rounded-2xl border border-border bg-card p-6 transition-colors hover:border-neon/50">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-neon">{s.i}</div>
              <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground">{s.t}</div>
              <div className="mt-2 font-display text-lg font-semibold">{s.d}</div>
              {idx < 3 && <div className="absolute -right-2 top-1/2 hidden h-px w-4 bg-border md:block" />}
            </div>
          ))}
        </div>
      </section>

      {/* CLINIC SHOWCASE */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="relative overflow-hidden rounded-3xl border border-clinic/30 bg-card shadow-clinic">
            <img src={kineticChain} alt="Visualización de la cadena cinética" width={1280} height={1280} loading="lazy" className="w-full" />
            <div className="absolute left-4 top-4 glass rounded-lg px-3 py-2 font-mono text-[10px]">
              <div className="text-muted-foreground">CADENA CINÉTICA</div>
              <div className="text-clinic">RUNTIME · ACTIVO</div>
            </div>
          </div>
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-clinic/40 bg-clinic/10 px-3 py-1 font-mono text-xs uppercase tracking-widest text-clinic">
              <Stethoscope className="h-3 w-3" /> Módulo Clínico · Beta
            </div>
            <h2 className="mt-6 font-display text-4xl font-bold md:text-5xl">El primer <span className="text-gradient-clinic">kinesiólogo</span> con ojos artificiales.</h2>
            <p className="mt-5 text-lg text-muted-foreground">
              Mientras vos pensás en ganar el punto, KinetiQ vigila tu cuerpo. Analizamos cómo se transfiere la energía desde el suelo hasta la raqueta, frame a frame.
            </p>
            <div className="mt-8 space-y-4">
              {[
                { i: <Target />, t: "Detección de asimetrías", d: "Compara hombro dominante vs no dominante, rotación de cadera y flexión de rodilla." },
                { i: <HeartPulse />, t: "Riesgo articular", d: "Estima carga sobre codo, hombro y zona lumbar según tu técnica." },
                { i: <Zap />, t: "Eficiencia kinética", d: "Mide cómo se acopla la cadena: piernas → core → tronco → brazo → muñeca." },
              ].map((f) => (
                <div key={f.t} className="flex gap-4 rounded-2xl border border-border bg-card p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-clinic/15 text-clinic">{f.i}</div>
                  <div>
                    <div className="font-display font-semibold">{f.t}</div>
                    <div className="text-sm text-muted-foreground">{f.d}</div>
                  </div>
                </div>
              ))}
            </div>
            <Link to="/clinica" className="mt-8 inline-flex items-center gap-2 rounded-xl bg-gradient-clinic px-6 py-3 font-semibold text-neon-foreground shadow-clinic">
              Ver reporte clínico de ejemplo <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* TECH STRIP */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="rounded-3xl border border-border bg-card p-10">
          <div className="grid items-center gap-10 lg:grid-cols-2">
            <div>
              <div className="font-mono text-xs uppercase tracking-widest text-neon">Tecnología</div>
              <h2 className="mt-3 font-display text-3xl font-bold md:text-4xl">Visión artificial entrenada en tenis real.</h2>
              <p className="mt-4 text-muted-foreground">Nuestro stack combina detección de pose YOLO con un dataset propio de +120k frames anotados por entrenadores y kinesiólogos profesionales.</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { k: "YOLOv9-Pose", v: "Backbone" },
                { k: "17 keypoints", v: "Por frame" },
                { k: "Edge GPU", v: "Procesamiento" },
                { k: "DICOM-ready", v: "Export clínico" },
              ].map((c) => (
                <div key={c.k} className="rounded-xl border border-border bg-background p-5">
                  <div className="font-display text-xl font-bold">{c.k}</div>
                  <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{c.v}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-4xl px-6 py-20 text-center">
        <Activity className="mx-auto h-10 w-10 text-neon" />
        <h2 className="mt-4 font-display text-4xl font-bold md:text-6xl">Empezá a entrenar con <span className="text-gradient-neon">visión real</span>.</h2>
        <p className="mt-4 text-lg text-muted-foreground">Gratis para tu primer video. Sin tarjeta. Resultados en menos de un minuto.</p>
        <Link to="/performance" className="mt-8 inline-flex items-center gap-2 rounded-xl bg-gradient-neon px-8 py-4 font-display text-lg font-semibold text-neon-foreground shadow-neon">
          Subir mi primer video <ArrowRight className="h-5 w-5" />
        </Link>
      </section>
    </main>
  );
}

function PillarCard({ tag, color, icon, title, desc, features, cta, to }: {
  tag: string; color: "neon" | "clinic"; icon: React.ReactNode; title: string; desc: string; features: string[]; cta: string; to: string;
}) {
  const isNeon = color === "neon";
  return (
    <div className={`group relative overflow-hidden rounded-3xl border bg-card p-8 transition-all hover:-translate-y-1 ${isNeon ? "border-neon/30 hover:shadow-neon" : "border-clinic/30 hover:shadow-clinic"}`}>
      <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full opacity-20 blur-3xl ${isNeon ? "bg-neon" : "bg-clinic"}`} />
      <div className="relative">
        <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 font-mono text-xs uppercase tracking-widest ${isNeon ? "border-neon/40 bg-neon/10 text-neon" : "border-clinic/40 bg-clinic/10 text-clinic"}`}>
          {icon} {tag}
        </div>
        <h3 className="mt-5 font-display text-2xl font-bold md:text-3xl">{title}</h3>
        <p className="mt-3 text-muted-foreground">{desc}</p>
        <ul className="mt-6 grid gap-2">
          {features.map((f) => (
            <li key={f} className="flex items-center gap-2 text-sm">
              <span className={`h-1.5 w-1.5 rounded-full ${isNeon ? "bg-neon" : "bg-clinic"}`} />
              {f}
            </li>
          ))}
        </ul>
        <Link to={to as string} className={`mt-8 inline-flex items-center gap-2 font-display font-semibold ${isNeon ? "text-neon" : "text-clinic"}`}>
          {cta} <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </Link>
      </div>
    </div>
  );
}
