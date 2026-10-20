import { useEffect, useState, type ReactNode } from "react";
import type { PicoNoMedidoLeido, artefactosDe } from "@/lib/reporte-simple";
import { VERSION_TEXTOS, type FotosTexto, type GrupoDetalle, type Item, type Literatura, type Profesional } from "@/lib/textos-reporte";
import { urlsDeArtefactos } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

/**
 * El PDF como DOCUMENTO (14/10/2026): una vista de impresión PROPIA, A4 vertical, en 1 o 2 páginas, que no es la pantalla impresa. Existe
 * solo en el papel (`hidden print:block`); la pantalla lleva `print:hidden`. La impresión es la del navegador ("Guardar como PDF"): no se
 * genera nada en el servidor. Pensado para compartir con un entrenador o un kinesiólogo: lo completo, con confianza y trazabilidad.
 */

/** "de la cadera", "del tronco", "del brazo": con su artículo, para frases como "Pico del tronco". */
export const DEL_SEGMENTO = { pelvis: "de la cadera", torso: "del tronco", brazo: "del brazo" } as const;

export function Hoja({ children }: { children: ReactNode }) {
  return <div className="documento hidden text-[9.5pt] leading-snug text-black print:block">{children}</div>;
}

export function CabeceraDeDocumento({ titulo, datos }: { titulo: string; datos: { k: string; v: string }[] }) {
  return (
    <header className="border-b-2 border-black pb-2">
      <div className="flex items-baseline justify-between gap-4">
        <p className="font-display text-[15pt] font-bold">KinetiQ</p>
        <p className="text-[8.5pt]">Análisis de movimiento · tenis</p>
      </div>
      <h1 className="mt-1 font-display text-[13pt] font-bold">{titulo}</h1>
      <dl className="mt-2 grid grid-cols-3 gap-x-4 gap-y-1">
        {datos.map((d) => (
          <div key={d.k}>
            <dt className="text-[7.5pt] uppercase tracking-wider text-gray-600">{d.k}</dt>
            <dd className="font-semibold">{d.v}</dd>
          </div>
        ))}
      </dl>
    </header>
  );
}

export function Seccion({ titulo, children, cortable = false }: { titulo: string; children: ReactNode; cortable?: boolean }) {
  return (
    <section className={cortable ? "mt-4" : "mt-4 break-inside-avoid"}>
      <h2 className="border-b border-gray-400 pb-0.5 text-[8.5pt] font-bold uppercase tracking-wider text-gray-700">{titulo}</h2>
      <div className="mt-1.5">{children}</div>
    </section>
  );
}

export function Tabla({ columnas, filas, anchos }: { columnas: string[]; filas: ReactNode[][]; anchos?: string[] }) {
  return (
    <table className={"w-full border-collapse text-[9pt]" + (anchos ? " table-fixed" : "")}>
      {anchos && (
        <colgroup>
          {anchos.map((a, i) => (
            <col key={i} style={{ width: a }} />
          ))}
        </colgroup>
      )}
      <thead>
        <tr>
          {columnas.map((c) => (
            <th key={c} className="border-b border-gray-500 py-1 pr-2 text-left text-[7.5pt] font-bold uppercase tracking-wider text-gray-700">
              {c}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {filas.map((f, i) => (
          <tr key={i} className="break-inside-avoid">
            {f.map((c, j) => (
              <td key={j} className="border-b border-gray-300 py-1 pr-2 align-top">
                {c}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/**
 * Las fotos chicas del PDF: tres en una fila (cadera, tronco, brazo) o UNA sola cuando cadera y tronco quedaron a la vez; donde no hay,
 * una caja "no medido" con el motivo. Debajo, la línea de qué mirar (los mismos textos que la pantalla).
 */
export function FotogramasChicos({
  artefactos,
  noMedidos,
  textos,
  desdeS = null,
}: {
  artefactos: ReturnType<typeof artefactosDe>;
  noMedidos: PicoNoMedidoLeido[];
  textos: FotosTexto;
  desdeS?: number | null;
}) {
  const [urls, setUrls] = useState<Record<string, string>>({});
  const rutas = artefactos.fotogramas.map((f) => f.ruta);
  const clave = rutas.join("|");
  useEffect(() => {
    let activo = true;
    urlsDeArtefactos(rutas)
      .then((u) => activo && setUrls(u))
      .catch(() => undefined);
    return () => {
      activo = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clave]);

  // El brazo que no se midió no lleva caja: ya lo explica «Lo que no se pudo medir».
  const hayBrazo = artefactos.fotogramas.some((x) => x.segmento === "brazo");
  const segmentos: ("pelvis" | "torso" | "brazo")[] = [...(textos.fotoUnica ? (["torso"] as const) : (["pelvis", "torso"] as const)), ...(hayBrazo ? (["brazo"] as const) : [])];
  const columnas = segmentos.length === 1 ? "grid grid-cols-1 gap-3 max-w-[70mm] mx-auto" : segmentos.length === 2 ? "grid grid-cols-2 gap-3" : "grid grid-cols-3 gap-3";
  return (
    <>
      <ul className={columnas}>
        {segmentos.map((s) => {
          // En la foto única, la del tronco hace de "cadera y tronco" (y si solo hay la de la cadera, esa).
          const f = artefactos.fotogramas.find((x) => x.segmento === s) ?? (textos.fotoUnica && s === "torso" ? artefactos.fotogramas.find((x) => x.segmento === "pelvis") : undefined);
          const falta = noMedidos.find((n) => n.segmento === s);
          return (
            <li key={s} className="break-inside-avoid">
              {f && urls[f.ruta] ? (
                <img
                  src={urls[f.ruta]}
                  alt={`Fotograma en el giro más rápido ${textos.fotoUnica && s === "torso" ? "de la cadera y del tronco" : DEL_SEGMENTO[s]}`}
                  loading="eager"
                  className="mx-auto block h-[44mm] w-auto max-w-full border border-gray-400 object-contain"
                />
              ) : (
                <div className="flex h-[44mm] items-center justify-center border border-dashed border-gray-500 p-2 text-center text-[8pt] text-gray-700">
                  {f ? "Imagen no disponible" : falta ? falta.motivo : "No medido"}
                </div>
              )}
              <p className="mt-1 text-center text-[8.5pt]">
                {textos.fotoUnica && s === "torso" && textos.etiquetaFotoUnica ? (
                  <strong>{textos.etiquetaFotoUnica}</strong>
                ) : (
                  <>
                    <strong>Giro más rápido {DEL_SEGMENTO[s]}</strong>
                    {f ? (desdeS !== null ? ` · a los ${fmt(desdeS + f.instante_s, 2)} s del video` : "") : " · no medido"}
                  </>
                )}
              </p>
            </li>
          );
        })}
      </ul>
      <p className="mt-1 text-[8.5pt]">
        <strong>Qué mirar:</strong> {textos.queMirarFoto}
        {textos.video ? " En la aplicación hay además un video corto con el esqueleto dibujado." : ""}
      </p>
    </>
  );
}

/** Una lista de líneas del reporte (con su título en negrita): la misma que la pantalla, sin los ⓘ. */
export function ItemsPdf({ items }: { items: Item[] }) {
  return (
    <ul className="list-disc space-y-1 pl-4">
      {items.map((m, i) => (
        <li key={i}>
          {m.titulo && <strong>{m.titulo} </strong>}
          {m.texto}
        </li>
      ))}
    </ul>
  );
}

export function Subtitulo({ children }: { children: ReactNode }) {
  return <p className="mt-2 text-[7.5pt] font-bold uppercase tracking-wider text-gray-600 first:mt-0">{children}</p>;
}

/** «Qué podés hacer con esto», con el recuadro de la literatura aparte. */
export function QuePodesHacerPdf({ medir, usar, literatura }: { medir: Item[]; usar: Item[]; literatura: Literatura }) {
  return (
    <Seccion titulo="Qué podés hacer con esto">
      {medir.length > 0 && (
        <>
          <Subtitulo>Para medir mejor</Subtitulo>
          <ItemsPdf items={medir} />
        </>
      )}
      {usar.length > 0 && (
        <>
          <Subtitulo>Para usar estos datos al entrenar</Subtitulo>
          <ItemsPdf items={usar} />
        </>
      )}
      <div className="mt-2 break-inside-avoid border-2 border-dashed border-gray-500 p-2">
        <p className="text-[7.5pt] font-bold uppercase tracking-wider text-gray-600">{literatura.titulo}</p>
        <p className="text-[8pt] text-gray-600">{literatura.aclaracion}</p>
        <p className="mt-1">{literatura.texto}</p>
      </div>
    </Seccion>
  );
}

/** «Para tu entrenador o profesional»: las preguntas, cuánto confiar en cada medición y el aviso. */
export function ParaProfesionalPdf({ profesional }: { profesional: Profesional }) {
  return (
    <Seccion titulo="Para tu entrenador o profesional">
      <Subtitulo>Preguntas para llevar</Subtitulo>
      <ol className="list-decimal space-y-1 pl-4">
        {profesional.preguntas.map((q, i) => (
          <li key={i}>{q}</li>
        ))}
      </ol>
      <Subtitulo>Cuánto se puede confiar en cada medición</Subtitulo>
      <ItemsPdf items={profesional.confianza} />
      <p className="mt-2 break-inside-avoid border border-gray-500 p-2">{profesional.aviso}</p>
    </Seccion>
  );
}

/** El detalle técnico del golpe, abierto en el papel: cada dato con su explicación en una línea. */
export function DetalleGruposPdf({ grupos, antes }: { grupos: GrupoDetalle[]; antes?: ReactNode }) {
  return (
    <Seccion titulo="Detalle técnico" cortable>
      {antes}
      {grupos.map((g) => (
        <div key={g.titulo} className="mb-2">
          <Subtitulo>{g.titulo}</Subtitulo>
          <Tabla anchos={["27%", "20%", "53%"]} columnas={["Dato", "Valor", "Qué significa"]} filas={g.filas.map((f) => [<strong key={f.dato}>{f.dato}</strong>, f.valor, f.significa])} />
        </div>
      ))}
    </Seccion>
  );
}

export function Limitaciones() {
  return (
    <ul className="list-disc space-y-0.5 pl-4 text-[8.5pt] leading-snug">
      <li>KinetiQ documenta el movimiento observado. No diagnostica, no predice y no reemplaza la evaluación de un profesional.</li>
      <li>
        El análisis es en dos dimensiones, con una sola cámara: los ángulos y el orden entre la cadera y el tronco dependen del encuadre. Por eso
        el orden se registra y no se evalúa; solo se compara con las propias sesiones grabadas desde el mismo lugar.
      </li>
      <li>
        Los instantes tienen la resolución del video: diferencias menores a unos 8 ms entre dos picos no se pueden distinguir. Es el límite del
        instrumento, no un error.
      </li>
      <li>Un valor «no medido» no es un valor normal: es un dato que el sistema no pudo establecer con confianza.</li>
      <li>No se compara con otros jugadores ni con un modelo ideal.</li>
    </ul>
  );
}

export function PieDeDocumento({ versiones, generado }: { versiones: string[]; generado: string }) {
  return (
    <footer className="mt-4 border-t border-gray-400 pt-1 text-[7.5pt] text-gray-600">
      KinetiQ documenta el movimiento. No diagnostica ni reemplaza la evaluación de un profesional. · motor {versiones.length ? versiones.join(", ") : "—"} ·
      textos v{VERSION_TEXTOS} · documento generado el {generado}. Para compartir con un entrenador o un profesional de la salud.
    </footer>
  );
}

export function fechaDeHoy(): string {
  return new Date().toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" });
}
