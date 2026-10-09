import { useEffect, type ReactNode } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useSesion } from "@/lib/sesion";

/**
 * Pantallas que requieren sesión (especificación §3: con sesión, Biblioteca · Cargar · Perfil).
 *
 * Esto es una comodidad de la interfaz, no la seguridad: la barrera real está en la base (RLS y permisos
 * por columna) y en la API (JWT + propiedad del video). Quien no tiene sesión simplemente no ve datos.
 */
export function RutaProtegida({ children }: { children: ReactNode }) {
  const { sesion, cargando } = useSesion();
  const navegar = useNavigate();

  useEffect(() => {
    if (!cargando && !sesion) navegar({ to: "/ingreso" });
  }, [cargando, sesion, navegar]);

  if (cargando || !sesion) {
    return (
      <main className="mx-auto flex min-h-[50vh] max-w-md items-center justify-center px-6">
        <p className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          Verificando tu sesión…
        </p>
      </main>
    );
  }
  return <>{children}</>;
}
