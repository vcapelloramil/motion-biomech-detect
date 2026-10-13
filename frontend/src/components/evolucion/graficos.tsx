import { CircleSlash } from "lucide-react";

/**
 * Gráficos de Evolución (paso 6). Sin color de estado: el turquesa de datos y el gris. Una sesión sin dato es un HUECO marcado "SIN DATO",
 * nunca un punto interpolado. Solo SVG propio (sin librería): la pantalla tiene que verse igual en papel.
 */

const W = 640;
const H = 200;
const PAD_L = 54;
const PAD_R = 18;
const PAD_T = 22;
const PAD_B = 36;
const PLOT_W = W - PAD_L - PAD_R;
const PLOT_H = H - PAD_T - PAD_B;

type Punto = { valor: number | null; dispersion?: number | null };

export function PanelLinea({
  titulo,
  unidad,
  puntos,
  etiquetas,
  banda,
  nota,
  textoBanda,
}: {
  titulo: string;
  unidad: string;
  puntos: Punto[];
  etiquetas: string[];
  /** Centro y semiancho de "tu variación habitual" (solo con 3 sesiones o más). */
  banda?: { centro: number; semiancho: number } | null;
  nota: string;
  textoBanda?: string;
}) {
  const presentes = puntos.filter((p): p is { valor: number; dispersion?: number | null } => p.valor !== null);
  const extremos = presentes.flatMap((p) => [p.valor - (p.dispersion ?? 0), p.valor + (p.dispersion ?? 0)]);
  if (banda) extremos.push(banda.centro - banda.semiancho, banda.centro + banda.semiancho);
  const min = extremos.length ? Math.min(...extremos) : 0;
  const max = extremos.length ? Math.max(...extremos) : 1;
  const margen = (max - min) * 0.2 || 1;
  const lo = min - margen;
  const hi = max + margen;
  const n = puntos.length;
  const x = (i: number) => PAD_L + (n === 1 ? PLOT_W / 2 : (i / (n - 1)) * PLOT_W);
  const y = (v: number) => PAD_T + PLOT_H - ((v - lo) / (hi - lo)) * PLOT_H;

  // Un valor faltante corta la línea: no se interpola para tapar el hueco.
  const tramos: { i: number; v: number }[][] = [];
  let actual: { i: number; v: number }[] = [];
  puntos.forEach((p, i) => {
    if (p.valor === null) {
      if (actual.length) tramos.push(actual);
      actual = [];
    } else {
      actual.push({ i, v: p.valor });
    }
  });
  if (actual.length) tramos.push(actual);

  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-display font-semibold">{titulo}</h3>
        <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{unidad}</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="mt-3 w-full" role="img" aria-label={`${titulo} por sesión`}>
        {banda && (
          <g>
            <rect
              x={PAD_L}
              y={y(banda.centro + banda.semiancho)}
              width={PLOT_W}
              height={Math.max(2, y(banda.centro - banda.semiancho) - y(banda.centro + banda.semiancho))}
              fill="var(--accent)"
              opacity={0.1}
            />
            <text x={PAD_L + PLOT_W - 4} y={y(banda.centro + banda.semiancho) - 5} textAnchor="end" fontSize={10} fill="var(--muted-foreground)" fontFamily="var(--font-mono)">
              {textoBanda ?? "tu variación habitual"}
            </text>
          </g>
        )}
        {[min, max].map((v) => (
          <g key={v}>
            <line x1={PAD_L} y1={y(v)} x2={PAD_L + PLOT_W} y2={y(v)} stroke="var(--border)" strokeWidth={1} strokeDasharray="2 6" />
            <text x={PAD_L - 10} y={y(v) + 4} textAnchor="end" fill="var(--muted-foreground)" fontSize={11} fontFamily="var(--font-mono)">
              {Math.round(v)}
            </text>
          </g>
        ))}
        {puntos.map((p, i) =>
          p.valor === null ? (
            <g key={`hueco-${i}`}>
              <line x1={x(i)} y1={PAD_T} x2={x(i)} y2={PAD_T + PLOT_H} stroke="var(--state-none)" strokeWidth={1} strokeDasharray="3 4" opacity={0.8} />
              <text x={x(i)} y={PAD_T + 12} textAnchor="middle" fill="var(--state-none)" fontSize={9} fontFamily="var(--font-mono)" letterSpacing="0.1em">
                SIN DATO
              </text>
            </g>
          ) : p.dispersion ? (
            <line key={`b-${i}`} x1={x(i)} y1={y(p.valor - p.dispersion)} x2={x(i)} y2={y(p.valor + p.dispersion)} stroke="var(--accent)" strokeWidth={2} opacity={0.45} />
          ) : null,
        )}
        {tramos.map((t, k) => (
          <polyline key={k} points={t.map((p) => `${x(p.i)},${y(p.v)}`).join(" ")} fill="none" stroke="var(--accent)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        ))}
        {puntos.map((p, i) =>
          p.valor === null ? null : (
            <g key={`p-${i}`}>
              <circle cx={x(i)} cy={y(p.valor)} r={4.5} fill="var(--accent)" stroke="var(--background)" strokeWidth={2} />
              <text x={x(i)} y={y(p.valor) - 10} textAnchor="middle" fontSize={11} fill="var(--foreground)" fontFamily="var(--font-mono)">
                {Math.round(p.valor)}°
              </text>
            </g>
          ),
        )}
        {etiquetas.map((e, i) => (
          <text key={`${e}-${i}`} x={x(i)} y={H - 12} textAnchor="middle" fill="var(--muted-foreground)" fontSize={11} fontFamily="var(--font-mono)">
            {e}
          </text>
        ))}
      </svg>
      <p className="mt-2 text-xs text-muted-foreground">{nota}</p>
    </div>
  );
}

export type BarraDeOrden = { mismo: number; ordenables: number; suficiente: boolean };

/** "En k de m golpes ordenables fue el mismo orden", por sesión. Sin suficientes ordenables es un hueco con el motivo. */
export function PanelBarras({ titulo, barras, etiquetas, nota }: { titulo: string; barras: BarraDeOrden[]; etiquetas: string[]; nota: string }) {
  const n = barras.length;
  const ancho = Math.min(70, (PLOT_W / Math.max(n, 1)) * 0.6);
  const x = (i: number) => PAD_L + (n === 1 ? PLOT_W / 2 : (i / (n - 1)) * PLOT_W);
  const maximo = Math.max(1, ...barras.map((b) => b.ordenables));
  const alto = (v: number) => (v / maximo) * PLOT_H;
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-display font-semibold">{titulo}</h3>
        <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">golpes</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="mt-3 w-full" role="img" aria-label={`${titulo} por sesión`}>
        <line x1={PAD_L} y1={PAD_T + PLOT_H} x2={PAD_L + PLOT_W} y2={PAD_T + PLOT_H} stroke="var(--border)" />
        {barras.map((b, i) =>
          b.suficiente ? (
            <g key={i}>
              <rect x={x(i) - ancho / 2} y={PAD_T + PLOT_H - alto(b.ordenables)} width={ancho} height={alto(b.ordenables)} fill="var(--secondary)" stroke="var(--border)" />
              <rect x={x(i) - ancho / 2} y={PAD_T + PLOT_H - alto(b.mismo)} width={ancho} height={alto(b.mismo)} fill="var(--accent)" />
              <text x={x(i)} y={PAD_T + PLOT_H - alto(b.ordenables) - 8} textAnchor="middle" fontSize={11} fill="var(--foreground)" fontFamily="var(--font-mono)">
                {b.mismo} de {b.ordenables}
              </text>
            </g>
          ) : (
            <g key={i}>
              <line x1={x(i)} y1={PAD_T} x2={x(i)} y2={PAD_T + PLOT_H} stroke="var(--state-none)" strokeWidth={1} strokeDasharray="3 4" opacity={0.8} />
              <text x={x(i)} y={PAD_T + 12} textAnchor="middle" fill="var(--state-none)" fontSize={9} fontFamily="var(--font-mono)" letterSpacing="0.1em">
                {b.ordenables === 0 ? "SIN ORDEN" : "POCOS"}
              </text>
            </g>
          ),
        )}
        {etiquetas.map((e, i) => (
          <text key={`${e}-${i}`} x={x(i)} y={H - 12} textAnchor="middle" fill="var(--muted-foreground)" fontSize={11} fontFamily="var(--font-mono)">
            {e}
          </text>
        ))}
      </svg>
      <p className="mt-2 text-xs text-muted-foreground">{nota}</p>
    </div>
  );
}

export function Hueco({ children }: { children: React.ReactNode }) {
  return (
    <p className="flex items-start gap-2 rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground">
      <CircleSlash className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>{children}</span>
    </p>
  );
}
