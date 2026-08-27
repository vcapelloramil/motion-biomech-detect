import { ArrowRight, Check, AlertOctagon } from "lucide-react";
import { EstadoBadge } from "@/components/estado";
import { CASOS, ETIQUETAS, ORDEN_ESPERADO, type Caso } from "@/lib/reporte-mock";

/**
 * Elemento central del producto (seccion 3 del CLAUDE.md):
 * un eje temporal unico con los instantes en que pelvis, torso y brazo alcanzan
 * su velocidad maxima. Correcto = escalera ordenada de izquierda a derecha.
 * Incorrecto = cruce.
 *
 * SVG a mano en vez de recharts: el grafico tiene tres marcadores sobre un eje
 * unico, no una serie continua, y asi el trazo de la escalera queda bajo control
 * exacto.
 */

const W = 720;
const H = 230;
const PAD_L = 96;
const PAD_R = 32;
const PAD_T = 24;
const PAD_B = 44;
const PLOT_W = W - PAD_L - PAD_R;
const PLOT_H = H - PAD_T - PAD_B;

const seg2 = (n: number) => n.toFixed(2).replace(".", ",");

export function GraficoSecuenciacion({
  caso,
  onCambiarCaso,
}: {
  caso: Caso;
  onCambiarCaso: (id: Caso["id"]) => void;
}) {
  const x = (t: number) => PAD_L + (t / caso.duracion) * PLOT_W;
  const y = (fila: number) => PAD_T + (fila + 0.5) * (PLOT_H / 3);

  // Las filas se dibujan siempre en el orden esperado (pelvis, torso, brazo).
  // Si los picos respetan ese orden, la poligonal baja en escalera hacia la
  // derecha; si no, vuelve sobre si misma y el cruce se ve solo.
  const filas = ORDEN_ESPERADO.map((id, i) => {
    const s = caso.segmentos.find((sg) => sg.id === id)!;
    return { ...s, fila: i, cx: x(s.pico), cy: y(i) };
  });

  const ordenado = caso.estado !== "alerta";
  const trazo = ordenado ? "var(--state-ok)" : "var(--state-alert)";
  const ticks = Array.from({ length: 8 }, (_, i) => i * 0.1);

  return (
    <section
      id="secuenciacion"
      className="scroll-mt-24 rounded-3xl border border-border bg-card p-6 md:p-8"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Nivel 2 · Evidencia
          </div>
          <h3 className="mt-1 font-display text-2xl font-bold">Secuenciación de la cadena</h3>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">
            Instante en que cada segmento alcanza su velocidad máxima, sobre un eje temporal único.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Repetición
          </span>
          <div className="flex gap-2">
            {(Object.keys(CASOS) as Caso["id"][]).map((id) => (
              <button
                key={id}
                onClick={() => onCambiarCaso(id)}
                className={`rounded-lg border px-3 py-1.5 font-mono text-xs transition-colors ${
                  caso.id === id
                    ? "border-neon/60 bg-neon/10 text-neon"
                    : "border-border text-muted-foreground hover:text-foreground"
                }`}
              >
                {CASOS[id].repeticion}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 overflow-x-auto">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full min-w-[36rem]"
          role="img"
          aria-label="Gráfico de secuenciación"
        >
          {/* eje temporal */}
          <line
            x1={PAD_L}
            y1={PAD_T + PLOT_H}
            x2={PAD_L + PLOT_W}
            y2={PAD_T + PLOT_H}
            stroke="var(--border)"
            strokeWidth={1}
          />
          {ticks.map((t) => (
            <g key={t}>
              <line
                x1={x(t)}
                y1={PAD_T + PLOT_H}
                x2={x(t)}
                y2={PAD_T + PLOT_H + 5}
                stroke="var(--border)"
                strokeWidth={1}
              />
              <text
                x={x(t)}
                y={PAD_T + PLOT_H + 20}
                textAnchor="middle"
                fill="var(--muted-foreground)"
                fontSize={11}
                fontFamily="var(--font-mono)"
              >
                {seg2(t)}
              </text>
            </g>
          ))}
          <text
            x={PAD_L + PLOT_W}
            y={PAD_T + PLOT_H + 38}
            textAnchor="end"
            fill="var(--muted-foreground)"
            fontSize={10}
            fontFamily="var(--font-mono)"
          >
            TIEMPO (s)
          </text>

          {/* impacto */}
          <line
            x1={x(caso.impacto)}
            y1={PAD_T - 8}
            x2={x(caso.impacto)}
            y2={PAD_T + PLOT_H}
            stroke="var(--muted-foreground)"
            strokeWidth={1}
            strokeDasharray="3 4"
          />
          <text
            x={x(caso.impacto) - 6}
            y={PAD_T - 12}
            textAnchor="end"
            fill="var(--muted-foreground)"
            fontSize={10}
            fontFamily="var(--font-mono)"
          >
            IMPACTO {seg2(caso.impacto)} s
          </text>

          {/* carriles */}
          {filas.map((f) => (
            <g key={f.id}>
              <line
                x1={PAD_L}
                y1={f.cy}
                x2={PAD_L + PLOT_W}
                y2={f.cy}
                stroke="var(--border)"
                strokeWidth={1}
                strokeDasharray="2 6"
              />
              <text
                x={PAD_L - 14}
                y={f.cy + 4}
                textAnchor="end"
                fill="var(--muted-foreground)"
                fontSize={11}
                fontFamily="var(--font-mono)"
                letterSpacing="0.12em"
              >
                {f.label.toUpperCase()}
              </text>
            </g>
          ))}

          {/* escalera: une los picos en el orden esperado */}
          <polyline
            points={filas.map((f) => `${f.cx},${f.cy}`).join(" ")}
            fill="none"
            stroke={trazo}
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity={0.85}
          />

          {/* marcadores */}
          {filas.map((f) => (
            <g key={`m-${f.id}`}>
              <line
                x1={f.cx}
                y1={f.cy}
                x2={f.cx}
                y2={PAD_T + PLOT_H}
                stroke={f.color}
                strokeWidth={1}
                opacity={0.35}
              />
              <circle
                cx={f.cx}
                cy={f.cy}
                r={7}
                fill={f.color}
                stroke="var(--card)"
                strokeWidth={2}
              />
              <text
                x={f.cx}
                y={f.cy - 14}
                textAnchor="middle"
                fill="var(--foreground)"
                fontSize={12}
                fontWeight={600}
                fontFamily="var(--font-mono)"
              >
                {seg2(f.pico)} s
              </text>
            </g>
          ))}

          {!ordenado && (
            <text
              x={x(caso.segmentos.find((s) => s.id === "torso")!.pico)}
              y={PAD_T + PLOT_H - 6}
              textAnchor="middle"
              fill="var(--state-alert)"
              fontSize={10}
              fontFamily="var(--font-mono)"
              letterSpacing="0.12em"
            >
              CRUCE
            </text>
          )}
        </svg>
      </div>

      {/* lectura en texto — nunca solo color */}
      <div className="mt-6 grid gap-4 rounded-2xl border border-border bg-background p-5 md:grid-cols-2">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Orden observado
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {caso.ordenObservado.map((id, i) => (
              <span key={id} className="flex items-center gap-2">
                {i > 0 && <ArrowRight className="h-3 w-3 text-muted-foreground" />}
                <span className="font-display font-semibold">{ETIQUETAS[id].toLowerCase()}</span>
              </span>
            ))}
          </div>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Orden esperado
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {ORDEN_ESPERADO.map((id, i) => (
              <span key={id} className="flex items-center gap-2">
                {i > 0 && <ArrowRight className="h-3 w-3 text-muted-foreground" />}
                <span className="font-display font-semibold text-muted-foreground">
                  {ETIQUETAS[id].toLowerCase()}
                </span>
              </span>
            ))}
          </div>
        </div>
        <div className="md:col-span-2">
          <div
            className={`flex items-start gap-3 rounded-xl border p-4 ${
              ordenado
                ? "border-state-ok/40 bg-state-ok/10"
                : "border-state-alert/40 bg-state-alert/10"
            }`}
          >
            {ordenado ? (
              <Check className="mt-0.5 h-5 w-5 shrink-0 text-state-ok" />
            ) : (
              <AlertOctagon className="mt-0.5 h-5 w-5 shrink-0 text-state-alert" />
            )}
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-display font-semibold">
                  {ordenado
                    ? "Coincide con el orden esperado"
                    : "No coincide con el orden esperado"}
                </span>
                <EstadoBadge estado={ordenado ? "correcto" : "alerta"} />
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{caso.veredicto}</p>
              {caso.alerta && (
                <p className="mt-2 font-mono text-[11px] text-muted-foreground">
                  Magnitud: {caso.alerta.magnitud} · Fuente: {caso.alerta.referencia}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
