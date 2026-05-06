import { createFileRoute } from "@tanstack/react-router";
import { AlertTriangle, HeartPulse, Stethoscope, Activity, Shield, FileText } from "lucide-react";

export const Route = createFileRoute("/clinica")({
  head: () => ({
    meta: [
      { title: "Análisis Clínico — KinetiQ" },
      { name: "description", content: "Evaluación de la cadena cinética, asimetrías y riesgo articular con visión artificial." },
    ],
  }),
  component: ClinicaPage,
});

function ClinicaPage() {
  const joints = [
    { name: "Hombro derecho", load: 78, status: "alto", note: "Sobrecarga rotacional en saque" },
    { name: "Codo derecho", load: 62, status: "medio", note: "Patrón compatible con epicondilitis temprana" },
    { name: "Lumbar", load: 45, status: "ok", note: "Carga dentro de rango" },
    { name: "Rodilla izquierda", load: 71, status: "medio", note: "Frenado asimétrico detectado" },
    { name: "Cadera", load: 38, status: "ok", note: "Buena rotación bilateral" },
    { name: "Muñeca derecha", load: 58, status: "medio", note: "Flexión excesiva en derecha" },
  ] as const;

  const chain = [
    { stage: "Pierna trasera (drive)", value: 95 },
    { stage: "Cadera → tronco", value: 88 },
    { stage: "Tronco → hombro", value: 74 },
    { stage: "Hombro → codo", value: 81 },
    { stage: "Codo → muñeca", value: 69 },
  ];

  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-clinic">
        <Stethoscope className="h-3 w-3" /> / Análisis clínico
      </div>
      <h1 className="mt-3 font-display text-5xl font-bold md:text-6xl">Tu cuerpo bajo el <span className="text-gradient-clinic">microscopio</span>.</h1>
      <p className="mt-4 max-w-2xl text-lg text-muted-foreground">Evaluación biomecánica automatizada usando keypoints YOLO. No reemplaza a un profesional de la salud, pero le da datos objetivos.</p>

      {/* RISK BANNER */}
      <div className="mt-10 flex items-start gap-4 rounded-2xl border border-destructive/40 bg-destructive/10 p-5">
        <AlertTriangle className="h-6 w-6 shrink-0 text-destructive" />
        <div>
          <div className="font-display text-lg font-semibold">Riesgo moderado detectado · Hombro derecho</div>
          <div className="text-sm text-muted-foreground">Patrón de carga repetitiva con apertura escapular limitada en 38 saques. Recomendamos revisión kinesiológica y reducir intensidad de saque 7-10 días.</div>
        </div>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-3">
        {/* KINETIC CHAIN */}
        <div className="rounded-2xl border border-clinic/30 bg-card p-6 lg:col-span-2">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-clinic" />
            <h3 className="font-display text-xl font-semibold">Cadena cinética · transferencia de energía</h3>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">Eficiencia con la que la energía viaja desde el suelo hasta la raqueta.</p>
          <div className="mt-6 space-y-4">
            {chain.map((c, i) => (
              <div key={c.stage} className="flex items-center gap-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-clinic/40 bg-clinic/10 font-mono text-xs text-clinic">{i + 1}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-display font-semibold">{c.stage}</span>
                    <span className="font-mono text-xs text-muted-foreground">{c.value}%</span>
                  </div>
                  <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-secondary">
                    <div className="h-full bg-gradient-clinic" style={{ width: `${c.value}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-xl border border-border bg-background p-4">
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Diagnóstico IA</div>
            <div className="mt-1 text-sm">Pérdida del <strong className="text-clinic">14%</strong> de energía en la transferencia tronco→hombro. Probable causa: rotación torácica insuficiente. Trabajo sugerido: movilidad T-spine y activación serrato anterior.</div>
          </div>
        </div>

        {/* ASYMMETRIES */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <h3 className="font-display text-xl font-semibold">Asimetrías</h3>
          <div className="mt-5 space-y-5">
            {[
              { l: "Rotación cadera", left: 58, right: 78 },
              { l: "Flexión rodilla", left: 92, right: 71 },
              { l: "Apertura escapular", left: 84, right: 62 },
            ].map((a) => (
              <div key={a.l}>
                <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground">{a.l}</div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex flex-1 justify-end">
                    <div className="h-3 rounded-l-full bg-clinic/60" style={{ width: `${a.left}%` }} />
                  </div>
                  <div className="font-mono text-[10px] text-muted-foreground">|</div>
                  <div className="flex flex-1">
                    <div className="h-3 rounded-r-full bg-neon/70" style={{ width: `${a.right}%` }} />
                  </div>
                </div>
                <div className="mt-1 flex justify-between font-mono text-[10px] text-muted-foreground">
                  <span>IZQ {a.left}°</span><span>DER {a.right}°</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* JOINT LOAD GRID */}
      <div className="mt-10">
        <h3 className="font-display text-2xl font-bold">Carga articular acumulada</h3>
        <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {joints.map((j) => {
            const colorMap = { ok: "text-court border-court/40 bg-court/10", medio: "text-clinic border-clinic/40 bg-clinic/10", alto: "text-destructive border-destructive/40 bg-destructive/10" } as const;
            return (
              <div key={j.name} className="rounded-2xl border border-border bg-card p-5">
                <div className="flex items-center justify-between">
                  <div className="font-display font-semibold">{j.name}</div>
                  <span className={`rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest ${colorMap[j.status]}`}>{j.status}</span>
                </div>
                <div className="mt-4 flex items-end gap-2">
                  <div className="font-display text-3xl font-bold">{j.load}<span className="text-base text-muted-foreground">%</span></div>
                </div>
                <div className="mt-2 h-1.5 rounded-full bg-secondary">
                  <div className={`h-full rounded-full ${j.status === "alto" ? "bg-destructive" : j.status === "medio" ? "bg-gradient-clinic" : "bg-court"}`} style={{ width: `${j.load}%` }} />
                </div>
                <div className="mt-3 text-sm text-muted-foreground">{j.note}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* PLAN */}
      <div className="mt-10 grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-clinic/30 bg-card p-6">
          <div className="flex items-center gap-2 text-clinic"><Shield className="h-5 w-5" /><h3 className="font-display text-xl font-semibold">Plan preventivo</h3></div>
          <ul className="mt-4 space-y-3 text-sm">
            {[
              "Movilidad torácica · 3×/semana · 10 min",
              "Activación serrato y manguito rotador · diaria",
              "Reducir intensidad de saque por 7 días",
              "Reevaluación con video en 14 días",
            ].map((t) => (
              <li key={t} className="flex items-start gap-2"><HeartPulse className="mt-0.5 h-4 w-4 shrink-0 text-clinic" />{t}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-2xl border border-border bg-card p-6">
          <div className="flex items-center gap-2"><FileText className="h-5 w-5 text-neon" /><h3 className="font-display text-xl font-semibold">Reporte para tu kinesiólogo</h3></div>
          <p className="mt-3 text-sm text-muted-foreground">Generamos un PDF con todas las métricas, screenshots de los frames críticos y comparativa pre/post.</p>
          <button className="mt-5 w-full rounded-xl bg-gradient-clinic px-6 py-3 font-display font-semibold text-neon-foreground shadow-clinic">
            Descargar reporte clínico (PDF)
          </button>
          <div className="mt-3 text-center font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Compatible HL7 · DICOM-ready</div>
        </div>
      </div>
    </main>
  );
}
