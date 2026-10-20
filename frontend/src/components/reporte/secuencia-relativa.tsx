import { datosDeSecuencia } from "@/lib/textos-reporte";

/**
 * «Cuándo giró cada parte» (el elemento central del producto, CLAUDE.md §3), simplificado en la decisión 039: todo relativo al TRONCO
 * (tronco = 0), en milésimas de segundo, con una franja sombreada de ± la diferencia mínima para poder ordenar dos momentos. Un punto dentro
 * de la franja no se puede ordenar respecto del tronco. Dibuja solo lo medido; lo que no, queda como «no medido» (R3).
 */

const FILAS = ["pelvis", "torso", "brazo"] as const;
const NOMBRE = { pelvis: "Cadera", torso: "Tronco", brazo: "Brazo" } as const;
// Colores de segmento de la especificación §2; el brazo (blanco en la pantalla oscura) lleva trazo para verse también en el papel.
const COLOR = { pelvis: "#a78bfa", torso: "#22d3ee", brazo: "#f1f5f9" } as const;

const W = 360;
const PAD_L = 62;
const PAD_R = 18;
const TOP = 46;
const FILA_H = 50;
const BASE = TOP + FILAS.length * FILA_H;
const H = BASE + 62;

const PASOS = [5, 10, 20, 25, 50, 100, 200, 500];

export function SecuenciaRelativa({ reporte }: { reporte: Record<string, unknown> }) {
  const d = datosDeSecuencia(reporte);
  if (d.sinReferencia) {
    return <p className="rounded-xl border border-dashed border-border p-5 text-sm text-muted-foreground">{d.resumen}</p>;
  }
  const tol = d.toleranciaMs;
  const deltas = d.puntos.map((p) => p.deltaMs).filter((x): x is number => x !== null);
  const margen = Math.max(tol * 1.5, 12);
  const minX = Math.min(-tol * 2.5, Math.min(...deltas) - margen);
  const maxX = Math.max(tol * 2.5, Math.max(...deltas) + margen);
  const plotW = W - PAD_L - PAD_R;
  const x = (ms: number) => PAD_L + ((ms - minX) / (maxX - minX)) * plotW;
  const y = (i: number) => TOP + i * FILA_H + FILA_H / 2;
  const paso = PASOS.find((s) => (maxX - minX) / s <= 7) ?? 500;
  const marcas: number[] = [];
  for (let t = Math.ceil(minX / paso) * paso; t <= maxX; t += paso) marcas.push(t);
  const cx = Math.min(Math.max(x(0), PAD_L + 85), W - PAD_R - 85);

  return (
    <figure>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`Cuándo giró cada parte, respecto del tronco. ${d.resumen}. La zona donde no se puede distinguir cuál fue primero es de más o menos ${Math.round(tol)} milésimas de segundo.`}
        className="mx-auto w-full max-w-xl"
      >
        {/* franja de ± la tolerancia: no se puede decir cuál fue primero */}
        <rect x={x(-tol)} y={TOP - 6} width={x(tol) - x(-tol)} height={FILAS.length * FILA_H + 6} fill="var(--muted-foreground)" fillOpacity="0.18" />
        <text x={cx} y={TOP - 28} textAnchor="middle" fontSize="11" fill="var(--muted-foreground)">
          Zona donde no se puede distinguir
        </text>
        <text x={cx} y={TOP - 15} textAnchor="middle" fontSize="11" fill="var(--muted-foreground)">
          cuál fue primero (± {Math.round(tol)} ms)
        </text>

        {/* la línea del tronco = 0 */}
        <line x1={x(0)} x2={x(0)} y1={TOP - 6} y2={BASE} stroke="var(--muted-foreground)" strokeDasharray="3 4" strokeOpacity="0.7" />

        {FILAS.map((s, i) => (
          <g key={s}>
            <line x1={PAD_L} x2={W - PAD_R} y1={y(i)} y2={y(i)} stroke="var(--border)" strokeDasharray="2 5" />
            <text x={PAD_L - 10} y={y(i) + 4} textAnchor="end" fontSize="13" fontWeight="600" fill="var(--foreground)">
              {NOMBRE[s]}
            </text>
          </g>
        ))}

        {d.puntos.map((p, i) =>
          p.deltaMs === null ? (
            <text key={p.segmento} x={PAD_L + 10} y={y(i) + 4} fontSize="12" fill="var(--muted-foreground)">
              no medido
            </text>
          ) : (
            <g key={p.segmento}>
              <circle cx={x(p.deltaMs)} cy={y(i)} r="9" fill={COLOR[p.segmento]} stroke="var(--foreground)" strokeOpacity="0.55" strokeWidth="1.5" />
              <text
                x={Math.min(Math.max(x(p.deltaMs), PAD_L + 34), W - PAD_R - 34)}
                y={y(i) - 15}
                textAnchor="middle"
                fontSize="12"
                fill="var(--foreground)"
                fontFamily="var(--font-mono)"
              >
                {p.etiqueta}
              </text>
            </g>
          ),
        )}

        {/* eje en milésimas de segundo, respecto del tronco */}
        <line x1={PAD_L} x2={W - PAD_R} y1={BASE + 6} y2={BASE + 6} stroke="var(--muted-foreground)" strokeOpacity="0.6" />
        {marcas.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={BASE + 6} y2={BASE + 11} stroke="var(--muted-foreground)" strokeOpacity="0.6" />
            <text x={x(t)} y={BASE + 25} textAnchor="middle" fontSize="10.5" fill="var(--muted-foreground)" fontFamily="var(--font-mono)">
              {t === 0 ? "0" : t > 0 ? `+${t}` : `−${Math.abs(t)}`}
            </text>
          </g>
        ))}
        <text x={PAD_L + plotW / 2} y={BASE + 43} textAnchor="middle" fontSize="10.5" fill="var(--muted-foreground)">
          milésimas de segundo respecto del tronco
        </text>
        <text x={PAD_L + plotW / 2} y={BASE + 57} textAnchor="middle" fontSize="10.5" fill="var(--muted-foreground)">
          izquierda: antes del tronco · derecha: después
        </text>
      </svg>
    </figure>
  );
}
