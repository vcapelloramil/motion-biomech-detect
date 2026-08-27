import { createFileRoute, Link } from "@tanstack/react-router";
import heroPose from "@/assets/player-hero.jpg";
import kineticChain from "@/assets/clinic-session.jpg";
import {
  Activity,
  Gauge,
  CircleSlash,
  Ruler,
  Upload,
  Video,
  Timer,
  ScanLine,
  ArrowRight,
  BarChart3,
  FileText,
} from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "KinetiQ — Análisis biomecánico de tenis con visión artificial" },
      {
        name: "description",
        content:
          "Documenta el orden en que pelvis, torso y brazo alcanzan su velocidad máxima en el saque, el drive y el revés, a partir de un video de entrenamiento.",
      },
      { property: "og:title", content: "KinetiQ — Secuenciación de la cadena cinética" },
      {
        property: "og:description",
        content:
          "Del video al reporte: orden de los picos de velocidad, ángulos medidos y trazabilidad del cálculo.",
      },
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
              MediaPipe Pose · Cadena cinética · Tenis
            </div>
            <h1 className="mt-6 font-display text-5xl font-bold leading-[1.05] md:text-7xl">
              Tu gesto, cuadro por cuadro, <span className="text-gradient-neon">documentado</span>.
            </h1>
            <p className="mt-6 max-w-xl text-lg text-muted-foreground">
              KinetiQ procesa videos de entrenamiento y documenta el{" "}
              <strong className="text-foreground">orden temporal</strong> en que pelvis, torso y
              brazo alcanzan su velocidad máxima, junto con los{" "}
              <strong className="text-foreground">ángulos articulares</strong> del gesto.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/upload"
                className="group inline-flex items-center gap-2 rounded-xl bg-gradient-neon px-6 py-3 font-semibold text-neon-foreground shadow-neon transition-transform hover:scale-105"
              >
                <Upload className="h-4 w-4" /> Cargar un video
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                to="/reporte"
                className="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-6 py-3 font-semibold text-foreground hover:border-clinic"
              >
                <FileText className="h-4 w-4 text-clinic" /> Ver un reporte de ejemplo
              </Link>
            </div>
            <div className="mt-10 grid grid-cols-3 gap-6 border-t border-border pt-6">
              {[
                { k: "120 fps", v: "Frecuencia mínima" },
                { k: "3", v: "Gestos: saque, drive, revés" },
                { k: "4", v: "Estados, incluido no auditable" },
              ].map((s) => (
                <div key={s.v}>
                  <div className="font-display text-3xl font-bold text-gradient-neon">{s.k}</div>
                  <div className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                    {s.v}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="relative overflow-hidden rounded-3xl border border-border shadow-elevated">
              <img
                src={heroPose}
                alt="Análisis de pose en jugador de tenis"
                width={1536}
                height={1024}
                className="w-full"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
              <div className="pointer-events-none absolute inset-x-0 top-0 h-24 animate-scan bg-gradient-to-b from-neon/40 to-transparent" />
              {/* HUD */}
              <div className="absolute left-4 top-4 glass rounded-lg px-3 py-2 font-mono text-[10px]">
                <div className="text-muted-foreground">CUADRO 0042 · POSE</div>
                <div className="text-neon">CONF 0.97</div>
              </div>
              <div className="absolute right-4 top-4 glass rounded-lg px-3 py-2 font-mono text-[10px]">
                <div className="text-muted-foreground">PICO PELVIS</div>
                <div className="text-neon">0,42 s</div>
              </div>
              <div className="absolute bottom-4 left-4 right-4 glass rounded-xl px-4 py-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                      Orden observado
                    </div>
                    <div className="font-display text-sm font-semibold">pelvis → torso → brazo</div>
                  </div>
                  <div className="font-mono text-xs text-state-ok">✓ Coincide</div>
                </div>
                <div className="mt-2 font-mono text-[10px] text-muted-foreground">
                  Orden esperado: pelvis → torso → brazo
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ALCANCE DECLARADO */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 max-w-2xl">
          <div className="font-mono text-xs uppercase tracking-widest text-neon">
            Alcance declarado
          </div>
          <h2 className="mt-3 font-display text-4xl font-bold md:text-5xl">
            Lo que mide <span className="text-muted-foreground">y</span>{" "}
            <span className="text-gradient-clinic">lo que no</span>
          </h2>
          <p className="mt-3 text-muted-foreground">
            El límite está escrito en la interfaz, no en la letra chica.
          </p>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <PillarCard
            tag="Dentro del alcance"
            color="neon"
            icon={<BarChart3 className="h-5 w-5" />}
            title="Lo que el sistema documenta"
            desc="Sobre videos de entrenamiento de un solo jugador, grabados a 120 fps o más, en saque, drive y revés."
            features={[
              "Orden de los picos de velocidad: pelvis, torso, brazo",
              "Separación cadera-hombro y ángulos articulares",
              "Comparación del jugador consigo mismo entre sesiones",
              "Confianza por articulación y estado no auditable explícito",
            ]}
            cta="Ver un reporte de ejemplo"
            to="/reporte"
          />
          <PillarCard
            tag="Fuera del alcance"
            color="clinic"
            icon={<CircleSlash className="h-5 w-5" />}
            title="Lo que el sistema no hace"
            desc="No porque falte desarrollarlo, sino porque requeriría medir cosas que este trabajo no mide."
            features={[
              "Velocidad de la pelota, precisión de tiro y ubicación en cancha",
              "Partidos completos, voleas y varios jugadores en cuadro",
              "Análisis en tiempo real y comparativas contra jugadores profesionales",
              "Exportación a formatos médicos y conclusiones clínicas",
            ]}
            cta="Cómo grabar correctamente"
            to="/upload"
          />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 text-center">
          <div className="font-mono text-xs uppercase tracking-widest text-neon">Pipeline</div>
          <h2 className="mt-3 font-display text-4xl font-bold md:text-5xl">
            De un video a un <span className="text-gradient-neon">reporte trazable</span>
          </h2>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[
            {
              i: <Video />,
              t: "01 · Capturá",
              d: "Modo cámara lenta, trípode y cuerpo completo. 120 fps mínimo, 240 recomendado.",
            },
            {
              i: <Upload />,
              t: "02 · Cargá",
              d: "Se verifica la frecuencia real del archivo antes de procesar nada.",
            },
            {
              i: <ScanLine />,
              t: "03 · Se procesa",
              d: "Landmarks por cuadro, validación por confianza y filtrado de fase cero.",
            },
            {
              i: <FileText />,
              t: "04 · Reporte",
              d: "Veredicto en tres observaciones, evidencia y fundamento de cada número.",
            },
          ].map((s, idx) => (
            <div
              key={s.t}
              className="relative rounded-2xl border border-border bg-card p-6 transition-colors hover:border-neon/50"
            >
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-neon">
                {s.i}
              </div>
              <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
                {s.t}
              </div>
              <div className="mt-2 font-display text-lg font-semibold">{s.d}</div>
              {idx < 3 && (
                <div className="absolute -right-2 top-1/2 hidden h-px w-4 bg-border md:block" />
              )}
            </div>
          ))}
        </div>
        <p className="mt-6 text-center text-sm text-muted-foreground">
          El procesamiento es asincrónico: se avisa cuando el reporte está listo.
        </p>
      </section>

      {/* SHOWCASE */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="relative overflow-hidden rounded-3xl border border-clinic/30 bg-card shadow-clinic">
            <img
              src={kineticChain}
              alt="Visualización de la cadena cinética"
              width={1280}
              height={1280}
              loading="lazy"
              className="w-full"
            />
            <div className="absolute left-4 top-4 glass rounded-lg px-3 py-2 font-mono text-[10px]">
              <div className="text-muted-foreground">CADENA CINÉTICA</div>
              <div className="text-clinic">PELVIS → TORSO → BRAZO</div>
            </div>
          </div>
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-clinic/40 bg-clinic/10 px-3 py-1 font-mono text-xs uppercase tracking-widest text-clinic">
              <Activity className="h-3 w-3" /> Secuenciación
            </div>
            <h2 className="mt-6 font-display text-4xl font-bold md:text-5xl">
              El dato que el ojo <span className="text-gradient-clinic">no alcanza a ver</span>.
            </h2>
            <p className="mt-5 text-lg text-muted-foreground">
              Entre el pico de velocidad de la pelvis y el del brazo pasan unos 160 milisegundos. A
              esa escala, el orden en que se encadenan los segmentos no se juzga a ojo: se mide, o
              no se mide.
            </p>
            <div className="mt-8 space-y-4">
              {[
                {
                  i: <Timer />,
                  t: "Orden de los picos",
                  d: "El instante en que cada segmento alcanza su velocidad máxima, sobre un eje temporal único.",
                },
                {
                  i: <Ruler />,
                  t: "Magnitudes con unidad",
                  d: "Separación cadera-hombro, flexión de rodilla y ángulo de tronco, cada una con su confianza.",
                },
                {
                  i: <CircleSlash />,
                  t: "Lo que no se pudo medir",
                  d: "Cuando la confianza cae bajo el umbral, el reporte lo dice. No se rellena el hueco con una estimación.",
                },
              ].map((f) => (
                <div key={f.t} className="flex gap-4 rounded-2xl border border-border bg-card p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-clinic/15 text-clinic">
                    {f.i}
                  </div>
                  <div>
                    <div className="font-display font-semibold">{f.t}</div>
                    <div className="text-sm text-muted-foreground">{f.d}</div>
                  </div>
                </div>
              ))}
            </div>
            <Link
              to="/reporte"
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-gradient-clinic px-6 py-3 font-semibold text-neon-foreground shadow-clinic"
            >
              Ver reporte de ejemplo <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* TECH STRIP */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="rounded-3xl border border-border bg-card p-10">
          <div className="grid items-center gap-10 lg:grid-cols-2">
            <div>
              <div className="font-mono text-xs uppercase tracking-widest text-neon">
                Tecnología
              </div>
              <h2 className="mt-3 font-display text-3xl font-bold md:text-4xl">
                Cada número sabe de dónde viene.
              </h2>
              <p className="mt-4 text-muted-foreground">
                Todo reporte lleva la versión del motor, el backend de estimación de pose y los
                parámetros de filtrado con los que se calculó. Sin eso, un número en pantalla es una
                opinión.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { k: "MediaPipe Pose", v: "Estimación de pose" },
                { k: "Butterworth", v: "Filtrado de fase cero" },
                { k: "120 fps", v: "Frecuencia mínima" },
                { k: "4 estados", v: "Incluye no auditable" },
              ].map((c) => (
                <div key={c.k} className="rounded-xl border border-border bg-background p-5">
                  <div className="font-display text-xl font-bold">{c.k}</div>
                  <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    {c.v}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-4xl px-6 py-20 text-center">
        <Gauge className="mx-auto h-10 w-10 text-neon" />
        <h2 className="mt-4 font-display text-4xl font-bold md:text-6xl">
          Empezá por el <span className="text-gradient-neon">video correcto</span>.
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Antes de procesar nada, KinetiQ verifica que el archivo tenga la frecuencia de captura
          necesaria.
        </p>
        <Link
          to="/upload"
          className="mt-8 inline-flex items-center gap-2 rounded-xl bg-gradient-neon px-8 py-4 font-display text-lg font-semibold text-neon-foreground shadow-neon"
        >
          Cargar mi primer video <ArrowRight className="h-5 w-5" />
        </Link>
      </section>
    </main>
  );
}

function PillarCard({
  tag,
  color,
  icon,
  title,
  desc,
  features,
  cta,
  to,
}: {
  tag: string;
  color: "neon" | "clinic";
  icon: React.ReactNode;
  title: string;
  desc: string;
  features: string[];
  cta: string;
  to: string;
}) {
  const isNeon = color === "neon";
  return (
    <div
      className={`group relative overflow-hidden rounded-3xl border bg-card p-8 transition-all hover:-translate-y-1 ${isNeon ? "border-neon/30 hover:shadow-neon" : "border-clinic/30 hover:shadow-clinic"}`}
    >
      <div
        className={`absolute -right-20 -top-20 h-64 w-64 rounded-full opacity-20 blur-3xl ${isNeon ? "bg-neon" : "bg-clinic"}`}
      />
      <div className="relative">
        <div
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 font-mono text-xs uppercase tracking-widest ${isNeon ? "border-neon/40 bg-neon/10 text-neon" : "border-clinic/40 bg-clinic/10 text-clinic"}`}
        >
          {icon} {tag}
        </div>
        <h3 className="mt-5 font-display text-2xl font-bold md:text-3xl">{title}</h3>
        <p className="mt-3 text-muted-foreground">{desc}</p>
        <ul className="mt-6 grid gap-2">
          {features.map((f) => (
            <li key={f} className="flex items-start gap-2 text-sm">
              <span
                className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${isNeon ? "bg-neon" : "bg-clinic"}`}
              />
              {f}
            </li>
          ))}
        </ul>
        <Link
          to={to as string}
          className={`mt-8 inline-flex items-center gap-2 font-display font-semibold ${isNeon ? "text-neon" : "text-clinic"}`}
        >
          {cta} <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </Link>
      </div>
    </div>
  );
}
