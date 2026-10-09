import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";
import { getSupabase } from "@/lib/supabase";

/**
 * Sesión de Supabase para toda la aplicación.
 *
 * `cargando` es `true` hasta que se lee la sesión guardada en el navegador. En el servidor (SSR) y en el
 * primer render del cliente siempre es `true`, así que ambos renderizan lo mismo y no hay desajuste de
 * hidratación; las rutas protegidas esperan a que termine antes de decidir.
 */

type ValorSesion = {
  sesion: Session | null;
  cargando: boolean;
  /** Nombre para mostrar: el que se eligió al registrarse, o la parte local del correo. */
  nombre: string | null;
  cerrarSesion: () => Promise<void>;
};

const Contexto = createContext<ValorSesion>({
  sesion: null,
  cargando: true,
  nombre: null,
  cerrarSesion: async () => {},
});

export function SesionProvider({ children }: { children: ReactNode }) {
  const [sesion, setSesion] = useState<Session | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const supabase = getSupabase();
    if (!supabase) {
      setCargando(false);
      return;
    }
    let activo = true;
    supabase.auth.getSession().then(({ data }) => {
      if (!activo) return;
      setSesion(data.session);
      setCargando(false);
    });
    const { data } = supabase.auth.onAuthStateChange((_evento, nueva) => {
      setSesion(nueva);
      setCargando(false);
    });
    return () => {
      activo = false;
      data.subscription.unsubscribe();
    };
  }, []);

  const cerrarSesion = useCallback(async () => {
    await getSupabase()?.auth.signOut();
  }, []);

  const valor = useMemo<ValorSesion>(() => {
    const meta = sesion?.user.user_metadata as { nombre?: string } | undefined;
    const nombre = sesion ? (meta?.nombre?.trim() || sesion.user.email?.split("@")[0] || null) : null;
    return { sesion, cargando, nombre, cerrarSesion };
  }, [sesion, cargando, cerrarSesion]);

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useSesion(): ValorSesion {
  return useContext(Contexto);
}
