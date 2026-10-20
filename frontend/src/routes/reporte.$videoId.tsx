import { useEffect, useMemo, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { SecuenciaRelativa } from "@/components/reporte/secuencia-relativa";
import { SecuenciaSimple } from "@/components/reporte/secuencia-simple";
import { TresMomentos } from "@/components/reporte/tres-momentos";
import {
  DetalleTecnico,
  EnUnaFrase,
  GruposDeDetalle,
  ParaTuProfesional,
  PieDeTextos,
  QuePodesHacer,
  QueVimos,
} from "@/components/reporte/bloques";
import { DocumentoDeGolpe } from "@/components/reporte/documento-golpe";
import { useSesion } from "@/lib/sesion";
import { ENCUADRE_ETIQUETA, GESTO_ETIQUETA, enCurso, versionAnteriorA, tiemposDe, numero, reporteDe } from "@/lib/estado-video";
import type { Consistencia } from "@/lib/consistencia";
import { leerConsistencia } from "@/lib/consistencia-api";
import { artefactosDe, picosNoMedidosDe, repeticionesDe, trazabilidadDe } from "@/lib/reporte-simple";
import { contextoDeGolpe, textosDeGolpe, tituloDeGolpe } from "@/lib/textos-reporte";
import { golpesDeSesion, leerVideo, type VideoConReporte } from "@/lib/videos-data";

export const Route = createFileRoute("/reporte/$videoId")({
  head: () => ({ meta: [{ title: "Reporte — KinetiQ" }, { name: "robots", content: "noindex" }] }),
  component: () => (
    <RutaProtegida>
      <ReportePage />
    </RutaProtegida>
  ),
});

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
  const { sesion: auth } = useSesion();
  const sesion = video.sesiones;
  const [consistencia, setConsistencia] = useState<Consistencia | null>(null);
  const [posicion, setPosicion] = useState<{ n: number; m: number } | null>(null);
  const token = auth?.access_token;

  // Qué golpe de la sesión es («golpe 4 de 6»), en el orden en que se cargaron. Si no se puede leer, el título dice solo el golpe.
  useEffect(() => {
    let activo = true;
    golpesDeSesion(video.sesion_id)
      .then((lista) => {
        const i = lista.findIndex((x) => x.id === video.id);
        if (activo && i >= 0) setPosicion({ n: i + 1, m: lista.length });
      })
      .catch(() => undefined);
    return () => {
      activo = false;
    };
  }, [video.id, video.sesion_id]);

  // La comparación con los demás golpes de su sesión (si el golpe es el típico, cuántos son, entre qué valores va la torsión).
  // Si no llega, el reporte se arma igual, sin esa parte.
  useEffect(() => {
    if (!token) return;
    let activo = true;
    leerConsistencia(video.sesion_id, token).then((c) => activo && setConsistencia(c));
    return () => {
      activo = false;
    };
  }, [token, video.sesion_id]);

  const t = trazabilidadDe(reporte);
  const fps = t.fps_real ?? numero(video.fps_real);
  const r0 = repeticionesDe(reporte)[0] ?? null;
  const artefactos = artefactosDe(reporte);
  const tiempos = tiemposDe(video);
  const fecha = sesion ? new Date(sesion.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" }) : null;
  const textos = useMemo(
    () =>
      textosDeGolpe({
        reporte,
        gesto: sesion?.gesto ?? "",
        encuadre: sesion?.encuadre ?? "",
        ladoCamara: sesion?.lado_camara ?? "",
        manoDominante: sesion?.atletas?.mano_dominante ?? null,
        contexto: contextoDeGolpe(consistencia, video.id),
        tiempos,
      }),
    // `tiempos` se recalcula en cada render; sus dos números son lo que importa.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [reporte, sesion, consistencia, video.id, tiempos.espera_cola_s, tiempos.procesamiento_s],
  );

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
          {tituloDeGolpe(sesion?.gesto ?? "", posicion).gesto}{" "}
          {tituloDeGolpe(sesion?.gesto ?? "", posicion).resto && (
            <span className="text-gradient-neon">· {tituloDeGolpe(sesion?.gesto ?? "", posicion).resto}</span>
          )}
        </h1>
        <p className="mt-3 text-muted-foreground">
          {fecha ? `${fecha} · ` : ""}
          {fps !== null ? `${Math.round(fps)} fps reales · ` : ""}
          {sesion ? `cámara de ${ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre}` : ""}
          {sesion?.atletas?.nombre ? ` · ${sesion.atletas.nombre}` : ""}
        </p>

        {versionAnteriorA(t.version_motor) && (
          <p role="note" className="mt-6 rounded-xl border border-dashed border-border px-4 py-3 text-sm text-muted-foreground">
            Este reporte se calculó con una versión anterior del motor{t.version_motor ? ` (${t.version_motor})` : ""} y no se vuelve a calcular.
            Para ver el análisis con la versión actual, volvé a subir el golpe.
          </p>
        )}

        <EnUnaFrase texto={textos.enUnaFrase} />
        <QueVimos medido={textos.vimos.medido} noMedido={textos.vimos.noMedido} sesionId={video.sesion_id} />

        {/* Elemento central (CLAUDE.md §3): qué giró primero, sin ejes ni números. */}
        <section aria-labelledby="secuencia" className="mt-12">
          <h2 id="secuencia" className="font-mono text-xs uppercase tracking-widest text-state-ok">¿Qué giró primero?</h2>
          <div className="mt-4">
            <SecuenciaSimple reporte={reporte} />
          </div>
        </section>

        {(artefactos.fotogramas.length > 0 || artefactos.overlay) && (
          <TresMomentos artefactos={artefactos} noMedidos={picosNoMedidosDe(reporte)} textos={textos.fotos} desdeS={r0?.desde_s ?? null} />
        )}

        <QuePodesHacer medir={textos.hacer.medir} usar={textos.hacer.usar} literatura={textos.hacer.literatura} sesionId={video.sesion_id} />
        <ParaTuProfesional profesional={textos.profesional} />

        <DetalleTecnico>
          <div>
            <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Momentos respecto del tronco</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              El giro más rápido de cada parte, medido respecto del tronco, en milésimas de segundo. Lo que cae dentro de la franja gris no se puede
              ordenar. Los momentos desde el inicio del tramo analizado están en la tabla de abajo.
            </p>
            <div className="mt-3 rounded-2xl border border-border p-3 md:p-6">
              <SecuenciaRelativa reporte={reporte} />
            </div>
          </div>
          <GruposDeDetalle grupos={textos.detalle} />
          <PieDeTextos />
        </DetalleTecnico>
      </main>
      {/* El PDF es un documento aparte (A4 vertical), no esta pantalla impresa: ver documento-golpe.tsx. */}
      <DocumentoDeGolpe video={video} reporte={reporte} consistencia={consistencia} posicion={posicion} />
    </>
  );
}
