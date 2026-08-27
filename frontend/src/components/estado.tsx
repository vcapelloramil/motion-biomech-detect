import { CheckCircle2, AlertTriangle, AlertOctagon, CircleSlash } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * R3 del CLAUDE.md — el semaforo tiene CUATRO estados y ninguno se comunica
 * solo por color: cada uno lleva siempre icono + texto.
 *
 * Este modulo centraliza los cuatro estados para que todas las pantallas
 * (carga, reporte, biblioteca) usen exactamente la misma semantica.
 */
export type Estado = "correcto" | "desvio" | "alerta" | "no-auditable";

export const ESTADOS = {
  correcto: {
    label: "Correcto",
    descripcion: "Dentro del rango de referencia",
    Icono: CheckCircle2,
    texto: "text-state-ok",
    borde: "border-state-ok/40",
    fondo: "bg-state-ok/10",
    relleno: "bg-state-ok",
  },
  desvio: {
    label: "Desvío leve",
    descripcion: "Se aparta, sin alcanzar criterio de alerta",
    Icono: AlertTriangle,
    texto: "text-state-warn",
    borde: "border-state-warn/40",
    fondo: "bg-state-warn/10",
    relleno: "bg-state-warn",
  },
  alerta: {
    label: "Alerta de carga",
    descripcion: "Patrón asociado en la literatura con mayor carga articular",
    Icono: AlertOctagon,
    texto: "text-state-alert",
    borde: "border-state-alert/40",
    fondo: "bg-state-alert/10",
    relleno: "bg-state-alert",
  },
  "no-auditable": {
    label: "No auditable",
    descripcion: "El sistema no pudo medir con confianza suficiente",
    Icono: CircleSlash,
    texto: "text-state-none",
    borde: "border-state-none/40",
    fondo: "bg-state-none/10",
    relleno: "bg-state-none",
  },
} as const satisfies Record<Estado, unknown>;

/** Pastilla compacta: icono + texto. Nunca renderiza color sin etiqueta. */
export function EstadoBadge({
  estado,
  children,
  className,
}: {
  estado: Estado;
  children?: React.ReactNode;
  className?: string;
}) {
  const e = ESTADOS[estado];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-widest",
        e.texto,
        e.borde,
        e.fondo,
        className,
      )}
    >
      <e.Icono className="h-3 w-3 shrink-0" aria-hidden />
      {children ?? e.label}
    </span>
  );
}
