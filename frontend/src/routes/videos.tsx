import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Play,
  Calendar,
  Repeat2,
  Filter,
  Search,
  CheckCircle2,
  CircleSlash,
  Loader2,
  XCircle,
  Gauge,
} from "lucide-react";
import { EvolucionAtleta } from "@/components/evolucion-atleta";
import t1 from "@/assets/video-thumb-1.jpg";
import t2 from "@/assets/video-thumb-2.jpg";
import t3 from "@/assets/video-thumb-3.jpg";
import { RutaProtegida } from "@/components/ruta-protegida";
import { DatosDeEjemplo } from "@/components/datos-de-ejemplo";

export const Route = createFileRoute("/videos")({
  head: () => ({
    meta: [
      { title: "Mis sesiones — KinetiQ" },
      {
        name: "description",
        content:
          "Sesiones de entrenamiento analizadas y evolución del atleta a lo largo del tiempo.",
      },
    ],
  }),
  // Requiere sesión (especificación §3). La barrera real son RLS y la API; esto evita mostrar datos de ejemplo a un anónimo.
  component: () => (
    <RutaProtegida>
      <VideosPage />
    </RutaProtegida>
  ),
});

/**
 * Estado del ANALISIS, no del jugador. Es una taxonomia distinta del semaforo de
 * auditoria (R3) y por eso vive aparte: aca se responde "en que quedo el
 * procesamiento", no "que tan bien se midio el gesto".
 * Como todo estado del sistema, nunca se comunica solo por color: icono + texto.
 */
const ESTADOS_ANALISIS = {
  completado: {
    label: "Completado",
    Icono: CheckCircle2,
    clases: "text-state-ok border-state-ok/40 bg-state-ok/10",
  },
  parcial: {
    label: "Parcial",
    Icono: CircleSlash,
    clases: "text-state-none border-state-none/40 bg-state-none/10",
  },
  procesando: {
    label: "Procesando",
    Icono: Loader2,
    clases: "text-muted-foreground border-border bg-secondary/50",
  },
  fallido: {
    label: "Fallido",
    Icono: XCircle,
    clases: "text-state-alert border-state-alert/40 bg-state-alert/10",
  },
} as const;

type EstadoAnalisis = keyof typeof ESTADOS_ANALISIS;

interface Sesion {
  thumb: string;
  gesto: "Saque" | "Drive" | "Revés";
  titulo: string;
  fecha: string;
  duracion: string;
  repeticiones: number;
  fps: number;
  estado: EstadoAnalisis;
  /** Repeticiones con cobertura auditable completa, sobre el total. */
  auditables: number | null;
  nota: string | null;
}

const SESIONES: Sesion[] = [
  {
    thumb: t1,
    gesto: "Saque",
    titulo: "Tanda de saques plano",
    fecha: "12 May 2026",
    duracion: "4:12",
    repeticiones: 6,
    fps: 240,
    estado: "parcial",
    auditables: 4,
    nota: "En 2 repeticiones no se pudo medir el instante de impacto.",
  },
  {
    thumb: t2,
    gesto: "Drive",
    titulo: "Drive cruzado con canasto",
    fecha: "08 May 2026",
    duracion: "6:48",
    repeticiones: 24,
    fps: 240,
    estado: "completado",
    auditables: 24,
    nota: null,
  },
  {
    thumb: t3,
    gesto: "Revés",
    titulo: "Revés a una mano · paralelo",
    fecha: "01 May 2026",
    duracion: "5:30",
    repeticiones: 18,
    fps: 120,
    estado: "completado",
    auditables: 18,
    nota: null,
  },
  {
    thumb: t1,
    gesto: "Saque",
    titulo: "Tanda de saques slice",
    fecha: "26 Abr 2026",
    duracion: "3:55",
    repeticiones: 16,
    fps: 240,
    estado: "completado",
    auditables: 16,
    nota: null,
  },
  {
    thumb: t2,
    gesto: "Drive",
    titulo: "Drive paralelo con canasto",
    fecha: "19 Abr 2026",
    duracion: "5:02",
    repeticiones: 22,
    fps: 60,
    estado: "fallido",
    auditables: null,
    nota: "Video grabado a 60 fps: por debajo del mínimo de 120 fps requerido.",
  },
  {
    thumb: t3,
    gesto: "Revés",
    titulo: "Revés cortado",
    fecha: "12 Abr 2026",
    duracion: "4:40",
    repeticiones: 14,
    fps: 120,
    estado: "procesando",
    auditables: null,
    nota: "Etapa 4 de 6 · Filtrado.",
  },
];

function VideosPage() {
  const analizadas = SESIONES.filter((s) => s.estado === "completado" || s.estado === "parcial");
  const repeticiones = analizadas.reduce((acc, s) => acc + s.repeticiones, 0);
  const rechazadas = SESIONES.filter((s) => s.estado === "fallido").length;

  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <DatosDeEjemplo detalle="Las tarjetas de sesiones son una maqueta: todavía no se leen tus sesiones reales (pieza 7 del plan)." />
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Sesiones</div>
          <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">
            Tus <span className="text-gradient-neon">sesiones</span>
          </h1>
          <p className="mt-3 text-muted-foreground">
            {analizadas.length} sesiones analizadas · {repeticiones} repeticiones · {rechazadas}{" "}
            rechazada por frecuencia de captura insuficiente
          </p>
        </div>
        <Link
          to="/upload"
          className="rounded-xl bg-gradient-neon px-5 py-3 font-display font-semibold text-neon-foreground shadow-neon"
        >
          + Nueva sesión
        </Link>
      </div>

      {/* EVOLUCION DEL ATLETA */}
      <div className="mt-10">
        <EvolucionAtleta />
      </div>

      <div className="mt-12 flex flex-wrap items-center gap-3">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            placeholder="Buscar por gesto, fecha o estado del análisis…"
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>
        <button className="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm">
          <Filter className="h-4 w-4" /> Filtros
        </button>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {SESIONES.map((s, i) => {
          const e = ESTADOS_ANALISIS[s.estado];
          const navegable = s.estado === "completado" || s.estado === "parcial";
          const contenido = (
            <>
              <div className="relative aspect-video overflow-hidden">
                <img
                  src={s.thumb}
                  alt={s.titulo}
                  loading="lazy"
                  className={`h-full w-full object-cover transition-transform group-hover:scale-105 ${
                    navegable ? "" : "opacity-50 grayscale"
                  }`}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-background/10 to-transparent" />
                <div className="absolute left-3 top-3 rounded-md bg-background/80 px-2 py-1 font-mono text-[10px] uppercase tracking-widest text-neon backdrop-blur">
                  {s.gesto}
                </div>
                <div className="absolute right-3 top-3 flex items-center gap-1 rounded-md bg-background/80 px-2 py-1 font-mono text-[10px] backdrop-blur">
                  <Gauge className="h-3 w-3" />
                  {s.fps} fps
                </div>
                <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between">
                  {navegable && (
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-neon shadow-neon transition-transform group-hover:scale-110">
                      <Play className="h-4 w-4 text-neon-foreground" fill="currentColor" />
                    </div>
                  )}
                  <div className="ml-auto rounded-md bg-background/80 px-2 py-1 font-mono text-[10px] backdrop-blur">
                    {s.duracion}
                  </div>
                </div>
              </div>

              <div className="p-4">
                <div className="font-display font-semibold">{s.titulo}</div>
                <div className="mt-1 flex flex-wrap items-center gap-3 font-mono text-[11px] text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {s.fecha}
                  </span>
                  <span className="flex items-center gap-1">
                    <Repeat2 className="h-3 w-3" />
                    {s.repeticiones} repeticiones
                  </span>
                </div>

                <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-widest ${e.clases}`}
                  >
                    <e.Icono
                      className={`h-3 w-3 shrink-0 ${s.estado === "procesando" ? "animate-spin" : ""}`}
                    />
                    {e.label}
                  </span>
                  {s.auditables !== null && (
                    <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                      Auditables {s.auditables} de {s.repeticiones}
                    </span>
                  )}
                </div>

                {s.nota && <p className="mt-3 text-xs text-muted-foreground">{s.nota}</p>}
              </div>
            </>
          );

          return navegable ? (
            <Link
              key={i}
              to="/reporte"
              className="group overflow-hidden rounded-2xl border border-border bg-card transition-all hover:-translate-y-1 hover:border-neon/50 hover:shadow-neon"
            >
              {contenido}
            </Link>
          ) : (
            <div key={i} className="group overflow-hidden rounded-2xl border border-border bg-card">
              {contenido}
            </div>
          );
        })}
      </div>
    </main>
  );
}
