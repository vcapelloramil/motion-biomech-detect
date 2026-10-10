import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { CheckCircle2, AlertTriangle, CircleSlash, ChevronRight, FlaskConical } from "lucide-react";
import { EstadoBadge, ESTADOS, type Estado } from "@/components/estado";
import { GraficoSecuenciacion } from "@/components/reporte/grafico-secuenciacion";
import { ReproductorSincronizado } from "@/components/reporte/reproductor-sincronizado";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  CASOS,
  CONFIANZA_POR_ARTICULACION,
  ETIQUETAS,
  METRICAS,
  MOTOR,
  REFERENCIAS,
  TRAMO_NO_AUDITABLE,
  type Caso,
} from "@/lib/reporte-mock";
import { RutaProtegida } from "@/components/ruta-protegida";
import { DatosDeEjemplo } from "@/components/datos-de-ejemplo";

/**
 * Parametros de captura de pantalla. Dejan la pantalla en un estado concreto sin
 * tocar el panel de demostracion, para que no aparezca en la imagen:
 *   /reporte?caso=alterado&tramo=auditable&demo=false
 */
interface BusquedaReporte {
  caso?: Caso["id"];
  tramo?: "auditable" | "no-auditable";
  demo?: false;
}

export const Route = createFileRoute("/reporte/")({
  validateSearch: (busqueda: Record<string, unknown>): BusquedaReporte => ({
    caso:
      busqueda.caso === "alterado"
        ? "alterado"
        : busqueda.caso === "correcto"
          ? "correcto"
          : undefined,
    tramo:
      busqueda.tramo === "auditable"
        ? "auditable"
        : busqueda.tramo === "no-auditable"
          ? "no-auditable"
          : undefined,
    demo: busqueda.demo === false ? false : undefined,
  }),
  head: () => ({
    meta: [
      { title: "Reporte — KinetiQ" },
      {
        name: "description",
        content:
          "Veredicto, evidencia y fundamento del gesto analizado: orden de los picos de velocidad, ángulos medidos y trazabilidad del cálculo.",
      },
    ],
  }),
  // Requiere sesión (especificación §3). La barrera real son RLS y la API; esto evita mostrar datos de ejemplo a un anónimo.
  component: () => (
    <RutaProtegida>
      <ReportePage />
    </RutaProtegida>
  ),
});

/**
 * Jerarquia de tres niveles (seccion 3 del CLAUDE.md).
 * Nivel 1 — Veredicto: maximo TRES observaciones, lenguaje llano, sin desplazamiento.
 * Nivel 2 — Evidencia: grafico de secuenciacion, reproductor, metricas medidas.
 * Nivel 3 — Dato y fundamento: valores, confianza, parametros y bibliografia.
 */

interface Observacion {
  estado: Estado;
  texto: string;
  destino: string;
  destinoLabel: string;
}

const OBSERVACIONES: Observacion[] = [
  {
    estado: "correcto",
    texto:
      "La secuencia se ordenó correctamente en 5 de 6 saques: cadera, torso y brazo alcanzaron su velocidad máxima en el orden esperado.",
    destino: "#secuenciacion",
    destinoLabel: "Ver gráfico de secuenciación",
  },
  {
    estado: "desvio",
    texto: "El torso alcanzó su pico 30 ms más tarde que en tu sesión del 12 de mayo.",
    destino: "#reproductor",
    destinoLabel: "Ver curvas de velocidad",
  },
  {
    estado: "no-auditable",
    texto: "No se pudo medir el instante de impacto en 2 de 6 saques.",
    destino: "#metricas",
    destinoLabel: "Ver métricas medidas",
  },
];

function ReportePage() {
  const busqueda = Route.useSearch();
  const [casoId, setCasoId] = useState<Caso["id"]>(busqueda.caso ?? "correcto");
  const [tramoNoAuditable, setTramoNoAuditable] = useState(busqueda.tramo !== "auditable");
  const caso = CASOS[casoId];

  return (
    <main className="mx-auto max-w-6xl px-6 py-16">
      <DatosDeEjemplo detalle="Este reporte es una maqueta con valores inventados: todavía no muestra el resultado real de tu video (pieza 8 del plan)." />
      {import.meta.env.DEV && busqueda.demo !== false && (
        <div className="mb-8 rounded-2xl border border-dashed border-border bg-card/50 p-4">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
            <span className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              <FlaskConical className="h-3 w-3" /> Demostración · solo en desarrollo
            </span>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                Secuencia
              </span>
              {(Object.keys(CASOS) as Caso["id"][]).map((id) => (
                <button
                  key={id}
                  onClick={() => setCasoId(id)}
                  className={`rounded-lg border px-3 py-1.5 font-mono text-xs transition-colors ${
                    casoId === id
                      ? "border-neon/60 bg-neon/10 text-neon"
                      : "border-border text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {id === "correcto" ? "correcta" : "alterada"}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                Tramo del impacto
              </span>
              {[false, true].map((v) => (
                <button
                  key={String(v)}
                  onClick={() => setTramoNoAuditable(v)}
                  className={`rounded-lg border px-3 py-1.5 font-mono text-xs transition-colors ${
                    tramoNoAuditable === v
                      ? "border-neon/60 bg-neon/10 text-neon"
                      : "border-border text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {v ? "no auditable" : "auditable"}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ───────── NIVEL 1 · VEREDICTO ───────── */}
      <div className="font-mono text-xs uppercase tracking-widest text-neon">
        / Reporte · Nivel 1 · Veredicto
      </div>
      <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl font-bold md:text-5xl">
            Saque · <span className="text-gradient-neon">6 repeticiones</span>
          </h1>
          <p className="mt-2 font-mono text-sm text-muted-foreground">
            Sesión del 12 de mayo de 2026 · video a {MOTOR.fpsVideo} fps
          </p>
        </div>
        <div className="rounded-2xl border border-border bg-card px-5 py-4">
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Cobertura auditable
          </div>
          <div className="mt-1 font-display text-2xl font-bold">
            4 <span className="text-base text-muted-foreground">de 6 repeticiones</span>
          </div>
          <div className="mt-2">
            <EstadoBadge estado="no-auditable">2 sin instante de impacto</EstadoBadge>
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {OBSERVACIONES.map((o) => {
          const e = ESTADOS[o.estado];
          const Icono =
            o.estado === "correcto"
              ? CheckCircle2
              : o.estado === "desvio"
                ? AlertTriangle
                : CircleSlash;
          return (
            <a
              key={o.texto}
              href={o.destino}
              className={`group flex flex-col rounded-2xl border bg-card p-5 transition-all hover:-translate-y-0.5 ${e.borde}`}
            >
              <div className="flex items-center gap-2">
                <Icono className={`h-5 w-5 shrink-0 ${e.texto}`} />
                <span className={`font-mono text-[10px] uppercase tracking-widest ${e.texto}`}>
                  {e.label}
                </span>
              </div>
              <p className="mt-3 flex-1 text-sm leading-relaxed">{o.texto}</p>
              <span className="mt-4 inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground group-hover:text-foreground">
                {o.destinoLabel}
                <ChevronRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
              </span>
            </a>
          );
        })}
      </div>

      {/* ───────── NIVEL 2 · EVIDENCIA ───────── */}
      <div className="mt-14 space-y-6">
        <GraficoSecuenciacion caso={caso} onCambiarCaso={setCasoId} />
        <ReproductorSincronizado caso={caso} tramoNoAuditable={tramoNoAuditable} />

        {/* METRICAS MEDIDAS */}
        <section
          id="metricas"
          className="scroll-mt-24 rounded-3xl border border-border bg-card p-6 md:p-8"
        >
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Nivel 2 · Evidencia
          </div>
          <h3 className="mt-1 font-display text-2xl font-bold">Métricas medidas</h3>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            Magnitudes que el motor calcula sobre este gesto. Cada una lleva su estado y su nivel de
            confianza.
          </p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {METRICAS.map((m) => {
              const e = ESTADOS[m.estado];
              return (
                <div key={m.nombre} className={`rounded-2xl border bg-background p-5 ${e.borde}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="font-display font-semibold">{m.nombre}</div>
                    <EstadoBadge estado={m.estado} />
                  </div>
                  <div className="mt-4 flex items-end gap-2">
                    {m.valor ? (
                      <>
                        <span className={`font-display text-4xl font-bold ${e.texto}`}>
                          {m.valor}
                        </span>
                        <span className="pb-1 font-display text-xl text-muted-foreground">
                          {m.unidad}
                        </span>
                      </>
                    ) : (
                      <span className="font-display text-2xl font-bold text-state-none">
                        No auditable
                      </span>
                    )}
                  </div>
                  <div className="mt-4 flex items-center justify-between font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    <span>
                      Confianza{" "}
                      {m.confianza !== null ? (
                        <span className="text-foreground">
                          {m.confianza.toFixed(2).replace(".", ",")}
                        </span>
                      ) : (
                        <span className="text-state-none">bajo umbral</span>
                      )}
                    </span>
                    <span>{m.referencia}</span>
                  </div>
                  {m.confianza !== null && (
                    <div className="mt-2 h-1 overflow-hidden rounded-full bg-secondary">
                      <div
                        className={`h-full rounded-full ${e.relleno}`}
                        style={{ width: `${m.confianza * 100}%` }}
                      />
                    </div>
                  )}
                  <p className="mt-3 text-xs text-muted-foreground">{m.detalle}</p>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      {/* ───────── NIVEL 3 · DATO Y FUNDAMENTO ───────── */}
      <section className="mt-6 rounded-3xl border border-border bg-card p-6 md:p-8">
        <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          Nivel 3 · Dato y fundamento
        </div>
        <h3 className="mt-1 font-display text-2xl font-bold">Trazabilidad</h3>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Todo lo que hay que poder responder sobre cualquier número de esta pantalla: de dónde
          salió, con qué confianza y con qué fuente.
        </p>

        <Accordion type="multiple" className="mt-4">
          <AccordionItem value="valores">
            <AccordionTrigger className="font-display text-base">
              Valores numéricos completos
            </AccordionTrigger>
            <AccordionContent>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[34rem] text-left font-mono text-xs">
                  <thead className="text-muted-foreground">
                    <tr className="border-b border-border">
                      <th className="py-2 font-normal uppercase tracking-widest">Segmento</th>
                      <th className="py-2 font-normal uppercase tracking-widest">Pico (s)</th>
                      <th className="py-2 font-normal uppercase tracking-widest">Pico (ms)</th>
                      <th className="py-2 font-normal uppercase tracking-widest">Δ al anterior</th>
                      <th className="py-2 font-normal uppercase tracking-widest">Confianza</th>
                    </tr>
                  </thead>
                  <tbody>
                    {caso.segmentos.map((s, i) => {
                      const previo = i > 0 ? caso.segmentos[i - 1].pico : null;
                      const delta = previo !== null ? Math.round((s.pico - previo) * 1000) : null;
                      return (
                        <tr key={s.id} className="border-b border-border/50">
                          <td className="py-2">{ETIQUETAS[s.id]}</td>
                          <td className="py-2">{s.pico.toFixed(3).replace(".", ",")}</td>
                          <td className="py-2">{Math.round(s.pico * 1000)}</td>
                          <td
                            className={`py-2 ${delta !== null && delta < 0 ? "text-state-alert" : ""}`}
                          >
                            {delta === null ? "—" : `${delta > 0 ? "+" : ""}${delta} ms`}
                          </td>
                          <td className="py-2">{s.confianza.toFixed(2).replace(".", ",")}</td>
                        </tr>
                      );
                    })}
                    <tr>
                      <td className="py-2">Impacto</td>
                      <td className="py-2">{caso.impacto.toFixed(3).replace(".", ",")}</td>
                      <td className="py-2">{Math.round(caso.impacto * 1000)}</td>
                      <td className="py-2">—</td>
                      <td className="py-2 text-state-none">
                        {tramoNoAuditable ? "bajo umbral" : "0,79"}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="confianza">
            <AccordionTrigger className="font-display text-base">
              Confianza por articulación
            </AccordionTrigger>
            <AccordionContent>
              <div className="grid gap-3 sm:grid-cols-2">
                {CONFIANZA_POR_ARTICULACION.map((c) => {
                  const bajo = c.valor < 0.7;
                  return (
                    <div
                      key={c.articulacion}
                      className="rounded-xl border border-border bg-background p-3"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span>{c.articulacion}</span>
                        <span
                          className={`font-mono ${bajo ? "text-state-none" : "text-foreground"}`}
                        >
                          {c.valor.toFixed(2).replace(".", ",")}
                        </span>
                      </div>
                      <div className="mt-2 h-1 overflow-hidden rounded-full bg-secondary">
                        <div
                          className={`h-full rounded-full ${bajo ? "bg-state-none" : "bg-state-ok"}`}
                          style={{ width: `${c.valor * 100}%` }}
                        />
                      </div>
                      <div className="mt-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                        {c.cuadrosDescartados} cuadros descartados
                        {bajo && <span className="text-state-none"> · bajo umbral</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="mt-4 text-xs text-muted-foreground">
                Umbral de aceptación: 0,70. Por debajo de ese valor el segmento se marca como no
                auditable y no se rellena con una estimación.
              </p>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="parametros">
            <AccordionTrigger className="font-display text-base">
              Parámetros del procesamiento
            </AccordionTrigger>
            <AccordionContent>
              <dl className="grid gap-4 sm:grid-cols-2">
                {[
                  ["Versión del motor", MOTOR.version],
                  ["Backend de pose", MOTOR.backendPose],
                  ["Filtro", MOTOR.filtro],
                  ["Frecuencia de corte", `${MOTOR.corteHz} Hz`],
                  ["Frecuencia del video", `${MOTOR.fpsVideo} fps`],
                  [
                    "Tramo no auditable",
                    tramoNoAuditable
                      ? `${TRAMO_NO_AUDITABLE.desde}–${TRAMO_NO_AUDITABLE.hasta} s`
                      : "ninguno",
                  ],
                ].map(([k, v]) => (
                  <div key={k} className="rounded-xl border border-border bg-background p-3">
                    <dt className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                      {k}
                    </dt>
                    <dd className="mt-1 text-sm">{v}</dd>
                  </div>
                ))}
              </dl>
              <p className="mt-4 text-xs text-muted-foreground">
                El filtro se aplica hacia adelante y hacia atrás. Un filtro unidireccional correría
                los picos en el tiempo, que es justamente lo que este reporte mide.
              </p>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="fuentes" className="border-b-0">
            <AccordionTrigger className="font-display text-base">
              Fundamento bibliográfico
            </AccordionTrigger>
            <AccordionContent>
              <ul className="space-y-4">
                {REFERENCIAS.map((r) => (
                  <li key={r.clave} className="rounded-xl border border-border bg-background p-4">
                    <div className="font-mono text-[10px] uppercase tracking-widest text-neon">
                      {r.clave}
                    </div>
                    <p className="mt-1 text-sm">{r.cita}</p>
                    <p className="mt-2 text-xs text-muted-foreground">Respalda: {r.usoEn}</p>
                  </li>
                ))}
              </ul>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-border pt-5">
          <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Sello del reporte
          </span>
          <span className="rounded-full border border-border px-3 py-1 font-mono text-[10px] text-muted-foreground">
            {MOTOR.sello}
          </span>
        </div>
      </section>

      <p className="mt-8 text-center text-xs text-muted-foreground">
        KinetiQ documenta el movimiento observado. La interpretación clínica corresponde al
        profesional.
      </p>
    </main>
  );
}
