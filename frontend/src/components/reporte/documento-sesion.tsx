import {
  CabeceraDeDocumento,
  FotogramasChicos,
  Hoja,
  Limitaciones,
  PieDeDocumento,
  Seccion,
  Tabla,
  fechaDeHoy,
} from "@/components/reporte/documento";
import { ETIQUETA_SIN_DIFERENCIA } from "@/components/estado";
import { ENCUADRE_ETIQUETA, GESTO_ETIQUETA, enCurso, numero, reporteDe, tiemposDe, formatearDuracion, type EstadoVideo } from "@/lib/estado-video";
import { fraseGolpeQueSeAparta, tarjetasDeConsistencia, type Consistencia } from "@/lib/consistencia";
import { artefactosDe, fraseDeSecuencia, picosNoMedidosDe, repeticionesDe, trazabilidadDe } from "@/lib/reporte-simple";
import type { SesionConVideos } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

const ESTADO: Record<EstadoVideo, string> = {
  pendiente: "Subido",
  encolado: "En cola",
  procesando: "Analizando",
  completado: "Medido",
  parcial: "Medido en parte",
  fallido: "No se pudo medir",
};

type Reporte = Record<string, unknown> | null;

/** Qué llegó primero en un golpe, como dato observado (no como juicio): la diferencia en ms entre los picos de cadera y tronco. */
function ordenDelGolpe(reporte: Reporte): string {
  const rep = repeticionesDe(reporte)[0];
  const p = rep?.picos.find((x) => x.segmento === "pelvis");
  const t = rep?.picos.find((x) => x.segmento === "torso");
  if (!p || !t) return "—";
  const tolMs = trazabilidadDe(reporte).tolerancia_orden_ms ?? 1000 / 120;
  const dMs = (t.instante_s - p.instante_s) * 1000;
  if (Math.abs(dMs) <= tolMs + 1e-6) return `${ETIQUETA_SIN_DIFERENCIA} (${fmt(Math.abs(dMs), 0)} ms)`;
  return dMs > 0 ? `Cadera primero, ${fmt(dMs, 0)} ms antes` : `Tronco primero, ${fmt(-dMs, 0)} ms antes`;
}

/** La sesión como documento A4 vertical (solo en el papel). */
export function DocumentoDeSesion({
  datos,
  consistencia,
  idTipico,
}: {
  datos: SesionConVideos;
  consistencia: Consistencia | null;
  /** El golpe de los "tres momentos": el típico (el más cercano a la mediana). */
  idTipico: string | null;
}) {
  const videos = datos.videos;
  const num = new Map(videos.map((v, i) => [v.id, i + 1]));
  const valores = new Map((consistencia?.separacion_cadera_hombro.valores ?? []).map((x) => [x.video_id, x.valor]));
  const tipico = videos.find((v) => v.id === idTipico) ?? null;
  const repTipico = reporteDe(tipico ?? {})?.reporte ?? null;
  const trazTipico = trazabilidadDe(repTipico);
  const frase = repTipico
    ? fraseDeSecuencia(repeticionesDe(repTipico)[0] ?? null, trazTipico.fps_real ?? numero(tipico?.fps_real), trazTipico.tolerancia_orden_ms)
    : null;
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
          { k: "Golpes de la sesión", v: String(videos.length) },
          { k: "Versión del motor", v: versiones.length ? versiones.join(", ") : "—" },
        ]}
      />

      <Seccion titulo="Resumen: tus golpes entre sí">
        {consistencia ? (
          <ul className="space-y-1.5">
            {tarjetasDeConsistencia(consistencia).map((t) => (
              <li key={t.clave}>
                <strong>
                  {t.titulo}
                  {t.valor ? `: ${t.valor}` : ""}.
                </strong>{" "}
                {t.texto}
              </li>
            ))}
            {consistencia.golpes_que_se_apartan.map((id) => (
              <li key={id}>{fraseGolpeQueSeAparta(num.get(id) ?? 0)}</li>
            ))}
          </ul>
        ) : (
          <p>La comparación entre golpes no estaba disponible al generar este documento.</p>
        )}
      </Seccion>

      {tipico && (
        <Seccion titulo={`Golpe típico (golpe ${num.get(tipico.id)}): tres momentos`}>
          <FotogramasChicos artefactos={artefactosDe(repTipico)} noMedidos={picosNoMedidosDe(repTipico)} />
          {frase && <p className="mt-1.5">{frase.texto}</p>}
          <p className="mt-1 text-[8pt] text-gray-600">
            El golpe típico es el más cercano a la mediana de la sesión en la separación cadera-hombro; no es el «mejor».
          </p>
        </Seccion>
      )}

      <Seccion titulo="Los golpes de la sesión">
        <Tabla
          columnas={["Golpe", "Estado", "Separación cadera-hombro", "Cadera y tronco", "fps reales", "Procesamiento"]}
          filas={videos.map((v) => {
            const rep = reporteDe(v)?.reporte ?? null;
            const t = trazabilidadDe(rep);
            const tiempos = tiemposDe(v);
            const sep = valores.get(v.id);
            return [
              String(num.get(v.id)),
              ESTADO[v.estado],
              sep !== undefined ? `${fmt(sep, 1)} °` : enCurso(v.estado) ? "—" : "no medido",
              rep ? ordenDelGolpe(rep) : "—",
              t.fps_real !== null ? fmt(t.fps_real, 0) : "—",
              tiempos.procesamiento_s !== null ? formatearDuracion(tiempos.procesamiento_s) : "—",
            ];
          })}
        />
        <p className="mt-1 text-[8pt] text-gray-600">
          Las diferencias entre cadera y tronco son datos observados: el orden no se evalúa porque con una sola cámara depende del encuadre.
        </p>
      </Seccion>

      <Seccion titulo="Trazabilidad">
        <p className="text-[8.5pt]">
          Motor {versiones.length ? versiones.join(", ") : "—"}. Tolerancia del orden: 8,3 ms. La mediana y la variación entre golpes se calculan
          sobre los golpes medidos (cadera y tronco con confianza ≥ 0,5); la variación es el desvío robusto (MAD × 1,4826), desde 4 golpes.
          {consistencia?.mezcla_de_versiones ? " Algunos golpes se calcularon con una versión anterior del motor." : ""}
        </p>
      </Seccion>

      <Seccion titulo="Limitaciones">
        <Limitaciones />
      </Seccion>

      <PieDeDocumento versiones={versiones} generado={fechaDeHoy()} />
    </Hoja>
  );
}
