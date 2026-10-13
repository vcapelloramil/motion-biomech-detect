import { createFileRoute, redirect } from "@tanstack/react-router";

/**
 * Esta ruta mostraba un reporte de ejemplo con valores inventados (y un veredicto que las decisiones 035 y 036
 * retiraron). Se conserva solo como redireccion para que no queden enlaces rotos: el reporte real vive en
 * /reporte/$videoId y se llega desde la biblioteca.
 */
export const Route = createFileRoute("/reporte/")({
  beforeLoad: () => {
    throw redirect({ to: "/videos" });
  },
});
