import { useMemo } from "react";
import {
  CabeceraDeDocumento,
  FotogramasChicos,
  Hoja,
  ItemsPdf,
  Limitaciones,
  ParaProfesionalPdf,
  PieDeDocumento,
  QuePodesHacerPdf,
  Seccion,
  Subtitulo,
  Tabla,
  fechaDeHoy,
} from "@/components/reporte/documento";
import { ENCUADRE_ETIQUETA, GESTO_ETIQUETA, reporteDe } from "@/lib/estado-video";
import type { Consistencia } from "@/lib/consistencia";
import { artefactosDe, picosNoMedidosDe, repeticionesDe } from "@/lib/reporte-simple";
import { fotosDe, textosDeSesion } from "@/lib/textos-reporte";
import type { SesionConVideos } from "@/lib/videos-data";

/**
 * La sesión como documento A4 vertical (solo en el papel). Mismos textos que la pantalla (`lib/textos-reporte.ts`, decisión 039);
 * el detalle técnico va abierto.
 */
export function DocumentoDeSesion({
  datos,
  consistencia,
  idTipico,
}: {
  datos: SesionConVideos;
  consistencia: Consistencia | null;
  /** El golpe de las fotos: el típico (el más cercano al valor típico), o el que se esté mirando. */
  idTipico: string | null;
}) {
  const videos = datos.videos;
  const textos = useMemo(
    () =>
      textosDeSesion({
        gesto: datos.gesto,
        encuadre: datos.encuadre,
        ladoCamara: datos.lado_camara,
        manoDominante: datos.atletas?.mano_dominante ?? null,
        golpes: videos.map((v) => ({ id: v.id, estado: v.estado, reporte: reporteDe(v)?.reporte ?? null })),
        consistencia,
      }),
    [datos, videos, consistencia],
  );
  const numeroDe = new Map(videos.map((v, i) => [v.id, i + 1]));
  const tipico = videos.find((v) => v.id === idTipico) ?? null;
  const repTipico = reporteDe(tipico ?? {})?.reporte ?? null;
  const fecha = new Date(datos.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" });
  const versiones = consistencia?.versiones_motor ?? [];

  return (
    <Hoja>
      <CabeceraDeDocumento
        titulo="Reporte de una sesión"
        datos={[
          { k: "Jugador", v: datos.atletas?.nombre ?? "—" },
          { k: "Fecha de la grabación", v: fecha },
          { k: "Golpe", v: GESTO_ETIQUETA[datos.gesto] ?? datos.gesto },
          { k: "Encuadre de la cámara", v: ENCUADRE_ETIQUETA[datos.encuadre] ?? datos.encuadre },
          { k: "Cámara a la", v: datos.lado_camara },
          { k: "Golpes de la sesión", v: String(videos.length) },
        ]}
      />

      <Seccion titulo="En una frase">
        <p className="text-[11pt] font-bold leading-snug">{textos.enUnaFrase}</p>
      </Seccion>

      <Seccion titulo="Qué vimos">
        {textos.vimos.medido.length > 0 ? <ItemsPdf items={textos.vimos.medido} /> : <p>No hay golpes medidos para resumir.</p>}
        {textos.vimos.seAparta.length > 0 && (
          <>
            <Subtitulo>Un golpe que se aparta</Subtitulo>
            <ItemsPdf items={textos.vimos.seAparta} />
          </>
        )}
        {textos.vimos.noMedido.length > 0 && (
          <>
            <Subtitulo>Lo que no se pudo medir</Subtitulo>
            <ItemsPdf items={textos.vimos.noMedido} />
          </>
        )}
      </Seccion>

      {tipico && textos.tipico && (
        <Seccion titulo={`Fotos y video · golpe ${numeroDe.get(tipico.id)}`}>
          <p className="mb-1.5">{textos.tipico.texto}</p>
          <FotogramasChicos
            artefactos={artefactosDe(repTipico)}
            noMedidos={picosNoMedidosDe(repTipico)}
            textos={fotosDe(repTipico)}
            desdeS={repeticionesDe(repTipico)[0]?.desde_s ?? null}
          />
          <p className="mt-1 text-[8.5pt]">{textos.tipico.queMirar}</p>
        </Seccion>
      )}

      <QuePodesHacerPdf medir={textos.hacer.medir} usar={textos.hacer.usar} literatura={textos.hacer.literatura} />
      <ParaProfesionalPdf profesional={textos.profesional} />

      <Seccion titulo="Detalle técnico" cortable>
        <Tabla columnas={textos.detalle.columnas} filas={textos.detalle.filas} />
        <p className="mt-1 text-[8pt] text-gray-600">{textos.detalle.nota}</p>
        <Subtitulo>Qué significa cada término</Subtitulo>
        <dl className="space-y-1 text-[8.5pt]">
          {textos.detalle.terminos.map((x) => (
            <div key={x.termino}>
              <dt className="inline font-bold">{x.termino}: </dt>
              <dd className="inline">{x.significa}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-1 text-[8pt] text-gray-600">{textos.detalle.versiones}</p>
      </Seccion>

      <Seccion titulo="Limitaciones">
        <Limitaciones />
      </Seccion>

      <PieDeDocumento versiones={versiones} generado={fechaDeHoy()} />
    </Hoja>
  );
}
