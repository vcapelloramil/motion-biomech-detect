import { useEffect, useState, type ReactNode } from "react";
import type { PicoNoMedidoLeido, artefactosDe } from "@/lib/reporte-simple";
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

export function Seccion({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <section className="mt-4 break-inside-avoid">
      <h2 className="border-b border-gray-400 pb-0.5 text-[8.5pt] font-bold uppercase tracking-wider text-gray-700">{titulo}</h2>
      <div className="mt-1.5">{children}</div>
    </section>
  );
}

export function Tabla({ columnas, filas }: { columnas: string[]; filas: ReactNode[][] }) {
  return (
    <table className="w-full border-collapse text-[9pt]">
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

/** Los tres fotogramas chicos en una fila; donde no hay, una caja "no medido" con el motivo. */
export function FotogramasChicos({
  artefactos,
  noMedidos,
}: {
  artefactos: ReturnType<typeof artefactosDe>;
  noMedidos: PicoNoMedidoLeido[];
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

  return (
    <ul className="grid grid-cols-3 gap-3">
      {(["pelvis", "torso", "brazo"] as const).map((s) => {
        const f = artefactos.fotogramas.find((x) => x.segmento === s);
        const falta = noMedidos.find((n) => n.segmento === s);
        return (
          <li key={s} className="break-inside-avoid">
            {f && urls[f.ruta] ? (
              <img
                src={urls[f.ruta]}
                alt={`Fotograma en el pico de velocidad ${DEL_SEGMENTO[s]}`}
                loading="eager"
                className="mx-auto block h-[44mm] w-auto max-w-full border border-gray-400 object-contain"
              />
            ) : (
              <div className="flex h-[44mm] items-center justify-center border border-dashed border-gray-500 p-2 text-center text-[8pt] text-gray-700">
                {f ? "Imagen no disponible" : falta ? falta.motivo : "No medido"}
              </div>
            )}
            <p className="mt-1 text-center text-[8.5pt]">
              <strong>Pico {DEL_SEGMENTO[s]}</strong>
              {f ? ` · ${fmt(f.instante_s, 3)} s` : " · no medido"}
            </p>
          </li>
        );
      })}
    </ul>
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
      KinetiQ · motor {versiones.length ? versiones.join(", ") : "—"} · documento generado el {generado}. Para compartir con un entrenador o
      un profesional de la salud.
    </footer>
  );
}

export function fechaDeHoy(): string {
  return new Date().toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" });
}
