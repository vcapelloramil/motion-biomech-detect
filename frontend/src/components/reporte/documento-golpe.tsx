import { useMemo } from "react";
import { SecuenciaRelativa } from "@/components/reporte/secuencia-relativa";
import { SecuenciaSimple } from "@/components/reporte/secuencia-simple";
import {
  CabeceraDeDocumento,
  DetalleGruposPdf,
  FotogramasChicos,
  Hoja,
  ItemsPdf,
  Limitaciones,
  ParaProfesionalPdf,
  PieDeDocumento,
  QuePodesHacerPdf,
  Seccion,
  fechaDeHoy,
} from "@/components/reporte/documento";
import { ENCUADRE_ETIQUETA, GESTO_ETIQUETA, numero, tiemposDe } from "@/lib/estado-video";
import type { Consistencia } from "@/lib/consistencia";
import { artefactosDe, picosNoMedidosDe, repeticionesDe, trazabilidadDe } from "@/lib/reporte-simple";
import { contextoDeGolpe, textosDeGolpe, tituloDeGolpe } from "@/lib/textos-reporte";
import type { VideoConReporte } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

/**
 * El reporte de un golpe como documento A4 vertical (solo en el papel). Usa EXACTAMENTE los mismos textos que la pantalla
 * (`lib/textos-reporte.ts`, decisión 039); la diferencia es que el detalle técnico va abierto y no hay ⓘ ni video.
 */
export function DocumentoDeGolpe({
  video,
  reporte,
  consistencia = null,
  posicion = null,
}: {
  video: VideoConReporte;
  reporte: Record<string, unknown>;
  consistencia?: Consistencia | null;
  /** Qué golpe de la sesión es («golpe 4 de 6»); `null` mientras se lee. */
  posicion?: { n: number; m: number } | null;
}) {
  const sesion = video.sesiones;
  const t = trazabilidadDe(reporte);
  const fps = t.fps_real ?? numero(video.fps_real);
  const r0 = repeticionesDe(reporte)[0] ?? null;
  const tiempos = tiemposDe(video);
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [reporte, sesion, consistencia, video.id, tiempos.espera_cola_s, tiempos.procesamiento_s],
  );
  const fecha = sesion
    ? new Date(sesion.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" })
    : "—";

  return (
    <Hoja>
      <CabeceraDeDocumento
        titulo="Reporte de un golpe"
        datos={[
          { k: "Jugador", v: sesion?.atletas?.nombre ?? "—" },
          { k: "Fecha de la grabación", v: fecha },
          {
            k: "Golpe",
            v: sesion
              ? `${GESTO_ETIQUETA[sesion.gesto] ?? sesion.gesto}${tituloDeGolpe(sesion.gesto, posicion).resto ? ` · ${tituloDeGolpe(sesion.gesto, posicion).resto}` : ""}`
              : "—",
          },
          { k: "Encuadre de la cámara", v: sesion ? (ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre) : "—" },
          { k: "Cámara a la", v: sesion?.lado_camara ?? "—" },
          { k: "Frecuencia real medida", v: fps !== null ? `${fmt(fps, 1)} fps` : "—" },
        ]}
      />

      <Seccion titulo="En una frase">
        <p className="text-[11pt] font-bold leading-snug">{textos.enUnaFrase}</p>
      </Seccion>

      <Seccion titulo="Qué vimos">
        {textos.vimos.medido.length > 0 ? (
          <ItemsPdf items={textos.vimos.medido} />
        ) : (
          <p>De este reporte no hay una medición con confianza suficiente para resumir.</p>
        )}
        {textos.vimos.noMedido.length > 0 && (
          <>
            <p className="mt-2 text-[7.5pt] font-bold uppercase tracking-wider text-gray-600">Lo que no se pudo medir</p>
            <ItemsPdf items={textos.vimos.noMedido} />
          </>
        )}
      </Seccion>

      <Seccion titulo="¿Qué giró primero?">
        <SecuenciaSimple reporte={reporte} />
      </Seccion>

      <Seccion titulo="Fotos y video">
        <FotogramasChicos artefactos={artefactosDe(reporte)} noMedidos={picosNoMedidosDe(reporte)} textos={textos.fotos} desdeS={r0?.desde_s ?? null} />
      </Seccion>

      <QuePodesHacerPdf medir={textos.hacer.medir} usar={textos.hacer.usar} literatura={textos.hacer.literatura} />
      <ParaProfesionalPdf profesional={textos.profesional} />
      <DetalleGruposPdf
        grupos={textos.detalle}
        antes={
          <div className="mb-2 break-inside-avoid">
            <p className="text-[7.5pt] font-bold uppercase tracking-wider text-gray-600">Momentos respecto del tronco</p>
            <p className="text-[8.5pt]">
              El giro más rápido de cada parte, medido respecto del tronco. Lo que cae dentro de la franja gris no se puede ordenar.
            </p>
            <div className="mx-auto max-w-[105mm]">
              <SecuenciaRelativa reporte={reporte} />
            </div>
          </div>
        }
      />

      <Seccion titulo="Limitaciones">
        <Limitaciones />
      </Seccion>

      <PieDeDocumento versiones={t.version_motor ? [t.version_motor] : []} generado={fechaDeHoy()} />
    </Hoja>
  );
}
