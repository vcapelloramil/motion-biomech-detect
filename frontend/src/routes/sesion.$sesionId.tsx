import { useCallback, useEffect, useMemo, useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { ArrowRight, CircleDashed, Loader2, Trash2 } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { EstadoBadge, SinDiferenciaBadge } from "@/components/estado";
import { TresMomentos } from "@/components/reporte/tres-momentos";
import { DetalleTecnico, EnUnaFrase, ParaTuProfesional, PieDeTextos, QuePodesHacer, QueVimos } from "@/components/reporte/bloques";
import { DocumentoDeSesion } from "@/components/reporte/documento-sesion";
import { useSesion } from "@/lib/sesion";
import {
  ENCUADRE_ETIQUETA,
  GESTO_ETIQUETA,
  TEXTO_VERSION_ANTERIOR,
  enCurso,
  golpeMedido,
  ordenDistinguible,
  reporteDe,
  reporteDeVersionAnterior,
  tiemposDe,
  formatearDuracion,
  type EstadoVideo,
} from "@/lib/estado-video";
import { NOTA_MEZCLA_DE_VERSIONES, type Consistencia } from "@/lib/consistencia";
import { leerConsistencia } from "@/lib/consistencia-api";
import { artefactosDe, picosNoMedidosDe, repeticionesDe } from "@/lib/reporte-simple";
import { fotosDe, textosDeSesion } from "@/lib/textos-reporte";
import { eliminarGolpe, eliminarSesion, leerSesion, type SesionConVideos } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

export const Route = createFileRoute("/sesion/$sesionId")({
  head: () => ({ meta: [{ title: "Sesión — KinetiQ" }, { name: "robots", content: "noindex" }] }),
  component: () => (
    <RutaProtegida>
      <SesionPage />
    </RutaProtegida>
  ),
});

const ETIQUETA_ESTADO: Record<EstadoVideo, string> = {
  pendiente: "Subido",
  encolado: "En cola",
  procesando: "Analizando",
  completado: "Medido",
  parcial: "Medido",
  fallido: "No se pudo",
};

function SesionPage() {
  const { sesionId } = Route.useParams();
  const { sesion: auth, cargando } = useSesion();
  const navegar = useNavigate();
  const [datos, setDatos] = useState<SesionConVideos | null | undefined>(undefined);
  const [error, setError] = useState(false);
  const [consistencia, setConsistencia] = useState<Consistencia | null>(null);
  const [elegido, setElegido] = useState<string | null>(null);
  const [confirmar, setConfirmar] = useState<string | null>(null); // id del golpe, o "sesion"
  const [borrando, setBorrando] = useState(false);

  const cargar = useCallback(async () => {
    try {
      const s = await leerSesion(sesionId);
      setDatos(s);
      setError(false);
    } catch {
      setError(true);
      setDatos((previo) => previo ?? null);
    }
  }, [sesionId]);

  useEffect(() => {
    if (cargando) return;
    void cargar();
  }, [cargando, cargar]);

  const videos = datos?.videos ?? [];
  const hayEnCurso = videos.some((v) => enCurso(v.estado));
  // Mientras haya golpes analizándose, la vista se actualiza sola.
  useEffect(() => {
    if (!hayEnCurso) return;
    const t = window.setInterval(() => {
      if (document.visibilityState === "visible") void cargar();
    }, 8000);
    return () => window.clearInterval(t);
  }, [hayEnCurso, cargar]);

  // La consistencia se vuelve a pedir cuando cambia el estado de algún golpe (no en cada refresco).
  const firma = videos.map((v) => `${v.id}:${v.estado}`).join("|");
  const token = auth?.access_token;
  useEffect(() => {
    if (!datos || !token || videos.length === 0) return;
    let activo = true;
    leerConsistencia(sesionId, token).then((c) => activo && setConsistencia(c));
    return () => {
      activo = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [firma, token, sesionId]);

  const textos = useMemo(
    () =>
      datos
        ? textosDeSesion({
            gesto: datos.gesto,
            encuadre: datos.encuadre,
            ladoCamara: datos.lado_camara,
            manoDominante: datos.atletas?.mano_dominante ?? null,
            golpes: datos.videos.map((v) => ({ id: v.id, estado: v.estado, reporte: reporteDe(v)?.reporte ?? null })),
            consistencia,
          })
        : null,
    [datos, consistencia],
  );
  const numeroDe = useMemo(() => new Map(videos.map((v, i) => [v.id, i + 1])), [videos]);
  const valorDe = useMemo(() => new Map((consistencia?.separacion_cadera_hombro.valores ?? []).map((x) => [x.video_id, x.valor])), [consistencia]);
  const seApartan = new Set(consistencia?.golpes_que_se_apartan ?? []);

  if (datos === undefined) {
    return (
      <main className="mx-auto max-w-5xl px-5 py-16">
        <p role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando la sesión…
        </p>
      </main>
    );
  }
  if (datos === null) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-16">
        <h1 className="font-display text-3xl font-extrabold md:text-5xl">No encontramos esta sesión</h1>
        <p className="mt-3 text-muted-foreground">{error ? "No pudimos leerla ahora. Probá de nuevo en un momento." : "No existe o no es tuya."}</p>
        <Link to="/videos" className="mt-6 inline-flex min-h-11 items-center rounded-xl border border-border px-5 text-sm font-semibold">
          Volver a la biblioteca
        </Link>
      </main>
    );
  }

  const gesto = GESTO_ETIQUETA[datos.gesto] ?? datos.gesto;
  const encuadre = ENCUADRE_ETIQUETA[datos.encuadre] ?? datos.encuadre;
  const fecha = new Date(datos.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" });
  const listos = videos.filter((v) => !enCurso(v.estado)).length;

  // El golpe que se muestra en "Tres momentos": el elegido, y si no, el típico, y si no, el primero que tenga reporte.
  const conReporte = videos.filter((v) => reporteDe(v)?.reporte);
  const idMostrado =
    (elegido && videos.some((v) => v.id === elegido) ? elegido : null) ?? consistencia?.golpe_tipico ?? conReporte[0]?.id ?? null;
  const mostrado = videos.find((v) => v.id === idMostrado) ?? null;
  const repMostrado = reporteDe(mostrado ?? {})?.reporte ?? null;
  const artefactos = artefactosDe(repMostrado);
  const fotos = fotosDe(repMostrado);
  const algunoViejo = videos.some((v) => reporteDeVersionAnterior(reporteDe(v)?.reporte ?? null));

  async function borrarGolpe(id: string) {
    const v = videos.find((x) => x.id === id);
    if (!v) return;
    setBorrando(true);
    try {
      const r = await eliminarGolpe({ id: v.id, sesion_id: v.sesion_id, ruta_almacenamiento: v.ruta_almacenamiento, reportes_biomecanicos: v.reportes_biomecanicos });
      if (r.sesionEliminada) return void navegar({ to: "/videos" });
      setConfirmar(null);
      await cargar();
    } catch {
      setError(true);
    } finally {
      setBorrando(false);
    }
  }

  async function borrarSesion() {
    setBorrando(true);
    try {
      await eliminarSesion({ id: datos!.id, videos: datos!.videos });
      void navegar({ to: "/videos" });
    } catch {
      setError(true);
      setBorrando(false);
    }
  }

  return (
    <>
    <main className="mx-auto max-w-5xl px-5 py-10 md:py-14 print:hidden">
      <nav aria-label="Ruta" className="font-mono text-xs text-muted-foreground print:hidden">
        <Link to="/videos" className="hover:text-foreground">Biblioteca</Link>
        {" / "}
        {gesto} · {encuadre} · {fecha}
      </nav>

      <h1 className="mt-4 font-display text-4xl font-extrabold tracking-tight md:text-6xl">
        {gesto} <span className="text-gradient-neon">· {videos.length} {videos.length === 1 ? "golpe" : "golpes"}</span>
      </h1>
      <p className="mt-3 text-muted-foreground">
        {fecha} · cámara de {encuadre}
        {datos.atletas?.nombre ? ` · ${datos.atletas.nombre}` : ""}
      </p>

      {error && (
        <p role="alert" className="mt-4 rounded-xl border border-state-alert/40 bg-state-alert-bg px-4 py-3 text-sm">
          No pudimos completar la operación ahora. Probá de nuevo en un momento.
        </p>
      )}

      {hayEnCurso && (
        <p role="status" className="mt-6 flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 text-sm print:hidden">
          <Loader2 className="h-4 w-4 shrink-0 animate-spin" aria-hidden="true" />
          <span>
            <strong>{listos} de {videos.length}</strong> golpes analizados. Se analizan de a uno: la página se actualiza sola y podés cerrarla.
          </span>
        </p>
      )}

      {/* En una frase y Qué vimos: lo medido primero (decisión 039). */}
      {textos && consistencia ? (
        <>
          <EnUnaFrase texto={textos.enUnaFrase} />
          <QueVimos medido={textos.vimos.medido} noMedido={textos.vimos.noMedido} seAparta={textos.vimos.seAparta} sesionId={datos.id} />
          {consistencia.mezcla_de_versiones && <p className="mt-3 text-xs text-muted-foreground">{NOTA_MEZCLA_DE_VERSIONES}</p>}
        </>
      ) : (
        <section aria-labelledby="que-vimos" className="mt-10">
          <h2 id="que-vimos" className="font-mono text-xs uppercase tracking-widest text-state-ok">Qué vimos</h2>
          <p className="mt-4 rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground">
            {hayEnCurso ? "Se calcula cuando termine el análisis de los golpes." : "No pudimos calcular la comparación entre golpes ahora."}
          </p>
        </section>
      )}

      {/* Fotos y video de un golpe de la sesión: el típico por defecto (el más cercano al valor típico, no un golpe ejemplar). */}
      {conReporte.length > 0 && (
        <section aria-labelledby="golpe-elegido" className="mt-12">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 id="golpe-elegido" className="font-mono text-xs uppercase tracking-widest text-state-ok">
                {mostrado && mostrado.id === consistencia?.golpe_tipico ? "Fotos y video · tu golpe típico" : "Fotos y video · un golpe de la sesión"}
              </h2>
              <p className="mt-2 font-display text-2xl font-bold md:text-3xl">
                Golpe {mostrado ? numeroDe.get(mostrado.id) : "—"}
              </p>
            </div>
            <div role="group" aria-label="Elegir el golpe" className="flex flex-wrap gap-2 print:hidden">
              {videos.map((v) => {
                const tiene = !!reporteDe(v)?.reporte;
                const activo = v.id === idMostrado;
                return (
                  <button
                    key={v.id}
                    type="button"
                    disabled={!tiene}
                    aria-pressed={activo}
                    onClick={() => setElegido(v.id)}
                    className={
                      "min-h-10 min-w-10 rounded-lg border px-3 font-mono text-sm " +
                      (activo ? "border-neon bg-neon/10 text-neon" : "border-border text-muted-foreground hover:text-foreground") +
                      (tiene ? "" : " cursor-not-allowed opacity-40")
                    }
                  >
                    {numeroDe.get(v.id)}
                  </button>
                );
              })}
            </div>
          </div>
          {textos?.tipico && mostrado?.id === consistencia?.golpe_tipico && (
            <p className="mt-4 text-sm text-muted-foreground">{textos.tipico.texto}</p>
          )}
          {(artefactos.fotogramas.length > 0 || artefactos.overlay) && (
            <TresMomentos
              key={idMostrado ?? "ninguno"}
              artefactos={artefactos}
              noMedidos={picosNoMedidosDe(repMostrado)}
              textos={fotos}
              desdeS={repeticionesDe(repMostrado)[0]?.desde_s ?? null}
            />
          )}
          {textos?.tipico && mostrado?.id === consistencia?.golpe_tipico && <p className="mt-3 text-sm text-muted-foreground">{textos.tipico.queMirar}</p>}
          {mostrado && (
            <Link
              to="/reporte/$videoId"
              params={{ videoId: mostrado.id }}
              className="mt-5 inline-flex min-h-11 items-center gap-1.5 text-sm font-semibold text-state-ok hover:underline print:hidden"
            >
              Ver el reporte completo de este golpe <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          )}
        </section>
      )}

      {/* Todos los golpes */}
      <section aria-labelledby="todos" className="mt-12">
        <h2 id="todos" className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Los golpes de la sesión</h2>
        <ul className="mt-4 space-y-2">
          {videos.map((v) => {
            const n = numeroDe.get(v.id);
            const rep = reporteDe(v)?.reporte ?? null;
            const sep = valorDe.get(v.id);
            const t = tiemposDe(v);
            const nombre = v.ruta_almacenamiento?.split("/").pop() ?? "video";
            return (
              <li key={v.id} className="rounded-xl border border-border bg-card px-4 py-3">
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                  <span className="font-mono text-xs text-muted-foreground">Golpe {n}</span>
                  <span className="min-w-0 flex-1 truncate text-sm font-medium">{nombre}</span>
                  {v.estado === "fallido" ? (
                    <EstadoBadge estado="no-auditable">No se pudo medir</EstadoBadge>
                  ) : (
                    <span className="flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
                      {enCurso(v.estado) ? <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" /> : <CircleDashed className="h-3 w-3" aria-hidden="true" />}
                      {ETIQUETA_ESTADO[v.estado]}
                    </span>
                  )}
                  {sep !== undefined && <span className="font-mono text-sm">{fmt(sep, 0)}°</span>}
                  {golpeMedido(rep) && !ordenDistinguible(rep) && <SinDiferenciaBadge />}
                  {seApartan.has(v.id) && (
                    <span className="rounded-full border border-dashed border-border px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                      Se pareció menos
                    </span>
                  )}
                  <Link
                    to={rep ? "/reporte/$videoId" : "/procesando/$videoId"}
                    params={{ videoId: v.id }}
                    className="text-sm font-semibold text-state-ok hover:underline"
                  >
                    {rep ? "Ver reporte" : enCurso(v.estado) ? "Ver progreso" : "Ver qué pasó"}
                  </Link>
                  <button
                    type="button"
                    onClick={() => setConfirmar(confirmar === v.id ? null : v.id)}
                    className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground print:hidden"
                    aria-label={`Eliminar el golpe ${n}`}
                  >
                    <Trash2 className="h-3.5 w-3.5" aria-hidden="true" /> Eliminar
                  </button>
                </div>
                {t.espera_cola_s !== null && t.procesamiento_s !== null && (
                  <p className="mt-1 font-mono text-[11px] text-muted-foreground">
                    Esperó {formatearDuracion(t.espera_cola_s)} en la cola · procesamiento {formatearDuracion(t.procesamiento_s)}
                  </p>
                )}
                {confirmar === v.id && (
                  <div role="alert" className="mt-3 rounded-lg border border-destructive/50 px-3 py-2 text-sm">
                    ¿Eliminar el golpe {n}? Se borran el video y su reporte. No se puede deshacer.
                    <span className="mt-2 flex gap-3">
                      <button type="button" disabled={borrando} onClick={() => void borrarGolpe(v.id)} className="font-semibold text-destructive underline underline-offset-4">
                        {borrando ? "Eliminando…" : "Sí, eliminar"}
                      </button>
                      <button type="button" disabled={borrando} onClick={() => setConfirmar(null)} className="underline underline-offset-4">
                        Cancelar
                      </button>
                    </span>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
        {algunoViejo && <p className="mt-3 text-xs text-muted-foreground">{TEXTO_VERSION_ANTERIOR} en algunos golpes.</p>}
      </section>

      {textos && consistencia && (
        <>
          <QuePodesHacer medir={textos.hacer.medir} usar={textos.hacer.usar} literatura={textos.hacer.literatura} />
          <ParaTuProfesional profesional={textos.profesional} />
          <DetalleTecnico>
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Los golpes, uno por uno</h3>
              <div className="mt-3 overflow-x-auto">
                <table className="w-full min-w-[40rem] text-left text-sm">
                  <thead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    <tr>
                      {textos.detalle.columnas.map((c) => (
                        <th key={c} className="py-2 pr-4">{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {textos.detalle.filas.map((f) => (
                      <tr key={f[0]} className="border-t border-border align-top">
                        {f.map((c, k) => (
                          <td key={k} className={"py-2 pr-4 " + (k === 0 ? "font-semibold" : "font-mono")}>{c}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">{textos.detalle.nota}</p>
            </div>
            <div>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Qué significa cada término</h3>
              <dl className="mt-3 divide-y divide-border text-sm">
                {textos.detalle.terminos.map((x) => (
                  <div key={x.termino} className="grid gap-x-4 gap-y-1 py-2.5 md:grid-cols-[14rem_1fr]">
                    <dt className="font-semibold">{x.termino}</dt>
                    <dd className="text-muted-foreground">{x.significa}</dd>
                  </div>
                ))}
              </dl>
            </div>
            <p className="font-mono text-xs text-muted-foreground">{textos.detalle.versiones}</p>
            <PieDeTextos />
          </DetalleTecnico>
        </>
      )}

      <section className="mt-12 rounded-2xl border border-border p-5 print:hidden">
        {confirmar === "sesion" ? (
          <div role="alert" className="text-sm">
            ¿Eliminar esta sesión con sus {videos.length} {videos.length === 1 ? "golpe" : "golpes"}? Se borran los videos y los reportes. No se
            puede deshacer.
            <span className="mt-3 flex gap-4">
              <button type="button" disabled={borrando} onClick={() => void borrarSesion()} className="font-semibold text-destructive underline underline-offset-4">
                {borrando ? "Eliminando…" : "Sí, eliminar la sesión"}
              </button>
              <button type="button" disabled={borrando} onClick={() => setConfirmar(null)} className="underline underline-offset-4">
                Cancelar
              </button>
            </span>
          </div>
        ) : (
          <button type="button" onClick={() => setConfirmar("sesion")} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
            <Trash2 className="h-4 w-4" aria-hidden="true" /> Eliminar esta sesión
          </button>
        )}
      </section>

    </main>
    {/* El PDF es un documento aparte (A4 vertical), no esta pantalla impresa: ver documento-sesion.tsx. */}
    <DocumentoDeSesion datos={datos} consistencia={consistencia} idTipico={idMostrado} />
    </>
  );
}
