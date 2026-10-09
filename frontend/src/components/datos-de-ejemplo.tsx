import { FlaskConical } from "lucide-react";

/**
 * Marca visible de las pantallas que todavía muestran datos simulados (plan de punta a punta §5).
 *
 * Un dato de ejemplo presentado como del usuario es un dato equivocado presentado como bueno (R3/R4).
 * La marca lleva ícono y texto, no solo color, y se reemplaza por los datos reales cuando la pantalla
 * se conecta (se cambia el origen de los datos, no la pantalla).
 */
export function DatosDeEjemplo({ detalle }: { detalle?: string }) {
  return (
    <div
      role="note"
      className="mx-auto mt-4 flex max-w-7xl items-start gap-3 rounded-lg border border-dashed border-state-warn/60 bg-state-warn/10 px-4 py-3 text-sm"
    >
      <FlaskConical className="mt-0.5 h-4 w-4 shrink-0 text-state-warn" aria-hidden="true" />
      <p>
        <strong className="font-semibold">Datos de ejemplo.</strong>{" "}
        {detalle ?? "Esta pantalla todavía no muestra tus datos reales: lo que ves es una maqueta con valores inventados."}
      </p>
    </div>
  );
}
