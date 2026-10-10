import { COLOR_SEGMENTO, NOMBRE_SEGMENTO, type PicoLeido, type Segmento } from "@/lib/reporte-simple";

/**
 * El elemento central del producto (CLAUDE.md §3): un eje temporal único con los instantes en que la cadera, el tronco
 * y el brazo alcanzan su velocidad máxima. Escalera ordenada de arriba a abajo y de izquierda a derecha = el orden
 * descrito en la literatura; si se cruzan, el cruce se ve solo.
 *
 * Dibuja SOLO lo que el motor midió (los picos del reporte). Si falta un segmento, esa fila queda vacía con su motivo:
 * no se completa con una estimación (R3). Con la escala temporal sin confirmar no se muestran segundos (R3/R4).
 */

const FILAS: Segmento[] = ["pelvis", "torso", "brazo"];
const W = 640;
const FILA_H = 56;
const PAD_L = 84;
const PAD_R = 28;
const PAD_T = 18;
const PAD_B = 40;
const H = PAD_T + FILAS.length * FILA_H + PAD_B;

const seg3 = (n: number) => n.toFixed(3).replace(".", ",");

export function SecuenciaReal({
  picos,
  mostrarTiempos,
  fps,
}: {
  picos: PicoLeido[];
  mostrarTiempos: boolean;
  /** Tasa de la grilla de tiempo del reporte (o la real media si no se regularizó): un fotograma = 1 / fps. */
  fps: number | null;
}) {
  const porSegmento = new Map(picos.map((p) => [p.segmento, p]));
  const instantes = picos.map((p) => p.instante_s);
  if (instantes.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-border p-5 text-sm text-muted-foreground">
        No se pudo medir el instante de ningún segmento en este golpe.
      </p>
    );
  }

  const fotograma = fps && fps > 0 ? 1 / fps : null;
  const minT = Math.min(...instantes);
  const maxT = Math.max(...instantes);
  // margen para que los rótulos no se corten y para que un empate se vea como empate
  const margen = Math.max((maxT - minT) * 0.18, fotograma ? fotograma * 4 : 0.02);
  const t0 = minT - margen;
  const t1 = maxT + margen;
  const plotW = W - PAD_L - PAD_R;
  const x = (t: number) => PAD_L + ((t - t0) / (t1 - t0)) * plotW;
  const y = (i: number) => PAD_T + i * FILA_H + FILA_H / 2;

  const puntos = FILAS.map((s, i) => ({ s, i, p: porSegmento.get(s) })).filter((f) => f.p);

  return (
    <figure>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={
          "Instantes de velocidad máxima: " +
          FILAS.map((s) => {
            const p = porSegmento.get(s);
            return `${NOMBRE_SEGMENTO[s]} ${p ? (mostrarTiempos ? seg3(p.instante_s) + " s" : "medido") : "no medido"}`;
          }).join(", ")
        }
        className="w-full"
      >
        {/* filas */}
        {FILAS.map((s, i) => (
          <g key={s}>
            <line x1={PAD_L} x2={W - PAD_R} y1={y(i)} y2={y(i)} stroke="var(--border)" strokeDasharray="3 5" />
            <text x={PAD_L - 12} y={y(i) + 4} textAnchor="end" fontSize="13" fill="var(--foreground)" fontWeight="600">
              {NOMBRE_SEGMENTO[s][0].toUpperCase() + NOMBRE_SEGMENTO[s].slice(1)}
            </text>
          </g>
        ))}

        {/* la escalera: une los picos en el orden de las filas */}
        {puntos.length > 1 && (
          <polyline
            points={puntos.map((f) => `${x(f.p!.instante_s)},${y(f.i)}`).join(" ")}
            fill="none"
            stroke="var(--muted-foreground)"
            strokeOpacity="0.55"
            strokeWidth="1.5"
          />
        )}

        {/* un fotograma de resolución, junto al primer pico */}
        {mostrarTiempos && fotograma && (
          <g>
            <line x1={x(t0 + margen * 0.35)} x2={x(t0 + margen * 0.35 + fotograma)} y1={H - PAD_B + 14} y2={H - PAD_B + 14} stroke="var(--muted-foreground)" strokeWidth="3" />
            <text x={x(t0 + margen * 0.35)} y={H - PAD_B + 32} fontSize="11" fill="var(--muted-foreground)">
              1 fotograma ≈ {(fotograma * 1000).toFixed(1).replace(".", ",")} ms
            </text>
          </g>
        )}

        {/* marcadores */}
        {FILAS.map((s, i) => {
          const p = porSegmento.get(s);
          if (!p) {
            return (
              <text key={s} x={PAD_L + 8} y={y(i) + 4} fontSize="12" fill="var(--muted-foreground)">
                no medido
              </text>
            );
          }
          return (
            <g key={s}>
              <circle cx={x(p.instante_s)} cy={y(i)} r="9" fill={COLOR_SEGMENTO[s]} stroke="var(--background)" strokeWidth="3" />
              {mostrarTiempos && (
                <text x={x(p.instante_s)} y={y(i) - 16} textAnchor="middle" fontSize="12" fill="var(--foreground)" fontFamily="var(--font-mono)">
                  {seg3(p.instante_s)} s
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <figcaption className="mt-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
        {mostrarTiempos ? "Segundos desde el inicio de la ventana analizada" : "Orden de los picos; los tiempos no se muestran porque la escala temporal no está confirmada"}
      </figcaption>
    </figure>
  );
}
