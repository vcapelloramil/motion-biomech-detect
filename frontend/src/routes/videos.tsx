import { useEffect, useMemo, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Film, Loader2, Search } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { EstadoBadge, SinEvaluarBadge } from "@/components/estado";
import { useSesion } from "@/lib/sesion";
import {
  ENCUADRE_ETIQUETA,
  GESTO_ETIQUETA,
  contarObservaciones,
  enCurso,
  estadoDeSesion,
  numero,
  observacionesDe,
  reporteDe,
  type EstadoSesion,
} from "@/lib/estado-video";
import { listarSesiones, type SesionConVideos } from "@/lib/videos-data";

export const Route = createFileRoute("/videos")({
  head: () => ({
    meta: [
      { title: "Biblioteca — KinetiQ" },
      { name: "description", content: "Tus sesiones cargadas, con el estado de cada análisis." },
    ],
  }),
  component: () => (
    <RutaProtegida>
      <BibliotecaPage />
    </RutaProtegida>
  ),
});

const FILTROS = [
  { valor: "todos", etiqueta: "Todas" },
  { valor: "saque", etiqueta: "Saque" },
  { valor: "drive", etiqueta: "Drive" },
  { valor: "reves", etiqueta: "Revés" },
] as const;

function BibliotecaPage() {
  const { cargando: cargandoSesion } = useSesion();
  const [sesiones, setSesiones] = useState<SesionConVideos[] | null>(null);
  const [error, setError] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [filtro, setFiltro] = useState<(typeof FILTROS)[number]["valor"]>("todos");

  useEffect(() => {
    if (cargandoSesion) return;
    let activo = true;
    const leer = () =>
      listarSesiones()
        .then((s) => {
          if (!activo) return;
          setSesiones(s);
          setError(false);
        })
        .catch(() => {
          if (!activo) return;
          setError(true);
          setSesiones((previo) => previo ?? []);
        });
    void leer();
    // Mientras haya análisis en curso la lista se actualiza sola.
    const t = window.setInterval(() => {
      if (document.visibilityState === "visible") void leer();
    }, 8000);
    return () => {
      activo = false;
      window.clearInterval(t);
    };
  }, [cargandoSesion]);

  const visibles = useMemo(() => {
    const q = busqueda.trim().toLowerCase();
    return (sesiones ?? []).filter((s) => {
      if (filtro !== "todos" && s.gesto !== filtro) return false;
      if (!q) return true;
      const texto = `${GESTO_ETIQUETA[s.gesto] ?? s.gesto} ${ENCUADRE_ETIQUETA[s.encuadre] ?? s.encuadre} ${s.fecha} ${s.atletas?.nombre ?? ""}`;
      return texto.toLowerCase().includes(q);
    });
  }, [sesiones, busqueda, filtro]);

  const totalGolpes = (sesiones ?? []).reduce((n, s) => n + s.videos.length, 0);

  return (
    <main className="mx-auto max-w-6xl px-5 py-10 md:py-14">
      <p className="font-mono text-xs uppercase tracking-widest text-acento">/ Biblioteca</p>
      <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="font-display text-4xl font-extrabold tracking-tight md:text-6xl">
            Tus <span className="text-gradient-neon">sesiones</span>
          </h1>
          <p className="mt-3 text-muted-foreground">
            {sesiones === null
              ? "Cargando…"
              : `${sesiones.length} ${sesiones.length === 1 ? "sesión" : "sesiones"} · ${totalGolpes} ${totalGolpes === 1 ? "golpe" : "golpes"}`}
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex min-h-11 items-center justify-center rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground shadow-neon"
        >
          + Nueva sesión
        </Link>
      </div>

      <div className="mt-8 flex flex-col gap-3 md:flex-row">
        <label className="relative flex-1">
          <span className="sr-only">Buscar por fecha, gesto o jugador</span>
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
          <input
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar por fecha, gesto o jugador"
            className="min-h-11 w-full rounded-xl border border-border bg-card pl-10 pr-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </label>
        <div className="flex gap-2 overflow-x-auto" role="group" aria-label="Filtrar por golpe">
          {FILTROS.map((f) => (
            <button
              key={f.valor}
              type="button"
              onClick={() => setFiltro(f.valor)}
              aria-pressed={filtro === f.valor}
              className={
                "min-h-11 shrink-0 rounded-xl border px-4 text-sm font-semibold " +
                (filtro === f.valor ? "border-border bg-secondary" : "border-border text-muted-foreground hover:text-foreground")
              }
            >
              {f.etiqueta}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <p role="alert" className="mt-6 rounded-xl border border-state-alert/40 bg-state-alert-bg px-4 py-3 text-sm">
          No pudimos leer tus sesiones ahora. Revisá tu conexión: se vuelve a intentar solo.
        </p>
      )}

      {sesiones === null ? (
        <p role="status" className="mt-10 flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando tus sesiones…
        </p>
      ) : sesiones.length === 0 && !error ? (
        <div className="mt-10 rounded-2xl border border-dashed border-border p-8 text-center">
          <Film className="mx-auto h-8 w-8 text-muted-foreground" aria-hidden="true" />
          <h2 className="mt-4 font-display text-xl font-bold">Todavía no cargaste ningún golpe</h2>
          <p className="mt-2 text-sm text-muted-foreground">Subí el video de un golpe y acá vas a ver el estado del análisis y su resultado.</p>
          <Link to="/upload" className="mt-5 inline-flex min-h-11 items-center rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground">
            Cargar un golpe
          </Link>
        </div>
      ) : (
        <ul className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {visibles.map((s) => (
            <TarjetaSesion key={s.id} sesion={s} />
          ))}
          {visibles.length === 0 && sesiones.length > 0 && (
            <li className="text-sm text-muted-foreground md:col-span-2 lg:col-span-3">Ninguna sesión coincide con la búsqueda.</li>
          )}
        </ul>
      )}
    </main>
  );
}

const ETIQUETA_SESION: Record<EstadoSesion, string> = {
  en_curso: "Procesando",
  completada: "Completado",
  parcial: "Parcial",
  fallida: "No se pudo",
  vacia: "Sin golpes",
};

function TarjetaSesion({ sesion }: { sesion: SesionConVideos }) {
  const videos = sesion.videos;
  const estado = estadoDeSesion(videos.map((v) => v.estado));
  const primero = videos[0];
  const fps = numero(primero?.fps_real);
  const fecha = new Date(sesion.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "short", year: "numeric" });

  // Conteo de lo observado, sumando las observaciones de los golpes con reporte.
  const todas = videos.flatMap((v) => observacionesDe(reporteDe(v)?.reporte ?? null));
  const c = contarObservaciones(todas);
  const hayConteo = Object.values(c).some((n) => n > 0);
  const analizando = videos.some((v) => enCurso(v.estado));

  return (
    <li className="overflow-hidden rounded-2xl border border-border bg-card">
      {/* Sin miniatura real todavía: un panel neutro, no una imagen inventada. */}
      <div className="relative flex h-36 items-center justify-center bg-gradient-to-b from-secondary to-card">
        <Film className="h-8 w-8 text-muted-foreground/60" aria-hidden="true" />
        <span className="absolute left-3 top-3 rounded-lg border border-border bg-background/80 px-2.5 py-1 font-mono text-[11px] text-foreground">
          {analizando && <Loader2 className="mr-1 inline h-3 w-3 animate-spin" aria-hidden="true" />}
          {ETIQUETA_SESION[estado]}
        </span>
        {fps !== null && (
          <span className="absolute bottom-3 right-3 rounded-lg border border-border bg-background/80 px-2.5 py-1 font-mono text-[11px] uppercase tracking-widest">
            {Math.round(fps)} fps
          </span>
        )}
      </div>

      <div className="p-5">
        <h2 className="font-display text-xl font-bold">
          {GESTO_ETIQUETA[sesion.gesto] ?? sesion.gesto} · {ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre}
        </h2>
        <p className="mt-1 font-mono text-xs text-muted-foreground">
          {fecha} · {videos.length} {videos.length === 1 ? "golpe" : "golpes"}
          {sesion.atletas?.nombre ? ` · ${sesion.atletas.nombre}` : ""}
        </p>

        <div className="mt-4 border-t border-border pt-4">
          {analizando ? (
            <p className="text-sm text-muted-foreground">Analizando. El resultado aparece acá cuando esté listo.</p>
          ) : hayConteo ? (
            <div className="flex flex-wrap gap-2">
              {c.correcto > 0 && <EstadoBadge estado="correcto">{c.correcto} correcto{c.correcto > 1 ? "s" : ""}</EstadoBadge>}
              {c.desvio_leve > 0 && <EstadoBadge estado="desvio">{c.desvio_leve} desvío{c.desvio_leve > 1 ? "s" : ""} leve{c.desvio_leve > 1 ? "s" : ""}</EstadoBadge>}
              {c.alerta_de_carga > 0 && <EstadoBadge estado="alerta">{c.alerta_de_carga} alerta{c.alerta_de_carga > 1 ? "s" : ""} de carga</EstadoBadge>}
              {c.no_auditable > 0 && <EstadoBadge estado="no-auditable">{c.no_auditable} no auditable{c.no_auditable > 1 ? "s" : ""}</EstadoBadge>}
              {c.sin_evaluar > 0 && <SinEvaluarBadge />}
            </div>
          ) : estado === "fallida" ? (
            <p className="text-sm text-muted-foreground">No se pudo analizar. Abrí el detalle para ver qué hacer.</p>
          ) : (
            <p className="text-sm text-muted-foreground">Este golpe no produjo observaciones.</p>
          )}

          {primero && (reporteDe(primero)?.reporte ?? null) && !analizando ? (
            <Link
              to="/reporte/$videoId"
              params={{ videoId: primero.id }}
              className="mt-4 inline-flex min-h-11 items-center gap-1.5 text-sm font-semibold text-state-ok hover:underline"
            >
              Ver reporte
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          ) : (
            primero && (
              <Link
                to="/procesando/$videoId"
                params={{ videoId: primero.id }}
                className="mt-4 inline-flex min-h-11 items-center gap-1.5 text-sm font-semibold text-state-ok hover:underline"
              >
                {analizando ? "Ver progreso" : estado === "fallida" ? "Ver qué pasó" : "Ver detalle"}
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            )
          )}
        </div>
      </div>
    </li>
  );
}
