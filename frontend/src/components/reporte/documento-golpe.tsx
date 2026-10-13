import {
  DEL_SEGMENTO,
  CabeceraDeDocumento,
  FotogramasChicos,
  Hoja,
  Limitaciones,
  PieDeDocumento,
  Seccion,
  Tabla,
  fechaDeHoy,
} from "@/components/reporte/documento";
import { ETIQUETA_SIN_DIFERENCIA, ETIQUETA_SIN_EVALUAR } from "@/components/estado";
import {
  ENCUADRE_ETIQUETA,
  GESTO_ETIQUETA,
  TEXTO_VERSION_ANTERIOR,
  formatearDuracion,
  numero,
  observacionesDe,
  tiemposDe,
} from "@/lib/estado-video";
import {
  artefactosDe,
  coberturaDe,
  fraseDeSecuencia,
  magnitudesDe,
  masImportantes,
  picosNoMedidosDe,
  picosOrdenados,
  repeticionesDe,
  resolucionTexto,
  tramosNoAuditablesDe,
  trazabilidadDe,
} from "@/lib/reporte-simple";
import type { VideoConReporte } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

const ETIQUETA_SEVERIDAD: Record<string, string> = {
  correcto: "Correcto",
  desvio_leve: "Desvío leve",
  alerta_de_carga: "Alerta de carga",
  no_auditable: "No auditable",
  sin_evaluar: ETIQUETA_SIN_EVALUAR,
  sin_diferencia_medible: ETIQUETA_SIN_DIFERENCIA,
};

const SEGMENTO_ETIQUETA = { pelvis: "Cadera", torso: "Tronco", brazo: "Brazo" } as const;

/** El reporte de un golpe como documento A4 vertical (solo en el papel). */
export function DocumentoDeGolpe({ video, reporte }: { video: VideoConReporte; reporte: Record<string, unknown> }) {
  const sesion = video.sesiones;
  const t = trazabilidadDe(reporte);
  const fps = t.fps_real ?? numero(video.fps_real);
  const reps = repeticionesDe(reporte);
  const r0 = reps[0] ?? null;
  const frase = fraseDeSecuencia(r0, fps, t.tolerancia_orden_ms);
  // La frase de la secuencia ya dice que cadera y tronco quedaron al mismo tiempo: no se repite como una observación más.
  const observaciones = masImportantes(
    observacionesDe(reporte).filter((o) => !(frase.tipo === "simultaneo" && o.severidad === "sin_diferencia_medible")),
    4,
  ).visibles;
  const picos = picosOrdenados(r0);
  const noMedidos = picosNoMedidosDe(reporte);
  const magnitudes = magnitudesDe(reporte);
  const artefactos = artefactosDe(reporte);
  const tramos = tramosNoAuditablesDe(reporte);
  const cobertura = coberturaDe(reporte);
  const tiempos = tiemposDe(video);
  const inicio = r0?.desde_s ?? null;
  const filtro = (reporte.trazabilidad as { filtro?: { tipo?: string; orden?: number; corte_hz?: number; fase_cero?: boolean } } | undefined)?.filtro;
  const fecha = sesion
    ? new Date(sesion.fecha + "T12:00:00").toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" })
    : "—";
  const medido = t.escala_conocida;
  const viejo = t.version_motor !== null && /^0\.[0-4]\./.test(t.version_motor);

  return (
    <Hoja>
      <CabeceraDeDocumento
        titulo="Reporte de un golpe"
        datos={[
          { k: "Jugador", v: sesion?.atletas?.nombre ?? "—" },
          { k: "Fecha de la grabación", v: fecha },
          { k: "Golpe", v: sesion ? (GESTO_ETIQUETA[sesion.gesto] ?? sesion.gesto) : "—" },
          { k: "Encuadre de la cámara", v: sesion ? (ENCUADRE_ETIQUETA[sesion.encuadre] ?? sesion.encuadre) : "—" },
          { k: "Frecuencia real medida", v: fps !== null ? `${fmt(fps, 1)} fps` : "—" },
          { k: "Versión del motor", v: `${t.version_motor ?? "—"} · ${t.backend_pose ?? "—"}` },
        ]}
      />

      <Seccion titulo="Resumen">
        <p>{frase.texto}</p>
        {observaciones.length > 0 && (
          <ul className="mt-1.5 space-y-1">
            {observaciones.map((o, i) => (
              <li key={i}>
                <strong>[{ETIQUETA_SEVERIDAD[o.severidad] ?? o.severidad}]</strong> {o.texto}
                {o.anterior ? ` (${TEXTO_VERSION_ANTERIOR})` : ""}
                {o.severidad === "no_auditable" && o.fundamento ? ` ${o.fundamento}` : ""}
              </li>
            ))}
          </ul>
        )}
        {viejo && <p className="mt-1 text-[8.5pt]">Este reporte se calculó con una versión anterior del motor y no se volvió a calcular.</p>}
      </Seccion>

      <Seccion titulo="Tres momentos del golpe">
        <FotogramasChicos artefactos={artefactos} noMedidos={noMedidos} />
        <p className="mt-1 text-[8pt] text-gray-600">
          Fotogramas reales del video con el esqueleto dibujado, en el instante de máxima velocidad de cada segmento.
        </p>
      </Seccion>

      <Seccion titulo="Mediciones, con su confianza">
        <Tabla
          columnas={["Medición", "Valor", "Instante", "Confianza"]}
          filas={[
            ...picos.map((p) => [
              `Velocidad máxima ${DEL_SEGMENTO[p.segmento]}`,
              medido ? `${fmt(p.velocidad, 0)} ${p.unidad}` : "no auditable",
              medido ? `${fmt(p.instante_s, 3)} s${inicio !== null ? ` (video: ${fmt(inicio + p.instante_s, 3)} s)` : ""}` : "—",
              fmt(p.confianza, 2),
            ]),
            ...noMedidos.map((n) => [
              `Velocidad máxima ${DEL_SEGMENTO[n.segmento]}`,
              <em key={n.segmento}>no medido</em>,
              "—",
              "—",
            ]),
            ...magnitudes.map((m) => [
              m.etiqueta,
              m.auditable && m.valor !== null ? `${fmt(m.valor, 1)} °` : <em key={m.nombre}>no medido</em>,
              "—",
              fmt(m.confianza, 2),
            ]),
          ]}
        />
        {noMedidos.length > 0 && (
          <ul className="mt-1.5 list-disc space-y-0.5 pl-4 text-[8.5pt]">
            {noMedidos.map((n) => (
              <li key={n.segmento}>
                <strong>{SEGMENTO_ETIQUETA[n.segmento]} no medido:</strong> {n.motivo}
              </li>
            ))}
          </ul>
        )}
        <p className="mt-1 text-[8pt] text-gray-600">
          Son datos del golpe, sin juicio: no hay un rango de referencia propio para compararlos. La confianza va de 0 a 1 y es la de las articulaciones
          que definen cada medición.
        </p>
      </Seccion>

      <Seccion titulo="Trazabilidad">
        <dl className="grid grid-cols-3 gap-x-4 gap-y-1 text-[8.5pt]">
          <Par k="Frecuencia nominal" v={t.fps_nominal !== null ? `${fmt(t.fps_nominal, 0)} fps` : "—"} />
          <Par k="Fotogramas perdidos" v={t.fotogramas_perdidos_pct !== null ? `${fmt(t.fotogramas_perdidos_pct, 1)} %` : "—"} />
          <Par k="Puntos interpolados" v={t.puntos_interpolados_pct !== null ? `${fmt(t.puntos_interpolados_pct, 1)} %` : "no se regularizó"} />
          <Par k="Resolución" v={resolucionTexto(t.fps_real ?? fps) ?? "—"} />
          <Par k="Tolerancia del orden" v={t.tolerancia_orden_ms !== null ? `${fmt(t.tolerancia_orden_ms, 1)} ms` : "no registrada"} />
          <Par k="Cobertura auditable" v={cobertura !== null ? `${fmt(cobertura, 1)} %` : "—"} />
          <Par
            k="Filtro"
            v={filtro ? `${(filtro.tipo ?? "butterworth").replace(/^./, (c) => c.toUpperCase())} de ${filtro.orden ?? "—"}º orden${filtro.fase_cero ? ", fase cero" : ""}, corte ${filtro.corte_hz !== undefined ? fmt(filtro.corte_hz, 1) : "—"} Hz` : "—"}
          />
          <Par k="Modo de captura declarado" v={t.modo_captura ?? "—"} />
          <Par k="Escala temporal" v={t.escala_conocida ? "conocida" : "no confirmada"} />
          {tiempos.espera_cola_s !== null && <Par k="Espera en la cola" v={formatearDuracion(tiempos.espera_cola_s)} />}
          {tiempos.procesamiento_s !== null && <Par k="Procesamiento" v={formatearDuracion(tiempos.procesamiento_s)} />}
        </dl>
        {tramos.length > 0 && (
          <p className="mt-1.5 text-[8.5pt]">
            <strong>Tramos no auditables</strong> (desde el inicio del video):{" "}
            {tramos.map((tr) => `${fmt(tr.desde_s, 2)}–${fmt(tr.hasta_s, 2)} s`).join(" · ")}.
          </p>
        )}
      </Seccion>

      <Seccion titulo="Limitaciones">
        <Limitaciones />
      </Seccion>

      <PieDeDocumento versiones={t.version_motor ? [t.version_motor] : []} generado={fechaDeHoy()} />
    </Hoja>
  );
}

function Par({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-[7.5pt] uppercase tracking-wider text-gray-600">{k}</dt>
      <dd>{v}</dd>
    </div>
  );
}
