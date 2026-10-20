import { Fragment } from "react";
import { ArrowRight } from "lucide-react";
import { secuenciaSimple, type SegmentoDeSecuencia } from "@/lib/textos-reporte";

/**
 * «¿Qué giró primero?» (decisión 039, segunda ronda): cajas de izquierda a derecha en el orden en que llegó el giro más rápido de cada
 * parte, sin ejes ni números. Dos partes dentro de la tolerancia van juntas en UNA caja con «casi a la vez»; si se distingue, una flecha
 * con «antes». Una parte que no se midió es una caja gris punteada («Brazo · no se vio»). Es el elemento central del reporte (CLAUDE.md §3);
 * el gráfico en milésimas de segundo está en el detalle técnico.
 */

// Colores de segmento de la especificación §2; el brazo (blanco en la pantalla oscura) lleva trazo para verse también en el papel.
const COLOR: Record<SegmentoDeSecuencia, string> = { pelvis: "#a78bfa", torso: "#22d3ee", brazo: "#f1f5f9" };

export function SecuenciaSimple({ reporte }: { reporte: Record<string, unknown> }) {
  const s = secuenciaSimple(reporte);
  if (s.sinDatos) {
    return <p className="rounded-xl border border-dashed border-border p-4 text-sm text-muted-foreground">No se pudo ver qué giró primero en este golpe.</p>;
  }
  return (
    <div role="group" aria-label={s.resumen}>
      <ol className="flex flex-wrap items-center gap-x-2 gap-y-3">
        {s.cajas.map((c, i) => (
          <Fragment key={c.partes.join("-")}>
            {i > 0 && (
              <li aria-hidden="true" className="flex items-center gap-1 px-1 text-sm font-semibold text-muted-foreground">
                antes <ArrowRight className="h-4 w-4" />
              </li>
            )}
            <li className="rounded-2xl border border-border bg-card px-4 py-3">
              <span className="flex items-center gap-2 font-display text-lg font-bold">
                {c.partes.map((p) => (
                  <span
                    key={p}
                    aria-hidden="true"
                    className="inline-block h-3 w-3 rounded-full border border-foreground/40"
                    style={{ backgroundColor: COLOR[p] }}
                  />
                ))}
                {c.etiqueta}
              </span>
              {c.casiALaVez && <span className="mt-0.5 block text-sm text-muted-foreground">casi a la vez</span>}
            </li>
          </Fragment>
        ))}
        {s.noVistas.map((n) => (
          <li key={n.segmento} className="rounded-2xl border border-dashed border-muted-foreground/50 bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
            {n.etiqueta}
          </li>
        ))}
      </ol>
    </div>
  );
}
