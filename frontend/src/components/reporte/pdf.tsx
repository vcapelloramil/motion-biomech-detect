import { Download } from "lucide-react";

/**
 * PDF barato (paso 4 del plan §8): el reporte con una hoja de estilos de impresión y "Guardar como PDF" del navegador. No se genera
 * ni se guarda en el servidor; es una exportación fiel de lo que se ve, con el sello de versión y las limitaciones (R4 y R5).
 */

/**
 * Imprime con el diálogo del navegador ("Guardar como PDF"). El reporte de un golpe y la sesión tienen una vista de impresión PROPIA
 * (`documento-golpe.tsx`, `documento-sesion.tsx`: un documento A4 vertical); Evolución imprime la pantalla con la hoja de estilos de impresión.
 */
export function imprimirReporte() {
  window.print();
}

export function BotonDescargarPdf({ className }: { className?: string }) {
  return (
    <button
      type="button"
      onClick={imprimirReporte}
      className={
        "inline-flex min-h-11 items-center gap-2 rounded-xl border border-border px-4 text-sm font-semibold hover:border-accent/60 print:hidden " +
        (className ?? "")
      }
    >
      <Download className="h-4 w-4" aria-hidden="true" /> Descargar PDF
    </button>
  );
}

/** Solo en el papel: de qué es el reporte, con qué versión del motor y cuándo se generó el PDF. */
export function SelloDelPdf({ titulo, versiones }: { titulo: string; versiones: string[] }) {
  const hoy = new Date().toLocaleDateString("es-AR", { day: "numeric", month: "long", year: "numeric" });
  return (
    <div className="mb-6 hidden border-b border-border pb-3 text-xs print:block">
      <p className="font-display text-lg font-bold">KinetiQ · Reporte de análisis de movimiento</p>
      <p className="mt-1">{titulo}</p>
      <p className="mt-1 font-mono">
        Motor {versiones.length > 0 ? versiones.join(", ") : "—"} · PDF generado el {hoy}
      </p>
    </div>
  );
}

/** Solo en el papel: lo que este reporte NO dice (R2 y R5). */
export function LimitacionesDelPdf() {
  return (
    <section className="mt-10 hidden print:block" aria-label="Limitaciones">
      <h2 className="font-mono text-xs uppercase tracking-widest">Limitaciones</h2>
      <ul className="mt-3 list-disc space-y-1.5 pl-5 text-xs leading-relaxed">
        <li>KinetiQ documenta el movimiento observado. No diagnostica, no predice y no reemplaza la evaluación de un profesional.</li>
        <li>
          El análisis es en dos dimensiones, con una sola cámara: los ángulos y el orden entre la cadera y el tronco dependen del encuadre.
          Por eso este reporte no emite un juicio sobre ese orden: lo registra, y solo se compara con las propias sesiones grabadas desde el
          mismo lugar.
        </li>
        <li>
          Los instantes tienen la resolución del video: diferencias menores a unos 8 ms entre dos picos no se pueden distinguir. Eso no es un
          error, es el límite del instrumento.
        </li>
        <li>
          Un valor «no medido» no es un valor normal: es un dato que el sistema no pudo establecer con confianza y por eso no se muestra.
        </li>
        <li>No se compara con otros jugadores ni con un modelo ideal.</li>
      </ul>
    </section>
  );
}
