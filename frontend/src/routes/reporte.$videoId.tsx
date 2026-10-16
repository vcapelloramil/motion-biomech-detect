import { useEffect, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ChevronDown, Info, Loader2 } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { BadgePorClave, type Estado } from "@/components/estado";
import { SecuenciaReal } from "@/components/reporte/secuencia-real";
import { TresMomentos } from "@/components/reporte/tres-momentos";
import { BotonDescargarPdf } from "@/components/reporte/pdf";
import { DocumentoDeGolpe } from "@/components/reporte/documento-golpe";
import { useSesion } from "@/lib/sesion";
import {
  ENCUADRE_ETIQUETA,
  GESTO_ETIQUETA,
  TEXTO_VERSION_ANTERIOR,
  enCurso,
  versionAnteriorA,
  formatearDuracion,
  tiemposDe,
  numero,
  observacionesDe,
  reporteDe,
} from "@/lib/estado-video";
import {
  NOMBRE_SEGMENTO,
  artefactosDe,
  coberturaDe,
  fraseDeSecuencia,
  fundamentosSinRepetir,
  magnitudesDe,
  masImportantes,
  picosNoMedidosDe,
  picosOrdenados,
  repeticionesDe,
  resolucionTexto,
  tramosNoAuditablesDe,
  trazabilidadDe,
} from "@/lib/reporte-simple";
import { leerVideo, urlsDeArtefactos, type VideoConReporte } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

export const Route = createFileRoute("/reporte/$videoId")({
  head: () => ({ meta: [{ title: "Reporte — KinetiQ" }, { name: "robots", content: "noindex" }] }),
  component: () => (
    <RutaProtegida>
      <ReportePage />
    </RutaProtegida>
  ),
});

const BADGE: Record<string, Estado | "sin_evaluar" | "sin_diferencia"> = {
  correcto: "correcto",
  desvio_leve: "desvio",
  alerta_de_carga: "alerta",
  no_auditable: "no-auditable",
  sin_evaluar: "sin_evaluar",
  sin_diferencia_medible: "sin_diferencia",
};

const BORDE: Record<string, string> = {
  correcto: "border-state-ok/40",
  desvio_leve: "border-state-warn/40",
  alerta_de_carga: "border-state-alert/40",
  no_auditable: "border-border",
  sin_evaluar: "border-border border-dashed",
  sin_diferencia_medible: "border-border border-dashed",
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
  const observaciones = observacionesDe(reporte);
  const { visibles, ocultas } = masImportantes(observaciones);
  const fundamentos = fundamentosSinRepetir(observaciones);
  const frase = fraseDeSecuencia(r0, fps, t.tolerancia_orden_ms);
  const artefactos = artefactosDe(reporte);
  const magnitudes = magnitudesDe(reporte);
  const picos = picosOrdenados(r0);
  const tramos = tramosNoAuditablesDe(reporte);
  const inicioVentana = r0?.desde_s ?? null;
  const cobertura = coberturaDe(reporte);
  const tiempos = tiemposDe(video);
  const fecha = sesion ? new Date(sesion.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" }) : null;

  return (
    <>
    <main className="mx-auto max-w-5xl px-5 py-10 md:py-14 print:hidden">
      <nav aria-label="Ruta" className="font-mono text-xs text-muted-foreground print:hidden">
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
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <p className="text-muted-foreground">
          {fecha ? `${fecha} · ` : ""}
          {fps !== null ? `${Math.round(fps)} fps reales · ` : ""}
          {sesion ? `cámara de ${ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre}` : ""}
          {sesion?.atletas?.nombre ? ` · ${sesion.atletas.nombre}` : ""}
        </p>
        <BotonDescargarPdf />
      </div>

      {versionAnteriorA(t.version_motor) && (
        <p role="note" className="mt-6 rounded-xl border border-dashed border-border px-4 py-3 text-sm text-muted-foreground">
          Este reporte se calculó con una versión anterior del motor{t.version_motor ? ` (${t.version_motor})` : ""} y no se vuelve a calcular.
          Para ver el análisis con la versión actual, volvé a subir el golpe.
        </p>
      )}

      {/* Nivel 1 — lo más importante: máximo tres observaciones, en lenguaje llano. */}
      <section aria-labelledby="importante" className="mt-10">
        <h2 id="importante" className="font-mono text-xs uppercase tracking-widest text-state-ok">Lo más importante</h2>
        <ul className="mt-4 grid gap-4 md:grid-cols-3">
          {visibles.map((o, i) => {
            const clave = BADGE[o.severidad];
            return (
              <li key={i} className={"flex flex-col rounded-2xl border bg-card p-5 " + (BORDE[o.severidad] ?? "border-border")}>
                <BadgePorClave clave={clave} className="self-start" />
                {/* Nivel 1: lenguaje llano. El fundamento y la fuente de cada observación están en "Ver detalle técnico". */}
                <p className="mt-4 text-base font-semibold leading-snug">{o.texto}</p>
                {o.anterior && <p className="mt-2 text-xs text-muted-foreground">{TEXTO_VERSION_ANTERIOR}.</p>}
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
        <div className="mt-5 overflow-x-auto rounded-2xl border border-border bg-card p-4 md:p-6">
          <SecuenciaReal picos={picos} mostrarTiempos={t.escala_conocida} fps={fps} />
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

      {/* Tres momentos del golpe y video con esqueleto (artefactos del motor; ausentes = no generados). */}
      {(artefactos.fotogramas.length > 0 || artefactos.overlay) && (
        <TresMomentos artefactos={artefactos} noMedidos={picosNoMedidosDe(reporte)} />
      )}

      {/* Nivel 3, plegado: dato y fundamento. */}
      <details className="group mt-12 rounded-2xl border border-border bg-card">
        <summary className="flex min-h-14 cursor-pointer list-none items-center justify-between px-5 font-display text-lg font-bold">
          Ver detalle técnico
          <ChevronDown className="h-5 w-5 transition-transform group-open:rotate-180" aria-hidden="true" />
        </summary>
        <div className="space-y-8 border-t border-border p-5">
          {fundamentos.length > 0 && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Observaciones y su fundamento</h3>
              <ul className="mt-3 space-y-3">
                {fundamentos.map((o, i) => {
                  const clave = BADGE[o.severidad];
                  return (
                    <li key={i} className="rounded-xl border border-border p-4 text-sm">
                      <BadgePorClave clave={clave} />
                      <p className="mt-2">{o.texto}</p>
                      {o.anterior && <p className="mt-1 text-xs text-muted-foreground">{TEXTO_VERSION_ANTERIOR}.</p>}
                      {o.fundamento && <p className="mt-1 font-mono text-xs text-muted-foreground">{o.fundamento}</p>}
                      {o.referencia && <p className="mt-1 text-xs text-muted-foreground">Fuente: {o.referencia}</p>}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          <div>
            <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Trazabilidad</h3>
            <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-3">
              <Dato k="Frecuencia real medida" v={t.fps_real !== null ? `${fmt(t.fps_real, 1)} fps` : "—"} />
              <Dato k="Frecuencia nominal" v={t.fps_nominal !== null ? `${fmt(t.fps_nominal, 0)} fps` : "—"} />
              <Dato k="Fotogramas perdidos" v={t.fotogramas_perdidos_pct !== null ? `${fmt(t.fotogramas_perdidos_pct, 1)} %` : "—"} />
              <Dato k="Puntos interpolados" v={t.puntos_interpolados_pct !== null ? `${fmt(t.puntos_interpolados_pct, 1)} %` : "no se regularizó"} />
              <Dato k="Escala temporal" v={t.escala_conocida ? "conocida" : "no confirmada"} />
              <Dato k="Resolución" v={resolucionTexto(t.fps_real ?? fps) ?? "—"} />
              <Dato
                k="Tolerancia del orden"
                v={t.tolerancia_orden_ms !== null ? `${fmt(t.tolerancia_orden_ms, 1)} ms` : "no registrada (reporte anterior)"}
              />
              <Dato k="Cobertura auditable" v={cobertura !== null ? `${fmt(cobertura, 1)} %` : "—"} />
              <Dato k="Modo de captura declarado" v={t.modo_captura ?? "—"} />
              <Dato k="Motor" v={`${t.version_motor ?? "—"} · ${t.backend_pose ?? "—"}`} />
              {tiempos.espera_cola_s !== null && <Dato k="Esperó en la cola" v={formatearDuracion(tiempos.espera_cola_s)} />}
              {tiempos.procesamiento_s !== null && <Dato k="Procesamiento" v={formatearDuracion(tiempos.procesamiento_s)} />}
            </dl>
            {t.puntos_interpolados !== null && t.puntos_de_la_grilla !== null && t.fps_real !== null && (
              <p className="mt-3 text-xs text-muted-foreground">
                El teléfono graba sobre un reloj de 240 fotogramas por segundo y entregó {fmt(t.fps_real, 1)} en promedio: los fotogramas que faltaron
                (los mismos {fmt(t.fotogramas_perdidos_pct ?? 0, 1)} %) se reconstruyen por interpolación para tener un muestreo parejo. Fueron{" "}
                {t.puntos_interpolados} de {t.puntos_de_la_grilla} puntos
                {t.hueco_maximo_ms !== null ? `, con huecos de hasta ${fmt(t.hueco_maximo_ms, 1)} ms` : ""}. Un instante que cae en uno de esos
                puntos es una reconstrucción, no una medición.
              </p>
            )}
          </div>

          {picos.length > 0 && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Velocidad máxima por segmento</h3>
              <div className="mt-3 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    <tr>
                      <th className="py-2 pr-4">Segmento</th>
                      <th className="py-2 pr-4">Desde el inicio de la ventana</th>
                      {inicioVentana !== null && <th className="py-2 pr-4">En el video</th>}
                      <th className="py-2 pr-4">Velocidad</th>
                      <th className="py-2">Confianza</th>
                    </tr>
                  </thead>
                  <tbody>
                    {picos.map((p) => (
                      <tr key={p.segmento} className="border-t border-border">
                        <td className="py-2 pr-4 font-semibold">{{ pelvis: "Cadera", torso: "Tronco", brazo: "Brazo" }[p.segmento]}</td>
                        <td className="py-2 pr-4 font-mono">{t.escala_conocida ? `${fmt(p.instante_s, 3)} s` : "no auditable"}</td>
                        {inicioVentana !== null && (
                          <td className="py-2 pr-4 font-mono">{t.escala_conocida ? `${fmt(inicioVentana + p.instante_s, 3)} s` : "no auditable"}</td>
                        )}
                        <td className="py-2 pr-4 font-mono">{t.escala_conocida ? `${fmt(p.velocidad, 0)} ${p.unidad}` : "no auditable"}</td>
                        <td className="py-2 font-mono">{fmt(p.confianza, 2)}</td>
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

          {magnitudes.length > 0 && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Magnitudes articulares</h3>
              <div className="mt-3 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    <tr><th className="py-2 pr-4">Magnitud</th><th className="py-2 pr-4">Valor</th><th className="py-2 pr-4">Confianza</th><th className="py-2">Qué tan confiable es</th></tr>
                  </thead>
                  <tbody>
                    {magnitudes.map((m) => (
                      <tr key={m.nombre} className="border-t border-border align-top">
                        <td className="py-2 pr-4 font-semibold">{m.etiqueta}</td>
                        <td className="py-2 pr-4 font-mono">{m.auditable && m.valor !== null ? `${fmt(m.valor, 1)} °` : "no auditable"}</td>
                        <td className="py-2 pr-4 font-mono">{fmt(m.confianza, 2)}</td>
                        <td className="py-2 text-xs text-muted-foreground">{m.nota}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Son datos de tu golpe: el sistema no los juzga porque no hay un rango de referencia propio para compararlos todavía.
              </p>
            </div>
          )}

          {tramos.length > 0 && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Tramos no auditables</h3>
              <p className="mt-2 text-xs text-muted-foreground">
                Tiempos desde el inicio del <strong>video</strong>
                {inicioVentana !== null ? ` (la ventana analizada empieza en ${fmt(inicioVentana, 2)} s)` : ""}. Un tramo sin datos de una
                articulación solo afecta al segmento que la usa.
              </p>
              <ul className="mt-3 space-y-2 text-sm">
                {tramos.map((tr, i) => (
                  <li key={i} className="rounded-xl border border-border px-4 py-2">
                    <span className="font-mono">{fmt(tr.desde_s, 2)} s – {fmt(tr.hasta_s, 2)} s</span> · {tr.motivo.replace("sin_datos_confiables: ", "sin datos confiables en ")}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </details>

    </main>
    {/* El PDF es un documento aparte (A4 vertical), no esta pantalla impresa: ver documento-golpe.tsx. */}
    <DocumentoDeGolpe video={video} reporte={reporte} />
    </>
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
