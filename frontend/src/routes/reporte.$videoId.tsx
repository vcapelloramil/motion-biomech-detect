import { useEffect, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ChevronDown, Info, Loader2 } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { EstadoBadge, SinEvaluarBadge, type Estado } from "@/components/estado";
import { SecuenciaReal } from "@/components/reporte/secuencia-real";
import { useSesion } from "@/lib/sesion";
import {
  ENCUADRE_ETIQUETA,
  GESTO_ETIQUETA,
  enCurso,
  formatearDuracion,
  latenciaDe,
  numero,
  observacionesDe,
  reporteDe,
} from "@/lib/estado-video";
import {
  coberturaDe,
  fraseDeSecuencia,
  masImportantes,
  picosOrdenados,
  repeticionesDe,
  tramosNoAuditablesDe,
  trazabilidadDe,
} from "@/lib/reporte-simple";
import { leerVideo, type VideoConReporte } from "@/lib/videos-data";

export const Route = createFileRoute("/reporte/$videoId")({
  head: () => ({ meta: [{ title: "Reporte — KinetiQ" }, { name: "robots", content: "noindex" }] }),
  component: () => (
    <RutaProtegida>
      <ReportePage />
    </RutaProtegida>
  ),
});

const BADGE: Record<string, Estado | "sin_evaluar"> = {
  correcto: "correcto",
  desvio_leve: "desvio",
  alerta_de_carga: "alerta",
  no_auditable: "no-auditable",
  sin_evaluar: "sin_evaluar",
};

const BORDE: Record<string, string> = {
  correcto: "border-state-ok/40",
  desvio_leve: "border-state-warn/40",
  alerta_de_carga: "border-state-alert/40",
  no_auditable: "border-border",
  sin_evaluar: "border-border border-dashed",
};

function ReportePage() {
  const { videoId } = Route.useParams();
  const { cargando } = useSesion();
  const [video, setVideo] = useState<VideoConReporte | null | undefined>(undefined);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (cargando) return;
    let activo = true;
    leerVideo(videoId)
      .then((v) => activo && setVideo(v))
      .catch(() => {
        if (!activo) return;
        setError(true);
        setVideo(null);
      });
    return () => {
      activo = false;
    };
  }, [videoId, cargando]);

  if (video === undefined) {
    return (
      <main className="mx-auto max-w-5xl px-5 py-16">
        <p role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando el reporte…
        </p>
      </main>
    );
  }
  if (video === null) return <SinReporte titulo="No encontramos este reporte" texto={error ? "No pudimos leerlo ahora. Probá de nuevo en un momento." : "No existe o no es tuyo."} />;
  if (enCurso(video.estado)) {
    return (
      <SinReporte
        titulo="Todavía se está analizando"
        texto="Cuando termine, el reporte aparece acá."
        accion={{ to: "/procesando/$videoId", params: { videoId: video.id }, etiqueta: "Ver el progreso" }}
      />
    );
  }

  const rep = reporteDe(video)?.reporte ?? null;
  if (!rep) {
    return (
      <SinReporte
        titulo="Este golpe no tiene reporte"
        texto="El análisis no llegó a medir la secuencia de este video. Podés ver qué pasó."
        accion={{ to: "/procesando/$videoId", params: { videoId: video.id }, etiqueta: "Ver qué pasó" }}
      />
    );
  }
  return <Reporte video={video} reporte={rep} />;
}

function SinReporte({
  titulo,
  texto,
  accion,
}: {
  titulo: string;
  texto: string;
  accion?: { to: "/procesando/$videoId"; params: { videoId: string }; etiqueta: string };
}) {
  return (
    <main className="mx-auto max-w-3xl px-5 py-16">
      <p className="font-mono text-xs uppercase tracking-widest text-acento">/ Reporte</p>
      <h1 className="mt-4 font-display text-3xl font-extrabold md:text-5xl">{titulo}</h1>
      <p className="mt-3 text-muted-foreground">{texto}</p>
      <div className="mt-6 flex flex-wrap gap-3">
        {accion && (
          <Link to={accion.to} params={accion.params} className="inline-flex min-h-11 items-center rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground">
            {accion.etiqueta}
          </Link>
        )}
        <Link to="/videos" className="inline-flex min-h-11 items-center rounded-xl border border-border px-5 text-sm font-semibold">
          Volver a la biblioteca
        </Link>
      </div>
    </main>
  );
}

function Reporte({ video, reporte }: { video: VideoConReporte; reporte: Record<string, unknown> }) {
  const sesion = video.sesiones;
  const t = trazabilidadDe(reporte);
  const fps = t.fps_real ?? numero(video.fps_real);
  const reps = repeticionesDe(reporte);
  const r0 = reps[0] ?? null;
  const { visibles, ocultas } = masImportantes(observacionesDe(reporte));
  const frase = fraseDeSecuencia(r0, fps);
  const picos = picosOrdenados(r0);
  const tramos = tramosNoAuditablesDe(reporte);
  const cobertura = coberturaDe(reporte);
  const latencia = latenciaDe(video);
  const fecha = sesion ? new Date(sesion.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" }) : null;

  return (
    <main className="mx-auto max-w-5xl px-5 py-10 md:py-14">
      <nav aria-label="Ruta" className="font-mono text-xs text-muted-foreground">
        <Link to="/videos" className="hover:text-foreground">Biblioteca</Link>
        {sesion && (
          <>
            {" / "}
            {GESTO_ETIQUETA[sesion.gesto] ?? sesion.gesto} · {ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre}
            {fecha ? ` · ${fecha}` : ""}
          </>
        )}
      </nav>

      <h1 className="mt-4 font-display text-4xl font-extrabold tracking-tight md:text-6xl">
        {sesion ? (GESTO_ETIQUETA[sesion.gesto] ?? sesion.gesto) : "Golpe"} <span className="text-gradient-neon">· 1 golpe</span>
      </h1>
      <p className="mt-3 text-muted-foreground">
        {fecha ? `${fecha} · ` : ""}
        {fps !== null ? `${Math.round(fps)} fps reales · ` : ""}
        {sesion ? `cámara de ${ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre}` : ""}
        {sesion?.atletas?.nombre ? ` · ${sesion.atletas.nombre}` : ""}
      </p>

      {/* Nivel 1 — veredicto: máximo tres observaciones, en lenguaje llano. */}
      <section aria-labelledby="importante" className="mt-10">
        <h2 id="importante" className="font-mono text-xs uppercase tracking-widest text-state-ok">Lo más importante</h2>
        <ul className="mt-4 grid gap-4 md:grid-cols-3">
          {visibles.map((o, i) => {
            const clave = BADGE[o.severidad];
            return (
              <li key={i} className={"flex flex-col rounded-2xl border bg-card p-5 " + (BORDE[o.severidad] ?? "border-border")}>
                {clave === "sin_evaluar" ? <SinEvaluarBadge className="self-start" /> : clave ? <EstadoBadge estado={clave} className="self-start" /> : null}
                <p className="mt-4 text-base font-semibold leading-snug">{o.texto}</p>
                {o.fundamento && <p className="mt-3 text-sm text-muted-foreground">{o.fundamento}</p>}
                {o.referencia && <p className="mt-2 text-xs text-muted-foreground">Fuente: {o.referencia}</p>}
              </li>
            );
          })}
          {visibles.length === 0 && (
            <li className="rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground md:col-span-3">
              Este golpe no produjo observaciones.
            </li>
          )}
        </ul>
        {ocultas.length > 0 && (
          <p className="mt-3 text-sm text-muted-foreground">
            {ocultas.length === 1 ? "Hay 1 observación más" : `Hay ${ocultas.length} observaciones más`} en el detalle técnico.
          </p>
        )}
      </section>

      {/* Elemento central: eje temporal único con los picos. */}
      <section aria-labelledby="secuencia" className="mt-12">
        <h2 id="secuencia" className="font-mono text-xs uppercase tracking-widest text-state-ok">Tu golpe en el tiempo</h2>
        <p className="mt-2 font-display text-2xl font-bold md:text-3xl">Cuándo alcanzó su velocidad máxima cada parte</p>
        <div className="mt-5 rounded-2xl border border-border bg-card p-4 md:p-6">
          <SecuenciaReal picos={picos} mostrarTiempos={t.escala_conocida} fps={t.fps_grilla ?? fps} />
        </div>
        <p
          className={
            "mt-4 flex items-start gap-3 rounded-2xl border bg-card px-4 py-3 text-sm " +
            (frase.tipo === "simultaneo" ? "border-border border-dashed" : "border-border")
          }
        >
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-acento" aria-hidden="true" />
          {frase.texto}
        </p>
      </section>

      {/* Nivel 3, plegado: dato y fundamento. */}
      <details className="group mt-12 rounded-2xl border border-border bg-card">
        <summary className="flex min-h-14 cursor-pointer list-none items-center justify-between px-5 font-display text-lg font-bold">
          Ver detalle técnico
          <ChevronDown className="h-5 w-5 transition-transform group-open:rotate-180" aria-hidden="true" />
        </summary>
        <div className="space-y-8 border-t border-border p-5">
          {ocultas.length > 0 && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Otras observaciones</h3>
              <ul className="mt-3 space-y-3">
                {ocultas.map((o, i) => {
                  const clave = BADGE[o.severidad];
                  return (
                    <li key={i} className="rounded-xl border border-border p-4 text-sm">
                      {clave === "sin_evaluar" ? <SinEvaluarBadge /> : clave ? <EstadoBadge estado={clave} /> : null}
                      <p className="mt-2">{o.texto}</p>
                      {o.fundamento && <p className="mt-1 font-mono text-xs text-muted-foreground">{o.fundamento}</p>}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          <div>
            <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Trazabilidad</h3>
            <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-3">
              <Dato k="Frecuencia real medida" v={t.fps_real !== null ? `${t.fps_real.toFixed(1)} fps` : "—"} />
              <Dato k="Frecuencia nominal" v={t.fps_nominal !== null ? `${t.fps_nominal.toFixed(0)} fps` : "—"} />
              <Dato k="Fotogramas perdidos" v={t.fotogramas_perdidos_pct !== null ? `${t.fotogramas_perdidos_pct.toFixed(1)} %` : "—"} />
              <Dato k="Puntos interpolados" v={t.puntos_interpolados_pct !== null ? `${t.puntos_interpolados_pct.toFixed(1)} %` : "no se regularizó"} />
              <Dato k="Escala temporal" v={t.escala_conocida ? "conocida" : "no confirmada"} />
              <Dato k="Cobertura auditable" v={cobertura !== null ? `${cobertura.toFixed(1)} %` : "—"} />
              <Dato k="Modo de captura declarado" v={t.modo_captura ?? "—"} />
              <Dato k="Motor" v={`${t.version_motor ?? "—"} · ${t.backend_pose ?? "—"}`} />
              {latencia !== null && <Dato k="Tardó en procesarse" v={formatearDuracion(latencia)} />}
            </dl>
          </div>

          {picos.length > 0 && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Velocidad máxima por segmento</h3>
              <div className="mt-3 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    <tr><th className="py-2 pr-4">Segmento</th><th className="py-2 pr-4">Instante</th><th className="py-2 pr-4">Velocidad</th><th className="py-2">Confianza</th></tr>
                  </thead>
                  <tbody>
                    {picos.map((p) => (
                      <tr key={p.segmento} className="border-t border-border">
                        <td className="py-2 pr-4 font-semibold">{{ pelvis: "Cadera", torso: "Tronco", brazo: "Brazo" }[p.segmento]}</td>
                        <td className="py-2 pr-4 font-mono">{t.escala_conocida ? `${p.instante_s.toFixed(3)} s` : "no auditable"}</td>
                        <td className="py-2 pr-4 font-mono">{t.escala_conocida ? `${p.velocidad.toFixed(0)} ${p.unidad}` : "no auditable"}</td>
                        <td className="py-2 font-mono">{p.confianza.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {!t.escala_conocida && (
                <p className="mt-2 text-xs text-muted-foreground">Sin escala temporal confirmada, los tiempos y las velocidades no son auditables (R3).</p>
              )}
            </div>
          )}

          {tramos.length > 0 && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Tramos no auditables</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {tramos.map((tr, i) => (
                  <li key={i} className="rounded-xl border border-border px-4 py-2">
                    <span className="font-mono">{tr.desde_s.toFixed(2)} s – {tr.hasta_s.toFixed(2)} s</span> · {tr.motivo.replace("sin_datos_confiables: ", "sin datos confiables en ")}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </details>

      <p className="mt-10 text-center text-xs text-muted-foreground">
        KinetiQ documenta el movimiento. No diagnostica ni reemplaza la evaluación de un profesional.
      </p>
    </main>
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
