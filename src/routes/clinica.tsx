import { createFileRoute, redirect } from "@tanstack/react-router";

/**
 * La pantalla clinica se unifico en /reporte (fase 2).
 * Se conserva la ruta como redireccion para que no queden enlaces rotos.
 */
export const Route = createFileRoute("/clinica")({
  beforeLoad: () => {
    throw redirect({ to: "/reporte" });
  },
});
