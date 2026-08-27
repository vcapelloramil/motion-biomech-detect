import { createFileRoute } from "@tanstack/react-router";
import { Cpu, Waves, Eye, Layers, Gauge, Shield } from "lucide-react";

export const Route = createFileRoute("/tecnologia")({
  head: () => ({
    meta: [
      { title: "Tecnología — KinetiQ" },
      {
        name: "description",
        content:
          "Estimación de pose, filtrado de fase cero y auditoría por confianza: cómo se calcula cada número del reporte.",
      },
    ],
  }),
  component: TechPage,
});

function TechPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Tecnología</div>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">
        Del cuadro al número, <span className="text-gradient-neon">sin atajos</span>.
      </h1>
      <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
        El motor recibe un archivo de video y devuelve estructuras de datos: instantes de pico,
        ángulos y confianza por articulación. Todo lo que la interfaz muestra viene de ahí.
      </p>

      <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[
          {
            i: <Gauge />,
            t: "120 fps como piso",
            d: "El criterio de Nyquist-Shannon fija el mínimo. Por debajo de esa frecuencia, el instante del pico cae entre cuadros y no está en el archivo: no es un problema de nitidez.",
          },
          {
            i: <Eye />,
            t: "Estimación de pose",
            d: "MediaPipe Pose por defecto, con YOLOv8-Pose como alternativa detrás de la misma interfaz. La etapa es intercambiable sin tocar el resto del pipeline.",
          },
          {
            i: <Shield />,
            t: "Validación por confianza",
            d: "Cada landmark trae su puntaje. Por debajo del umbral, el tramo se marca como no auditable en vez de completarse con una estimación.",
          },
          {
            i: <Waves />,
            t: "Filtrado de fase cero",
            d: "Butterworth de 4º orden aplicado hacia adelante y hacia atrás. Un filtro unidireccional correría los picos en el tiempo, que es justamente lo que se mide.",
          },
          {
            i: <Layers />,
            t: "Capa cinemática",
            d: "Ángulos articulares, velocidades por segmento y orden de los picos. Sin rastreo de pelota, de raqueta ni de cancha.",
          },
          {
            i: <Cpu />,
            t: "Procesamiento asincrónico",
            d: "El video se procesa fuera de línea y el reporte queda disponible al terminar. No hay análisis en tiempo real.",
          },
        ].map((b) => (
          <div
            key={b.t}
            className="rounded-2xl border border-border bg-card p-6 transition-colors hover:border-neon/40"
          >
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-neon">
              {b.i}
            </div>
            <h3 className="mt-4 font-display text-lg font-semibold">{b.t}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{b.d}</p>
          </div>
        ))}
      </div>

      <div className="mt-12 rounded-3xl border border-border bg-card p-8">
        <h2 className="font-display text-2xl font-bold">Pipeline del motor</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          El filtrado va después de la elevación y antes de calcular velocidades. El orden importa.
        </p>
        <div className="mt-6 grid gap-3 md:grid-cols-3 lg:grid-cols-6">
          {[
            { id: "E0", s: "Ingesta", d: "FPS reales" },
            { id: "E1", s: "Pose", d: "Landmarks" },
            { id: "E1b", s: "Validación", d: "Confianza" },
            { id: "E3", s: "Filtrado", d: "Fase cero" },
            { id: "E4", s: "Cinemática", d: "Ángulos y picos" },
            { id: "E5", s: "Auditoría", d: "Estados y alertas" },
          ].map((e) => (
            <div key={e.id} className="rounded-xl border border-border bg-background p-4">
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                {e.id}
              </div>
              <div className="mt-1 font-display font-semibold">{e.s}</div>
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                {e.d}
              </div>
            </div>
          ))}
        </div>
        <p className="mt-6 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          Sello de versión del reporte · v0.1.0 · MediaPipe Pose · Butterworth 4º orden fase cero ·
          corte 8 Hz
        </p>
      </div>
    </main>
  );
}
