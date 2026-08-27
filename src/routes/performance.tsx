import { createFileRoute, redirect } from "@tanstack/react-router";

/**
 * La pantalla de performance se unifico en /reporte (fase 2).
 * Se conserva la ruta como redireccion para que no queden enlaces rotos.
 */
export const Route = createFileRoute("/performance")({
  beforeLoad: () => {
    throw redirect({ to: "/reporte" });
  },
});
