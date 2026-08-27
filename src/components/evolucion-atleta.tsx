import { CircleSlash } from "lucide-react";
import { EVOLUCION } from "@/lib/evolucion-mock";

/**
 * Comparar al jugador consigo mismo es la base del reporte (seccion 3 del
 * CLAUDE.md): no hay promedio poblacional ni "modelo ideal" en esta vista.
 *
 * Dos paneles de linea sobre el mismo eje de sesiones, en vez de un solo
 * grafico de doble eje: las magnitudes tienen unidades distintas (grados y
 * milisegundos) y superponerlas en una escala compartida sugeriria una
 * correlacion que el dato no afirma.
 */

const W = 640;
const H = 176;
const PAD_L = 54;
const PAD_R = 18;
const PAD_T = 18;
const PAD_B = 34;
const PLOT_W = W - PAD_L - PAD_R;
const PLOT_H = H - PAD_T - PAD_B;

function PanelLinea({
  titulo,
  unidad,
  color,
  valores,
  etiquetas,
  nota,
}: {
  titulo: string;
  unidad: string;
  color: string;
  valores: (number | null)[];
  etiquetas: string[];
  nota: string;
}) {
  const presentes = valores.filter((v): v is number => v !== null);
  const min = Math.min(...presentes);
  const max = Math.max(...presentes);
  const margen = (max - min) * 0.35 || 1;
  const lo = min - margen;
  const hi = max + margen;

  const x = (i: number) => PAD_L + (i / (valores.length - 1)) * PLOT_W;
  const y = (v: number) => PAD_T + PLOT_H - ((v - lo) / (hi - lo)) * PLOT_H;

  // Un valor faltante corta la linea: no se interpola para tapar el hueco.
  const tramos: { i: number; v: number }[][] = [];
  let actual: { i: number; v: number }[] = [];
  valores.forEach((v, i) => {
    if (v === null) {
      if (actual.length) tramos.push(actual);
      actual = [];
    } else {
      actual.push({ i, v });
    }
  });
  if (actual.length) tramos.push(actual);

  const ticksY = [min, max];

  return (
    <div className="rounded-2xl border border-border bg-background p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div className="font-display font-semibold">{titulo}</div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          {unidad}
        </div>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="mt-3 w-full" role="img" aria-label={titulo}>
        {ticksY.map((v) => (
          <g key={v}>
            <line
              x1={PAD_L}
              y1={y(v)}
              x2={PAD_L + PLOT_W}
              y2={y(v)}
              stroke="var(--border)"
              strokeWidth={1}
              strokeDasharray="2 6"
            />
            <text
              x={PAD_L - 10}
              y={y(v) + 4}
              textAnchor="end"
              fill="var(--muted-foreground)"
              fontSize={11}
              fontFamily="var(--font-mono)"
            >
              {v}
            </text>
          </g>
        ))}

        {valores.map((v, i) =>
          v === null ? (
            <g key={`hueco-${i}`}>
              <line
                x1={x(i)}
                y1={PAD_T}
                x2={x(i)}
                y2={PAD_T + PLOT_H}
                stroke="var(--state-none)"
                strokeWidth={1}
                strokeDasharray="3 4"
                opacity={0.8}
              />
              <text
                x={x(i)}
                y={PAD_T + 12}
                textAnchor="middle"
                fill="var(--state-none)"
                fontSize={9}
                fontFamily="var(--font-mono)"
                letterSpacing="0.1em"
              >
                SIN DATO
              </text>
            </g>
          ) : null,
        )}

        {tramos.map((tramo, k) => (
          <polyline
            key={k}
            points={tramo.map((p) => `${x(p.i)},${y(p.v)}`).join(" ")}
            fill="none"
            stroke={color}
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ))}

        {valores.map((v, i) =>
          v === null ? (
            <circle
              key={`p-${i}`}
              cx={x(i)}
              cy={PAD_T + PLOT_H / 2}
              r={4}
              fill="var(--background)"
              stroke="var(--state-none)"
              strokeWidth={1.5}
              strokeDasharray="2 2"
            />
          ) : (
            <circle
              key={`p-${i}`}
              cx={x(i)}
              cy={y(v)}
              r={4}
              fill={color}
              stroke="var(--background)"
              strokeWidth={2}
            />
          ),
        )}

        {etiquetas.map((e, i) => (
          <text
            key={e}
            x={x(i)}
            y={H - 12}
            textAnchor="middle"
            fill="var(--muted-foreground)"
            fontSize={11}
            fontFamily="var(--font-mono)"
          >
            {e}
          </text>
        ))}
      </svg>

      <p className="mt-2 text-xs text-muted-foreground">{nota}</p>
    </div>
  );
}

export function EvolucionAtleta() {
  const etiquetas = EVOLUCION.map((s) => s.fecha);
  const sinDato = EVOLUCION.filter((s) => s.desfase === null).length;

  return (
    <section
      id="evolucion"
      className="scroll-mt-24 rounded-3xl border border-border bg-card p-6 md:p-8"
    >
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Evolución del atleta
          </div>
          <h2 className="mt-1 font-display text-2xl font-bold">Últimas seis sesiones</h2>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            El jugador comparado consigo mismo. No hay comparación contra un promedio poblacional ni
            contra un modelo ideal.
          </p>
        </div>
        {sinDato > 0 && (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-state-none/40 bg-state-none/10 px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-widest text-state-none">
            <CircleSlash className="h-3 w-3" />
            {sinDato} sesión sin dato de desfase
          </span>
        )}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <PanelLinea
          titulo="Separación cadera-hombro máxima"
          unidad="grados"
          color="var(--neon)"
          valores={EVOLUCION.map((s) => s.separacion)}
          etiquetas={etiquetas}
          nota="Ángulo entre el eje de la pelvis y el eje de los hombros en el instante de máxima disociación."
        />
        <PanelLinea
          titulo="Desfase entre picos · pelvis → torso"
          unidad="milisegundos"
          color="var(--clinic)"
          valores={EVOLUCION.map((s) => s.desfase)}
          etiquetas={etiquetas}
          nota="Tiempo entre el pico de velocidad de la pelvis y el del torso. El 01 de mayo no se midió: la confianza quedó bajo umbral."
        />
      </div>
    </section>
  );
}
