import { useMemo, useState } from "react";
import { EstadoBadge } from "@/components/estado";
import { serieVelocidad, TRAMO_NO_AUDITABLE, type Caso } from "@/lib/reporte-mock";
import frame from "@/assets/player-serve.jpg";

/**
 * Nivel 2 del reporte: video con esqueleto superpuesto, linea de tiempo con
 * marcas en los picos y curvas de velocidad por segmento sobre el mismo eje
 * temporal. Todo se posiciona en porcentaje del mismo ancho, asi el instante t
 * cae exactamente en la misma vertical en las tres piezas.
 */

const seg2 = (n: number) => n.toFixed(2).replace(".", ",");

/** Landmarks normalizados (0-100) ajustados al cuadro de src/assets/player-serve.jpg */
const J = {
  nariz: [48.5, 23.5],
  hombroD: [46, 31.5],
  hombroI: [56.5, 31],
  codoD: [40, 25.5],
  codoI: [64, 26],
  munecaD: [36.5, 20],
  munecaI: [69.5, 21],
  caderaD: [49.5, 53],
  caderaI: [58.5, 53],
  rodillaD: [42.5, 68.5],
  rodillaI: [63.5, 68.5],
  tobilloD: [34, 86],
  tobilloI: [68.5, 86.5],
} as const;

type Punto = readonly [number, number];

function Hueso({
  a,
  b,
  color,
  ancho = 2,
  discontinuo = false,
  opacidad = 1,
}: {
  a: Punto;
  b: Punto;
  color: string;
  ancho?: number;
  discontinuo?: boolean;
  opacidad?: number;
}) {
  return (
    <line
      x1={a[0]}
      y1={a[1]}
      x2={b[0]}
      y2={b[1]}
      stroke={color}
      strokeWidth={ancho}
      strokeDasharray={discontinuo ? "4 3" : undefined}
      strokeLinecap="round"
      opacity={opacidad}
      vectorEffect="non-scaling-stroke"
    />
  );
}

export function ReproductorSincronizado({
  caso,
  tramoNoAuditable,
}: {
  caso: Caso;
  tramoNoAuditable: boolean;
}) {
  const [t, setT] = useState(caso.impacto * 0.68);

  const series = useMemo(
    () => caso.segmentos.map((s) => ({ s, puntos: serieVelocidad(s, caso.duracion) })),
    [caso],
  );

  const pct = (valor: number) => (valor / caso.duracion) * 100;
  const enTramoCiego = tramoNoAuditable && t >= TRAMO_NO_AUDITABLE.desde;

  const grisNoAuditable = "var(--state-none)";

  return (
    <section
      id="reproductor"
      className="scroll-mt-24 rounded-3xl border border-border bg-card p-6 md:p-8"
    >
      <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
        Nivel 2 · Evidencia
      </div>
      <h3 className="mt-1 font-display text-2xl font-bold">Reproductor sincronizado</h3>
      <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
        El cuadro, la línea de tiempo y las curvas comparten el mismo eje. Al desplazar el tiempo,
        el marcador se mueve sobre las tres.
      </p>

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,22rem)_1fr]">
        {/* CUADRO CON ESQUELETO */}
        <div>
          <div className="relative aspect-square overflow-hidden rounded-2xl border border-border">
            <img
              src={frame}
              alt="Cuadro del saque analizado"
              className="h-full w-full object-cover"
            />
            <svg
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              className="absolute inset-0 h-full w-full"
              aria-hidden
            >
              {/* piernas y cuello: contexto, en neutro */}
              <Hueso a={J.nariz} b={[52.2, 31.2]} color="var(--muted-foreground)" opacidad={0.7} />
              <Hueso a={J.caderaD} b={J.rodillaD} color="var(--muted-foreground)" opacidad={0.7} />
              <Hueso a={J.rodillaD} b={J.tobilloD} color="var(--muted-foreground)" opacidad={0.7} />
              <Hueso a={J.caderaI} b={J.rodillaI} color="var(--muted-foreground)" opacidad={0.7} />
              <Hueso a={J.rodillaI} b={J.tobilloI} color="var(--muted-foreground)" opacidad={0.7} />
              <Hueso a={J.hombroI} b={J.codoI} color="var(--muted-foreground)" opacidad={0.7} />
              <Hueso a={J.codoI} b={J.munecaI} color="var(--muted-foreground)" opacidad={0.7} />

              {/* torso: hombros y laterales */}
              <Hueso a={J.hombroD} b={J.hombroI} color="var(--clinic)" ancho={3} />
              <Hueso a={J.hombroD} b={J.caderaD} color="var(--clinic)" ancho={2} opacidad={0.8} />
              <Hueso a={J.hombroI} b={J.caderaI} color="var(--clinic)" ancho={2} opacidad={0.8} />

              {/* pelvis */}
              <Hueso a={J.caderaD} b={J.caderaI} color="var(--neon)" ancho={3} />

              {/* brazo ejecutor: gris discontinuo si el tramo no es auditable */}
              <Hueso
                a={J.hombroD}
                b={J.codoD}
                color={tramoNoAuditable ? grisNoAuditable : "var(--foreground)"}
                ancho={3}
                discontinuo={tramoNoAuditable}
              />
              <Hueso
                a={J.codoD}
                b={J.munecaD}
                color={tramoNoAuditable ? grisNoAuditable : "var(--foreground)"}
                ancho={3}
                discontinuo={tramoNoAuditable}
              />

              {Object.values(J).map((p, i) => (
                <circle
                  key={i}
                  cx={p[0]}
                  cy={p[1]}
                  r={0.9}
                  fill="var(--background)"
                  stroke="var(--foreground)"
                  strokeWidth={1.2}
                  vectorEffect="non-scaling-stroke"
                />
              ))}
            </svg>

            <div className="absolute left-3 top-3 glass rounded-lg px-3 py-2 font-mono text-[10px]">
              <div className="text-muted-foreground">t = {seg2(t)} s</div>
              <div className="text-neon">{caso.repeticion}</div>
            </div>

            {tramoNoAuditable && (
              <div className="absolute bottom-3 left-3 right-3">
                <EstadoBadge estado="no-auditable" className="bg-background/80 backdrop-blur">
                  Codo y muñeca sin confianza
                </EstadoBadge>
              </div>
            )}
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Landmarks del motor superpuestos al cuadro. <span className="text-neon">Pelvis</span> ·{" "}
            <span className="text-clinic">torso</span> ·{" "}
            <span className={tramoNoAuditable ? "text-state-none" : "text-foreground"}>brazo</span>.
          </p>
        </div>

        {/* CURVAS + LINEA DE TIEMPO */}
        <div>
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Velocidad angular normalizada por segmento
            </div>
            <div className="font-mono text-xs text-muted-foreground">
              t = <span className="text-foreground">{seg2(t)} s</span>
            </div>
          </div>

          <div className="relative mt-3">
            <svg
              viewBox="0 0 100 40"
              preserveAspectRatio="none"
              className="h-44 w-full"
              role="img"
              aria-label="Curvas de velocidad por segmento"
            >
              {tramoNoAuditable && (
                <rect
                  x={pct(TRAMO_NO_AUDITABLE.desde)}
                  y={0}
                  width={pct(TRAMO_NO_AUDITABLE.hasta) - pct(TRAMO_NO_AUDITABLE.desde)}
                  height={40}
                  fill={grisNoAuditable}
                  opacity={0.16}
                />
              )}
              <line
                x1={0}
                y1={39.5}
                x2={100}
                y2={39.5}
                stroke="var(--border)"
                strokeWidth={1}
                vectorEffect="non-scaling-stroke"
              />
              {series.map(({ s, puntos }) => (
                <polyline
                  key={s.id}
                  points={puntos.map((p) => `${pct(p.t)},${40 - p.v * 35}`).join(" ")}
                  fill="none"
                  stroke={s.color}
                  strokeWidth={2}
                  strokeLinejoin="round"
                  vectorEffect="non-scaling-stroke"
                />
              ))}
              {caso.segmentos.map((s) => (
                <circle
                  key={`p-${s.id}`}
                  cx={pct(s.pico)}
                  cy={40 - s.amplitud * 35}
                  r={3}
                  fill={s.color}
                  stroke="var(--card)"
                  strokeWidth={1.5}
                  vectorEffect="non-scaling-stroke"
                />
              ))}
              <line
                x1={pct(t)}
                y1={0}
                x2={pct(t)}
                y2={40}
                stroke="var(--foreground)"
                strokeWidth={1.5}
                strokeDasharray="3 3"
                vectorEffect="non-scaling-stroke"
              />
            </svg>
          </div>

          {/* LINEA DE TIEMPO con marcas en los picos */}
          <div className="relative mt-4 h-14">
            <div className="absolute inset-x-0 top-2 h-1.5 rounded-full bg-secondary" />
            {tramoNoAuditable && (
              <div
                className="absolute top-2 h-1.5 rounded-full"
                style={{
                  left: `${pct(TRAMO_NO_AUDITABLE.desde)}%`,
                  width: `${pct(TRAMO_NO_AUDITABLE.hasta) - pct(TRAMO_NO_AUDITABLE.desde)}%`,
                  backgroundImage:
                    "repeating-linear-gradient(45deg, var(--state-none) 0 3px, transparent 3px 6px)",
                }}
              />
            )}
            <div
              className="absolute top-0 h-5 w-px bg-foreground"
              style={{ left: `${pct(t)}%` }}
              aria-hidden
            />
            {caso.segmentos.map((s) => (
              <div
                key={`marca-${s.id}`}
                className="absolute top-0 -translate-x-1/2 text-center"
                style={{ left: `${pct(s.pico)}%` }}
              >
                <div className="mx-auto h-5 w-0.5" style={{ background: s.color }} />
                <div className="mt-1 whitespace-nowrap font-mono text-[10px] text-muted-foreground">
                  {s.label} {seg2(s.pico)}
                </div>
              </div>
            ))}
            <div
              className="absolute top-0 -translate-x-1/2 text-center"
              style={{ left: `${pct(caso.impacto)}%` }}
            >
              <div className="mx-auto h-5 w-px bg-muted-foreground" />
              <div className="mt-1 whitespace-nowrap font-mono text-[10px] text-muted-foreground">
                Impacto
              </div>
            </div>
          </div>

          <input
            type="range"
            min={0}
            max={caso.duracion}
            step={0.005}
            value={t}
            onChange={(e) => setT(Number(e.target.value))}
            aria-label="Línea de tiempo del gesto"
            className="mt-6 w-full accent-[var(--neon)]"
          />

          {/* lectura instantanea */}
          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            {series.map(({ s, puntos }) => {
              const i = Math.round((t / caso.duracion) * (puntos.length - 1));
              const v = puntos[Math.max(0, Math.min(i, puntos.length - 1))].v;
              const ciego = enTramoCiego && s.id === "brazo";
              return (
                <div
                  key={`v-${s.id}`}
                  className="rounded-xl border border-border bg-background p-3"
                >
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
                    <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                      {s.label}
                    </span>
                  </div>
                  {ciego ? (
                    <div className="mt-1 flex items-center gap-2">
                      <span className="font-display text-xl font-bold text-state-none">—</span>
                      <span className="font-mono text-[10px] uppercase tracking-widest text-state-none">
                        no auditable
                      </span>
                    </div>
                  ) : (
                    <div className="mt-1 font-display text-xl font-bold">
                      {v.toFixed(2).replace(".", ",")}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {tramoNoAuditable && (
            <div className="mt-4 flex items-start gap-3 rounded-xl border border-state-none/40 bg-state-none/10 p-4">
              <div>
                <EstadoBadge estado="no-auditable">
                  Tramo {seg2(TRAMO_NO_AUDITABLE.desde)}–{seg2(TRAMO_NO_AUDITABLE.hasta)} s
                </EstadoBadge>
                <p className="mt-2 text-sm text-muted-foreground">
                  La confianza de codo y muñeca cayó por debajo del umbral en este tramo. No se
                  muestra un valor estimado en su lugar.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
