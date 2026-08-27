import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import {
  UploadCloud,
  Film,
  Camera,
  Check,
  Gauge,
  Loader2,
  RotateCcw,
  ArrowRight,
  FlaskConical,
} from "lucide-react";
import { EstadoBadge, ESTADOS, type Estado } from "@/components/estado";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

/**
 * Parametros de captura de pantalla. Permiten dejar la pantalla en un estado
 * concreto sin tocar el panel de demostracion, para que no aparezca en la imagen:
 *   /upload?fps=60&paso=verificado&demo=false
 */
interface BusquedaUpload {
  fps?: 240 | 120 | 60;
  paso?: "verificado";
  demo?: false;
}

export const Route = createFileRoute("/upload")({
  validateSearch: (busqueda: Record<string, unknown>): BusquedaUpload => ({
    fps:
      Number(busqueda.fps) === 60
        ? 60
        : Number(busqueda.fps) === 120
          ? 120
          : Number(busqueda.fps) === 240
            ? 240
            : undefined,
    paso: busqueda.paso === "verificado" ? "verificado" : undefined,
    demo: busqueda.demo === false ? false : undefined,
  }),
  head: () => ({
    meta: [
      { title: "Cargar video — KinetiQ" },
      {
        name: "description",
        content: "Requisitos de captura y verificación de frecuencia de cuadro antes del análisis.",
      },
    ],
  }),
  component: UploadPage,
});

/**
 * R1 del CLAUDE.md — Nyquist-Shannon: por debajo de 120 fps la información del
 * gesto rápido no está "borrosa", está perdida, y ningún filtro la recupera.
 * Por eso la verificación de FPS es el elemento protagónico de esta pantalla.
 */
type Fps = 240 | 120 | 60;

const PERFILES: Record<
  Fps,
  {
    estado: Estado;
    titulo: string;
    detalle: string;
    cobertura: string;
    requiereConfirmacion: boolean;
  }
> = {
  240: {
    estado: "correcto",
    titulo: "Video apto para análisis completo.",
    detalle:
      "La frecuencia de captura permite medir todo el gesto, incluido el instante de impacto.",
    cobertura: "Preparación · aceleración · impacto",
    requiereConfirmacion: false,
  },
  120: {
    estado: "correcto",
    titulo: "Video apto. Para el impacto se recomiendan 240 fps.",
    detalle:
      "Alcanza para medir la secuencia de picos de velocidad. El instante de impacto se resuelve con menos precisión temporal.",
    cobertura: "Preparación · aceleración · impacto (precisión reducida)",
    requiereConfirmacion: false,
  },
  60: {
    estado: "desvio",
    titulo: "Solo se podrá auditar la fase de preparación.",
    detalle: "El gesto rápido no es medible a esta frecuencia de captura.",
    cobertura: "Preparación",
    requiereConfirmacion: true,
  },
};

/** Pipeline real del motor (sección 4 del CLAUDE.md). Se muestra la etapa en curso, no solo un porcentaje. */
const ETAPAS = [
  { id: "E0", label: "Ingesta", detalle: "Lectura del archivo y de los FPS reales" },
  { id: "E1", label: "Detección de pose", detalle: "MediaPipe Pose · landmarks por cuadro" },
  { id: "E1b", label: "Validación", detalle: "Descarte de landmarks bajo el umbral de confianza" },
  { id: "E3", label: "Filtrado", detalle: "Butterworth 4º orden, fase cero · corte 8 Hz" },
  { id: "E4", label: "Cálculo cinemático", detalle: "Ángulos, velocidades y orden de picos" },
  { id: "E5", label: "Reporte", detalle: "Auditoría de estados y sello de trazabilidad" },
] as const;

type Fase = "idle" | "verificando" | "verificado" | "procesando" | "listo";

function UploadPage() {
  const busqueda = Route.useSearch();
  const [fps, setFps] = useState<Fps>(busqueda.fps ?? 240);
  const [fase, setFase] = useState<Fase>(busqueda.paso === "verificado" ? "verificado" : "idle");
  const [etapaActual, setEtapaActual] = useState(0);
  const [confirmado, setConfirmado] = useState(false);
  const timers = useRef<number[]>([]);

  useEffect(() => {
    const t = timers.current;
    return () => t.forEach(clearTimeout);
  }, []);

  const agendar = (fn: () => void, ms: number) => {
    timers.current.push(window.setTimeout(fn, ms));
  };

  const seleccionarArchivo = () => {
    setFase("verificando");
    agendar(() => setFase("verificado"), 900);
  };

  const analizar = () => {
    setFase("procesando");
    setEtapaActual(0);
    ETAPAS.forEach((_, i) => agendar(() => setEtapaActual(i + 1), 850 * (i + 1)));
    agendar(() => setFase("listo"), 850 * (ETAPAS.length + 1));
  };

  const reiniciar = () => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setFase("idle");
    setEtapaActual(0);
    setConfirmado(false);
  };

  const perfil = PERFILES[fps];
  const puedeAnalizar = !perfil.requiereConfirmacion || confirmado;

  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Carga</div>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">
        Cargá tu sesión de <span className="text-gradient-neon">entrenamiento</span>
      </h1>
      <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
        MP4 o MOV · <strong className="text-foreground">mínimo 120 fps</strong>, 240 recomendado ·
        un jugador en cuadro · cuerpo completo visible.
      </p>

      {import.meta.env.DEV && busqueda.demo !== false && (
        <div className="mt-8 rounded-2xl border border-dashed border-border bg-card/50 p-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              <FlaskConical className="h-3 w-3" /> Demostración · solo en desarrollo
            </span>
            <div className="flex gap-2">
              {([240, 120, 60] as Fps[]).map((f) => (
                <button
                  key={f}
                  onClick={() => {
                    setFps(f);
                    reiniciar();
                  }}
                  className={`rounded-lg border px-3 py-1.5 font-mono text-xs transition-colors ${
                    fps === f
                      ? "border-neon/60 bg-neon/10 text-neon"
                      : "border-border text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {f} fps
                </button>
              ))}
            </div>
            {fase !== "idle" && (
              <button
                onClick={reiniciar}
                className="ml-auto flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 font-mono text-xs text-muted-foreground hover:text-foreground"
              >
                <RotateCcw className="h-3 w-3" /> Reiniciar
              </button>
            )}
          </div>
        </div>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {fase === "idle" && (
            <button
              onClick={seleccionarArchivo}
              className="group flex w-full flex-col items-center justify-center gap-4 rounded-3xl border-2 border-dashed border-border bg-card p-16 transition-colors hover:border-neon/60"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-neon shadow-neon">
                <UploadCloud className="h-8 w-8 text-neon-foreground" />
              </div>
              <div className="text-center">
                <div className="font-display text-2xl font-bold">Arrastrá tu video o hacé clic</div>
                <div className="mt-1 font-mono text-xs text-muted-foreground">
                  MP4 · MOV · 120 fps mínimo · máx. 2 GB
                </div>
              </div>
            </button>
          )}

          {fase !== "idle" && (
            <div className="rounded-3xl border border-border bg-card p-6">
              <div className="flex items-center gap-3">
                <Film className="h-5 w-5 text-neon" />
                <div className="font-display font-semibold">saque-2026-05-12.mp4</div>
                <span className="ml-auto font-mono text-xs text-muted-foreground">
                  412 MB · 1080p
                </span>
              </div>
            </div>
          )}

          {/* BLOQUE PROTAGÓNICO — verificación de frecuencia de captura */}
          {(fase === "verificando" || fase === "verificado") && (
            <VerificacionFps fps={fps} verificando={fase === "verificando"} />
          )}

          {fase === "verificado" && (
            <div className="space-y-4">
              {perfil.requiereConfirmacion && (
                <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-state-warn/40 bg-state-warn/5 p-4">
                  <input
                    type="checkbox"
                    checked={confirmado}
                    onChange={(e) => setConfirmado(e.target.checked)}
                    className="mt-0.5 h-4 w-4 shrink-0 accent-[var(--state-warn)]"
                  />
                  <span className="text-sm text-muted-foreground">
                    Entiendo que a {fps} fps el análisis se limita a la fase de preparación y que el
                    resto del gesto quedará marcado como{" "}
                    <span className="text-state-none">no auditable</span>.
                  </span>
                </label>
              )}
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={analizar}
                  disabled={!puedeAnalizar}
                  className={`inline-flex items-center gap-2 rounded-xl px-6 py-3 font-display font-semibold transition ${
                    puedeAnalizar
                      ? "bg-gradient-neon text-neon-foreground shadow-neon hover:scale-[1.02]"
                      : "cursor-not-allowed border border-border bg-background text-muted-foreground"
                  }`}
                >
                  Analizar video <ArrowRight className="h-4 w-4" />
                </button>
                <button
                  onClick={reiniciar}
                  className="rounded-xl border border-border px-6 py-3 font-display font-semibold text-muted-foreground hover:text-foreground"
                >
                  Elegir otro archivo
                </button>
              </div>
            </div>
          )}

          {fase === "procesando" && <Procesando etapaActual={etapaActual} />}

          {fase === "listo" && (
            <div className="rounded-3xl border border-neon/40 bg-card p-8">
              <div className="flex items-center gap-3 text-neon">
                <Check className="h-6 w-6" />
                <div className="font-display text-2xl font-bold">Reporte generado</div>
              </div>
              <p className="mt-3 text-muted-foreground">
                {fps === 60
                  ? "Se documentó la fase de preparación de 6 saques. El instante de impacto quedó marcado como no auditable en los 6."
                  : "Se documentó la secuencia de picos de velocidad en 6 saques. Cobertura auditable: 6 de 6."}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <EstadoBadge estado="correcto">
                  Cobertura {fps === 60 ? "1 de 3 fases" : "3 de 3 fases"}
                </EstadoBadge>
                {fps === 60 && <EstadoBadge estado="no-auditable">Impacto no medible</EstadoBadge>}
                <span className="inline-flex items-center rounded-full border border-border px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  v0.1.0 · MediaPipe Pose
                </span>
              </div>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  to="/reporte"
                  className="rounded-xl bg-gradient-neon px-6 py-3 font-display font-semibold text-neon-foreground shadow-neon"
                >
                  Ver reporte
                </Link>
                <Link
                  to="/videos"
                  className="rounded-xl border border-border px-6 py-3 font-display font-semibold"
                >
                  Mis sesiones
                </Link>
                <button
                  onClick={reiniciar}
                  className="rounded-xl border border-border px-6 py-3 font-display font-semibold"
                >
                  Cargar otro video
                </button>
              </div>
            </div>
          )}
        </div>

        <aside className="space-y-4">
          <div className="rounded-2xl border border-border bg-card p-5">
            <div className="flex items-center gap-2 text-neon">
              <Camera className="h-4 w-4" />
              <div className="font-display font-semibold">Cómo grabar correctamente</div>
            </div>
            <Accordion type="single" collapsible className="mt-2">
              <AccordionItem value="protocolo" className="border-b-0">
                <AccordionTrigger className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
                  Protocolo de captura
                </AccordionTrigger>
                <AccordionContent>
                  <ul className="space-y-2.5 text-sm text-muted-foreground">
                    {[
                      "Activá el modo cámara lenta del celular: es lo que habilita los 120 o 240 fps.",
                      "Cámara fija sobre trípode o apoyo estable. Nunca a pulso.",
                      "Ubicación de perfil o a tres cuartos respecto del jugador.",
                      "Cuerpo completo dentro del cuadro durante todo el gesto, pies incluidos.",
                      "Buena luz, sin contraluz. Preferentemente al aire libre o con luz pareja.",
                      "Un solo jugador en cuadro.",
                    ].map((t) => (
                      <li key={t} className="flex gap-2">
                        <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-neon" />
                        {t}
                      </li>
                    ))}
                  </ul>
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="porque" className="border-b-0">
                <AccordionTrigger className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
                  Por qué 120 fps
                </AccordionTrigger>
                <AccordionContent>
                  <p className="text-sm text-muted-foreground">
                    A 30 cuadros por segundo el hombro rota casi 80° entre un cuadro y el siguiente:
                    el instante del pico de velocidad cae en el hueco entre cuadros y ya no está en
                    el archivo. No es un problema de nitidez, es información ausente, y ningún
                    filtro la reconstruye.
                  </p>
                  <p className="mt-3 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    Criterio de Nyquist-Shannon
                  </p>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>

          <div className="rounded-2xl border border-border bg-card p-5">
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Alcance del análisis
            </div>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              <li>· Gestos: saque, drive y revés</li>
              <li>· Un jugador por video</li>
              <li>· Videos de entrenamiento, no de partido</li>
            </ul>
          </div>
        </aside>
      </div>
    </main>
  );
}

function VerificacionFps({ fps, verificando }: { fps: Fps; verificando: boolean }) {
  const perfil = PERFILES[fps];
  const e = ESTADOS[perfil.estado];

  if (verificando) {
    return (
      <div className="rounded-3xl border border-border bg-card p-8">
        <div className="flex items-center gap-3 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="font-display font-semibold">Verificando frecuencia de captura…</span>
        </div>
      </div>
    );
  }

  const insuficiente = fps < 120;

  return (
    <div className={`rounded-3xl border-2 bg-card p-8 ${e.borde}`}>
      <div className="flex flex-wrap items-start gap-6">
        <div className="flex items-center gap-4">
          <Gauge className={`h-8 w-8 shrink-0 ${e.texto}`} />
          <div>
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Frecuencia detectada
            </div>
            <div className={`font-display text-5xl font-bold ${e.texto}`}>
              {fps}
              <span className="ml-1 text-2xl">fps</span>
            </div>
          </div>
        </div>
        <div className="min-w-[16rem] flex-1">
          <EstadoBadge estado={perfil.estado}>
            {insuficiente ? "Frecuencia insuficiente" : "Frecuencia suficiente"}
          </EstadoBadge>
          <div className="mt-3 font-display text-xl font-semibold">{perfil.titulo}</div>
          <p className="mt-2 text-sm text-muted-foreground">{perfil.detalle}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-3 border-t border-border pt-6 sm:grid-cols-2">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Requisito
          </div>
          <div className="mt-1 text-sm">120 fps mínimo · 240 recomendado</div>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Fases auditables con este archivo
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm">
            {perfil.cobertura}
            {insuficiente && <EstadoBadge estado="no-auditable">Aceleración e impacto</EstadoBadge>}
          </div>
        </div>
      </div>
    </div>
  );
}

function Procesando({ etapaActual }: { etapaActual: number }) {
  const total = ETAPAS.length;
  const enCurso = ETAPAS[Math.min(etapaActual, total - 1)];
  const porcentaje = Math.round((etapaActual / total) * 100);

  return (
    <div className="rounded-3xl border border-neon/40 bg-card p-8 shadow-neon">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Etapa {Math.min(etapaActual + 1, total)} de {total}
          </div>
          <div className="mt-1 font-display text-2xl font-bold">{enCurso.label}</div>
          <div className="mt-1 text-sm text-muted-foreground">{enCurso.detalle}</div>
        </div>
        <div className="font-mono text-xs text-neon">{porcentaje}%</div>
      </div>

      <div className="mt-5 h-2 overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full bg-gradient-neon transition-all duration-500"
          style={{ width: `${Math.max(porcentaje, 4)}%` }}
        />
      </div>

      <ol className="mt-6 space-y-2.5">
        {ETAPAS.map((etapa, i) => {
          const completa = i < etapaActual;
          const activa = i === etapaActual;
          return (
            <li key={etapa.id} className="flex items-center gap-3">
              {completa ? (
                <Check className="h-4 w-4 shrink-0 text-neon" />
              ) : activa ? (
                <Loader2 className="h-4 w-4 shrink-0 animate-spin text-neon" />
              ) : (
                <span className="h-4 w-4 shrink-0 rounded-full border border-border" />
              )}
              <span
                className={`font-mono text-xs ${
                  completa || activa ? "text-foreground" : "text-muted-foreground"
                }`}
              >
                {etapa.label}
              </span>
              <span className="ml-auto font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                {etapa.id}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
