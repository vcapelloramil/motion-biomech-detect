import { useCallback, useEffect, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { AlertTriangle, Check, Clock, Loader2, RefreshCw } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { EstadoBadge, SinEvaluarBadge, type Estado } from "@/components/estado";
import { useSesion } from "@/lib/sesion";
import { MODOS_CAPTURA, esValor, type ModoCaptura } from "@/lib/carga";
import {
  ENCUADRE_ETIQUETA,
  ETAPAS,
  GESTO_ETIQUETA,
  PASOS,
  enCurso,
  formatearDuracion,
  latenciaDe,
  numero,
  observacionesDe,
  pasoActual,
  reporteDe,
  segundosEntre,
  textoDeFallo,
  type ObservacionLeida,
} from "@/lib/estado-video";
import { corregirModo, leerVideo, reintentar, type VideoConReporte } from "@/lib/videos-data";

export const Route = createFileRoute("/procesando/$videoId")({
  head: () => ({ meta: [{ title: "Procesando — KinetiQ" }, { name: "robots", content: "noindex" }] }),
  component: () => (
    <RutaProtegida>
      <ProcesandoPage />
    </RutaProtegida>
  ),
});

const INTERVALO_MS = 5000;

const BADGE_POR_SEVERIDAD: Record<string, Estado | "sin_evaluar"> = {
  correcto: "correcto",
  desvio_leve: "desvio",
  alerta_de_carga: "alerta",
  no_auditable: "no-auditable",
  sin_evaluar: "sin_evaluar",
};

function ProcesandoPage() {
  const { videoId } = Route.useParams();
  const { cargando: cargandoSesion } = useSesion();
  const [video, setVideo] = useState<VideoConReporte | null | undefined>(undefined);
  const [errorLectura, setErrorLectura] = useState(false);
  const [ahora, setAhora] = useState(() => Date.now());

  const cargar = useCallback(async () => {
    try {
      const v = await leerVideo(videoId);
      setVideo(v);
      setErrorLectura(false);
    } catch {
      setErrorLectura(true);
      setVideo((previo) => (previo === undefined ? null : previo));
    }
  }, [videoId]);

  useEffect(() => {
    if (cargandoSesion) return;
    void cargar();
  }, [cargar, cargandoSesion]);

  // Polling mientras el análisis siga en curso; se detiene solo al llegar a un estado terminal.
  const sigue = video ? enCurso(video.estado) : false;
  useEffect(() => {
    if (!sigue) return;
    const t = window.setInterval(() => void cargar(), INTERVALO_MS);
    return () => window.clearInterval(t);
  }, [sigue, cargar]);

  useEffect(() => {
    if (!sigue) return;
    const t = window.setInterval(() => setAhora(Date.now()), 1000);
    return () => window.clearInterval(t);
  }, [sigue]);

  if (video === undefined) {
    return (
      <main className="mx-auto max-w-5xl px-5 py-16">
        <p role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando…
        </p>
      </main>
    );
  }

  if (video === null) {
    return (
      <main className="mx-auto max-w-5xl px-5 py-16">
        <p className="font-mono text-xs uppercase tracking-widest text-acento">/ Procesando</p>
        <h1 className="mt-4 font-display text-3xl font-extrabold">No encontramos este video</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          {errorLectura
            ? "No pudimos leerlo ahora. Revisá tu conexión y volvé a probar."
            : "No existe o no es tuyo. Podés ver tus sesiones en la biblioteca."}
        </p>
        <Link to="/videos" className="mt-6 inline-flex rounded-xl border border-border px-4 py-2.5 text-sm font-semibold">
          Volver a la biblioteca
        </Link>
      </main>
    );
  }

  return <Detalle video={video} ahora={ahora} alCambiar={cargar} />;
}

function Detalle({ video, ahora, alCambiar }: { video: VideoConReporte; ahora: number; alCambiar: () => Promise<void> }) {
  const sesion = video.sesiones;
  const fps = numero(video.fps_real);
  const termino = !enCurso(video.estado);
  const rep = reporteDe(video);
  const nombreArchivo = video.ruta_almacenamiento?.split("/").pop() ?? "video";

  const titulo =
    video.estado === "completado" ? (
      <>Tu golpe <span className="text-acento">está listo</span></>
    ) : video.estado === "parcial" ? (
      <>Tu golpe se analizó <span className="text-acento">en parte</span></>
    ) : video.estado === "fallido" ? (
      <>No pudimos <span className="text-acento">analizar este golpe</span></>
    ) : (
      <>Estamos analizando <span className="text-acento">tu golpe</span></>
    );

  const inicio = video.encolado_en ?? video.creado_en;
  const transcurrido = termino ? segundosEntre(inicio, video.fin_procesamiento_en) : Math.max(0, (ahora - Date.parse(inicio)) / 1000);

  return (
    <main className="mx-auto max-w-5xl px-5 py-10 md:py-14">
      <p className="font-mono text-xs uppercase tracking-widest text-acento">/ {termino ? "Resultado" : "Procesando"}</p>
      <div className="mt-4 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="font-display text-4xl font-extrabold leading-tight tracking-tight md:text-6xl">{titulo}</h1>
          <p className="mt-3 text-muted-foreground">
            {sesion
              ? `${GESTO_ETIQUETA[sesion.gesto] ?? sesion.gesto} · de ${ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre}`
              : "Golpe"}
            {sesion?.atletas?.nombre ? ` · ${sesion.atletas.nombre}` : ""}
          </p>
        </div>
        <Link
          to="/videos"
          className="inline-flex min-h-11 items-center justify-center rounded-xl border border-border px-5 text-sm font-semibold hover:border-accent/60"
        >
          Volver a la biblioteca
        </Link>
      </div>

      {!termino && (
        <p className="mt-6 flex items-start gap-3 rounded-2xl border border-accent/30 bg-card px-4 py-3 text-sm">
          <Clock className="mt-0.5 h-4 w-4 shrink-0 text-acento" aria-hidden="true" />
          <span>
            Cada golpe tarda unos minutos. <strong>Podés cerrar esta página:</strong> cuando termine, el resultado aparece listo en tu
            biblioteca.
          </span>
        </p>
      )}

      <div className="mt-6 grid gap-5 lg:grid-cols-[1.6fr_1fr]">
        <section aria-labelledby="estado-titulo" className="rounded-2xl border border-border bg-card p-5 md:p-7">
          <div className="flex items-start justify-between gap-3">
            <h2 id="estado-titulo" className="font-display text-xl font-bold md:text-2xl">
              Golpe · {nombreArchivo}
            </h2>
            <EtiquetaEstado estado={video.estado} />
          </div>

          <Pasos video={video} />

          {transcurrido !== null && (
            <p className="mt-5 font-mono text-xs uppercase tracking-widest text-muted-foreground">
              {termino ? "Tardó" : "Lleva"} {formatearDuracion(transcurrido)}
              {!termino && " · se actualiza solo"}
            </p>
          )}

          {!termino && <Etapas />}

          {video.estado === "fallido" && <Fallo video={video} fps={fps} alCambiar={alCambiar} />}

          {(video.estado === "completado" || video.estado === "parcial") && rep?.reporte && (
            <Link
              to="/reporte/$videoId"
              params={{ videoId: video.id }}
              className="mt-6 inline-flex min-h-11 items-center rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground"
            >
              Abrir el reporte
            </Link>
          )}

          {(video.estado === "completado" || video.estado === "parcial") && (
            <Resultado video={video} reporte={rep?.reporte ?? null} fps={fps} />
          )}
        </section>

        <aside aria-labelledby="golpes-titulo" className="h-fit rounded-2xl border border-border bg-card p-5 md:p-7">
          <h2 id="golpes-titulo" className="font-display text-xl font-bold">Golpe de esta sesión</h2>
          <div className="mt-4 rounded-xl border border-border px-4 py-3">
            <p className="font-display text-sm font-bold">{nombreArchivo}</p>
            <p className="mt-1 font-mono text-xs text-muted-foreground">
              {fps !== null ? `${Math.round(fps)} fps` : "fps: se lee al procesar"} · {resumenEstado(video.estado)}
            </p>
          </div>
        </aside>
      </div>
    </main>
  );
}

function resumenEstado(estado: VideoConReporte["estado"]): string {
  return { pendiente: "subido", encolado: "en cola", procesando: "en curso", completado: "listo", parcial: "parcial", fallido: "no se pudo" }[
    estado
  ];
}

function EtiquetaEstado({ estado }: { estado: VideoConReporte["estado"] }) {
  const mapa: Record<VideoConReporte["estado"], string> = {
    pendiente: "Subido",
    encolado: "En cola",
    procesando: "En curso",
    completado: "Completado",
    parcial: "Parcial",
    fallido: "No se pudo",
  };
  return (
    <span className="shrink-0 font-mono text-[11px] uppercase tracking-widest text-acento">
      {enCurso(estado) && <Loader2 className="mr-1.5 inline h-3 w-3 animate-spin" aria-hidden="true" />}
      {mapa[estado]}
    </span>
  );
}

function Pasos({ video }: { video: VideoConReporte }) {
  const actual = pasoActual(video.estado);
  const fallo = video.estado === "fallido";
  return (
    <ol className="mt-6 grid grid-cols-4 gap-2" aria-label="Progreso">
      {PASOS.map((p, i) => {
        const hecho = i < actual || (i === actual && !enCurso(video.estado) && !fallo);
        const enMarcha = i === actual && enCurso(video.estado);
        return (
          <li key={p.id} className="text-center">
            <div
              className={
                "mx-auto flex h-9 w-9 items-center justify-center rounded-full border text-xs " +
                (hecho
                  ? "border-state-ok/50 bg-state-ok-bg text-state-ok"
                  : enMarcha
                    ? "border-accent text-acento"
                    : fallo && i === actual
                      ? "border-state-alert/50 bg-state-alert-bg text-state-alert"
                      : "border-border text-muted-foreground")
              }
              aria-current={enMarcha ? "step" : undefined}
            >
              {hecho ? (
                <Check className="h-4 w-4" aria-hidden="true" />
              ) : enMarcha ? (
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              ) : fallo && i === actual ? (
                <AlertTriangle className="h-4 w-4" aria-hidden="true" />
              ) : (
                i + 1
              )}
            </div>
            <p className={"mt-2 text-xs " + (hecho || enMarcha ? "text-foreground" : "text-muted-foreground")}>{p.etiqueta}</p>
          </li>
        );
      })}
    </ol>
  );
}

/** Qué hace el análisis, en el orden del pipeline. Sin marcas de avance: el servidor todavía no informa la etapa (R3). */
function Etapas() {
  return (
    <div className="mt-7 border-t border-border pt-5">
      <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Lo que hace el análisis</h3>
      <ul className="mt-4 space-y-4">
        {ETAPAS.map((e) => (
          <li key={e.id}>
            <p className="font-semibold">{e.titulo}</p>
            <p className="text-sm text-muted-foreground">{e.detalle}</p>
            <p className="mt-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground/80">{e.id}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Fallo({ video, fps, alCambiar }: { video: VideoConReporte; fps: number | null; alCambiar: () => Promise<void> }) {
  const t = textoDeFallo(video.motivo_fallo, { fps, intentos: video.intentos });
  const sesion = video.sesiones;
  const [trabajando, setTrabajando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [modo, setModo] = useState<string>("");

  async function reenviar() {
    setTrabajando(true);
    setMensaje(null);
    const r = await reintentar(video.id);
    setTrabajando(false);
    if (!r.ok) setMensaje(r.texto);
    await alCambiar();
  }

  async function cambiarYReenviar(nuevo: ModoCaptura) {
    if (!sesion) return;
    setTrabajando(true);
    setMensaje(null);
    const c = await corregirModo(sesion.id, nuevo);
    if (!c.ok) {
      setTrabajando(false);
      return setMensaje(c.texto);
    }
    await reenviar();
  }

  return (
    <div role="alert" className="mt-6 rounded-xl border border-state-alert/40 bg-state-alert-bg p-4">
      <p className="flex items-start gap-2 font-semibold">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-state-alert" aria-hidden="true" />
        {t.titulo}
      </p>
      <p className="mt-2 text-sm">{t.texto}</p>
      {t.contador && <p className="mt-2 font-mono text-xs uppercase tracking-widest text-muted-foreground">{t.contador}</p>}

      <div className="mt-4 flex flex-wrap items-center gap-3">
        {t.accion === "subir_otro" && (
          <Link to="/upload" className="inline-flex min-h-11 items-center rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground">
            Subir otro archivo
          </Link>
        )}
        {t.accion === "reintentar" && (
          <button
            type="button"
            onClick={() => void reenviar()}
            disabled={trabajando}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground disabled:opacity-60"
          >
            {trabajando ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="h-4 w-4" aria-hidden="true" />}
            Reintentar
          </button>
        )}
        {t.accion === "corregir_modo" && (
          <div className="flex w-full flex-wrap items-end gap-3">
            <div className="min-w-56 flex-1">
              <label htmlFor="modo-nuevo" className="text-sm font-medium">¿Cómo lo grabaste?</label>
              <select
                id="modo-nuevo"
                value={modo}
                onChange={(e) => setModo(e.target.value)}
                className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm"
              >
                <option value="" disabled>Elegí una opción</option>
                {MODOS_CAPTURA.map((m) => (
                  <option key={m.valor} value={m.valor}>{m.etiqueta}</option>
                ))}
              </select>
            </div>
            <button
              type="button"
              disabled={trabajando || !esValor(MODOS_CAPTURA, modo)}
              onClick={() => esValor(MODOS_CAPTURA, modo) && void cambiarYReenviar(modo)}
              className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground disabled:opacity-60"
            >
              Corregir y reintentar
            </button>
          </div>
        )}
      </div>

      {video.motivo_fallo === "archivo_convertido" && (
        <p className="mt-4 text-sm text-muted-foreground">
          ¿No era cámara lenta?{" "}
          <button
            type="button"
            disabled={trabajando}
            onClick={() => void cambiarYReenviar("normal")}
            className="underline underline-offset-4 hover:text-foreground"
          >
            Cambiar a grabación normal y reintentar
          </button>{" "}
          (con menos de 120 fps solo se analizaría la preparación).
        </p>
      )}
      {mensaje && <p role="status" className="mt-3 text-sm">{mensaje}</p>}
    </div>
  );
}

function Resultado({ video, reporte, fps }: { video: VideoConReporte; reporte: Record<string, unknown> | null; fps: number | null }) {
  const obs = observacionesDe(reporte);
  const t = (reporte?.trazabilidad ?? null) as Record<string, unknown> | null;
  const reg = (t?.regularizacion ?? null) as Record<string, unknown> | null;
  const latencia = latenciaDe(video);

  // Parcial sin reporte: R1 (menos de 120 fps efectivos). El motor no analiza la secuencia y lo dice.
  if (!reporte) {
    return (
      <div className="mt-6 rounded-xl border border-border p-4 text-sm">
        <p className="flex items-center gap-2">
          <EstadoBadge estado="no-auditable" />
        </p>
        <p className="mt-3">
          {fps !== null && fps < 120
            ? `Este video tiene ${Math.round(fps)} fps. Con menos de 120 fps solo se podría analizar la fase de preparación, que todavía no está disponible: no se midió el orden de los picos.`
            : "El análisis no produjo un reporte para este video."}
        </p>
      </div>
    );
  }

  return (
    <div className="mt-7 border-t border-border pt-5">
      <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Lo que se observa</h3>
      <ul className="mt-4 space-y-4">
        {obs.map((o, i) => (
          <Observacion key={i} o={o} />
        ))}
      </ul>

      <h3 className="mt-8 font-mono text-xs uppercase tracking-widest text-muted-foreground">Trazabilidad</h3>
      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
        <Dato k="Frecuencia real medida" v={fps !== null ? `${fps.toFixed(1)} fps` : "—"} />
        <Dato k="Frecuencia nominal" v={numero(t?.fps_nominal as number | null) !== null ? `${Number(t?.fps_nominal).toFixed(0)} fps` : "—"} />
        <Dato k="Fotogramas perdidos" v={numero(t?.fotogramas_perdidos_pct as number | null) !== null ? `${Number(t?.fotogramas_perdidos_pct).toFixed(1)} %` : "—"} />
        <Dato k="Puntos interpolados" v={reg ? `${Number(reg.puntos_interpolados_pct).toFixed(1)} %` : "no se regularizó"} />
        <Dato k="Escala temporal" v={t?.escala_temporal_conocida === true ? "conocida" : "no confirmada"} />
        <Dato k="Versión del motor" v={`${String(t?.version_motor ?? "—")} · ${String(t?.backend_pose ?? "—")}`} />
        {latencia !== null && <Dato k="Tardó en procesarse" v={formatearDuracion(latencia)} />}
      </dl>
      <p className="mt-6 text-xs text-muted-foreground">
        El sistema documenta lo que se observa; la conclusión es del profesional.
      </p>
    </div>
  );
}

function Dato({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{k}</dt>
      <dd className="mt-0.5 font-mono text-sm">{v}</dd>
    </div>
  );
}

function Observacion({ o }: { o: ObservacionLeida }) {
  const clave = BADGE_POR_SEVERIDAD[o.severidad];
  return (
    <li className="rounded-xl border border-border p-4">
      {clave === "sin_evaluar" ? (
        <SinEvaluarBadge />
      ) : clave ? (
        <EstadoBadge estado={clave} />
      ) : null}
      <p className="mt-3 text-sm leading-relaxed">{o.texto}</p>
      {o.fundamento && <p className="mt-2 font-mono text-xs text-muted-foreground">{o.fundamento}</p>}
      {o.referencia && <p className="mt-1 text-xs text-muted-foreground">Fuente: {o.referencia}</p>}
    </li>
  );
}

