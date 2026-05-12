import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { UploadCloud, Film, Camera, Check, AlertCircle, Sparkles } from "lucide-react";

export const Route = createFileRoute("/upload")({
  head: () => ({
    meta: [
      { title: "Subir video — KinetiQ" },
      { name: "description", content: "Subí un video de tu sesión de tenis para análisis biomecánico." },
    ],
  }),
  component: UploadPage,
});

function UploadPage() {
  const [stage, setStage] = useState<"idle" | "uploading" | "processing" | "done">("idle");
  const [progress, setProgress] = useState(0);

  const start = () => {
    setStage("uploading");
    setProgress(0);
    const t = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(t);
          setStage("processing");
          setTimeout(() => setStage("done"), 2200);
          return 100;
        }
        return p + 7;
      });
    }, 180);
  };

  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Upload</div>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Subí tu sesión de <span className="text-gradient-neon">entrenamiento</span></h1>
      <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
        Aceptamos MP4, MOV y AVI hasta 4K · 30+ fps recomendado. La detección de pose YOLO se ejecuta automáticamente sobre cada frame.
      </p>

      <div className="mt-10 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          {stage === "idle" && (
            <button
              onClick={start}
              className="group flex w-full flex-col items-center justify-center gap-4 rounded-3xl border-2 border-dashed border-border bg-card p-16 transition-colors hover:border-neon/60"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-neon shadow-neon">
                <UploadCloud className="h-8 w-8 text-neon-foreground" />
              </div>
              <div className="text-center">
                <div className="font-display text-2xl font-bold">Arrastrá tu video o hacé clic</div>
                <div className="mt-1 font-mono text-xs text-muted-foreground">MP4 · MOV · AVI · máx. 2 GB</div>
              </div>
            </button>
          )}

          {(stage === "uploading" || stage === "processing") && (
            <div className="rounded-3xl border border-neon/40 bg-card p-10 shadow-neon">
              <div className="flex items-center gap-3">
                <Film className="h-5 w-5 text-neon" />
                <div className="font-display font-semibold">sesion-2026-05-12.mp4</div>
                <span className="ml-auto font-mono text-xs text-muted-foreground">412 MB</span>
              </div>
              <div className="mt-6">
                <div className="flex items-center justify-between font-mono text-xs">
                  <span className="text-muted-foreground">{stage === "uploading" ? "Subiendo" : "Procesando con YOLOv9-Pose"}</span>
                  <span className="text-neon">{stage === "uploading" ? `${progress}%` : "∞"}</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-secondary">
                  <div
                    className={`h-full ${stage === "processing" ? "animate-scan" : ""} bg-gradient-neon`}
                    style={{ width: stage === "uploading" ? `${progress}%` : "100%" }}
                  />
                </div>
              </div>
              <div className="mt-6 grid gap-2 font-mono text-xs">
                {[
                  { l: "Lectura de metadatos (FPS, resolución)", done: progress > 30 },
                  { l: "Detección de keypoints (17 joints)", done: stage === "processing" },
                  { l: "Filtro Kalman + suavizado", done: false },
                  { l: "Cálculo cinemático y reporte clínico", done: false },
                ].map((s) => (
                  <div key={s.l} className="flex items-center gap-2">
                    {s.done ? <Check className="h-3 w-3 text-neon" /> : <span className="h-3 w-3 rounded-full border border-border" />}
                    <span className={s.done ? "text-foreground" : "text-muted-foreground"}>{s.l}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {stage === "done" && (
            <div className="rounded-3xl border border-neon/40 bg-card p-10">
              <div className="flex items-center gap-3 text-neon">
                <Sparkles className="h-6 w-6" />
                <div className="font-display text-2xl font-bold">Análisis listo</div>
              </div>
              <p className="mt-2 text-muted-foreground">Detectamos 297 golpes en 4 sets. Encontramos 1 alerta clínica de riesgo moderado.</p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link to="/performance" className="rounded-xl bg-gradient-neon px-6 py-3 font-display font-semibold text-neon-foreground shadow-neon">
                  Ver performance
                </Link>
                <Link to="/clinica" className="rounded-xl bg-gradient-clinic px-6 py-3 font-display font-semibold text-neon-foreground shadow-clinic">
                  Ver reporte clínico
                </Link>
                <Link to="/videos" className="rounded-xl border border-border px-6 py-3 font-display font-semibold">
                  Mi biblioteca
                </Link>
              </div>
            </div>
          )}
        </div>

        <aside className="space-y-4">
          <div className="rounded-2xl border border-border bg-card p-5">
            <div className="flex items-center gap-2 text-neon">
              <Camera className="h-4 w-4" />
              <div className="font-display font-semibold">Cómo grabar</div>
            </div>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              <li>· Cámara fija en lateral o fondo</li>
              <li>· Altura ~1.5 m, trípode estable</li>
              <li>· Buena luz, sin contraluz</li>
              <li>· Cuerpo completo dentro del frame</li>
            </ul>
          </div>
          <div className="rounded-2xl border border-clinic/30 bg-card p-5">
            <div className="flex items-center gap-2 text-clinic">
              <AlertCircle className="h-4 w-4" />
              <div className="font-display font-semibold">Privacidad</div>
            </div>
            <p className="mt-3 text-sm text-muted-foreground">
              Tus videos se procesan en infraestructura cifrada. Solo vos y los profesionales que invites pueden verlos.
            </p>
          </div>
        </aside>
      </div>
    </main>
  );
}
